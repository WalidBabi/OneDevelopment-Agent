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
import uuid
from datetime import datetime
import random
import os
import requests
import logging
from openai import OpenAI

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
        'tools_info': result.get('tools_info', [])
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
        'metadata': metadata
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
        'version': '3.0.0'  # DeepAgent implementation
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

@api_view(['POST'])
def generate_avatar(request):
    """
    Generate a photorealistic talking avatar video.
    
    This endpoint proxies requests to the GPU avatar service running on your laptop.
    
    POST /api/avatar/generate/
    {
        "text": "Hello, I'm Luna",
        "audio_url": null,  // optional: pre-generated audio
        "voice_id": "default"
    }
    
    Response:
    {
        "video_url": "https://tunnel-url/videos/uuid.mp4",
        "video_id": "uuid",
        "duration": 5.2,
        "status": "generated"
    }
    """
    avatar_service_url = os.getenv('AVATAR_SERVICE_URL')
    
    if not avatar_service_url:
        return Response({
            'error': 'Avatar service not configured. Set AVATAR_SERVICE_URL environment variable.',
            'fallback': True
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    text = request.data.get('text')
    if not text:
        return Response({
            'error': 'Text is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Call the avatar GPU service
        logger.info(f"Requesting avatar generation for text: {text[:50]}...")
        
        response = requests.post(
            f"{avatar_service_url}/generate",
            json={
                'text': text,
                'audio_url': request.data.get('audio_url'),
                'voice_id': request.data.get('voice_id', 'default'),
                'quality': request.data.get('quality', 'fast')  # Default to 'fast' for speed
            },
            timeout=600  # 10 minute timeout for long video generation
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Avatar generated successfully: {data.get('video_id')}")
            return Response(data, status=status.HTTP_200_OK)
        else:
            logger.error(f"Avatar service error: {response.status_code} - {response.text}")
            return Response({
                'error': 'Avatar generation failed',
                'details': response.text,
                'fallback': True
            }, status=response.status_code)
            
    except requests.exceptions.Timeout:
        logger.error("Avatar service timeout")
        return Response({
            'error': 'Avatar generation timed out',
            'fallback': True
        }, status=status.HTTP_504_GATEWAY_TIMEOUT)
        
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to avatar service")
        return Response({
            'error': 'Avatar service unavailable. Make sure the GPU service is running and tunnel is active.',
            'fallback': True
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
    except Exception as e:
        logger.error(f"Unexpected error in avatar generation: {str(e)}")
        return Response({
            'error': f'Avatar generation error: {str(e)}',
            'fallback': True
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def avatar_health(request):
    """
    Check if the avatar GPU service is available and healthy.
    
    GET /api/avatar/health/
    """
    avatar_service_url = os.getenv('AVATAR_SERVICE_URL')
    
    if not avatar_service_url:
        return Response({
            'status': 'unavailable',
            'message': 'Avatar service not configured'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    try:
        response = requests.get(f"{avatar_service_url}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return Response({
                'status': 'healthy',
                'service_info': data,
                'url': avatar_service_url
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'unhealthy',
                'message': 'Service responded with error'
            }, status=response.status_code)
            
    except Exception as e:
        return Response({
            'status': 'unavailable',
            'message': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# ============================================================================
# TEXT-TO-SPEECH (OpenAI)
# ============================================================================

# OpenAI TTS Voice Options:
# - nova: warm, friendly female (best for Luna!)
# - alloy: neutral, balanced
# - echo: deeper male voice
# - fable: British accent
# - onyx: deep, authoritative male
# - shimmer: expressive female

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
def generate_tts(request):
    """
    Generate realistic speech using OpenAI TTS API.
    
    POST /api/tts/generate/
    {
        "text": "Hello, I'm Luna!",
        "voice": "nova"  // optional: nova (default), shimmer, alloy, echo, fable, onyx
    }
    
    Returns: MP3 audio file
    """
    text = request.data.get('text', '').strip()
    voice_id = request.data.get('voice', 'default')
    
    if not text:
        return Response({
            'error': 'Text is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Limit text length to prevent abuse
    if len(text) > 4096:
        text = text[:4096]
    
    # Get the actual voice name
    voice = OPENAI_TTS_VOICES.get(voice_id, 'nova')
    
    try:
        client = get_openai_client()
        
        logger.info(f"Generating TTS with OpenAI voice '{voice}' for text: {text[:50]}...")
        
        # Generate speech using OpenAI TTS
        response = client.audio.speech.create(
            model="tts-1",  # Use "tts-1-hd" for even higher quality (but slower)
            voice=voice,
            input=text,
            response_format="mp3"
        )
        
        # Get the audio content
        audio_content = response.content
        
        logger.info(f"TTS generated successfully, size: {len(audio_content)} bytes")
        
        # Return as audio file
        http_response = HttpResponse(audio_content, content_type='audio/mpeg')
        http_response['Content-Disposition'] = 'inline; filename="speech.mp3"'
        http_response['Content-Length'] = len(audio_content)
        
        return http_response
        
    except Exception as e:
        logger.error(f"OpenAI TTS error: {str(e)}")
        return Response({
            'error': f'TTS generation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def tts_voices(request):
    """
    Get available TTS voices.
    
    GET /api/tts/voices/
    """
    voices = [
        {'id': 'nova', 'name': 'Nova', 'description': 'Warm, friendly female - Luna\'s voice', 'default': True},
        {'id': 'shimmer', 'name': 'Shimmer', 'description': 'Expressive, animated female'},
        {'id': 'alloy', 'name': 'Alloy', 'description': 'Neutral, balanced voice'},
        {'id': 'echo', 'name': 'Echo', 'description': 'Deeper male voice'},
        {'id': 'fable', 'name': 'Fable', 'description': 'British accent'},
        {'id': 'onyx', 'name': 'Onyx', 'description': 'Deep, authoritative male'},
    ]
    return Response({'voices': voices}, status=status.HTTP_200_OK)

