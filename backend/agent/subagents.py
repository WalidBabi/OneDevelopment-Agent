"""
Luna Subagents
Specialized agents for specific tasks that can be spawned by the main Luna agent.

Based on DeepAgents pattern:
- Subagents handle specialized deep-dive tasks
- They have isolated context to prevent main agent context pollution
- Each subagent has specific expertise and tools

Currently implemented as enhanced tools (can be upgraded to full subagents later)
"""

from langchain_core.tools import tool
from typing import List, Dict, Any


# ============================================================================
# RESEARCH SUBAGENT (as enhanced tool)
# ============================================================================

@tool
def deep_research(topic: str, aspects: List[str] = None) -> str:
    """
    Perform deep research on a specific topic about UAE real estate.
    
    Use this for complex research questions that need thorough analysis:
    - Market analysis and trends
    - Area comparisons
    - Investment due diligence
    - Property type comparisons
    
    Args:
        topic: Main topic to research (e.g., "Dubai Marina investment potential")
        aspects: Specific aspects to cover (e.g., ["prices", "rental yields", "future development"])
        
    Returns:
        Comprehensive research findings
    """
    from agent.tools import search_knowledge_base, search_web_for_market_data, get_dubai_market_context
    
    results = []
    
    # Search internal knowledge
    kb_result = search_knowledge_base.invoke({"query": topic, "n_results": 5})
    if kb_result and "No relevant" not in kb_result:
        results.append(f"**Internal Knowledge:**\n{kb_result}")
    
    # Search web for market data
    web_result = search_web_for_market_data.invoke({"query": topic})
    if web_result and "unavailable" not in web_result.lower():
        results.append(f"**Market Data:**\n{web_result}")
    
    # Add market context
    context = get_dubai_market_context.invoke({})
    results.append(f"**Market Context:**\n{context}")
    
    if aspects:
        results.append(f"\n**Aspects Requested:** {', '.join(aspects)}")
    
    return "\n\n---\n\n".join(results) if results else "No research data found."


# ============================================================================
# PRICING SUBAGENT (as enhanced tool)
# ============================================================================

@tool
def analyze_pricing(
    property_type: str,
    location: str,
    bedrooms: int = None
) -> str:
    """
    Analyze pricing for a specific property type and location.
    
    Provides:
    - Price ranges from knowledge base
    - Market comparison data
    - Payment plan information
    - ROI estimates
    
    Use for pricing questions, budget discussions, and investment analysis.
    
    Args:
        property_type: Type of property (villa, apartment, townhouse, penthouse)
        location: Area in Dubai (e.g., "Dubai Marina", "Downtown")
        bedrooms: Number of bedrooms (optional)
        
    Returns:
        Comprehensive pricing analysis
    """
    from agent.tools import search_knowledge_base, search_web_for_market_data
    
    # Build query
    query_parts = [property_type, location]
    if bedrooms:
        query_parts.append(f"{bedrooms} bedroom")
    query = " ".join(query_parts) + " price"
    
    results = []
    
    # Search for One Development pricing
    kb_result = search_knowledge_base.invoke({"query": query + " One Development", "n_results": 5})
    if kb_result and "No relevant" not in kb_result:
        results.append(f"**One Development Properties:**\n{kb_result}")
    
    # Get market pricing
    market_query = f"{property_type} {location} price per sqft Dubai"
    market_result = search_web_for_market_data.invoke({"query": market_query})
    if market_result:
        results.append(f"**Market Pricing Context:**\n{market_result}")
    
    # Add standard pricing guidance
    pricing_guide = f"""
**General Pricing Guide for {location}:**

Typical price ranges in {location}:
- Apartments: AED 1,000 - 2,500 per sqft
- Villas: AED 1,500 - 3,500 per sqft
- Penthouses: AED 2,000 - 4,500 per sqft

Factors affecting price:
- Floor level and view
- Unit size and layout
- Finishing quality
- Developer reputation
- Market timing

For exact pricing on One Development properties, please contact our sales team.
"""
    results.append(pricing_guide)
    
    return "\n\n---\n\n".join(results)


# ============================================================================
# COMPARISON SUBAGENT (as enhanced tool)
# ============================================================================

@tool
def compare_properties(
    items: List[str],
    comparison_criteria: List[str] = None
) -> str:
    """
    Compare multiple properties, areas, or options.
    
    Use for:
    - Area comparisons (Dubai Marina vs Downtown)
    - Property type comparisons (villa vs apartment)
    - Project comparisons
    - Investment option comparisons
    
    Args:
        items: Items to compare (e.g., ["Dubai Marina", "Downtown Dubai"])
        comparison_criteria: What to compare (e.g., ["price", "amenities", "location"])
        
    Returns:
        Structured comparison with pros and cons
    """
    from agent.tools import search_knowledge_base, search_web_for_market_data
    
    if not comparison_criteria:
        comparison_criteria = ["price", "location", "amenities", "investment potential"]
    
    results = [f"**Comparison: {' vs '.join(items)}**\n"]
    
    for item in items:
        item_results = [f"\n### {item}\n"]
        
        # Get info from knowledge base
        kb_result = search_knowledge_base.invoke({"query": item, "n_results": 3})
        if kb_result and "No relevant" not in kb_result:
            item_results.append(kb_result[:500] + "...")
        
        results.append("\n".join(item_results))
    
    # Add comparison summary
    comparison_table = f"""
**Quick Comparison:**

| Criteria | {' | '.join(items)} |
|----------|{'|'.join(['---' for _ in items])}|
"""
    
    for criterion in comparison_criteria:
        comparison_table += f"| {criterion.title()} | {'| '.join(['See details' for _ in items])} |\n"
    
    results.append(comparison_table)
    results.append("\n*For detailed comparison, please speak with our advisors.*")
    
    return "\n".join(results)


# ============================================================================
# BUYER JOURNEY SUBAGENT (as enhanced tool)
# ============================================================================

@tool
def guide_buyer_journey(buyer_type: str, stage: str = "initial") -> str:
    """
    Guide users through the property buying journey.
    
    Use when users are:
    - First-time buyers asking about the process
    - Foreign investors asking about requirements
    - Anyone asking "how do I buy" or "what's the process"
    
    Args:
        buyer_type: Type of buyer (first_time, investor, expat, uae_resident)
        stage: Current stage (initial, searching, financing, closing)
        
    Returns:
        Tailored guidance for their situation
    """
    
    guides = {
        "first_time": """
**First-Time Buyer's Guide to Dubai Property**

**Step 1: Define Your Requirements**
- Budget and financing options
- Preferred location and property type
- Must-have amenities

**Step 2: Understand the Market**
- Freehold vs Leasehold areas
- Off-plan vs Ready properties
- Developer reputation

**Step 3: Financial Preparation**
- Down payment (typically 20-25%)
- Mortgage pre-approval if needed
- Additional costs (4% DLD fee, agent fee, etc.)

**Step 4: Property Search**
- Work with trusted developers like One Development
- Visit properties and showrooms
- Compare options

**Step 5: Make an Offer & Close**
- Sign reservation form
- Pay booking deposit
- Complete sale agreement (SPA)
- Register with Dubai Land Department

**One Development Support:**
We guide you through every step. Our team handles paperwork and ensures a smooth process.
""",
        "investor": """
**Investor's Guide to Dubai Property**

**Investment Considerations:**
- Expected ROI: 5-8% rental yield
- Capital appreciation potential
- Tax-free rental income
- Golden Visa eligibility (AED 2M+ properties)

**Investment Strategy Options:**
1. **Buy-to-Let**: Steady rental income
2. **Off-Plan**: Lower entry, potential appreciation
3. **Short-term Rental**: Higher returns, more management
4. **Commercial**: Different yield profile

**Due Diligence Checklist:**
☑️ Developer track record
☑️ Location growth potential
☑️ Build quality and amenities
☑️ Service charges
☑️ Exit strategy

**One Development Advantage:**
- Proven track record
- Prime locations
- Flexible payment plans
- Property management services
""",
        "expat": """
**Expat's Guide to Buying in Dubai**

**Can Foreigners Buy Property?**
Yes! In designated freehold areas, non-UAE nationals can:
- Own property outright
- Hold it indefinitely
- Rent it out
- Sell freely

**Popular Freehold Areas:**
- Dubai Marina
- Downtown Dubai
- Palm Jumeirah
- Business Bay
- JBR
- And many more

**Visa Benefits:**
- 3-year visa with AED 750K property
- 10-year Golden Visa with AED 2M property

**Process for Non-Residents:**
1. No residence requirement to buy
2. Can manage remotely
3. Bank accounts can be opened
4. Property management available

**One Development helps expat buyers** with streamlined processes and dedicated support.
"""
    }
    
    # Default to general guide
    guide = guides.get(buyer_type, guides["first_time"])
    
    return guide


# ============================================================================
# GET ALL SUBAGENT TOOLS
# ============================================================================

def get_subagent_tools() -> List:
    """Return all subagent tools for optional inclusion in main agent"""
    return [
        deep_research,
        analyze_pricing,
        compare_properties,
        guide_buyer_journey,
    ]









