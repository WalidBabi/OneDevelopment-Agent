# Agent app - Luna AI Assistant for One Development
"""
Luna ReAct Agent Module

This module provides the Luna AI assistant with Cursor-like reasoning capabilities.
Luna uses the ReAct (Reasoning + Acting) pattern to dynamically decide which tools
to use based on user queries.

Key Components:
- luna_react_agent.py: Main ReAct agent with reasoning loop
- tools.py: All tools Luna can use (search, memory, web, etc.)
- subagents.py: Specialized tools for deep research and analysis
- langgraph_agent.py: Legacy fixed-pipeline agent (kept for compatibility)

Usage:
    from agent.luna_react_agent import get_luna_agent, chat_with_luna
    
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

from agent.luna_react_agent import (
    LunaReActAgent,
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
    'LunaReActAgent',
    'get_luna_agent',
    'chat_with_luna',
    'get_all_tools',
    'get_core_tools',
    'search_knowledge_base',
    'search_web_for_market_data',
]

__version__ = '2.0.0'
