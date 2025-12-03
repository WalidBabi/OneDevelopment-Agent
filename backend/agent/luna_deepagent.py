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

Observability:
LangSmith tracing enabled for full visibility into agent reasoning and tool usage.
Set LANGCHAIN_TRACING_V2=true and LANGCHAIN_API_KEY in .env to enable.
"""

from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode

from agent.tools import get_all_tools
from agent.subagents import get_subagent_tools
from agent.deepagents_tools import get_deepagent_tools


# ============================================================================
# LANGSMITH OBSERVABILITY SETUP
# ============================================================================

def setup_langsmith():
    """
    Configure LangSmith tracing for observability.
    
    LangSmith provides:
    - Full trace of agent reasoning steps
    - Tool call inputs and outputs
    - Token usage and latency metrics
    - Error tracking and debugging
    
    Enable by setting in .env:
        LANGCHAIN_TRACING_V2=true
        LANGCHAIN_API_KEY=your-api-key
        LANGCHAIN_PROJECT=luna-deepagent
    """
    tracing_enabled = os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
    api_key = os.getenv('LANGCHAIN_API_KEY')
    
    if tracing_enabled and api_key:
        # Set default project name if not specified
        if not os.getenv('LANGCHAIN_PROJECT'):
            os.environ['LANGCHAIN_PROJECT'] = 'luna-deepagent'
        
        print(f"🔍 LangSmith tracing ENABLED - Project: {os.getenv('LANGCHAIN_PROJECT')}")
        return True
    else:
        if tracing_enabled and not api_key:
            print("⚠️  LangSmith tracing enabled but LANGCHAIN_API_KEY not set")
        return False


# Initialize LangSmith on module load
_langsmith_enabled = setup_langsmith()


# ============================================================================
# LUNA SYSTEM PROMPT
# ============================================================================

def get_luna_system_prompt(session_id: str = "default") -> str:
    """
    Create the system prompt that defines Luna's personality and behavior.
    Luna is a free-thinking AI agent - no rigid workflows, just intelligent reasoning.
    """
    return f"""You are Luna, an AI research agent for One Development (oneuae.com).

## YOUR PRIMARY TOOL: search_knowledge_base

**ALWAYS use `search_knowledge_base` first** — it contains accurate project data.

For questions about One Development projects:
→ Call: `search_knowledge_base(query="One Development projects portfolio")`

For specific project details:
→ Call: `search_knowledge_base(query="Laguna Residence")` (or project name)

## MANDATORY: Use Tools Before Answering

You MUST call a tool before responding to questions about One Development.
DO NOT answer from memory — always search first.

## Tool Priority (use in this order):

1. **`search_knowledge_base(query)`** — BEST. Contains accurate project data. USE THIS FIRST.
   - For projects: `search_knowledge_base(query="One Development projects")`
   - For specific project: `search_knowledge_base(query="[project name]")`

2. **`search_uploaded_documents(query)`** — Search PDF brochures

3. **`get_dubai_market_context(topic)`** — For market/pricing context

## Example Workflow

User: "Tell me about their projects"

You should:
1. Call `search_knowledge_base` with query="One Development projects portfolio"
2. Read the returned content with project names
3. Respond with the specific project names and URLs found

## KNOWN PROJECTS (verify via search):

Active: Laguna Residence, DO Dubai Islands, DO New Cairo
Pipeline: Al Marjan Islands, Al Reem Islands Abu Dhabi, DO Riyadh, DO Athens, W55 Waterway Egypt
Portfolio: https://oneuae.com/our-development

## Response Style

✅ DO: "One Development's current projects include: Laguna Residence, DO Dubai Islands, DO New Cairo..."
✅ DO: Include URLs like https://oneuae.com/development-detail?title=Laguna%20Residence
❌ DON'T: Generic descriptions without specific project names

Be concise. Give specific project names. Include URLs.

## Current Context
Session: {session_id}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

ALWAYS search knowledge base first. It has the latest project data."""


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
    
    # Create two versions of the LLM:
    # 1. One that FORCES tool usage (for first iteration - must research)
    # 2. One that allows choosing (for subsequent iterations - can respond)
    llm_force_tools = llm.bind_tools(tools, tool_choice="any")
    llm_optional_tools = llm.bind_tools(tools)
    
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
        
        # Check if this is the first iteration (no tool results yet)
        has_tool_results = any(
            isinstance(msg, ToolMessage) for msg in messages
        )
        
        # FORCE tool usage on first call (must research before answering)
        # Allow optional tools after we have research results
        if not has_tool_results and iteration_count == 0:
            # First call: MUST use a tool to research
            response = llm_force_tools.invoke([system_message] + list(messages))
        else:
            # Subsequent calls: can choose to respond or use more tools
            response = llm_optional_tools.invoke([system_message] + list(messages))
        
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
        
        # Get all available tools (core + subagents + deepagent enhancements)
        self.tools = get_all_tools() + get_subagent_tools() + get_deepagent_tools()
        
        # Create the LLM - using gpt-4o for better tool usage
        # Lower temperature to make it more deterministic and follow instructions
        self.llm = ChatOpenAI(
            model="gpt-4o",  # Better at following instructions than gpt-4o-mini
            temperature=0.3,  # Lower temperature = more deterministic, follows prompts better
            api_key=self.api_key
        )
        
        # Create the agent using simplified builder
        self.agent = create_luna_agent(
            tools=self.tools,
            llm=self.llm,
            system_prompt=get_luna_system_prompt(),
            max_iterations=10
        )
        
        print(f"✅ Luna Agent initialized with {len(self.tools)} tools (model: gpt-4o)")
    
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
    
    def add_knowledge(self, content: str, metadata: Dict[str, Any] = None):
        """
        Add content to the ChromaDB knowledge base.
        
        This enables PDF indexing and knowledge ingestion to work with LunaDeepAgent.
        
        Args:
            content: Text content to add
            metadata: Optional metadata dict (title, source, etc.)
        """
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Get or create ChromaDB client
            chroma_db_path = os.path.join(os.path.dirname(__file__), '..', 'chroma_db')
            os.makedirs(chroma_db_path, exist_ok=True)
            
            client = chromadb.PersistentClient(
                path=chroma_db_path,
                settings=Settings(anonymized_telemetry=False, allow_reset=False)
            )
            
            # Get or create collection
            try:
                collection = client.get_collection("onedevelopment_knowledge")
            except:
                collection = client.create_collection(
                    name="onedevelopment_knowledge",
                    metadata={"description": "Knowledge base for One Development"}
                )
            
            # Generate unique ID
            doc_id = f"doc_{datetime.now().timestamp()}"
            
            # Add to collection
            collection.add(
                documents=[content],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )
            
            title = metadata.get('title', 'Untitled') if metadata else 'Untitled'
            print(f"✅ Added knowledge: {title[:50]}...")
            
        except Exception as e:
            print(f"⚠️ Could not add to knowledge base: {str(e)}")


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
