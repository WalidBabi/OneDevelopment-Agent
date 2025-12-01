from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from agent.models import Conversation, Message, KnowledgeBase, SuggestedQuestion, PDFDocument
from .serializers import (
    ConversationSerializer, MessageSerializer, ChatRequestSerializer,
    ChatResponseSerializer, SuggestedQuestionSerializer, KnowledgeBaseSerializer,
    PDFDocumentSerializer
)
from agent.langgraph_agent import OneDevelopmentAgent
from agent.luna_react_agent import LunaReActAgent, get_luna_agent
from agent.data_ingestor import OneDevelopmentDataIngestor
from agent.pdf_processor import PDFProcessor
import uuid
from datetime import datetime
import random
import os


# ============================================================================
# AGENT INITIALIZATION
# ============================================================================

# Use environment variable to switch between agents
# Set LUNA_USE_REACT=true to use the new ReAct agent
USE_REACT_AGENT = os.getenv('LUNA_USE_REACT', 'true').lower() == 'true'

# Legacy agent (fixed pipeline)
_legacy_agent_instance = None

def get_legacy_agent():
    """Get the legacy fixed-pipeline agent"""
    global _legacy_agent_instance
    if _legacy_agent_instance is None:
        _legacy_agent_instance = OneDevelopmentAgent()
    return _legacy_agent_instance


def get_agent():
    """
    Get the appropriate agent based on configuration.
    By default, uses the new ReAct agent.
    Set LUNA_USE_REACT=false to use the legacy agent.
    """
    if USE_REACT_AGENT:
        return get_luna_agent()
    else:
        return get_legacy_agent()


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
        defaults={'metadata': {'agent_type': 'react' if USE_REACT_AGENT else 'legacy'}}
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
    
    # Build metadata based on agent type
    if USE_REACT_AGENT:
        # ReAct agent response with thinking visualization
        metadata = {
            'reasoning_steps': result.get('reasoning_steps', 0),
            'tools_used': result.get('tools_used', 0),
            'agent_type': 'react',
            'thinking': result.get('thinking', []),
            'tools_info': result.get('tools_info', [])
        }
        suggested_actions = _generate_suggested_actions_from_response(result['response'])
    else:
        # Legacy agent response
        metadata = {
            'intent': result.get('intent', 'general'),
            'entities': result.get('entities', []),
            'suggested_actions': result.get('suggested_actions', []),
            'agent_type': 'legacy'
        }
        suggested_actions = result.get('suggested_actions', [])
    
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
    
    # Include legacy fields for backward compatibility
    if not USE_REACT_AGENT:
        response_data['intent'] = result.get('intent', 'general')
        response_data['entities'] = result.get('entities', [])
    
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
        agent_type = 'react' if USE_REACT_AGENT else 'legacy'
        
        # Get tool count for ReAct agent
        if USE_REACT_AGENT and hasattr(agent, 'tools'):
            tools_count = len(agent.tools)
        else:
            tools_count = 0
            
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
        'version': '2.0.0'  # ReAct version
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

