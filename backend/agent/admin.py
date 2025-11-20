from django.contrib import admin
from .models import Conversation, Message, KnowledgeBase, AgentMemory, SuggestedQuestion


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'created_at', 'updated_at')
    search_fields = ('session_id',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'message_type', 'content_preview', 'created_at')
    list_filter = ('message_type', 'created_at')
    search_fields = ('content',)
    readonly_fields = ('id', 'created_at')
    
    def content_preview(self, obj):
        return obj.content[:100]


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'source_type', 'is_active', 'created_at')
    list_filter = ('source_type', 'is_active', 'created_at')
    search_fields = ('title', 'content', 'summary')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(AgentMemory)
class AgentMemoryAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'memory_type', 'key', 'importance_score', 'last_accessed')
    list_filter = ('memory_type', 'importance_score')
    search_fields = ('key', 'value')
    readonly_fields = ('id', 'created_at', 'last_accessed')


@admin.register(SuggestedQuestion)
class SuggestedQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'priority', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('question',)
    readonly_fields = ('id', 'created_at')

