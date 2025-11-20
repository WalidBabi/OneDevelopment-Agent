from django.contrib import admin
from .models import Conversation, Message, KnowledgeBase, AgentMemory, SuggestedQuestion, PDFDocument


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


@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'page_count', 'is_indexed', 'is_active', 'created_at')
    list_filter = ('is_indexed', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'extracted_text')
    readonly_fields = ('id', 'created_at', 'updated_at', 'extracted_text', 'page_count', 'file_size', 'is_indexed')
    fieldsets = (
        ('Document Information', {
            'fields': ('title', 'description', 'file')
        }),
        ('Indexing Status', {
            'fields': ('is_indexed', 'is_active')
        }),
        ('Extracted Content', {
            'fields': ('extracted_text', 'page_count', 'file_size'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-index PDF when saved through admin"""
        super().save_model(request, obj, form, change)
        
        # Trigger indexing if file is uploaded and not yet indexed
        if obj.file and not obj.is_indexed:
            from .pdf_processor import PDFProcessor
            processor = PDFProcessor()
            try:
                processor.process_and_index_pdf(obj)
            except Exception as e:
                self.message_user(request, f"Error indexing PDF: {str(e)}", level='ERROR')

