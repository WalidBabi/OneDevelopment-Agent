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
from agent.data_ingestor import OneDevelopmentDataIngestor
from agent.pdf_processor import PDFProcessor
import uuid
from datetime import datetime
import random


# Initialize the agent (singleton pattern)
_agent_instance = None

def get_agent():
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = OneDevelopmentAgent()
    return _agent_instance


@api_view(['POST'])
def chat(request):
    """
    Main chat endpoint
    
    POST /api/chat/
    {
        "message": "Tell me about One Development",
        "session_id": "optional-session-id"
    }
    """
    serializer = ChatRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    message = serializer.validated_data['message']
    session_id = serializer.validated_data.get('session_id') or str(uuid.uuid4())
    
    # Get or create conversation
    conversation, created = Conversation.objects.get_or_create(
        session_id=session_id,
        defaults={'metadata': {}}
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
    
    # Save AI response
    ai_message = Message.objects.create(
        conversation=conversation,
        message_type='ai',
        content=result['response'],
        metadata={
            'intent': result['intent'],
            'entities': result['entities'],
            'suggested_actions': result['suggested_actions']
        }
    )
    
    # Prepare response
    response_data = {
        'response': result['response'],
        'session_id': session_id,
        'intent': result['intent'],
        'entities': result['entities'],
        'suggested_actions': result['suggested_actions'],
        'timestamp': timezone.now()
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


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
    """
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now(),
        'agent_initialized': _agent_instance is not None
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

