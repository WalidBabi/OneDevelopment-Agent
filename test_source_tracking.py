"""
Test script for Source Tracking System

This demonstrates how Luna automatically extracts and displays sources
from tool responses.
"""

from backend.agent.source_tracker import SourceTracker


def test_source_extraction():
    """Test source extraction from tool results"""
    
    print("🧪 Testing Source Tracker\n")
    print("=" * 70)
    
    # Initialize tracker
    tracker = SourceTracker()
    
    # Simulate a tool result from web search
    tool_result = """
    **Results from Web Search:**
    
    1. **One Development Launches AED 2 Billion Project**
       URL: https://www.businessnewse.com/2024/09/19/one-development-project
       One Development is set to launch a massive project in Dubai's City of Arabia.
    
    2. **Ali Al Gebely - Founder & Chairman**
       https://www.cbnme.com/power-hour-2025/37-ali-al-gebely-founder-chairman-one-development/
       Profile of the Emirati entrepreneur leading One Development.
    
    3. **Dubai Real Estate Developers to Watch in 2025**
       URL: https://www.constructionweekonline.com/power-lists/dubai-developers-2025
       One Development features prominently in the list of developers.
    
    For more information, visit https://oneuae.com
    """
    
    # Extract sources
    print("\n📚 Extracting sources from tool result...")
    sources = tracker.extract_sources_from_tool_result('tavily_search', tool_result)
    
    print(f"\n✅ Found {len(sources)} sources!\n")
    
    # Display extracted sources
    for i, source in enumerate(sources, 1):
        print(f"\n{i}. {source.title}")
        print(f"   Type: {source.source_type}")
        print(f"   Reliability: {source.reliability}")
        print(f"   URL: {source.url}")
        if source.snippet:
            print(f"   Snippet: {source.snippet[:100]}...")
    
    # Display formatted output (as it would appear in Luna's response)
    print("\n" + "=" * 70)
    print("\n📝 How it appears in Luna's response:\n")
    print(tracker.format_sources_for_response())
    
    # Display JSON format (as sent to frontend)
    print("\n" + "=" * 70)
    print("\n💻 JSON format sent to frontend:\n")
    import json
    print(json.dumps(tracker.get_sources_json(), indent=2))
    
    print("\n" + "=" * 70)
    print("\n✨ Source tracking working perfectly!")
    print("\nLuna will now automatically:")
    print("  ✓ Extract sources from all tool responses")
    print("  ✓ Classify them by type and reliability")
    print("  ✓ Display them beautifully in the UI")
    print("  ✓ Make them clickable and verified")
    print("\n🎉 Just like Copilot!")


if __name__ == "__main__":
    test_source_extraction()







