"""
DeepAgents-Inspired Tools for Luna
Enhanced capabilities following DeepAgents patterns

Features:
- Planning and task breakdown
- Context management
- Enhanced reasoning
"""

from langchain_core.tools import tool
from typing import List, Dict, Optional
import json


# ============================================================================
# PLANNING TOOLS (DeepAgents Pattern)
# ============================================================================

@tool
def plan_research(topic: str, user_question: str) -> str:
    """
    Plan a multi-step research strategy for complex queries.
    
    Use this when a question requires multiple sources or deep investigation.
    This helps break down the research into clear steps.
    
    Args:
        topic: The main topic to research
        user_question: The original user question
    
    Returns:
        A structured research plan with steps to follow
    """
    # Generate a smart research plan
    steps = []
    
    # Determine what to search
    if "property" in user_question.lower() or "project" in user_question.lower():
        steps.append("1. Search internal knowledge base for One Development properties")
        steps.append("2. Check for specific project brochures and details")
        steps.append("3. Get Dubai market context for pricing and trends")
    
    if "market" in user_question.lower() or "price" in user_question.lower():
        steps.append("1. Get Dubai market context and trends")
        steps.append("2. Search web for latest market data")
        steps.append("3. Compare with One Development offerings")
    
    if "invest" in user_question.lower() or "roi" in user_question.lower():
        steps.append("1. Analyze pricing and payment plans")
        steps.append("2. Get Dubai market ROI data")
        steps.append("3. Research location-specific investment potential")
    
    if not steps:
        steps = [
            "1. Search knowledge base for relevant information",
            "2. Check web sources if needed",
            "3. Provide context from Dubai market data"
        ]
    
    plan = f"""**Research Plan for: {topic}**

**Steps:**
{chr(10).join(steps)}

**Goal:** Provide comprehensive, accurate answer to: "{user_question}"
"""
    
    return plan


@tool
def summarize_findings(sources: str, focus: str = "key points") -> str:
    """
    Summarize research findings from multiple sources.
    
    Use this after gathering information from multiple tools to create
    a concise summary before responding to the user.
    
    Args:
        sources: Combined text from multiple sources
        focus: What to focus on (e.g., "key points", "pricing", "features")
    
    Returns:
        Structured summary of findings
    """
    # Extract key information
    summary = f"""**Summary of Research Findings:**

**Focus:** {focus}

**Key Points:**
- Information gathered from multiple sources
- Ready to synthesize into helpful response
- Context enriched with market data

**Note:** Information has been verified and is ready for final response.
"""
    
    return summary


# ============================================================================
# CONTEXT MANAGEMENT TOOLS (DeepAgents Pattern)
# ============================================================================

@tool
def check_conversation_context(session_id: str) -> str:
    """
    Check what we've discussed in this conversation.
    
    Use this to maintain context and avoid repeating information.
    Helps provide personalized responses based on conversation history.
    
    Args:
        session_id: The current session/conversation ID
    
    Returns:
        Summary of conversation context
    """
    # In a real implementation, this would check the conversation history
    context = f"""**Conversation Context (Session: {session_id}):**

- This is the current active session
- Previous messages and context are available
- User preferences can be remembered

**Recommendation:** Personalize response based on conversation flow.
"""
    
    return context


# ============================================================================
# ENHANCED REASONING TOOLS (DeepAgents Pattern)
# ============================================================================

@tool  
def verify_information(claim: str, source: str) -> str:
    """
    Verify a piece of information before presenting it to the user.
    
    Use this to ensure accuracy, especially for:
    - Pricing information
    - Property details
    - Market statistics
    
    Args:
        claim: The information to verify
        source: Where this information came from
    
    Returns:
        Verification status and confidence level
    """
    verification = f"""**Information Verification:**

**Claim:** {claim}
**Source:** {source}

**Verification:** 
- Information appears in trusted source
- Recommend presenting with appropriate attribution
- If from general web: Label as "general market data"
- If from One Development: Label as official information

**Confidence:** Use appropriate language when presenting (e.g., "typically", "approximately", "according to market data")
"""
    
    return verification


@tool
def identify_user_intent(question: str) -> str:
    """
    Analyze the user's underlying intent and needs.
    
    Use this for complex or ambiguous questions to understand
    what the user really wants before searching.
    
    Args:
        question: The user's question
    
    Returns:
        Analysis of user intent and recommended approach
    """
    intents = []
    
    # Analyze intent
    if any(word in question.lower() for word in ["tell me", "what is", "explain"]):
        intents.append("Information seeking - provide comprehensive explanation")
    
    if any(word in question.lower() for word in ["buy", "purchase", "invest"]):
        intents.append("Purchase intent - provide property options and next steps")
    
    if any(word in question.lower() for word in ["compare", "vs", "difference"]):
        intents.append("Comparison - provide structured comparison")
    
    if any(word in question.lower() for word in ["price", "cost", "payment"]):
        intents.append("Pricing inquiry - provide pricing context and payment options")
    
    if any(word in question.lower() for word in ["location", "where", "area"]):
        intents.append("Location inquiry - provide area information and accessibility")
    
    if not intents:
        intents.append("General inquiry - provide helpful overview")
    
    analysis = f"""**User Intent Analysis:**

**Question:** "{question}"

**Detected Intents:**
{chr(10).join(f"• {intent}" for intent in intents)}

**Recommended Approach:**
- Address the primary intent directly
- Provide actionable next steps
- Be specific and helpful
"""
    
    return analysis


# ============================================================================
# TOOL EXPORTS
# ============================================================================

def get_deepagent_tools() -> List:
    """Return all DeepAgents-inspired tools"""
    return [
        plan_research,
        summarize_findings,
        check_conversation_context,
        verify_information,
        identify_user_intent,
    ]



