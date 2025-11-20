from rest_framework import serializers
from agent.models import Conversation, Message, KnowledgeBase, SuggestedQuestion


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'message_type', 'content', 'metadata', 'created_at']
        read_only_fields = ['id', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'session_id', 'created_at', 'updated_at', 'metadata', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat requests"""
    message = serializers.CharField(required=True)
    session_id = serializers.CharField(required=False, allow_null=True)
    
    def validate_message(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat responses"""
    response = serializers.CharField()
    session_id = serializers.CharField()
    intent = serializers.CharField()
    entities = serializers.ListField(child=serializers.CharField())
    suggested_actions = serializers.ListField(child=serializers.CharField())
    timestamp = serializers.DateTimeField()


class SuggestedQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestedQuestion
        fields = ['id', 'question', 'category', 'priority']


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = ['id', 'source_type', 'source_url', 'title', 'content', 
                 'summary', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']

