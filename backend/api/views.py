from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.http import HttpResponse
from agent.models import Conversation, Message, KnowledgeBase, SuggestedQuestion, PDFDocument
from .serializers import (
    ConversationSerializer, MessageSerializer, ChatRequestSerializer,
    ChatResponseSerializer, SuggestedQuestionSerializer, KnowledgeBaseSerializer,
    PDFDocumentSerializer
)
from agent import get_luna_agent, LunaDeepAgent  # Using DeepAgent implementation
from agent.data_ingestor import OneDevelopmentDataIngestor
from agent.pdf_processor import PDFProcessor
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime, timedelta
import random
import os
import requests
import logging
from openai import OpenAI
from pathlib import Path
from django.conf import settings
from livekit.api import AccessToken, VideoGrants

logger = logging.getLogger(__name__)

# Initialize OpenAI client for TTS
_openai_client = None

def get_openai_client():
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI()
    return _openai_client


# ============================================================================
# AGENT INITIALIZATION
# ============================================================================

def get_agent() -> LunaDeepAgent:
    """
    Get the Luna DeepAgent instance.
    
    Luna is an autonomous ReAct agent that decides its own path through reasoning.
    No more rigid pipelines - Luna thinks and acts dynamically.
    """
    return get_luna_agent()


@api_view(['POST'])
def chat(request):
    """
    Main chat endpoint - Luna AI Assistant
    
    POST /api/chat/
    {
        "message": "Tell me about One Development",
        "session_id": "optional-session-id"
    }
    
    Response includes:
    - response: Luna's answer
    - session_id: Session identifier for conversation continuity
    - reasoning_steps: How many think/act cycles Luna used (ReAct mode)
    - suggested_actions: Follow-up suggestions
    """
    serializer = ChatRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    message = serializer.validated_data['message']
    session_id = serializer.validated_data.get('session_id') or str(uuid.uuid4())
    
    # Get or create conversation
    conversation, created = Conversation.objects.get_or_create(
        session_id=session_id,
        defaults={'metadata': {'agent_type': 'deepagent'}}
    )
    
    # Save user message
    user_message = Message.objects.create(
        conversation=conversation,
        message_type='human',
        content=message
    )
    
    # Get conversation history
    history = list(
        conversation.messages.order_by('created_at').values('message_type', 'content')
    )
    
    # Process through agent
    agent = get_agent()
    result = agent.process_query(
        query=message,
        session_id=session_id,
        conversation_history=history
    )
    
    # Build metadata from DeepAgent response
    metadata = {
        'reasoning_steps': result.get('reasoning_steps', 0),
        'tools_used': result.get('tools_used', 0),
        'agent_type': 'deepagent',
        'thinking': result.get('thinking', []),
        'tools_info': result.get('tools_info', []),
        'sources': result.get('sources', [])  # Include sources in metadata
    }
    suggested_actions = _generate_suggested_actions_from_response(result['response'])
    
    # Save AI response
    ai_message = Message.objects.create(
        conversation=conversation,
        message_type='ai',
        content=result['response'],
        metadata=metadata
    )
    
    # Prepare response
    response_data = {
        'response': result['response'],
        'session_id': session_id,
        'suggested_actions': suggested_actions,
        'timestamp': timezone.now(),
        'metadata': metadata,
        'sources': result.get('sources', [])  # Include sources in top-level response
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def chat_stream(request):
    """
    TRUE Streaming chat endpoint - Shows Luna's actual thinking token by token
    Like Cursor's agent mode - you see every token as Luna thinks.
    
    POST /api/chat/stream/
    {
        "message": "Tell me about One Development",
        "session_id": "optional-session-id"
    }
    
    Returns: Server-Sent Events (SSE) stream with:
    - phase: Current phase (thinking/searching/responding)
    - thinking_token: Each token of Luna's thinking process
    - tool_start: When Luna starts using a tool
    - tool_result: Tool result preview
    - response_token: Each token of the final response
    - done: Complete with full response
    """
    from django.http import StreamingHttpResponse
    from agent.streaming_agent import get_streaming_agent
    import json
    
    message = request.data.get('message', '')
    session_id = request.data.get('session_id') or str(uuid.uuid4())
    
    if not message:
        return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    def generate_stream():
        """Generator that yields SSE events with actual LLM tokens"""
        try:
            # Get or create conversation
            conversation, _ = Conversation.objects.get_or_create(
                session_id=session_id,
                defaults={'metadata': {'agent_type': 'streaming'}}
            )
            
            # Save user message
            Message.objects.create(
                conversation=conversation,
                message_type='human',
                content=message
            )
            
            # Get streaming agent
            agent = get_streaming_agent()
            
            full_response = ""
            
            # Stream actual thinking and response tokens
            for event in agent.stream_thinking_and_response(message, session_id):
                event_type = event.get('type')
                
                if event_type == 'phase':
                    yield f"data: {json.dumps({'type': 'phase', 'phase': event['content']})}\n\n"
                
                elif event_type == 'thinking_token':
                    # Stream each thinking token
                    yield f"data: {json.dumps({'type': 'thinking', 'token': event['content']})}\n\n"
                
                elif event_type == 'thinking_complete':
                    yield f"data: {json.dumps({'type': 'thinking_done'})}\n\n"
                
                elif event_type == 'tool_start':
                    yield f"data: {json.dumps({'type': 'tool', 'action': 'start', 'tool': event['tool'], 'query': event.get('query', '')})}\n\n"
                
                elif event_type == 'tool_result':
                    yield f"data: {json.dumps({'type': 'tool', 'action': 'result', 'content': event['content']})}\n\n"
                
                elif event_type == 'tool_error':
                    yield f"data: {json.dumps({'type': 'tool', 'action': 'error', 'content': event['content']})}\n\n"
                
                elif event_type == 'response_token':
                    # Stream each response token
                    full_response += event['content']
                    yield f"data: {json.dumps({'type': 'response', 'token': event['content']})}\n\n"
                
                elif event_type == 'done':
                    full_response = event.get('full_response', full_response)
                    
                    # Save AI response
                    Message.objects.create(
                        conversation=conversation,
                        message_type='ai',
                        content=full_response,
                        metadata={'agent_type': 'streaming'}
                    )
                    
                    yield f"data: {json.dumps({'type': 'done', 'suggested_actions': _generate_suggested_actions_from_response(full_response)})}\n\n"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    response = StreamingHttpResponse(
        generate_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


def _generate_suggested_actions_from_response(response: str) -> list:
    """
    Generate contextual suggested actions based on Luna's response.
    This provides follow-up questions that make sense in context.
    """
    response_lower = response.lower()
    
    # Context-aware suggestions
    if any(word in response_lower for word in ['property', 'properties', 'villa', 'apartment', 'unit']):
        return [
            "What are the prices?",
            "Tell me about the amenities",
            "Can I schedule a viewing?"
        ]
    elif any(word in response_lower for word in ['price', 'cost', 'aed', 'payment']):
        return [
            "What payment plans are available?",
            "Are there any promotions?",
            "What's the ROI potential?"
        ]
    elif any(word in response_lower for word in ['invest', 'roi', 'return', 'rental']):
        return [
            "Which areas have best returns?",
            "Tell me about payment plans",
            "Can I speak with an advisor?"
        ]
    elif any(word in response_lower for word in ['contact', 'team', 'sales', 'call']):
        return [
            "What are your office hours?",
            "Where are you located?",
            "Can I schedule a meeting?"
        ]
    else:
        return [
            "Tell me about your projects",
            "What makes One Development unique?",
            "How can I invest in Dubai property?"
        ]


@api_view(['GET'])
def get_suggested_questions(request):
    """
    Get rotating suggested questions
    
    GET /api/suggested-questions/?count=3
    """
    count = int(request.query_params.get('count', 3))
    
    # Get random active questions
    questions = SuggestedQuestion.objects.filter(is_active=True)
    
    if questions.count() > count:
        questions = random.sample(list(questions), count)
    else:
        questions = list(questions)
    
    serializer = SuggestedQuestionSerializer(questions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_conversation_history(request, session_id):
    """
    Get conversation history for a session
    
    GET /api/conversations/{session_id}/
    """
    try:
        conversation = Conversation.objects.get(session_id=session_id)
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Conversation.DoesNotExist:
        return Response(
            {'error': 'Conversation not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def ingest_data(request):
    """
    Trigger data ingestion from various sources
    
    POST /api/ingest-data/
    {
        "source": "website|linkedin|manual",
        "data": {...}  // For manual ingestion
    }
    """
    source = request.data.get('source', 'initial')
    
    ingestor = OneDevelopmentDataIngestor()
    agent = get_agent()
    
    if source == 'website':
        # Scrape website
        data = ingestor.scrape_website(max_pages=20)
    elif source == 'linkedin':
        # Get LinkedIn data
        data = [ingestor.scrape_linkedin_company()]
    elif source == 'initial':
        # Get initial knowledge
        data = ingestor.get_initial_knowledge()
    else:
        return Response(
            {'error': 'Invalid source'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Store in database and vector store
    count = 0
    for item in data:
        # Store in database
        kb_entry = KnowledgeBase.objects.create(
            source_type=item.get('source_type', 'manual'),
            source_url=item.get('url'),
            title=item.get('title', 'Untitled'),
            content=item.get('content', ''),
            summary=item.get('content', '')[:500],
            metadata=item
        )
        
        # Add to agent's vector store
        agent.add_knowledge(
            content=item.get('content', ''),
            metadata={'source': item.get('source_type'), 'title': item.get('title')}
        )
        count += 1
    
    return Response(
        {'message': f'Successfully ingested {count} items', 'count': count},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint
    
    GET /api/health/
    
    Returns agent status and configuration
    """
    try:
        agent = get_agent()
        agent_ready = agent is not None
        agent_type = 'deepagent'
        
        # Get tool count
        tools_count = len(agent.tools) if hasattr(agent, 'tools') else 0
            
    except Exception as e:
        agent_ready = False
        agent_type = 'error'
        tools_count = 0
    
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now(),
        'agent': {
            'initialized': agent_ready,
            'type': agent_type,
            'name': 'Luna',
            'tools_available': tools_count
        },
        'version': '4.0.0'  # DeepAgents implementation
    }, status=status.HTTP_200_OK)


class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing knowledge base entries
    """
    queryset = KnowledgeBase.objects.filter(is_active=True)
    serializer_class = KnowledgeBaseSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        source_type = self.request.query_params.get('source_type')
        
        if source_type:
            queryset = queryset.filter(source_type=source_type)
        
        return queryset.order_by('-created_at')


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and managing conversations
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    lookup_field = 'session_id'
    
    def get_queryset(self):
        """Return conversations ordered by most recent"""
        return Conversation.objects.all().order_by('-updated_at')
    
    def destroy(self, request, *args, **kwargs):
        """Delete a conversation and all its messages"""
        try:
            conversation = self.get_object()
            conversation.delete()
            return Response(
                {'message': 'Conversation deleted successfully'},
                status=status.HTTP_200_OK
            )
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'])
    def clear_history(self, request, session_id=None):
        """Clear conversation messages but keep the conversation"""
        try:
            conversation = self.get_object()
            conversation.messages.all().delete()
            return Response(
                {'message': 'Conversation history cleared'},
                status=status.HTTP_200_OK
            )
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['delete'], url_path='delete-all')
    def delete_all(self, request):
        """Delete all conversations and their messages"""
        deleted_count, _ = Conversation.objects.all().delete()
        if deleted_count == 0:
            return Response(
                {'message': 'No conversations to delete'},
                status=status.HTTP_200_OK
            )
        return Response(
            {'message': 'All conversations deleted successfully'},
            status=status.HTTP_200_OK
        )


class PDFDocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing PDF documents
    Only accessible via admin panel
    """
    queryset = PDFDocument.objects.all()  # Show all documents, not just active
    serializer_class = PDFDocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Save PDF and trigger indexing"""
        pdf_document = serializer.save()
        
        # Process and index the PDF
        processor = PDFProcessor()
        try:
            processor.process_and_index_pdf(pdf_document)
        except Exception as e:
            # Mark as not indexed if there's an error
            pdf_document.is_indexed = False
            pdf_document.save()
            # Re-raise to let the create method handle the error
            raise
    
    @action(detail=True, methods=['post'])
    def reindex(self, request, pk=None):
        """Manually trigger reindexing of a PDF"""
        pdf_document = self.get_object()
        processor = PDFProcessor()
        
        try:
            result = processor.process_and_index_pdf(pdf_document)
            return Response({
                'message': 'PDF reindexed successfully',
                'result': result
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': f'Failed to reindex PDF: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def reindex_all(self, request):
        """Reindex all active PDFs"""
        processor = PDFProcessor()
        results = processor.reindex_all_pdfs()
        
        return Response({
            'message': 'Reindexing completed',
            'results': results
        }, status=status.HTTP_200_OK)


# ============================================================================
# AVATAR SERVICE INTEGRATION
# ============================================================================

# OpenAI TTS Voices mapping
OPENAI_TTS_VOICES = {
    'default': 'nova',      # Warm, natural female - perfect for Luna
    'nova': 'nova',         # Warm, friendly female
    'shimmer': 'shimmer',   # Expressive female
    'alloy': 'alloy',       # Neutral, balanced
    'echo': 'echo',         # Deeper male
    'fable': 'fable',       # British accent
    'onyx': 'onyx',         # Deep, authoritative male
}

@api_view(['POST'])
def generate_avatar(request):
    """
    Generate a photorealistic talking avatar video using HeyGen.
    
    HeyGen provides industry-leading lip-sync quality for realistic talking avatars.
    This creates videos directly in the cloud - no laptop or GPU needed!
    
    POST /api/avatar/generate/
    {
        "text": "Hello, I'm Luna",
        "voice_id": "en-US-JennyNeural"  // Optional voice for TTS
    }
    
    Response:
    {
        "video_url": "/api/avatar/videos/uuid.mp4",
        "video_id": "uuid",
        "duration": 5.2,
        "status": "generated"
    }
    """
    from agent.heygen_video import get_heygen_video
    from django.conf import settings
    
    text = request.data.get('text')
    if not text:
        return Response({
            'error': 'Text is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Use HeyGen's Juniper voice (warm, natural female voice perfect for Luna)
        voice_id = request.data.get('voice_id', 'Juniper')
        video_id = str(uuid.uuid4())
        
        logger.info(f"🎬 Generating realistic talking avatar with HeyGen...")
        logger.info(f"   Text: {text[:50]}...")
        logger.info(f"   Voice: {voice_id} (HeyGen Juniper)")
        
        # Get HeyGen video generator
        video_gen = get_heygen_video()
        
        if not video_gen.is_available():
            return Response({
                'error': 'HeyGen not configured. Set HEYGEN_API_KEY in environment.',
                'fallback': True
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Path to Luna's image
        luna_image = Path(settings.BASE_DIR).parent / 'frontend' / 'public' / 'Luna.png'
        
        if not luna_image.exists():
            logger.error(f"❌ Luna image not found: {luna_image}")
            return Response({
                'error': 'Luna image not found',
                'fallback': True
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        # Generate video with HeyGen using Juniper voice
        # This creates a realistic lip-synced video directly - no laptop needed!
        temp_video_dir = Path(settings.BASE_DIR) / 'temp_videos'
        temp_video_dir.mkdir(exist_ok=True)
        video_path = temp_video_dir / f"{video_id}.mp4"
        
        video_bytes = video_gen.generate_talking_video(
            text=text,
            image_path=str(luna_image),
            audio_url=None,  # Use HeyGen's built-in TTS with Juniper voice
            output_path=str(video_path),
            voice_id=voice_id
        )
        
        if not video_bytes:
            logger.error("❌ HeyGen video generation failed")
            return Response({
                'error': 'Video generation failed',
                'fallback': True
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Estimate duration from text
        words = len(text.split())
        duration = (words / 150) * 60  # 150 words per minute
        
        # Build video URL
        scheme = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        video_url = f"{scheme}://{host}/api/avatar/videos/{video_id}.mp4"
        
        logger.info(f"✅ HeyGen video generated successfully!")
        logger.info(f"   Video URL: {video_url}")
        logger.info(f"   Duration: ~{duration:.1f}s")
        
        # Schedule cleanup after 1 hour
        import threading
        def cleanup():
            import time
            time.sleep(3600)  # 1 hour
            if video_path.exists():
                video_path.unlink()
                logger.info(f"🗑️  Cleaned up video: {video_id}.mp4")
        
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()
        
        return Response({
            'video_url': video_url,
            'video_id': video_id,
            'duration': duration,
            'status': 'generated',
            'provider': 'HeyGen'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ HeyGen video generation error: {str(e)}")
        logger.exception("Full traceback:")
        return Response({
            'error': f'Video generation error: {str(e)}',
            'fallback': True
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def avatar_health(request):
    """
    Check if HeyGen avatar service is available and healthy.
    
    GET /api/avatar/health/
    """
    from agent.heygen_video import get_heygen_video
    
    try:
        video_gen = get_heygen_video()
        
        if video_gen.is_available():
            return Response({
                'status': 'healthy',
                'provider': 'HeyGen',
                'message': 'HeyGen avatar service is ready',
                'cloud_based': True
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'unavailable',
                'provider': 'HeyGen',
                'message': 'HeyGen API key not configured. Set HEYGEN_API_KEY in environment.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
    except Exception as e:
        return Response({
            'status': 'unavailable',
            'message': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


from django.http import StreamingHttpResponse, HttpResponse

@api_view(['GET'])
def avatar_audio(request, audio_id):
    """
    Serve temporary OpenAI TTS audio files for avatar generation.
    
    GET /api/avatar/audio/{audio_id}.mp3
    """
    try:
        temp_audio_dir = Path(settings.BASE_DIR) / 'temp_audio'
        audio_path = temp_audio_dir / f"{audio_id}.mp3"
        
        if not audio_path.exists():
            return Response({
                'error': 'Audio file not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Read and serve audio file
        with open(audio_path, 'rb') as f:
            audio_content = f.read()
        
        return HttpResponse(audio_content, content_type='audio/mpeg')
    except Exception as e:
        logger.error(f"Error serving avatar audio: {e}")
        return Response({
            'error': 'Failed to serve audio'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def avatar_video_proxy(request, video_id):
    """
    Proxy video streaming from the local GPU avatar service to the browser.
    
    Optimized for fast streaming with HTTP Range request support.
    This allows videos to start playing as soon as enough data is buffered.
    
    GET /api/avatar/videos/<video_id>.mp4
    Supports Range requests for efficient video seeking.
    """
    avatar_service_url = os.getenv('AVATAR_SERVICE_URL')
    
    if not avatar_service_url:
        return HttpResponse('Avatar service not configured', status=503)
    
    try:
        # Stream video from local avatar service
        video_url = f"{avatar_service_url}/videos/{video_id}"
        logger.info(f"Proxying video from: {video_url}")
        
        # Prepare headers for range request support
        headers = {}
        range_header = request.META.get('HTTP_RANGE', '')
        if range_header:
            headers['Range'] = range_header
        
        # Use larger chunk size for faster transfer (64KB instead of 8KB)
        response = requests.get(video_url, stream=True, timeout=60, headers=headers)
        
        if response.status_code in [200, 206]:  # 206 = Partial Content (Range request)
            def generate():
                # Use larger chunks for faster streaming
                for chunk in response.iter_content(chunk_size=65536):  # 64KB chunks
                    if chunk:
                        yield chunk
            
            streaming_response = StreamingHttpResponse(
                generate(),
                content_type='video/mp4'
            )
            
            # Essential headers for video streaming
            streaming_response['Content-Disposition'] = f'inline; filename="{video_id}"'
            streaming_response['Accept-Ranges'] = 'bytes'
            streaming_response['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
            
            # CORS headers for video streaming
            streaming_response['Access-Control-Allow-Origin'] = '*'
            streaming_response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
            streaming_response['Access-Control-Expose-Headers'] = 'Content-Length, Content-Range, Accept-Ranges'
            
            # Forward headers from local service
            if 'Content-Length' in response.headers:
                streaming_response['Content-Length'] = response.headers['Content-Length']
            if 'Content-Range' in response.headers:
                streaming_response['Content-Range'] = response.headers['Content-Range']
            
            # Set status code (206 for partial content, 200 for full)
            streaming_response.status_code = response.status_code
            
            return streaming_response
        else:
            # Try serving from local temp_videos as fallback
            logger.warning(f"Video not on avatar service, trying local storage...")
            video_path = Path(settings.BASE_DIR) / 'temp_videos' / video_id
            
            if video_path.exists():
                logger.info(f"✅ Found video in local storage: {video_id}")
                response = FileResponse(
                    open(video_path, 'rb'),
                    content_type='video/mp4'
                )
                response['Content-Disposition'] = f'inline; filename="{video_id}"'
                response['Accept-Ranges'] = 'bytes'
                response['Cache-Control'] = 'public, max-age=3600'
                return response
            else:
                logger.error(f"Video not found anywhere: {video_id}")
            return HttpResponse('Video not found', status=404)
            
    except requests.exceptions.ConnectionError:
        # If avatar service not available, try local storage
        logger.info("Avatar service not available, trying local storage...")
        try:
            video_path = Path(settings.BASE_DIR) / 'temp_videos' / video_id
            
            if video_path.exists():
                logger.info(f"✅ Serving from local storage: {video_id}")
                response = FileResponse(
                    open(video_path, 'rb'),
                    content_type='video/mp4'
                )
                response['Content-Disposition'] = f'inline; filename="{video_id}"'
                response['Accept-Ranges'] = 'bytes'
                response['Cache-Control'] = 'public, max-age=3600'
                return response
            else:
                return HttpResponse('Video not found', status=404)
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")
            return HttpResponse('Video not available', status=503)
    except Exception as e:
        logger.error(f"Error serving video: {e}")
        return HttpResponse('Error serving video', status=500)


@api_view(['GET'])
def get_last_avatar_video(request):
    """
    Get the URL of the last generated avatar video.
    
    GET /api/avatar/last-video/
    
    Response:
    {
        "video_url": "https://tunnel-url/videos/uuid.mp4",
        "video_id": "uuid",
        "exists": true
    }
    """
    avatar_service_url = os.getenv('AVATAR_SERVICE_URL')
    
    if not avatar_service_url:
        return Response({
            'error': 'Avatar service not configured',
            'exists': False
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    try:
        # Try to get the last video from the avatar service
        # First, try calling a /last-video endpoint if it exists
        try:
            response = requests.get(
                f"{avatar_service_url}/last-video",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Avatar service returned: {data}")
                # Rewrite video URL to go through our proxy
                if 'video_url' in data and data.get('video_id'):
                    scheme = 'https' if request.is_secure() else 'http'
                    host = request.get_host()
                    video_id = data['video_id']
                    if not video_id.endswith('.mp4'):
                        video_id = f"{video_id}.mp4"
                    data['video_url'] = f"{scheme}://{host}/api/avatar/videos/{video_id}"
                    logger.info(f"Rewritten video URL: {data['video_url']}")
                # Ensure exists field is set
                if 'exists' not in data:
                    data['exists'] = bool(data.get('video_url'))
                return Response(data)
        except requests.exceptions.RequestException:
            # If /last-video endpoint doesn't exist, try to list videos
            pass
        
        # Fallback: Try to get list of videos and return the latest
        try:
            response = requests.get(
                f"{avatar_service_url}/videos",
                timeout=5
            )
            if response.status_code == 200:
                videos = response.json()
                if videos and len(videos) > 0:
                    # Get the latest video (assuming they're sorted by date)
                    latest = videos[-1] if isinstance(videos, list) else videos.get('latest')
                    if latest:
                        video_id = latest.get('video_id') or latest.get('id') or latest.get('filename', '').replace('.mp4', '')
                        if video_id:
                            scheme = 'https' if request.is_secure() else 'http'
                            host = request.get_host()
                            if not video_id.endswith('.mp4'):
                                video_id = f"{video_id}.mp4"
                            return Response({
                                'video_url': f"{scheme}://{host}/api/avatar/videos/{video_id}",
                                'video_id': video_id.replace('.mp4', ''),
                                'exists': True
                            })
        except requests.exceptions.RequestException:
            pass
        
        # If no endpoint exists, return not found
        return Response({
            'error': 'No video endpoint available on avatar service',
            'exists': False
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Error getting last video: {e}")
        return Response({
            'error': str(e),
            'exists': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.error(f"Error proxying video: {str(e)}")
        return HttpResponse(f'Error: {str(e)}', status=500)


# ============================================================================
# TEXT-TO-SPEECH (ElevenLabs - High Quality & Fast!)
# ============================================================================

# ElevenLabs Voice Options for Luna:
# - default/luna: Rachel (Professional, warm female - Luna's main voice)
# - professional: Sarah (Business-like)
# - friendly: Bella (Casual, friendly)
# - elegant: Charlotte (Sophisticated)
# - energetic: Nicole (Upbeat, enthusiastic)

@api_view(['POST'])
def generate_tts(request):
    """Generate realistic speech using OpenAI TTS API."""
    text = request.data.get('text', '').strip()
    voice_id = request.data.get('voice', 'nova')
    
    if not text:
        return Response({
            'error': 'Text is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if len(text) > 4096:
        text = text[:4096]
    
    try:
        logger.info(f"Generating OpenAI TTS with voice {voice_id}")
        return _generate_openai_tts_fallback(text, voice_id)
    except Exception as e:
        logger.error(f"OpenAI TTS error: {str(e)}")
        return Response({
            'error': f'TTS generation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _generate_openai_tts_fallback(text: str, voice_id: str) -> HttpResponse:
    """
    Fallback to OpenAI TTS if ElevenLabs fails or is unavailable
    """
    try:
        client = get_openai_client()
        
        # Map ElevenLabs voice IDs to OpenAI voices
        voice_mapping = {
            'luna': 'nova',
            'default': 'nova',
            'professional': 'alloy',
            'friendly': 'shimmer',
            'elegant': 'nova',
            'energetic': 'shimmer',
        }
        openai_voice = voice_mapping.get(voice_id, 'nova')
        
        logger.info(f"🔄 Using OpenAI TTS fallback with voice '{openai_voice}'")
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=openai_voice,
            input=text,
            response_format="mp3"
        )
        
        audio_content = response.content
        
        http_response = HttpResponse(audio_content, content_type='audio/mpeg')
        http_response['Content-Disposition'] = 'inline; filename="luna_speech.mp3"'
        http_response['Content-Length'] = len(audio_content)
        http_response['X-TTS-Provider'] = 'OpenAI-Fallback'
        http_response['X-TTS-Voice'] = openai_voice
        
        return http_response
    except Exception as e:
        logger.error(f"OpenAI TTS fallback failed: {e}")
        raise


@api_view(['GET'])
def tts_voices(request):
    """
    Get available TTS voices (ElevenLabs).
    
    GET /api/tts/voices/
    """
    from agent.elevenlabs_tts import get_elevenlabs_tts
    
    # ElevenLabs voices
    voices = [
        {'id': 'luna', 'name': 'Luna (Rachel)', 'description': 'Professional, warm female - Luna\'s signature voice!', 'default': True, 'provider': 'ElevenLabs'},
        {'id': 'professional', 'name': 'Professional (Sarah)', 'description': 'Business-like, confident', 'default': False, 'provider': 'ElevenLabs'},
        {'id': 'friendly', 'name': 'Friendly (Bella)', 'description': 'Casual, warm, approachable', 'default': False, 'provider': 'ElevenLabs'},
        {'id': 'elegant', 'name': 'Elegant (Charlotte)', 'description': 'Sophisticated, refined', 'default': False, 'provider': 'ElevenLabs'},
        {'id': 'energetic', 'name': 'Energetic (Nicole)', 'description': 'Upbeat, enthusiastic', 'default': False, 'provider': 'ElevenLabs'},
    ]
    
    # Check if ElevenLabs is available
    tts = get_elevenlabs_tts()
    elevenlabs_available = tts.is_available()
    
    return Response({
        'voices': voices,
        'provider': 'ElevenLabs' if elevenlabs_available else 'OpenAI (Fallback)',
        'elevenlabs_available': elevenlabs_available
    }, status=status.HTTP_200_OK)


# ============================================================================
# CONTEXT MONITORING
# ============================================================================

@api_view(['POST'])
def generate_talking_video(request):
    """
    Generate a talking avatar video using ElevenLabs Image-to-Video.
    Luna.png will speak with natural lip-sync!
    
    POST /api/avatar/elevenlabs-video/
    {
        "text": "Hello! I'm Luna!",
        "voice": "luna"  // optional: luna (default), professional, friendly, elegant, energetic
    }
    
    Returns: MP4 video file
    """
    from agent.elevenlabs_tts import get_elevenlabs_tts
    from django.conf import settings
    import uuid
    
    text = request.data.get('text', '').strip()
    voice_id = request.data.get('voice', 'luna')
    
    if not text:
        return Response({
            'error': 'Text is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Limit text length
    if len(text) > 500:
        text = text[:500]
    
    try:
        logger.info(f"🎬 Generating talking video with ElevenLabs for text: {text[:50]}...")
        
        # Get ElevenLabs manager
        tts = get_elevenlabs_tts()
        
        if not tts.is_available():
            return Response({
                'error': 'ElevenLabs not configured. Set ELEVENLABS_API_KEY in environment.',
                'fallback': True
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Path to Luna's image
        luna_image = Path(settings.BASE_DIR).parent / 'frontend' / 'public' / 'Luna.png'
        
        if not luna_image.exists():
            logger.error(f"❌ Luna.png not found at: {luna_image}")
            return Response({
                'error': 'Luna image not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Generate unique video ID
        video_id = str(uuid.uuid4())
        temp_video_dir = Path(settings.BASE_DIR) / 'temp_videos'
        temp_video_dir.mkdir(exist_ok=True)
        video_path = temp_video_dir / f"{video_id}.mp4"
        
        # Generate talking video
        video_bytes = tts.generate_talking_video(
            text=text,
            image_path=str(luna_image),
            output_path=str(video_path),
            voice=voice_id
        )
        
        if not video_bytes:
            logger.error("❌ Video generation returned empty result")
            return Response({
                'error': 'Video generation failed',
                'fallback': True
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.info(f"✅ Video generated successfully: {len(video_bytes)} bytes")
        
        # Return video file
        from django.http import FileResponse
        
        response = FileResponse(
            open(video_path, 'rb'),
            content_type='video/mp4'
        )
        response['Content-Disposition'] = f'inline; filename="luna_{video_id}.mp4"'
        response['Content-Length'] = len(video_bytes)
        response['X-Video-Provider'] = 'ElevenLabs'
        response['X-Video-Voice'] = voice_id
        
        # Schedule cleanup after 1 hour
        import threading
        def cleanup():
            time.sleep(3600)
            if video_path.exists():
                video_path.unlink()
        threading.Thread(target=cleanup, daemon=True).start()
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Video generation error: {str(e)}")
        logger.exception("Full traceback:")
        return Response({
            'error': f'Video generation failed: {str(e)}',
            'fallback': True
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def serve_temp_video(request, video_filename):
    """
    Serve videos from temp directories (for ElevenLabs videos)
    
    GET /api/avatar/temp-video/<filename>
    """
    from django.http import FileResponse, HttpResponse
    import os
    
    # Check multiple possible locations
    possible_paths = [
        Path('/tmp') / video_filename,
        Path(settings.BASE_DIR) / 'temp_videos' / video_filename,
    ]
    
    for video_path in possible_paths:
        if video_path.exists():
            try:
                return FileResponse(
                    open(video_path, 'rb'),
                    content_type='video/mp4',
                    headers={
                        'Content-Disposition': f'inline; filename="{video_filename}"',
                        'Accept-Ranges': 'bytes',
                        'Cache-Control': 'public, max-age=3600'
                    }
                )
            except Exception as e:
                logger.error(f"Error serving video: {e}")
                return HttpResponse('Error serving video', status=500)
    
    return HttpResponse('Video not found', status=404)


@api_view(['GET'])
def context_status(request):
    """
    Get current context usage status for the agent.
    Shows token usage similar to Cursor's context monitor.
    
    GET /api/context/status/
    Optional params:
    - session_id: Get context for a specific conversation
    
    Response:
    {
        "model": "gpt-4o",
        "max_tokens": 128000,
        "current_tokens": 5432,
        "percentage_used": 4.24,
        "remaining_tokens": 122568,
        "filesystem_active": false,
        "filesystem_threshold": 85,
        "breakdown": {
            "messages": 3200,
            "system_prompt": 1800,
            "tools": 432
        }
    }
    """
    from agent.context_monitor import get_context_monitor
    from langchain_core.messages import HumanMessage, AIMessage
    
    session_id = request.query_params.get('session_id')
    
    # Get conversation messages if session_id provided
    messages = []
    if session_id:
        try:
            conversation = Conversation.objects.get(session_id=session_id)
            msg_list = conversation.messages.order_by('created_at').values('message_type', 'content')
            
            # Convert to LangChain message format
            for msg in msg_list:
                if msg['message_type'] == 'human':
                    messages.append(HumanMessage(content=msg['content']))
                else:
                    messages.append(AIMessage(content=msg['content']))
        except Conversation.DoesNotExist:
            pass
    
    # Get context monitor and analyze
    monitor = get_context_monitor('gpt-4o-mini')
    analysis = monitor.analyze_context(messages)
    
    return Response(analysis, status=status.HTTP_200_OK)


# ============================================================================
# LIVEAVATAR API INTEGRATION
# ============================================================================

@api_view(['POST'])
def liveavatar_create_session_token(request):
    """
    Create a LiveAvatar session token.
    
    POST /api/liveavatar/session-token/
    {
        "avatar_id": "26393b8e-e944-4367-98ef-e2bc75c4b792",  // Optional, defaults to Luna
        "voice_id": "optional-voice-id",
        "context_id": "optional-context-id",
        "mode": "FULL"  // or "CUSTOM"
    }
    
    Returns:
    {
        "session_token": "token-string",
        "session_id": "session-id"
    }
    """
    import os
    
    liveavatar_api_key = os.getenv('LIVEAVATAR_API_KEY')
    if not liveavatar_api_key:
        return Response({
            'error': 'LIVEAVATAR_API_KEY not configured. Please set it in your environment variables.'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    # Get configuration from request
    avatar_id = request.data.get(
        'avatar_id',
        os.getenv('LIVEAVATAR_AVATAR_ID', '33946dd1-8761-452b-b192-b38011b177a9')  # Default Luna avatar (placeholder)
    )
    voice_id = request.data.get('voice_id')
    context_id = request.data.get('context_id')
    mode = request.data.get('mode', 'FULL')
    
    try:
        # Call LiveAvatar API to create session token
        # According to LiveAvatar docs: https://docs.liveavatar.com/docs/quick-start-guide
        liveavatar_base_url = os.getenv('LIVEAVATAR_API_URL', 'https://api.liveavatar.com')
        
        payload = {
            'avatar_id': avatar_id,
            'mode': mode
        }
        
        if voice_id:
            payload['voice_id'] = voice_id
        if context_id:
            payload['context_id'] = context_id
        
        headers = {
            'X-API-KEY': liveavatar_api_key,
            'Content-Type': 'application/json'
        }
        
        logger.info(f"Creating LiveAvatar session token with avatar_id: {avatar_id}, mode: {mode}")
        
        # LiveAvatar API uses /v1/sessions/token (singular) for creating session tokens
        response = requests.post(
            f'{liveavatar_base_url}/v1/sessions/token',
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if not response.ok:
            logger.error(f"LiveAvatar API error: {response.status_code} - {response.text}")
            return Response({
                'error': f'LiveAvatar API error: {response.status_code}',
                'details': response.text
            }, status=status.HTTP_502_BAD_GATEWAY)
        
        data = response.json()
        logger.info(f"LiveAvatar session token created successfully: {data.get('session_id')}")
        
        return Response({
            'session_token': data.get('session_token'),
            'session_id': data.get('session_id'),
            'avatar_id': avatar_id
        }, status=status.HTTP_200_OK)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"LiveAvatar API request failed: {str(e)}")
        return Response({
            'error': f'Failed to connect to LiveAvatar API: {str(e)}'
        }, status=status.HTTP_502_BAD_GATEWAY)
    except Exception as e:
        logger.error(f"LiveAvatar session token creation error: {str(e)}")
        logger.exception("Full traceback:")
        return Response({
            'error': f'Internal error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def liveavatar_start_session(request):
    """
    Start a LiveAvatar session using a session token.
    
    POST /api/liveavatar/sessions/start/
    {
        "session_token": "token-from-create-session-token"
    }
    
    Returns:
    {
        "session_id": "session-id",
        "livekit_url": "wss://...",
        "livekit_token": "token-for-client"
    }
    """
    import os
    
    session_token = request.data.get('session_token')
    if not session_token:
        return Response({
            'error': 'session_token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        liveavatar_base_url = os.getenv('LIVEAVATAR_API_URL', 'https://api.liveavatar.com')
        
        headers = {
            'Authorization': f'Bearer {session_token}',
            'Content-Type': 'application/json'
        }
        
        logger.info("Starting LiveAvatar session...")
        
        response = requests.post(
            f'{liveavatar_base_url}/v1/sessions/start',
            headers=headers,
            timeout=30
        )
        
        if not response.ok:
            logger.error(f"LiveAvatar start session error: {response.status_code} - {response.text}")
            return Response({
                'error': f'LiveAvatar API error: {response.status_code}',
                'details': response.text
            }, status=status.HTTP_502_BAD_GATEWAY)
        
        data = response.json()
        logger.info(f"LiveAvatar session started successfully: {data.get('session_id')}")
        
        return Response({
            'session_id': data.get('session_id'),
            'livekit_url': data.get('livekit_url'),
            'livekit_token': data.get('livekit_token')
        }, status=status.HTTP_200_OK)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"LiveAvatar API request failed: {str(e)}")
        return Response({
            'error': f'Failed to connect to LiveAvatar API: {str(e)}'
        }, status=status.HTTP_502_BAD_GATEWAY)
    except Exception as e:
        logger.error(f"LiveAvatar start session error: {str(e)}")
        logger.exception("Full traceback:")
        return Response({
            'error': f'Internal error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def liveavatar_send_message(request):
    """
    Send a message to the LiveAvatar session (for Full Mode).
    
    POST /api/liveavatar/sessions/<session_id>/message/
    {
        "message": "Hello, I'm Luna!",
        "session_token": "token"
    }
    """
    import os
    
    session_id = request.data.get('session_id')
    message = request.data.get('message')
    session_token = request.data.get('session_token')
    
    if not all([session_id, message, session_token]):
        return Response({
            'error': 'session_id, message, and session_token are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        liveavatar_base_url = os.getenv('LIVEAVATAR_API_URL', 'https://api.liveavatar.com')
        
        headers = {
            'Authorization': f'Bearer {session_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'message': message
        }
        
        logger.info(f"Sending message to LiveAvatar session {session_id}: {message[:50]}...")
        
        response = requests.post(
            f'{liveavatar_base_url}/v1/sessions/{session_id}/message',
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if not response.ok:
            logger.error(f"LiveAvatar send message error: {response.status_code} - {response.text}")
            return Response({
                'error': f'LiveAvatar API error: {response.status_code}',
                'details': response.text
            }, status=status.HTTP_502_BAD_GATEWAY)
        
        data = response.json()
        return Response(data, status=status.HTTP_200_OK)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"LiveAvatar API request failed: {str(e)}")
        return Response({
            'error': f'Failed to connect to LiveAvatar API: {str(e)}'
        }, status=status.HTTP_502_BAD_GATEWAY)
    except Exception as e:
        logger.error(f"LiveAvatar send message error: {str(e)}")
        logger.exception("Full traceback:")
        return Response({
            'error': f'Internal error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def liveavatar_end_session(request, session_id):
    """
    End a LiveAvatar session.
    
    POST /api/liveavatar/sessions/<session_id>/end/
    {
        "session_token": "token"
    }
    """
    import os
    
    session_token = request.data.get('session_token')
    if not session_token:
        return Response({
            'error': 'session_token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        liveavatar_base_url = os.getenv('LIVEAVATAR_API_URL', 'https://api.liveavatar.com')
        
        headers = {
            'Authorization': f'Bearer {session_token}',
            'Content-Type': 'application/json'
        }
        
        logger.info(f"Ending LiveAvatar session {session_id}...")
        
        response = requests.post(
            f'{liveavatar_base_url}/v1/sessions/{session_id}/end',
            headers=headers,
            timeout=30
        )
        
        if not response.ok:
            logger.warning(f"LiveAvatar end session returned {response.status_code}: {response.text}")
            # Don't fail if session already ended
        
        return Response({
            'status': 'ended',
            'session_id': session_id
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"LiveAvatar end session error: {str(e)}")
        # Return success anyway since session cleanup is best-effort
        return Response({
            'status': 'ended',
            'session_id': session_id
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
def liveavatar_send_audio_custom_mode(request, session_id):
    """
    Send audio to LiveAvatar Custom Mode session.
    
    In Custom Mode, you manage the conversation (LLM) and TTS yourself.
    This endpoint accepts audio data and sends it to LiveAvatar for video generation.
    
    POST /api/liveavatar/sessions/<session_id>/audio/
    {
        "audio_data": "base64_encoded_audio_or_file",
        "session_token": "token",
        "format": "mp3"  // or "wav", "ogg"
    }
    
    Returns:
    {
        "status": "sent",
        "session_id": "session-id"
    }
    """
    import os
    import base64
    
    session_token = request.data.get('session_token')
    audio_data = request.data.get('audio_data')  # Base64 encoded or file
    audio_format = request.data.get('format', 'mp3')
    
    if not session_token:
        return Response({
            'error': 'session_token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not audio_data:
        return Response({
            'error': 'audio_data is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        liveavatar_base_url = os.getenv('LIVEAVATAR_API_URL', 'https://api.liveavatar.com')
        
        headers = {
            'Authorization': f'Bearer {session_token}',
            'Content-Type': 'application/json'
        }
        
        # Decode base64 audio if needed
        if isinstance(audio_data, str) and audio_data.startswith('data:'):
            # Data URL format: data:audio/mp3;base64,...
            audio_data = audio_data.split(',')[1]
        
        if isinstance(audio_data, str):
            try:
                audio_bytes = base64.b64decode(audio_data)
            except:
                return Response({
                    'error': 'Invalid audio_data format. Expected base64 encoded audio.'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            audio_bytes = audio_data
        
        # Send audio to LiveAvatar Custom Mode
        # According to LiveAvatar docs, in Custom Mode you send audio via LiveKit WebRTC
        # But we can also use the API endpoint if available
        # For now, we'll return the audio data and LiveKit connection info
        # The frontend will handle the actual WebRTC streaming
        
        logger.info(f"Sending audio to LiveAvatar Custom Mode session {session_id} ({len(audio_bytes)} bytes)")
        
        # Return audio data and session info for frontend to handle WebRTC
        return Response({
            'status': 'ready',
            'session_id': session_id,
            'audio_size': len(audio_bytes),
            'format': audio_format,
            'message': 'Audio ready. Use LiveKit WebRTC connection to send audio track.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"LiveAvatar send audio error: {str(e)}")
        logger.exception("Full traceback:")
        return Response({
            'error': f'Internal error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def liveavatar_chat_with_custom_mode(request):
    """
    Complete pipeline for LiveAvatar Custom Mode:
    1. Process user message through LLM (deepagents) → get text response
    2. Convert text to audio using TTS
    3. Return audio + LiveAvatar session info for Custom Mode
    
    POST /api/liveavatar/chat-custom/
    {
        "message": "Hello, I'm Luna!",
        "session_id": "optional-session-id",
        "avatar_id": "optional-avatar-id",
        "voice": "nova",  // TTS voice
        "livekit_room_url": "optional-custom-livekit-room",
        "livekit_room_token": "optional-custom-livekit-token"
    }
    
    Returns:
    {
        "text_response": "Luna's text response",
        "audio_url": "url-to-audio-file",
        "audio_base64": "base64-encoded-audio",
        "session_id": "liveavatar-session-id",
        "livekit_url": "wss://livekit-room-url",
        "livekit_token": "livekit-token",
        "session_token": "liveavatar-session-token"
    }
    """
    import os
    import base64
    from io import BytesIO
    
    message = request.data.get('message', '').strip()
    session_id = request.data.get('session_id') or str(uuid.uuid4())
    avatar_id = request.data.get(
        'avatar_id',
        os.getenv('LIVEAVATAR_AVATAR_ID', '26393b8e-e944-4367-98ef-e2bc75c4b792')
    )
    voice = request.data.get('voice', 'nova')
    custom_livekit_url = request.data.get('livekit_room_url')
    custom_livekit_token = request.data.get('livekit_room_token')
    
    if not message:
        return Response({
            'error': 'Message is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Step 1: Process message through LLM
        logger.info(f"Processing message: {message}")
        
        # Get or create conversation
        conversation, created = Conversation.objects.get_or_create(
            session_id=session_id,
            defaults={
                'metadata': {'first_message': message[:50] + '...' if len(message) > 50 else message},
                'created_at': timezone.now()
            }
        )
        
        # Save user message
        user_message = Message.objects.create(
            conversation=conversation,
            message_type='human',
            content=message
        )
        
        # Get conversation history
        history = list(
            conversation.messages.order_by('created_at').values('message_type', 'content')
        )
        
        # Process through agent
        agent = get_agent()
        result = agent.process_query(
            query=message,
            session_id=session_id,
            conversation_history=history
        )
        
        text_response = result.get('response', '')
        
        if not text_response:
            return Response({
                'error': 'No response from LLM'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.info(f"LLM response received: {text_response[:50]}...")
        
        # Step 2: Convert text to audio using OpenAI TTS
        logger.info(f"Converting text to audio with voice: {voice}")
        
        # Use existing TTS endpoint logic
        client = get_openai_client()
        voice_mapping = {
            'luna': 'nova',
            'default': 'nova',
            'professional': 'alloy',
            'friendly': 'shimmer',
            'elegant': 'nova',
            'energetic': 'shimmer',
        }
        openai_voice = voice_mapping.get(voice, 'nova')
        
        # Generate audio in WAV format for better compatibility with LiveAvatar
        tts_response = client.audio.speech.create(
            model="tts-1",
            voice=openai_voice,
            input=text_response,
            response_format="wav"  # WAV format for LiveAvatar compatibility
        )
        
        audio_bytes = tts_response.content
        logger.info(f"TTS audio generated (WAV): {len(audio_bytes)} bytes")
        
        # Step 3: Create LiveAvatar Custom Mode session (LiveAvatar handles TTS internally)
        logger.info(f"Creating LiveAvatar session with customer support voice")
        liveavatar_api_key = os.getenv('LIVEAVATAR_API_KEY')
        liveavatar_base_url = os.getenv('LIVEAVATAR_API_URL', 'https://api.liveavatar.com')
        
        if not liveavatar_api_key:
            return Response({
                'error': 'LIVEAVATAR_API_KEY not configured'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Create session token for Custom Mode using LiveAvatar API
        # Use avatar_id from request, fallback to env, then to default
        actual_avatar_id = avatar_id or os.getenv('LIVEAVATAR_AVATAR_ID', '26393b8e-e944-4367-98ef-e2bc75c4b792')
        logger.info(f"Using avatar_id: {actual_avatar_id} (from request: {avatar_id}, from env: {os.getenv('LIVEAVATAR_AVATAR_ID', 'not set')})")
        
        token_payload = {
            'avatar_id': actual_avatar_id,  # Use avatar_id from request or env
            'mode': 'CUSTOM'  # Use CUSTOM mode to push our own audio
        }
        
        # Add custom LiveKit room if provided
        if custom_livekit_url and custom_livekit_token:
            token_payload['livekit_room_url'] = custom_livekit_url
            token_payload['livekit_room_token'] = custom_livekit_token
        
        token_headers = {
            'X-API-KEY': liveavatar_api_key,
            'Content-Type': 'application/json'
        }
        
        token_response = requests.post(
            f'{liveavatar_base_url}/v1/sessions/token',
            headers=token_headers,
            json=token_payload,
            timeout=30
        )
        
        if not token_response.ok:
            return Response({
                'error': f'LiveAvatar session creation failed: {token_response.status_code}',
                'details': token_response.text
            }, status=status.HTTP_502_BAD_GATEWAY)
        
        token_data = token_response.json()
        # The actual data is nested under 'data' key
        data = token_data.get('data', {})
        session_token = data.get('session_token')
        liveavatar_session_id = data.get('session_id')
        
        if not session_token:
            logger.error("Session token is None - token creation failed")
            return Response({
                'error': 'Failed to create session token',
                'details': 'No session token in response'
            }, status=status.HTTP_502_BAD_GATEWAY)
        
        # Start the session (Empty for Custom Mode - we'll send audio separately)
        start_headers = {
            'Authorization': f'Bearer {session_token}',
            'Content-Type': 'application/json'
        }
        
        start_payload = {}
        
        logger.info(f"Starting Custom Mode session (no text - audio only)")
        start_response = requests.post(
            f'{liveavatar_base_url}/v1/sessions/start',
            headers=start_headers,
            json=start_payload,
            timeout=30
        )
        
        livekit_url = None
        livekit_token = None
        ws_url = None
        if start_response.ok:
            start_data = start_response.json()
            logger.info(f"Start session response keys: {list(start_data.keys())}")
            
            # The actual data is nested under 'data' key
            start_response_data = start_data.get('data', {})
            logger.info(f"Start session data keys: {list(start_response_data.keys())}")
            logger.info(f"Full start session data: {start_response_data}")
            
            livekit_url = start_response_data.get('livekit_url')
            livekit_token = start_response_data.get('livekit_client_token')
            ws_url = start_response_data.get('url') or start_response_data.get('realtime_endpoint') or start_response_data.get('ws_url') or start_response_data.get('websocket_url')
            
            logger.info(f"Extracted URLs - LiveKit: {livekit_url is not None}, WebSocket: {ws_url}")
            logger.info(f"LiveAvatar Custom Mode session started: {liveavatar_session_id}")
            
            # Step 4: Send OpenAI TTS audio to LiveAvatar Custom Mode
            logger.info(f"Sending OpenAI TTS audio to LiveAvatar session {liveavatar_session_id}")
            
            # Try the session-specific audio endpoint with WAV data
            audio_headers = {
                'Authorization': f'Bearer {session_token}',
                'Content-Type': 'audio/wav'
            }
            
            # Send audio data to the session
            audio_response = requests.post(
                f'{liveavatar_base_url}/v1/sessions/{liveavatar_session_id}/audio',
                headers=audio_headers,
                data=audio_bytes,  # Send WAV audio data directly as binary
                timeout=30
            )
            
            logger.info(f"Audio upload response status: {audio_response.status_code}")
            if audio_response.ok:
                logger.info(f"✅ OpenAI TTS audio sent successfully to LiveAvatar")
                logger.info(f"Response: {audio_response.text if audio_response.text else 'Empty response'}")
            else:
                logger.error(f"❌ Failed to send audio to LiveAvatar: {audio_response.status_code}")
                logger.error(f"Error details: {audio_response.text}")
                logger.error(f"Request headers: {audio_headers}")
                logger.error(f"Request URL: {liveavatar_base_url}/v1/sessions/{liveavatar_session_id}/audio")
                
        else:
            # Log error but continue returning Luna's response without streaming info
            logger.error(f"LiveAvatar start session error: {start_response.status_code} - {start_response.text}")
        
        # Encode audio as base64 for frontend fallback
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return Response({
            'text_response': text_response,
            'audio_base64': audio_base64,
            'audio_size': len(audio_bytes),
            'session_id': liveavatar_session_id,
            'livekit_url': livekit_url,
            'livekit_token': livekit_token,
            'url': ws_url,  # Use extracted WebSocket URL
            'realtime_endpoint': ws_url,  # Use same for compatibility
            'session_token': session_token,
            'avatar_id': avatar_id,
            'conversation_session_id': session_id
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"LiveAvatar Custom Mode chat error: {str(e)}")
        logger.exception("Full traceback:")
        return Response({
            'error': f'Internal error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
