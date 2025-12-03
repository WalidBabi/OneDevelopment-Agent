from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'knowledge', views.KnowledgeBaseViewSet, basename='knowledge')
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'pdf-documents', views.PDFDocumentViewSet, basename='pdf-document')

urlpatterns = [
    path('', include(router.urls)),
    path('chat/', views.chat, name='chat'),
    path('chat/stream/', views.chat_stream, name='chat-stream'),
    path('suggested-questions/', views.get_suggested_questions, name='suggested-questions'),
    path('conversations/<str:session_id>/', views.get_conversation_history, name='conversation-history'),
    path('ingest-data/', views.ingest_data, name='ingest-data'),
    path('health/', views.health_check, name='health'),
    # Avatar service endpoints
    path('avatar/generate/', views.generate_avatar, name='generate-avatar'),
    path('avatar/health/', views.avatar_health, name='avatar-health'),
    # TTS (Text-to-Speech) endpoints - OpenAI realistic voices
    path('tts/generate/', views.generate_tts, name='generate-tts'),
    path('tts/voices/', views.tts_voices, name='tts-voices'),
]

