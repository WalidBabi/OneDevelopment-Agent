"""
Luna - Free-Thinking AI Agent for One Development
Clean, Simplified Implementation (Python 3.9+ Compatible)

Luna is an autonomous AI agent that thinks freely and reasons independently.
This implementation provides a cleaner, more streamlined architecture inspired by
DeepAgents principles, but compatible with Python 3.9+.

Philosophy:
- No rigid workflows — Luna decides what to do based on the situation
- Autonomous reasoning — she thinks through problems creatively  
- Adaptive behavior — every conversation is unique
- Genuine helpfulness — not just information retrieval, but thoughtful assistance

Technical Foundation:
Clean wrapper around LangGraph's ReAct pattern with simplified setup and better code organization.
"""

from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode

from agent.tools import get_all_tools


# ============================================================================
# LUNA SYSTEM PROMPT
# ============================================================================

def get_luna_system_prompt(session_id: str = "default") -> str:
    """
    Create the system prompt that defines Luna's personality and behavior.
    Luna is a free-thinking AI agent - no rigid workflows, just intelligent reasoning.
    """
    return f"""You are Luna, an intelligent AI agent for One Development, a premier luxury real estate developer in the UAE.

## Who You Are

I am **Luna** — not a chatbot following scripts, but a thinking AI agent. I reason, explore, and adapt to each unique conversation. I represent **One Development** (oneuae.com), a luxury real estate developer in the UAE.

## How I Think

I don't follow rigid workflows. Instead, I:

- **Reason freely** about what each user actually needs
- **Choose my own path** — I decide which tools to use, in what order, or whether to use any at all
- **Adapt dynamically** — every conversation is different, and I respond accordingly
- **Think creatively** — I find connections, offer insights, and provide genuine value
- **Stay curious** — I explore multiple angles when a question is interesting or complex

## My Capabilities

I have access to various tools — knowledge bases, web search, PDF readers, market data, and user personalization. But I decide when and how to use them based on what makes sense for the conversation, not because a rule told me to.

**I can:**
- Search internal knowledge about One Development
- Search the web and One Development's website
- Read PDF brochures and documents directly
- Access Dubai real estate market context
- Remember user preferences and personalize responses

## My Principles

**Be genuinely helpful** — My goal is to provide real value, not just information dumps.

**Be honest** — I distinguish between what I know from One Development sources vs. general market data. I'm transparent about uncertainty.

**Be thoughtful** — I consider the user's underlying needs, not just their literal words.

**Be resourceful** — If one approach doesn't work, I try another. I don't give up easily.

**Be human** — I communicate naturally, with personality. I'm not robotic or formulaic.

## When I Don't Know Something

I explore before concluding I can't help. But if I genuinely can't find something, I'm honest about it and offer a clear path forward (like contacting the sales team at oneuae.com).

## Communication Style

- Natural and conversational, not corporate or stiff
- **Bold** for emphasis on key points
- Concise but complete — I don't pad responses with filler
- I end with actionable next steps when appropriate

## Current Context
Session: {session_id}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

I think for myself. I reason through problems. I'm here to genuinely help, not to follow a script."""


# ============================================================================
# SIMPLIFIED AGENT BUILDER
# ============================================================================

def create_luna_agent(tools: List, llm: ChatOpenAI, system_prompt: str, max_iterations: int = 10):
    """
    Simplified agent creation function - inspired by deepagents but Python 3.9 compatible.
    
    This function creates a clean ReAct agent with minimal boilerplate.
    
    Args:
        tools: List of LangChain tools
        llm: Language model instance
        system_prompt: System prompt defining agent behavior
        max_iterations: Maximum reasoning iterations
    
    Returns:
        Compiled LangGraph agent ready to use
    """
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # Define the agent node
    def agent_node(state: MessagesState) -> Dict:
        """Agent reasoning node"""
        messages = state["messages"]
        iteration_count = state.get("iteration_count", 0)
        
        # Safety: prevent infinite loops
        if iteration_count >= max_iterations:
            return {
                "messages": [AIMessage(content="I apologize, but I'm having trouble processing this request. Let me connect you with our team directly. You can reach One Development at their official website or contact their sales team for immediate assistance.")]
            }
        
        # Add system prompt
        system_message = SystemMessage(content=system_prompt)
        response = llm_with_tools.invoke([system_message] + list(messages))
        
        return {
            "messages": [response],
            "iteration_count": iteration_count + 1
        }
    
    # Define routing logic
    def should_continue(state: MessagesState) -> Literal["tools", "end"]:
        """Decide whether to continue (call tools) or end"""
        last_message = state["messages"][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        return "end"
    
    # Build the graph
    workflow = StateGraph(MessagesState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "end": END}
    )
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()


# ============================================================================
# LUNA AGENT CLASS
# ============================================================================

class LunaDeepAgent:
    """
    Luna - Free-Thinking AI Agent with Clean Architecture
    
    This is a streamlined implementation of Luna using a clean wrapper around LangGraph.
    Inspired by DeepAgents principles but compatible with Python 3.9+.
    
    Key Features:
    - Simplified setup and configuration
    - Clean, maintainable code
    - Full ReAct reasoning capabilities
    - Easy to extend and customize
    """
    
    def __init__(self, openai_api_key: str = None):
        """
        Initialize Luna with clean, simple configuration.
        
        Args:
            openai_api_key: OpenAI API key (defaults to env variable)
        """
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        # Get all available tools
        self.tools = get_all_tools()
        
        # Create the LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=self.api_key
        )
        
        # Create the agent using simplified builder
        self.agent = create_luna_agent(
            tools=self.tools,
            llm=self.llm,
            system_prompt=get_luna_system_prompt(),
            max_iterations=10
        )
        
        print(f"✅ Luna Agent initialized with {len(self.tools)} tools")
    
    def process_query(
        self,
        query: str,
        session_id: str = "default",
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process a user query through Luna's reasoning.
        
        Args:
            query: The user's message
            session_id: Unique session identifier for memory
            conversation_history: Previous messages (optional)
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Build conversation history
            messages = []
            
            if conversation_history:
                for msg in conversation_history[-10:]:  # Keep last 10 for context
                    if msg.get('message_type') == 'human':
                        messages.append(HumanMessage(content=msg['content']))
                    elif msg.get('message_type') == 'ai':
                        messages.append(AIMessage(content=msg['content']))
            
            # Add current query
            messages.append(HumanMessage(content=query))
            
            # Create initial state
            initial_state = {
                "messages": messages,
                "iteration_count": 0
            }
            
            # Run the agent
            result = self.agent.invoke(initial_state)
            
            # Extract response
            response_content = ""
            if "messages" in result:
                last_message = result["messages"][-1]
                if hasattr(last_message, 'content'):
                    response_content = last_message.content
                else:
                    response_content = str(last_message)
            
            # Extract thinking steps and tools used
            thinking_steps = []
            tools_info = []
            
            if "messages" in result:
                for msg in result["messages"]:
                    # Check for tool calls
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            tool_name = tool_call.get('name', 'unknown')
                            tool_args = tool_call.get('args', {})
                            
                            # Friendly descriptions
                            tool_descriptions = {
                                'search_knowledge_base': '🔍 Searching knowledge base',
                                'search_uploaded_documents': '📄 Searching documents',
                                'search_web_for_market_data': '🌐 Fetching market data',
                                'get_dubai_market_context': '📊 Getting market context',
                                'get_user_context': '🧠 Checking your preferences',
                                'save_user_information': '💾 Saving your info',
                                'search_web': '🌐 Searching the web',
                                'search_one_development_website': '🏢 Searching One Development site',
                                'download_and_read_pdf': '📄 Reading PDF',
                                'fetch_project_brochure': '📋 Fetching brochure',
                                'get_project_details': '🏗️ Getting project details',
                            }
                            
                            friendly_name = tool_descriptions.get(tool_name, f'🔧 {tool_name}')
                            query_arg = tool_args.get('query', tool_args.get('topic', ''))
                            
                            thinking_steps.append({
                                'type': 'tool_call',
                                'tool': tool_name,
                                'description': friendly_name,
                                'query': query_arg[:100] if query_arg else None
                            })
                            
                            tools_info.append({
                                'name': tool_name,
                                'friendly_name': friendly_name,
                                'args': tool_args
                            })
            
            # Add bookend thinking steps
            if thinking_steps:
                thinking_steps.insert(0, {
                    'type': 'thinking',
                    'description': '🤔 Analyzing your question...'
                })
                thinking_steps.append({
                    'type': 'responding',
                    'description': '✨ Generating response...'
                })
            
            return {
                'response': response_content,
                'session_id': session_id,
                'reasoning_steps': len(thinking_steps),
                'tools_used': len(tools_info),
                'thinking': thinking_steps,
                'tools_info': tools_info,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Luna error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Graceful fallback
            return {
                'response': f"""I apologize, but I encountered an issue processing your request. 

Here's how I can still help:
- **Visit our website**: www.oneuae.com for property information
- **Contact our team**: Our sales team can assist you directly
- **Try again**: Feel free to rephrase your question

Is there something specific about One Development I can try to help you with?""",
                'session_id': session_id,
                'reasoning_steps': 0,
                'tools_used': 0,
                'thinking': [{'type': 'error', 'description': '❌ Something went wrong'}],
                'tools_info': [],
                'success': False,
                'error': str(e)
            }
    
    async def aprocess_query(
        self,
        query: str,
        session_id: str = "default",
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Async version for streaming support.
        
        Args:
            query: The user's message
            session_id: Unique session identifier
            conversation_history: Previous messages (optional)
            
        Returns:
            Dictionary with response and metadata
        """
        # For now, wrap the sync version
        # Can be enhanced with true async later
        return self.process_query(query, session_id, conversation_history)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_luna_instance = None

def get_luna_agent() -> LunaDeepAgent:
    """Get or create the Luna agent singleton"""
    global _luna_instance
    if _luna_instance is None:
        _luna_instance = LunaDeepAgent()
    return _luna_instance


def chat_with_luna(
    message: str,
    session_id: str = "default",
    history: List[Dict] = None
) -> str:
    """
    Simple function to chat with Luna.
    
    Example:
        response = chat_with_luna("Tell me about One Development")
        print(response)
    """
    luna = get_luna_agent()
    result = luna.process_query(message, session_id, history)
    return result['response']


# ============================================================================
# CLI TESTING
# ============================================================================

if __name__ == "__main__":
    """Test Luna from command line"""
    print("=" * 60)
    print("🌙 Luna - One Development AI Assistant")
    print("=" * 60)
    print("Type 'quit' to exit\n")
    
    luna = LunaDeepAgent()
    session_id = f"cli_test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    history = []
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🤔 Luna is thinking...")
            
            result = luna.process_query(
                query=user_input,
                session_id=session_id,
                conversation_history=history
            )
            
            print(f"\n🌙 Luna: {result['response']}")
            print(f"\n   [Steps: {result['reasoning_steps']}, Tools: {result['tools_used']}]")
            
            # Update history
            history.append({'message_type': 'human', 'content': user_input})
            history.append({'message_type': 'ai', 'content': result['response']})
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
