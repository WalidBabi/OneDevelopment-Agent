"""
Context Monitor for Luna DeepAgent

Tracks token usage and context window utilization.
DeepAgents FilesystemMiddleware automatically handles overflow by offloading to files.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import tiktoken


class ContextMonitor:
    """
    Monitor context window usage for Luna DeepAgent.
    
    Features:
    - Track tokens used vs available
    - Calculate percentage utilization
    - Log when FilesystemMiddleware should activate
    - Provide warnings before hitting limits
    """
    
    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize context monitor.
        
        Args:
            model: Model name to get correct token limits
        """
        self.model = model
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        
        # Model context limits (tokens)
        self.context_limits = {
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
            "gpt-4": 8192,
            "gpt-3.5-turbo": 16385,
        }
        
        self.max_tokens = self.context_limits.get(model, 128000)
        
        # Reserve tokens for response
        self.response_reserve = 4096
        self.available_for_context = self.max_tokens - self.response_reserve
        
        # Filesystem offload thresholds
        self.offload_warning_threshold = 0.70  # Warn at 70% full
        self.offload_trigger_threshold = 0.85  # Trigger filesystem offload at 85%
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        try:
            return len(self.encoding.encode(text))
        except Exception:
            # Fallback: rough estimate
            return len(text) // 4
    
    def count_messages_tokens(self, messages: list) -> int:
        """Count total tokens in message list."""
        total = 0
        for msg in messages:
            if hasattr(msg, "content"):
                total += self.count_tokens(msg.content)
            elif isinstance(msg, dict) and "content" in msg:
                total += self.count_tokens(msg["content"])
        return total
    
    def analyze_context(
        self,
        messages: list,
        system_prompt: Optional[str] = None,
        tools_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze current context usage.
        
        Returns:
            Dict with:
            - tokens_used: Current token count
            - tokens_available: Remaining tokens
            - max_tokens: Total context window
            - percentage_used: % of context filled
            - status: "ok" | "warning" | "critical" | "offload"
            - filesystem_active: Should FilesystemMiddleware activate
            - recommendation: What to do
        """
        # Count tokens
        messages_tokens = self.count_messages_tokens(messages)
        system_tokens = self.count_tokens(system_prompt) if system_prompt else 0
        tools_tokens = self.count_tokens(tools_description) if tools_description else 0
        
        total_used = messages_tokens + system_tokens + tools_tokens
        tokens_remaining = self.available_for_context - total_used
        percentage_used = (total_used / self.available_for_context) * 100
        
        # Determine status
        if percentage_used < 50:
            status = "ok"
            recommendation = "Context is healthy. No action needed."
            filesystem_active = False
        elif percentage_used < 70:
            status = "ok"
            recommendation = "Context usage is moderate. Monitoring..."
            filesystem_active = False
        elif percentage_used < 85:
            status = "warning"
            recommendation = "Context usage is high. FilesystemMiddleware preparing to offload older messages."
            filesystem_active = False
        elif percentage_used < 95:
            status = "critical"
            recommendation = "Context near limit. FilesystemMiddleware actively offloading to files."
            filesystem_active = True
        else:
            status = "offload"
            recommendation = "Context at limit. FilesystemMiddleware managing overflow automatically."
            filesystem_active = True
        
        return {
            "model": self.model,
            "tokens_used": total_used,
            "tokens_available": tokens_remaining,
            "max_tokens": self.max_tokens,
            "available_for_context": self.available_for_context,
            "response_reserve": self.response_reserve,
            "percentage_used": round(percentage_used, 2),
            "status": status,
            "filesystem_active": filesystem_active,
            "recommendation": recommendation,
            "breakdown": {
                "messages": messages_tokens,
                "system_prompt": system_tokens,
                "tools": tools_tokens,
            },
            "timestamp": datetime.now().isoformat(),
        }
    
    def format_status(self, analysis: Dict[str, Any]) -> str:
        """Format analysis as human-readable string."""
        status_emoji = {
            "ok": "✅",
            "warning": "⚠️",
            "critical": "🔴",
            "offload": "💾"
        }
        
        emoji = status_emoji.get(analysis["status"], "ℹ️")
        
        # Create progress bar
        percentage = analysis["percentage_used"]
        bar_length = 40
        filled = int((percentage / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        return f"""
{emoji} Context Status: {analysis['status'].upper()}

Model: {analysis['model']}
Tokens: {analysis['tokens_used']:,} / {analysis['available_for_context']:,} ({analysis['percentage_used']}%)

[{bar}]

Breakdown:
  - Messages: {analysis['breakdown']['messages']:,} tokens
  - System Prompt: {analysis['breakdown']['system_prompt']:,} tokens
  - Tools: {analysis['breakdown']['tools']:,} tokens

Remaining: {analysis['tokens_available']:,} tokens
Reserved for Response: {analysis['response_reserve']:,} tokens

FilesystemMiddleware: {'🟢 ACTIVE - Offloading to files' if analysis['filesystem_active'] else '⏸️ Standby'}

{analysis['recommendation']}
"""

    def should_summarize(self, analysis: Dict[str, Any]) -> bool:
        """Check if we should summarize old messages."""
        return analysis["percentage_used"] > 70
    
    def get_offload_count(self, analysis: Dict[str, Any], messages: list) -> int:
        """
        Calculate how many messages to offload to stay under threshold.
        
        Returns:
            Number of old messages to offload to filesystem
        """
        if not self.should_summarize(analysis):
            return 0
        
        # Target: get back to 60% usage
        target_tokens = int(self.available_for_context * 0.60)
        tokens_to_free = analysis["tokens_used"] - target_tokens
        
        # Calculate average tokens per message
        avg_tokens_per_message = (
            analysis["breakdown"]["messages"] / len(messages) if messages else 100
        )
        
        # How many messages to offload?
        messages_to_offload = int(tokens_to_free / avg_tokens_per_message)
        
        # Offload older messages (keep recent ones)
        # Don't offload more than 50% of messages
        max_offload = len(messages) // 2
        
        return min(messages_to_offload, max_offload, len(messages) - 5)  # Keep at least 5 recent


# Singleton instance
_monitor_instance = None

def get_context_monitor(model: str = "gpt-4o") -> ContextMonitor:
    """Get or create context monitor singleton."""
    global _monitor_instance
    if _monitor_instance is None or _monitor_instance.model != model:
        _monitor_instance = ContextMonitor(model)
    return _monitor_instance


# Quick utility function for API responses
def get_context_status(messages: list, model: str = "gpt-4o") -> Dict[str, Any]:
    """
    Quick function to get context status.
    
    Use in API responses to show users their context usage.
    
    Example:
        status = get_context_status(conversation_messages, model="gpt-4o")
        return {
            "response": "...",
            "context_status": status
        }
    """
    monitor = get_context_monitor(model)
    return monitor.analyze_context(messages)







