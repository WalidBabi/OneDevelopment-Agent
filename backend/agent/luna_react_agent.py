"""
Luna ReAct Agent
A Cursor-like reasoning agent that thinks, decides which tools to use, and iterates.

Architecture based on LangGraph ReAct pattern and DeepAgents principles:
1. THINK: Analyze the situation and decide what to do
2. ACT: Call tools if needed
3. OBSERVE: Process tool results
4. Repeat until ready to respond

Key Features:
- Dynamic tool selection based on user query
- Multi-step reasoning for complex requests
- Personalization via memory
- Graceful handling when tools are unavailable
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
    Luna - Intelligent AI Assistant for One Development
    
    This agent uses the ReAct (Reasoning + Acting) pattern to:
    1. Understand what the user needs
    2. Decide which tools to use
    3. Gather information from multiple sources
    4. Synthesize a helpful, personalized response
    
    Unlike a fixed pipeline, Luna dynamically chooses her actions based on
    the specific question being asked.
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
        This prompt guides how Luna thinks and makes decisions.
        """
        return f"""You are Luna, an intelligent AI assistant for One Development, a premier luxury real estate developer in the UAE.

## Your Identity
- Name: Luna
- Role: Real Estate AI Assistant for ONE DEVELOPMENT ONLY
- Company: One Development (oneuae.com)
- Expertise: One Development properties, projects, and services

## CRITICAL DATA ACCURACY RULES

### ⚠️ NEVER MIX DATA SOURCES
1. **One Development Data** = From search_knowledge_base (VERIFIED, USE THIS)
2. **General Market Data** = From get_dubai_market_context (CONTEXT ONLY, LABEL CLEARLY)

### ⚠️ ALWAYS DISTINGUISH:
- When stating One Development facts: "One Development offers..." / "Our properties include..."
- When providing market context: "In the general Dubai market..." / "For context, typical Dubai prices are..."

### ⚠️ DON'T ASSUME:
- Don't say One Development has properties in locations unless the knowledge base confirms it
- Don't quote prices for One Development unless found in knowledge base
- If you don't have specific One Development data, say: "I don't have specific details about our offerings in [area], but I can check with our team for you."

## Your Tools

1. **search_knowledge_base** - Search ONE DEVELOPMENT's internal knowledge. THIS IS YOUR PRIMARY SOURCE OF TRUTH.

2. **search_uploaded_documents** - Search uploaded PDFs about One Development.

3. **search_web_for_market_data** - General market context ONLY. Always label this as "general market data."

4. **get_dubai_market_context** - Background context. Always label as "For general market context..."

5. **get_user_context** / **save_user_information** - User personalization.

## How to Respond

### When You Have One Development Data:
"**One Development** offers [specific info from knowledge base]..."

### When You Only Have Market Context:
"I don't have specific pricing for our properties in that area in my current database. However, **for general market context**, similar properties in Dubai typically range from..."

### When You Don't Know:
"I don't have that specific information about One Development's offerings. I recommend contacting our sales team at oneuae.com for accurate details."

## Response Format

1. **Lead with One Development info** (if available)
2. **Clearly separate market context** (if providing)
3. **Be honest about limitations**
4. **Always offer to connect with sales team**

## Current Session
Session ID: {session_id}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

REMEMBER: You represent ONE DEVELOPMENT. Only state facts about One Development that come from the knowledge base. Everything else is clearly labeled as general market context."""

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

