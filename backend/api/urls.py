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
    path('avatar/last-video/', views.get_last_avatar_video, name='get-last-avatar-video'),
    path('avatar/audio/<str:audio_id>.mp3', views.avatar_audio, name='avatar-audio'),
    path('avatar/videos/<str:video_id>', views.avatar_video_proxy, name='avatar-video-proxy'),
    # TTS (Text-to-Speech) endpoints - ElevenLabs
    path('tts/generate/', views.generate_tts, name='generate-tts'),
    path('tts/voices/', views.tts_voices, name='tts-voices'),
    # ElevenLabs Talking Video - Luna.png speaks!
    path('avatar/elevenlabs-video/', views.generate_talking_video, name='elevenlabs-video'),
    path('avatar/temp-video/<str:video_filename>', views.serve_temp_video, name='serve-temp-video'),
    # Context monitoring
    path('context/status/', views.context_status, name='context-status'),
    # LiveAvatar API endpoints
    path('liveavatar/session-token/', views.liveavatar_create_session_token, name='liveavatar-session-token'),
    path('liveavatar/sessions/start/', views.liveavatar_start_session, name='liveavatar-start-session'),
    path('liveavatar/sessions/<str:session_id>/message/', views.liveavatar_send_message, name='liveavatar-send-message'),
    path('liveavatar/sessions/<str:session_id>/end/', views.liveavatar_end_session, name='liveavatar-end-session'),
    # LiveAvatar Custom Mode endpoints
    path('liveavatar/sessions/<str:session_id>/audio/', views.liveavatar_send_audio_custom_mode, name='liveavatar-send-audio-custom'),
    path('liveavatar/chat-custom/', views.liveavatar_chat_with_custom_mode, name='liveavatar-chat-custom'),
]

