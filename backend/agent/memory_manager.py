"""
Persistent Memory Manager for the Agent
Stores and retrieves user-specific context across sessions
"""

from typing import Dict, Any, List, Optional
from agent.models import AgentMemory, Conversation
from datetime import datetime, timedelta
from django.utils import timezone


class MemoryManager:
    """Manages persistent memory for the agent"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.conversation = self._get_or_create_conversation()
    
    def _get_or_create_conversation(self) -> Conversation:
        """Get or create conversation for this session"""
        conversation, created = Conversation.objects.get_or_create(
            session_id=self.session_id
        )
        return conversation
    
    def store_memory(self, memory_type: str, key: str, value: str, 
                    importance: float = 0.5) -> None:
        """
        Store a memory
        
        Args:
            memory_type: Type of memory (e.g., 'user_name', 'preference', 'fact')
            key: Memory key
            value: Memory value
            importance: Importance score (0.0 to 1.0)
        """
        # Check if memory already exists
        memory, created = AgentMemory.objects.update_or_create(
            conversation=self.conversation,
            memory_type=memory_type,
            key=key,
            defaults={
                'value': value,
                'importance_score': importance,
                'last_accessed': timezone.now()
            }
        )
        
        print(f"{'Created' if created else 'Updated'} memory: {memory_type} - {key}")
    
    def retrieve_memory(self, memory_type: str = None, key: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve memories
        
        Args:
            memory_type: Filter by memory type (optional)
            key: Filter by specific key (optional)
            
        Returns:
            List of matching memories
        """
        query = AgentMemory.objects.filter(conversation=self.conversation)
        
        if memory_type:
            query = query.filter(memory_type=memory_type)
        
        if key:
            query = query.filter(key=key)
        
        # Update last_accessed time
        query.update(last_accessed=timezone.now())
        
        memories = []
        for memory in query:
            memories.append({
                'type': memory.memory_type,
                'key': memory.key,
                'value': memory.value,
                'importance': memory.importance_score,
                'created_at': memory.created_at,
                'last_accessed': memory.last_accessed
            })
        
        return memories
    
    def get_user_name(self) -> Optional[str]:
        """Get the user's name if stored"""
        memories = self.retrieve_memory(memory_type='user_info', key='name')
        if memories:
            return memories[0]['value']
        return None
    
    def store_user_name(self, name: str) -> None:
        """Store the user's name"""
        self.store_memory('user_info', 'name', name, importance=1.0)
    
    def get_user_preferences(self) -> Dict[str, str]:
        """Get all user preferences"""
        memories = self.retrieve_memory(memory_type='preference')
        return {m['key']: m['value'] for m in memories}
    
    def store_user_preference(self, preference_key: str, preference_value: str) -> None:
        """Store a user preference"""
        self.store_memory('preference', preference_key, preference_value, importance=0.8)
    
    def get_conversation_context(self) -> str:
        """Get a summary of important memories for this conversation"""
        memories = AgentMemory.objects.filter(
            conversation=self.conversation
        ).order_by('-importance_score', '-last_accessed')[:10]
        
        if not memories:
            return "No previous context available."
        
        context_parts = []
        user_name = None
        preferences = []
        facts = []
        
        for memory in memories:
            if memory.memory_type == 'user_info' and memory.key == 'name':
                user_name = memory.value
            elif memory.memory_type == 'preference':
                preferences.append(f"{memory.key}: {memory.value}")
            elif memory.memory_type == 'fact':
                facts.append(memory.value)
        
        if user_name:
            context_parts.append(f"User's name: {user_name}")
        
        if preferences:
            context_parts.append(f"User preferences: {', '.join(preferences)}")
        
        if facts:
            context_parts.append(f"Previous facts discussed: {'; '.join(facts[:3])}")
        
        return " | ".join(context_parts) if context_parts else "First conversation with this user."
    
    def extract_and_store_user_info(self, message: str, response: str) -> None:
        """
        Automatically extract and store user information from conversation
        
        Args:
            message: User's message
            response: Agent's response
        """
        message_lower = message.lower()
        
        # Extract name patterns
        name_patterns = [
            r"my name is (\w+)",
            r"i'm (\w+)",
            r"i am (\w+)",
            r"call me (\w+)",
            r"this is (\w+)"
        ]
        
        import re
        for pattern in name_patterns:
            match = re.search(pattern, message_lower)
            if match:
                name = match.group(1).capitalize()
                # Validate it's likely a name (not a common word)
                if len(name) > 2 and name not in ['the', 'and', 'for', 'you', 'that', 'this']:
                    self.store_user_name(name)
                    print(f"Stored user name: {name}")
                    break
        
        # Extract preferences
        if 'interested in' in message_lower or 'looking for' in message_lower:
            if 'villa' in message_lower:
                self.store_user_preference('property_type', 'villa')
            elif 'apartment' in message_lower:
                self.store_user_preference('property_type', 'apartment')
            elif 'penthouse' in message_lower:
                self.store_user_preference('property_type', 'penthouse')
        
        # Store location preferences
        locations = ['dubai', 'abu dhabi', 'sharjah', 'marina', 'downtown']
        for location in locations:
            if location in message_lower:
                self.store_user_preference('preferred_location', location.title())
                break
    
    def clear_old_memories(self, days: int = 90) -> int:
        """
        Clear memories older than specified days
        
        Args:
            days: Number of days to keep memories
            
        Returns:
            Number of memories deleted
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = AgentMemory.objects.filter(
            conversation=self.conversation,
            last_accessed__lt=cutoff_date,
            importance_score__lt=0.5
        ).delete()[0]
        
        return deleted_count

