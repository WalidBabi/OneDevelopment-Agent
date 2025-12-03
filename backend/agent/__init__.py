# Agent app - Luna AI Assistant for One Development
"""
Luna DeepAgent - Autonomous AI Agent

Luna uses the ReAct (Reasoning + Acting) pattern to autonomously decide
which tools to use and how to respond to user queries.

ARCHITECTURE:
    ┌─────────┐
    │  START  │
    └────┬────┘
         │
         ▼
    ╔═════════╗
    ║  AGENT  ║◀────┐  Luna thinks and decides
    ╚════╤════╝     │
         │          │
    ┌────┴────┐     │
    ▼         ▼     │
  tools      end    │
    │               │
    └───────────────┘

Key Components:
- luna_deepagent.py: Main agent using ReAct pattern
- tools.py: 24 tools (search, Tavily, PDF, memory, etc.)
- subagents.py: Specialized research tools
- deepagents_tools.py: Advanced reasoning tools

Usage:
    from agent import get_luna_agent, chat_with_luna
    
    luna = get_luna_agent()
    result = luna.process_query("Tell me about One Development", session_id="user_123")
    
    # Or simple helper
    response = chat_with_luna("What properties do you have?")
"""

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

__version__ = '4.0.0'  # Clean DeepAgent-only implementation
