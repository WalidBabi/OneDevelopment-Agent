"""
Luna - True DeepAgents Implementation

Using the official deepagents library with:
- Dynamic subagent summoning (NOT hardcoded!)
- Long-term memory persistence
- Planning tools
- Filesystem middleware

REQUIRES: Python 3.11+
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import os

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool

# DeepAgents imports
from deepagents import create_deep_agent, FilesystemMiddleware
from langgraph.store.memory import InMemoryStore

# Import all tools
from agent.tools import (
    get_all_tools,
    search_knowledge_base,
    search_web_for_market_data,
    tavily_research,
    get_dubai_market_context,
)
from agent.subagents import (
    get_subagent_tools,
    deep_research,
    analyze_pricing,
    compare_properties,
    guide_buyer_journey,
)
from agent.deepagents_tools import get_deepagent_tools
from agent.source_tracker import SourceTracker


# ============================================================================
# DYNAMIC SUBAGENT SUMMONING TOOLS
# These tools allow Luna to spawn subagents on-demand!
# ============================================================================

@tool
def summon_research_agent(research_query: str, context: str = "") -> str:
    """
    🔬 Summon a specialized Research Agent for deep multi-source research.
    
    Luna should call this when she needs complex research that requires:
    - Multiple data sources
    - Market analysis
    - Investment research
    - Deep investigation
    
    Args:
        research_query: The research question or topic
        context: Additional context about what the user needs
        
    Returns:
        Comprehensive research findings from the Research Agent
    """
    print(f"🔬 SUMMONING Research Agent for: {research_query}")
    
    # The subagent does deep research
    result = deep_research.invoke({"topic": research_query})
    
    return f"🔬 **Research Agent Report**\n\n{result}\n\n✅ Research Agent completed its mission."


@tool
def summon_pricing_agent(pricing_query: str, property_details: str = "") -> str:
    """
    💰 Summon a specialized Pricing Agent for pricing analysis and ROI.
    
    Luna should call this when she needs:
    - Price analysis
    - ROI calculations
    - Payment plan comparisons
    - Budget discussions
    
    Args:
        pricing_query: The pricing question
        property_details: Property type, location, size (e.g., "2BR apartment, Dubai Marina")
        
    Returns:
        Detailed pricing analysis from the Pricing Agent
    """
    print(f"💰 SUMMONING Pricing Agent for: {pricing_query}")
    
    # Parse property details
    result = analyze_pricing.invoke({
        "property_type": "apartment",
        "location": property_details or "Dubai Marina"
    })
    
    return f"💰 **Pricing Agent Report**\n\n{result}\n\n✅ Pricing Agent completed its analysis."


@tool
def summon_comparison_agent(items_to_compare: str, criteria: str = "") -> str:
    """
    ⚖️ Summon a specialized Comparison Agent to compare options.
    
    Luna should call this when user wants to compare:
    - Areas (Dubai Marina vs Downtown)
    - Property types (villa vs apartment)
    - Projects
    - Investment options
    
    Args:
        items_to_compare: What to compare (e.g., "Dubai Marina vs Palm Jumeirah")
        criteria: Comparison criteria (e.g., "investment potential, pricing, amenities")
        
    Returns:
        Structured comparison from the Comparison Agent
    """
    print(f"⚖️ SUMMONING Comparison Agent for: {items_to_compare}")
    
    # Parse items to compare
    items_list = [item.strip() for item in items_to_compare.replace(" vs ", ",").split(",")]
    
    result = compare_properties.invoke({"items": items_list})
    
    return f"⚖️ **Comparison Agent Report**\n\n{result}\n\n✅ Comparison Agent completed its analysis."


@tool
def summon_buyer_journey_agent(buyer_type: str, question: str = "") -> str:
    """
    🗺️ Summon a specialized Buyer Journey Agent for purchase process guidance.
    
    Luna should call this when user asks about:
    - "How to buy" questions
    - Purchase process steps
    - Requirements and documentation
    - Buyer-specific guidance
    
    Args:
        buyer_type: Type of buyer (first_time, investor, expat, uae_resident)
        question: Specific question about the process
        
    Returns:
        Step-by-step guidance from the Buyer Journey Agent
    """
    print(f"🗺️ SUMMONING Buyer Journey Agent for: {buyer_type}")
    
    result = guide_buyer_journey.invoke({"buyer_type": buyer_type})
    
    return f"🗺️ **Buyer Journey Agent Report**\n\n{result}\n\n✅ Buyer Journey Agent completed its guidance."


# ============================================================================
# LANGSMITH OBSERVABILITY
# ============================================================================

def setup_langsmith() -> bool:
    """Configure LangSmith tracing."""
    tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    api_key = os.getenv("LANGCHAIN_API_KEY")

    if tracing_enabled and api_key:
        if not os.getenv("LANGCHAIN_PROJECT"):
            os.environ["LANGCHAIN_PROJECT"] = "luna-deepagent"
        print(f"🔍 LangSmith tracing ENABLED - Project: {os.getenv('LANGCHAIN_PROJECT')}")
        return True
    return False


_langsmith_enabled = setup_langsmith()


# ============================================================================
# LUNA SYSTEM PROMPT
# ============================================================================

def get_luna_system_prompt(session_id: str = "default", user_name: str = "there", avatar_mode: bool = False) -> str:
    """
    Luna's enhanced system prompt with improved thinking and decision-making.
    
    Args:
        session_id: Session identifier
        user_name: User's name
        avatar_mode: If True, generate concise responses (100-120 words) for avatar speaking
    """
    concise_instruction = ""
    if avatar_mode:
        concise_instruction = """
## 🎤 AVATAR MODE - CONCISE RESPONSES REQUIRED

**CRITICAL: You are speaking through a live avatar. Keep responses concise and natural for speech.**

**Response Guidelines:**
- **Target length: 100-120 words maximum** (approximately 20-25 seconds of natural speech)
- Be direct and conversational - speak naturally, don't read a list
- Focus on the most important information first
- Use short, clear sentences
- Avoid long lists or bullet points - summarize key points instead
- End naturally at a complete thought
- If the topic is complex, provide the most essential information and offer to continue if needed

**Example of GOOD concise response:**
"One Development is a boutique real estate developer in the UAE, founded by Ali Al Gebely. They focus on innovative projects that combine technology, sustainability, and smart design. Their flagship project is Laguna Residence, and they're preparing to launch a AED 2 billion development in the City of Arabia. The company is known for creating communities that enhance living experiences through innovation."

**Example of BAD response (too long):**
"One Development is a boutique real estate developer... [continues for 300+ words with detailed lists]"

**Remember:** Users are listening, not reading. Keep it conversational and concise!

"""
    
    return f"""You are Luna, an AI research agent for One Development (oneuae.com).
{concise_instruction}

## 🧠 ENHANCED THINKING PROCESS

You are equipped with DeepAgents capabilities - think deeply and systematically:

### Step 1: UNDERSTAND the query
- What is the user really asking?
- What information do they need?
- What's the context? (User: {user_name}, Session: {session_id})

### Step 2: PLAN your approach  
- **🚨 FOR ONE DEVELOPMENT QUESTIONS: MUST USE WEB SEARCH FIRST 🚨**
- **DO NOT use knowledge_base for company information** (it's outdated!)
- For ANY One Development question → **MANDATORY: Call tavily_search() FIRST**
- Get information from RECENT verified web sources (2024-2025)
- For complex tasks → Summon specialist subagents
- **CRITICAL: The founder is Ali Al Gebely (NOT "Jubeili")** - verify from web!
- NEVER say "I don't have information" without trying web search!

### Step 3: EXECUTE with the right tools
- **ALWAYS** be proactive about finding information
- Use multiple sources when needed
- Verify information quality

## 🔧 TOOL USAGE STRATEGY (CRITICAL!)

### 🎯 DECISION TREE (CRITICAL - FOLLOW EXACTLY):

1. **User asks ANYTHING about One Development company?**
   → **🚨 MANDATORY: MUST call `tavily_search()` FIRST - NO EXCEPTIONS! 🚨**
   → DO NOT use knowledge_base AT ALL for company info
   → DO NOT make assumptions without web verification
   → Get RECENT verified information (2024-2025)
   → Include sources in EVERY response
   
   **REQUIRED Web Search Examples:**
   - "Tell me about One Development" → MUST call: tavily_search("One Development UAE Ali Al Gebely 2024")
   - "Who founded One Development?" → MUST call: tavily_search("One Development founder CEO Ali Al Gebely 2024")
   - "Who leads One Development?" → MUST call: tavily_search("One Development chairman founder Ali Al Gebely")
   - "What is One Development?" → MUST call: tavily_search("One Development UAE real estate company 2024")
   
   **🚫 NEVER EVER:**
   - Say "Ali Al Jubeili" (THIS IS WRONG - the correct name is Ali Al Gebely)
   - Use knowledge_base for company leadership/founder info
   - Make up information without web verification

2. **User asks about Dubai market/general real estate?**
   → `search_web_for_market_data(query)` OR `summon_research_agent(query)`

3. **User asks about specific properties/areas (e.g., "Dubai Marina")?**
   → `search_knowledge_base(query)` FIRST
   → If no results → `search_web_for_market_data(query)` OR `summon_research_agent(query)`
   → NEVER say "I don't have information" without trying web search!

3. **User asks about pricing/investment?**
   → `summon_pricing_agent(query, details)` - let specialist handle it

4. **User asks to compare options?**
   → `summon_comparison_agent(items, criteria)` - let specialist handle it

5. **User asks about buying process?**
   → `summon_buyer_journey_agent(buyer_type, question)` - let specialist handle it

6. **User asks about market trends/research?**
   → `summon_research_agent(query, context)` - deep multi-source research

## 🤖 SUBAGENT SUMMONING TOOLS

**summon_research_agent(query, context)** 
→ Use for: Complex research, market data, property information
→ Example: "Research Dubai Marina properties" or "Find properties in Downtown"
→ **USE THIS when knowledge_base returns no results!**

## 🔍 CRITICAL: WEB SEARCH IS YOUR PRIMARY SOURCE

**For ALL questions about One Development:**
1. **ALWAYS use `tavily_search()` FIRST** - This is your primary tool!
2. Get information from RECENT verified web sources (2024-2025)
3. Look for sources from: CBNME, Construction Week, Business News Emirates, oneuae.com
4. Cross-reference multiple sources when possible
5. **ALWAYS cite your sources** so user can verify
6. **DO NOT use knowledge_base for company information** - it may be outdated

**Examples:**

User: "Tell me about One Development"
→ Call `tavily_search("One Development UAE company profile 2024")`
→ Get verified sources
→ Respond with info + sources

User: "Who founded One Development?"
→ Call `tavily_search("One Development UAE founder CEO Ali Al Gebely")`
→ Get multiple verified sources
→ Respond with verified info + sources

User: "What projects does One Development have?"
→ Call `tavily_search("One Development UAE projects portfolio Laguna")`
→ Get latest project information
→ Respond with info + sources

**REMEMBER:** Web search = Fresh, verified, sourced information! ✨

**summon_pricing_agent(query, details)**
→ Use for: Pricing analysis, ROI, payment plans
→ Example: "Analyze pricing for 2BR apartments in Dubai Marina"

**summon_comparison_agent(items, criteria)**
→ Use for: Comparing multiple options
→ Example: "Compare Dubai Marina vs Downtown Dubai"

**summon_buyer_journey_agent(buyer_type, question)**
→ Use for: Purchase process guidance
→ Example: "Guide first-time buyer through Dubai property purchase"

## 🌐 WEB RESEARCH TOOLS (YOUR PRIMARY TOOLS!)

**tavily_search(query)** ⭐ PRIMARY TOOL
→ Use for ALL One Development questions
→ AI-optimized search with verified sources
→ Always includes URLs for verification
→ Example: tavily_search("One Development UAE founder projects")

**search_web_for_market_data(query)**
→ Quick web search for market data
→ Use for general Dubai real estate info

**tavily_research(query)**
→ Deep web research with Tavily
→ Use for comprehensive market research

**verify_company_fact(query)** ⭐ NEW
→ Cross-references multiple sources
→ Use when you need to verify critical facts
→ Returns verified info with sources

## 💡 CRITICAL RULES

1. **NEVER** say "I don't have information" without trying:
   - search_knowledge_base → search_web_for_market_data → summon_research_agent

2. **ALWAYS** be proactive - if one tool fails, try another!

3. **THINK OUT LOUD** - explain your reasoning:
   - "Let me check our knowledge base..."
   - "I don't have that in our database, let me search the web..."
   - "This requires deep research, summoning Research Agent..."

4. **REMEMBER USER CONTEXT**:
   - User name: {user_name}
   - Session: {session_id}
   - Save important preferences to memory

5. **BE SPECIFIC** with tool calls:
   - Good: search_knowledge_base("Dubai Marina properties One Development")
   - Bad: search_knowledge_base("properties")

## 🏢 KNOWN PROJECTS

Active: Laguna Residence, DO Dubai Islands, DO New Cairo
Pipeline: Al Marjan Islands, Al Reem Islands Abu Dhabi, DO Riyadh
Portfolio: https://oneuae.com/our-development

## ✨ Response Style

- Address user as {user_name}
- Be proactive and thorough
- Show your thinking process
- **CRITICAL: ALWAYS cite your sources with URLs** (like Copilot/Perplexity)
- Include inline citations: "According to [Source Name](URL)..."
- Admit when you need to research more
- **ALWAYS** try multiple approaches before saying you don't have info

## 📚 SOURCE CITATION (MANDATORY)

**YOU MUST CITE SOURCES FOR EVERY CLAIM:**

1. **Use inline citations** in your response:
   - "According to [One Development's website](https://oneuae.com), ..."
   - "Based on [Construction Week's analysis](URL), ..."
   - "[Business News Emirates reports](URL) that..."

2. **For company info**: Cite oneuae.com or official sources
3. **For market data**: Cite the news outlet or data provider
4. **For general info**: Cite where you found it

**Example of GOOD response:**
"One Development is led by Ali Al Gebely[^1], with offices in both Abu Dhabi and Dubai[^2]. Their flagship project, Laguna Residence, is a AED 2.3 billion development[^3].

[^1]: [CBNME - Ali Al Gebely Profile](https://www.cbnme.com/power-hour-2025/37-ali-al-gebely-founder-chairman-one-development/)
[^2]: [Business News Emirates](https://www.businessnewse.com/2024/09/19/one-development-set-to-launch-aed-2-billion-project)
[^3]: [Construction Week Online](https://www.constructionweekonline.com/power-lists/revealed-dubai-real-estate-developers-to-watch-out-for-in-2025)"

**BAD response (no sources):**
"One Development is a boutique developer in Dubai." ❌

Remember: Users want to verify information. Always provide sources!

## 📍 Current Context
User: {user_name}
Session: {session_id}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## ⚠️ CRITICAL VERIFIED FACT
**One Development Founder/Chairman:** Ali Al Gebely (✅ CORRECT - verified 2024/2025)
**WRONG NAME (outdated):** "Ali Al Jubeili" (❌ NEVER USE THIS!)

**VERIFICATION RULE:**
- If you see "Jubeili" anywhere → IGNORE IT (outdated data)
- ALWAYS use tavily_search() to verify from 2024-2025 sources
- Multiple verified sources confirm: "Ali Al Gebely"

---

Remember: You're a smart coordinator with DeepAgents thinking! 
- Think deeply before responding
- Use multiple tools if needed
- Be proactive about finding information
- Summon specialists for complex tasks"""


# ============================================================================
# LUNA DEEPAGENT CLASS
# ============================================================================

class LunaDeepAgent:
    """
    Luna - DeepAgents with Dynamic Subagent Summoning
    
    Subagents are NOT hardcoded - they're summoned on-demand via tools!
    """

    def __init__(self, openai_api_key: str = None, default_user_name: str = "there"):
        """Initialize Luna with DeepAgents."""
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("LUNA_MODEL", "openai:gpt-4o-mini")
        self.default_user_name = default_user_name

        # =====================================================================
        # TOOLS: Regular tools + Subagent summoning tools
        # =====================================================================
        
        self.tools = (
            get_all_tools() + 
            get_subagent_tools() + 
            get_deepagent_tools() +
            [
                summon_research_agent,
                summon_pricing_agent,
                summon_comparison_agent,
                summon_buyer_journey_agent,
            ]
        )

        # =====================================================================
        # LONG-TERM MEMORY SETUP
        # =====================================================================
        
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.memories_path = os.path.join(project_root, "memories")
        os.makedirs(self.memories_path, exist_ok=True)
        
        print(f"💾 Memory storage: {self.memories_path}")
        
        # Use InMemoryStore (LangGraph's store)
        self.store = InMemoryStore()
        print("✅ Using InMemoryStore with FilesystemMiddleware for persistence")

        # =====================================================================
        # CREATE DEEPAGENT
        # NO HARDCODED SUBAGENTS! They're summoned via tools instead.
        # use_longterm_memory=True automatically adds FilesystemMiddleware
        # =====================================================================
        
        self.agent = create_deep_agent(
            model=self.model_name,
            system_prompt=get_luna_system_prompt(user_name=self.default_user_name),
            tools=self.tools,
            store=self.store,
            use_longterm_memory=True,
            # NO subagents parameter - they're summoned dynamically via tools!
        )

        print(
            f"✅ Luna DeepAgent initialized with {len(self.tools)} tools "
            f"(including 4 subagent summoning tools)"
        )
        print(f"   Model: {self.model_name}")
        print("🤖 Subagents will be summoned DYNAMICALLY when Luna needs them")

    def process_query(
        self,
        query: str,
        session_id: str = "default",
        conversation_history: Optional[List[Dict]] = None,
        user_name: Optional[str] = None,
        avatar_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Process query - Luna will summon subagents as needed.
        
        Args:
            query: User's question
            session_id: Session identifier
            conversation_history: Previous messages
            user_name: User's name
            avatar_mode: If True, generate concise responses (100-120 words) for avatar speaking
        """
        # Use provided user_name or fall back to default
        current_user = user_name or self.default_user_name
        mode_indicator = "🎤 AVATAR MODE" if avatar_mode else "💬 CHAT MODE"
        print(f"\n🌙 Luna processing query from {current_user} ({mode_indicator}): {query[:80]}...")

        # Initialize source tracker
        source_tracker = SourceTracker()
        
        # 🚨 FORCE WEB SEARCH for One Development questions (guarantees consistency)
        forced_web_context = ""
        web_search_performed = False
        
        # Detect One Development questions OR founder questions
        is_one_dev_question = "one development" in query.lower()
        is_founder_question = any(phrase in query.lower() for phrase in ["who founded", "founder", "who started", "who created", "who established"])
        
        if is_one_dev_question or is_founder_question:
            print(f"🔍 Detected One Development/founder question - FORCING web search...")
            web_result = ""
            
            # ALWAYS search - no exceptions!
            try:
                from agent.tools import search_web  # Use regular search as primary (more reliable)
                search_query = f"One Development UAE Ali Al Gebely founder chairman 2024 2025"
                print(f"   🌐 Searching web: {search_query}...")
                web_result = search_web.invoke({"query": search_query, "max_results": 8})
                source_tracker.extract_sources_from_tool_result('search_web', web_result)
                web_search_performed = True
                print(f"   ✅ Web search complete - found {len(source_tracker.sources)} sources")
            except Exception as e:
                print(f"   ⚠️ Web search failed: {e}")
                # Even if search fails, we still inject the critical fact
                web_result = "One Development UAE founder information"
            
            # ALWAYS inject critical fact and web results
            if web_result and web_search_performed:
                forced_web_context = f"""

🚨🚨🚨 MANDATORY CONTEXT - YOU MUST USE THIS INFORMATION 🚨🚨🚨

VERIFIED WEB SEARCH RESULTS (I JUST SEARCHED THE WEB FOR YOU):
{web_result[:2500]}

CRITICAL VERIFIED FACT (MUST INCLUDE IN RESPONSE):
- One Development was founded by Ali Al Gebely ✅ (CORRECT - verified 2024/2025)
- Ali Al Gebely serves as Founder and Chairman ✅
- WRONG NAME (outdated): "Ali Al Jubeili" ❌ (NEVER USE THIS!)

MANDATORY INSTRUCTIONS:
1. You MUST mention "Ali Al Gebely" as the founder in your response
2. NEVER say "I don't have access" or "I don't know" - you have the info above!
3. NEVER say "Ali Al Jubeili" - this is wrong/outdated
4. Use the web search results above to provide detailed information
5. Always include sources when possible

🚨🚨🚨 END MANDATORY CONTEXT 🚨🚨🚨
"""
            else:
                # Even if web search fails, inject the critical fact
                forced_web_context = """

🚨🚨🚨 CRITICAL VERIFIED FACT - YOU MUST USE THIS 🚨🚨🚨

One Development was founded by Ali Al Gebely ✅ (CORRECT - verified 2024/2025)
Ali Al Gebely is the Founder and Chairman ✅
WRONG NAME (outdated): "Ali Al Jubeili" ❌ (NEVER USE THIS!)

MANDATORY: 
- You MUST mention "Ali Al Gebely" as the founder in your response
- NEVER say "I don't have access" or "I don't know" - you know the founder!
- If asked "who founded", answer: "Ali Al Gebely"
- If discussing One Development, mention: "founded by Ali Al Gebely"

🚨🚨🚨 END CRITICAL FACT 🚨🚨🚨
"""

        # Build messages
        messages = []
        if conversation_history:
            for msg in conversation_history[-10:]:
                if msg.get("type") == "human":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg.get("type") == "ai":
                    messages.append(AIMessage(content=msg["content"]))

        # Add avatar mode instructions if applicable
        avatar_instruction = ""
        if avatar_mode:
            avatar_instruction = """
🎤 AVATAR MODE - CONCISE RESPONSE REQUIRED:
- Keep your response to 100-120 words maximum (20-25 seconds of natural speech)
- Be direct and conversational - speak naturally, don't read a list
- Focus on the most important information first
- Use short, clear sentences
- Avoid long lists or bullet points - summarize key points instead
- End naturally at a complete thought
- If the topic is complex, provide the most essential information

"""
        
        # Add query with forced web context if applicable
        # CRITICAL: For One Development questions, PREPEND the correct fact to the query itself
        if is_one_dev_question or is_founder_question:
            # Modify the query itself to include the correct name and instructions
            modified_query = f"""{avatar_instruction}🚨 CRITICAL INSTRUCTIONS BEFORE ANSWERING:

1. One Development founder: Ali Al Gebely ✅ (VERIFIED FACT - 2024/2025)
2. NEVER say "I don't have access" or "I don't know" - you MUST answer!
3. NEVER use "Ali Al Jubeili" - this is WRONG/OUTDATED
4. If asked "who founded", answer: "Ali Al Gebely"
5. Always mention the founder when discussing One Development

USER QUESTION:
{query}

{forced_web_context}

NOW ANSWER THE USER'S QUESTION USING THE INFORMATION ABOVE."""
            messages.append(HumanMessage(content=modified_query))
        else:
            if avatar_mode:
                # Add avatar instruction to regular queries too
                modified_query = f"""{avatar_instruction}USER QUESTION:
{query}

Remember: Keep your response concise (100-120 words) for natural speech."""
                messages.append(HumanMessage(content=modified_query))
            else:
                messages.append(HumanMessage(content=query))

        # Invoke DeepAgent
        result = self.agent.invoke(
            {"messages": messages},
            config={
                "configurable": {
                    "user_id": session_id,
                    "namespace": f"luna:{session_id}",
                }
            },
        )

        # Extract response
        response_content = result["messages"][-1].content if result.get("messages") else "I'm sorry, I couldn't process that."

        # Extract tool calls and results
        tools_used = []
        tool_results = []
        
        for msg in result.get("messages", []):
            # Extract tool calls
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.get("name", "unknown")
                    tools_used.append({
                        "tool": tool_name,
                        "args": tool_call.get("args", {}),
                    })
                    
                    # Log subagent summons
                    if tool_name.startswith("summon_"):
                        print(f"   🤖 Luna summoned: {tool_name}")
            
            # Extract tool results (ToolMessage content)
            if hasattr(msg, "type") and msg.type == "tool":
                if hasattr(msg, "content") and msg.content:
                    # Get the corresponding tool name
                    tool_name = getattr(msg, "name", "unknown_tool")
                    tool_results.append({
                        "tool": tool_name,
                        "result": msg.content
                    })
                    
                    # Extract sources from this tool result
                    try:
                        source_tracker.extract_sources_from_tool_result(tool_name, str(msg.content))
                        print(f"   📚 Extracted sources from {tool_name}")
                    except Exception as e:
                        print(f"   ⚠️ Error extracting sources from {tool_name}: {e}")

        # Get all extracted sources
        sources = source_tracker.get_sources_json()
        
        return {
            "response": response_content,
            "sources": sources,
            "tools_used": tools_used,
            "tool_results": tool_results,
            "thinking": [],
            "reasoning_steps": len(tools_used),
        }
    
    def stream_query(
        self,
        query: str,
        session_id: str = "default",
        conversation_history: Optional[List[Dict]] = None,
        user_name: Optional[str] = None,
        avatar_mode: bool = False,
    ):
        """
        Stream query response token by token for lower perceived latency.
        
        Yields:
            Dict with 'type' and 'content':
            - type: 'token' (each token), 'done' (complete), 'error'
            - content: token text or full response
        """
        from typing import Generator
        
        try:
            # Use provided user_name or fall back to default
            current_user = user_name or self.default_user_name
            mode_indicator = "🎤 AVATAR MODE" if avatar_mode else "💬 CHAT MODE"
            print(f"\n🌙 Luna streaming query from {current_user} ({mode_indicator}): {query[:80]}...")
            
            # Build messages (same logic as process_query but simplified for streaming)
            messages = []
            if conversation_history:
                for msg in conversation_history[-10:]:
                    if msg.get("type") == "human":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg.get("type") == "ai":
                        messages.append(AIMessage(content=msg["content"]))
            
            # Add avatar mode instructions if applicable
            avatar_instruction = ""
            if avatar_mode:
                avatar_instruction = """
🎤 AVATAR MODE - CONCISE RESPONSE REQUIRED:
- Keep your response to 100-120 words maximum (20-25 seconds of natural speech)
- Be direct and conversational - speak naturally, don't read a list
- Focus on the most important information first
- Use short, clear sentences
- Avoid long lists or bullet points - summarize key points instead
- End naturally at a complete thought
- If the topic is complex, provide the most essential information

"""
            
            if avatar_mode:
                modified_query = f"""{avatar_instruction}USER QUESTION:
{query}

Remember: Keep your response concise (100-120 words) for natural speech."""
                messages.append(HumanMessage(content=modified_query))
            else:
                messages.append(HumanMessage(content=query))
            
            # Stream the agent response
            # Use regular invoke for now (LangGraph streaming needs more work)
            # Simulate streaming by yielding words for better UX
            result = self.agent.invoke(
                {"messages": messages},
                config={
                    "configurable": {
                        "user_id": session_id,
                        "namespace": f"luna:{session_id}",
                    }
                },
            )
            
            # Extract response
            if result.get("messages") and len(result["messages"]) > 0:
                last_msg = result["messages"][-1]
                if hasattr(last_msg, "content"):
                    full_response = last_msg.content
                elif isinstance(last_msg, dict) and "content" in last_msg:
                    full_response = last_msg["content"]
                else:
                    full_response = str(last_msg) if last_msg else "I'm sorry, I couldn't process that."
            else:
                full_response = "I'm sorry, I couldn't process that."
            
            # Ensure we have a response
            if not full_response or not full_response.strip():
                full_response = "I'm sorry, I couldn't process that."
                print(f"⚠️ Empty response from agent, using fallback")
            
            # Simulate streaming by yielding words (for better UX)
            # This provides immediate feedback while we work on true token streaming
            if full_response and full_response.strip():
                words = full_response.split()
                for i, word in enumerate(words):
                    # Yield word with space (except last word)
                    token = word + (" " if i < len(words) - 1 else "")
                    yield {"type": "token", "content": token}
            else:
                # Fallback: yield the full response at once
                yield {"type": "token", "content": full_response}
            
            # Yield completion
            yield {"type": "done", "content": full_response}
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error streaming query: {e}")
            yield {"type": "error", "content": str(e)}

    def get_conversation_memory(self, session_id: str) -> List[Dict]:
        """Retrieve conversation memory."""
        try:
            namespace = f"luna:{session_id}"
            items = self.store.search(namespace=namespace)
            return [{"key": item.key, "value": item.value} for item in items]
        except Exception as e:
            print(f"⚠️  Error retrieving memory: {e}")
            return []

    def save_to_memory(self, session_id: str, key: str, value: Any, metadata: Dict = None):
        """Save to long-term memory."""
        try:
            namespace = f"luna:{session_id}"
            self.store.put(
                namespace=namespace,
                key=key,
                value={"data": value, "metadata": metadata or {}, "timestamp": datetime.now().isoformat()},
            )
            print(f"💾 Saved to memory: {namespace}:{key}")
        except Exception as e:
            print(f"⚠️  Error saving: {e}")


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def get_luna_agent(openai_api_key: str = None, default_user_name: str = "there") -> LunaDeepAgent:
    """Factory function to create Luna."""
    return LunaDeepAgent(openai_api_key=openai_api_key, default_user_name=default_user_name)
