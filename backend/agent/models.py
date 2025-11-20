from django.db import models
from django.contrib.postgres.fields import JSONField
import uuid


class Conversation(models.Model):
    """Store conversation sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Conversation {self.session_id}"


class Message(models.Model):
    """Store individual messages in conversations"""
    MESSAGE_TYPES = [
        ('human', 'Human'),
        ('ai', 'AI'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}"


class KnowledgeBase(models.Model):
    """Store scraped and ingested knowledge about One Development"""
    SOURCE_TYPES = [
        ('website', 'Website'),
        ('linkedin', 'LinkedIn'),
        ('manual', 'Manual Entry'),
        ('document', 'Document'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    source_url = models.URLField(blank=True, null=True)
    title = models.CharField(max_length=500)
    content = models.TextField()
    summary = models.TextField(blank=True)
    embedding = models.JSONField(null=True, blank=True)  # Store vector embeddings
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source_type', 'is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.source_type}: {self.title[:50]}"


class AgentMemory(models.Model):
    """Store agent's long-term memory and learned patterns"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='memories')
    memory_type = models.CharField(max_length=50)  # e.g., 'user_preference', 'fact', 'context'
    key = models.CharField(max_length=255)
    value = models.TextField()
    importance_score = models.FloatField(default=0.5)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-importance_score', '-last_accessed']
        indexes = [
            models.Index(fields=['conversation', 'memory_type']),
        ]
    
    def __str__(self):
        return f"{self.memory_type}: {self.key}"


class SuggestedQuestion(models.Model):
    """Store rotating suggested questions for the chat interface"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=500)
    category = models.CharField(max_length=100)
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-priority', 'created_at']
    
    def __str__(self):
        return self.question

