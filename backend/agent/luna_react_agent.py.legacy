"""
Luna - Free-Thinking AI Agent for One Development

Luna is an autonomous AI agent that thinks freely and reasons independently.
She doesn't follow rigid workflows or predefined scripts — she adapts to each
conversation, chooses her own approach, and provides genuine value.

Philosophy:
- No rigid workflows — Luna decides what to do based on the situation
- Autonomous reasoning — she thinks through problems creatively
- Adaptive behavior — every conversation is unique
- Genuine helpfulness — not just information retrieval, but thoughtful assistance

Technical Foundation:
Built on LangGraph's ReAct pattern, but with a free-thinking prompt architecture
that encourages Luna to reason independently rather than follow rules.

Key Capabilities:
- Dynamic tool selection and multi-step reasoning
- Web search, knowledge base queries, PDF reading
- User personalization and context awareness
- Natural, conversational communication style
"""

from typing import TypedDict, Annotated, Sequence, List, Dict, Any, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
import os
from datetime import datetime

from agent.tools import get_all_tools


# ============================================================================
# STATE DEFINITION
# ============================================================================

class AgentState(TypedDict):
    """
    State that flows through the agent graph.
    Messages accumulate as the agent reasons and acts.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    session_id: str
    iteration_count: int  # Track reasoning iterations
    thinking_steps: List[Dict[str, Any]]  # Track reasoning for UI display


# ============================================================================
# LUNA REACT AGENT
# ============================================================================

class LunaReActAgent:
    """
    Luna - Free-Thinking AI Agent for One Development
    
    Luna is not bound by rigid workflows or predetermined steps. She:
    - Thinks freely about what each user actually needs
    - Chooses her own path through tools and information
    - Adapts her approach to each unique conversation
    - Reasons creatively to solve problems and provide value
    
    She's an autonomous agent that makes her own decisions about how best
    to help, guided by principles rather than rules.
    """
    
    MAX_ITERATIONS = 10  # Prevent infinite loops
    
    def __init__(self, openai_api_key: str = None):
        """Initialize Luna with tools and reasoning capabilities"""
        
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        # Get all available tools
        self.tools = get_all_tools()
        
        # Create the LLM with tools bound
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=self.api_key
        ).bind_tools(self.tools)
        
        # Build the reasoning graph
        self.graph = self._build_graph()
        
        print("✅ Luna ReAct Agent initialized with", len(self.tools), "tools")
    
    def _build_graph(self) -> StateGraph:
        """
        Build the ReAct agent graph.
        
        The graph has two main nodes:
        1. reason: Luna thinks and decides what to do
        2. tools: Execute any tools Luna wants to use
        
        Flow: reason -> (tools -> reason)* -> END
        """
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add the reasoning node (Luna's brain)
        workflow.add_node("reason", self._reason)
        
        # Add the tool execution node
        tool_node = ToolNode(self.tools)
        workflow.add_node("tools", tool_node)
        
        # Set entry point
        workflow.set_entry_point("reason")
        
        # Add conditional routing after reasoning
        workflow.add_conditional_edges(
            "reason",
            self._should_continue,
            {
                "tools": "tools",      # Luna wants to use a tool
                "end": END             # Luna is ready to respond
            }
        )
        
        # After tools execute, go back to reasoning
        workflow.add_edge("tools", "reason")
        
        return workflow.compile()
    
    def _get_system_prompt(self, session_id: str) -> str:
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

    def _reason(self, state: AgentState) -> dict:
        """
        The reasoning node - Luna's brain.
        
        This is where Luna:
        1. Looks at the conversation so far
        2. Thinks about what to do
        3. Either calls tools or generates a final response
        """
        messages = state["messages"]
        session_id = state.get("session_id", "default")
        iteration = state.get("iteration_count", 0)
        
        # Safety: prevent infinite loops
        if iteration >= self.MAX_ITERATIONS:
            return {
                "messages": [AIMessage(content="I apologize, but I'm having trouble processing this request. Let me connect you with our team directly. You can reach One Development at their official website or contact their sales team for immediate assistance.")]
            }
        
        # Create system prompt
        system_message = SystemMessage(content=self._get_system_prompt(session_id))
        
        # Call the LLM with tools available
        response = self.llm.invoke([system_message] + list(messages))
        
        return {
            "messages": [response],
            "iteration_count": iteration + 1
        }
    
    def _should_continue(self, state: AgentState) -> Literal["tools", "end"]:
        """
        Decide whether to continue (call tools) or end (respond to user).
        
        If Luna's last message has tool_calls, we need to execute them.
        Otherwise, Luna is ready to give her final response.
        """
        last_message = state["messages"][-1]
        
        # Check if Luna wants to call any tools
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        # Luna is ready to respond
        return "end"
    
    def process_query(
        self,
        query: str,
        session_id: str = "default",
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process a user query through Luna's reasoning loop.
        
        Args:
            query: The user's message
            session_id: Unique session identifier for memory
            conversation_history: Previous messages (optional)
            
        Returns:
            Dictionary with response and metadata including thinking steps
        """
        
        # Build initial messages from history
        messages = []
        
        if conversation_history:
            for msg in conversation_history[-10:]:  # Keep last 10 for context
                if msg.get('message_type') == 'human':
                    messages.append(HumanMessage(content=msg['content']))
                elif msg.get('message_type') == 'ai':
                    messages.append(AIMessage(content=msg['content']))
        
        # Add the current query
        messages.append(HumanMessage(content=query))
        
        # Create initial state
        initial_state = {
            "messages": messages,
            "session_id": session_id,
            "iteration_count": 0,
            "thinking_steps": []
        }
        
        # Run Luna through the reasoning graph
        try:
            final_state = self.graph.invoke(initial_state)
            
            # Extract the final response
            last_message = final_state["messages"][-1]
            response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # Extract thinking steps from messages
            thinking_steps = []
            tools_info = []
            
            for msg in final_state["messages"]:
                # Check for tool calls (Luna deciding to use tools)
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tool_name = tool_call.get('name', 'unknown')
                        tool_args = tool_call.get('args', {})
                        
                        # Create a friendly description of what Luna is doing
                        tool_descriptions = {
                            'search_knowledge_base': '🔍 Searching knowledge base',
                            'search_uploaded_documents': '📄 Searching documents',
                            'search_web_for_market_data': '🌐 Fetching market data',
                            'get_dubai_market_context': '📊 Getting market context',
                            'get_user_context': '🧠 Checking your preferences',
                            'save_user_information': '💾 Saving your info',
                            'plan_response': '📋 Planning response',
                            'deep_research': '🔬 Deep research',
                            'analyze_pricing': '💰 Analyzing prices',
                            'compare_properties': '⚖️ Comparing options',
                            'guide_buyer_journey': '🗺️ Getting buyer guide',
                        }
                        
                        friendly_name = tool_descriptions.get(tool_name, f'🔧 {tool_name}')
                        
                        # Extract query if present
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
                
                # Check for tool results
                if isinstance(msg, ToolMessage):
                    thinking_steps.append({
                        'type': 'tool_result',
                        'status': 'completed',
                        'preview': str(msg.content)[:150] + '...' if len(str(msg.content)) > 150 else str(msg.content)
                    })
            
            # Add initial thinking step
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
                'reasoning_steps': final_state.get('iteration_count', 0),
                'tools_used': len(tools_info),
                'thinking': thinking_steps,
                'tools_info': tools_info,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Luna error: {str(e)}")
            
            # Graceful fallback response
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
        Async version of process_query for streaming support.
        """
        # For now, just wrap the sync version
        # Can be enhanced with true async streaming later
        return self.process_query(query, session_id, conversation_history)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_luna_instance = None

def get_luna_agent() -> LunaReActAgent:
    """Get or create the Luna agent singleton"""
    global _luna_instance
    if _luna_instance is None:
        _luna_instance = LunaReActAgent()
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
    
    luna = LunaReActAgent()
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

