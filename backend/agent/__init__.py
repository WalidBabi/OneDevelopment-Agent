# Agent app - Luna AI Assistant for One Development
"""
Luna DeepAgent Module

This module provides the Luna AI assistant using DeepAgents - a standalone library
built on LangGraph that provides a cleaner, more streamlined interface for building
ReAct agents with built-in streaming, checkpointing, and human-in-the-loop capabilities.

Luna uses the ReAct (Reasoning + Acting) pattern to dynamically decide which tools
to use based on user queries.

Key Components:
- luna_deepagent.py: Main Luna agent using DeepAgents library (NEW!)
- tools.py: All tools Luna can use (search, memory, web, etc.)
- subagents.py: Specialized tools for deep research and analysis
- luna_react_agent.py: Legacy ReAct implementation (kept for reference)
- langgraph_agent.py: Legacy fixed-pipeline agent (kept for compatibility)

Usage:
    from agent import get_luna_agent, chat_with_luna
    
    # Get the singleton Luna instance
    luna = get_luna_agent()
    
    # Process a query
    result = luna.process_query(
        query="Tell me about One Development",
        session_id="user_123"
    )
    print(result['response'])
    
    # Or use the simple helper
    response = chat_with_luna("What properties do you have?")
"""

# NEW: Import from DeepAgent implementation
from agent.luna_deepagent import (
    LunaDeepAgent,
    get_luna_agent,
    chat_with_luna,
)

from agent.tools import (
    get_all_tools,
    get_core_tools,
    search_knowledge_base,
    search_web_for_market_data,
)

__all__ = [
    'LunaDeepAgent',
    'get_luna_agent',
    'chat_with_luna',
    'get_all_tools',
    'get_core_tools',
    'search_knowledge_base',
    'search_web_for_market_data',
]

__version__ = '3.0.0'  # Major version bump for DeepAgents implementation
