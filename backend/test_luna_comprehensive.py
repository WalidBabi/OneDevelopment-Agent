"""
Comprehensive Luna Testing Suite

Tests Luna's capabilities across multiple dimensions:
- Knowledge retrieval
- Web search fallback
- Subagent summoning
- Context awareness
- Error handling
- Response quality
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

# Setup paths
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, backend_dir)
sys.path.insert(0, project_root)

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Import Django and setup
import django
try:
    django.setup()
except Exception as e:
    print(f"Warning: Django setup partial failure: {e}")
    # Continue anyway - we mainly need the agent

from agent.luna_deepagent import get_luna_agent


# ============================================================================
# TEST CATEGORIES
# ============================================================================

TEST_CATEGORIES = {
    "knowledge_base": {
        "name": "Knowledge Base Queries",
        "questions": [
            "What is One Development?",
            "Tell me about Laguna Residence",
            "What projects do you have?",
            "Where is One Development located?",
            "What is DO Dubai Islands?",
        ]
    },
    "property_search": {
        "name": "Property Search (Should trigger web search)",
        "questions": [
            "What properties do you have in Dubai Marina?",
            "Show me apartments in Downtown Dubai",
            "What villas are available in Palm Jumeirah?",
            "Properties in Business Bay?",
            "Penthouses in JBR?",
        ]
    },
    "pricing": {
        "name": "Pricing & Investment (Should summon Pricing Agent)",
        "questions": [
            "What's the price range for 2 bedroom apartments?",
            "What is the ROI for Dubai Marina properties?",
            "What are payment plans available?",
            "Is it better to buy or rent in Dubai?",
            "What are the average prices in Downtown Dubai?",
        ]
    },
    "comparison": {
        "name": "Comparison Queries (Should summon Comparison Agent)",
        "questions": [
            "Compare Dubai Marina vs Downtown Dubai",
            "What's better: villa or apartment for investment?",
            "Compare Laguna Residence with other projects",
            "Dubai vs Abu Dhabi for property investment",
            "Palm Jumeirah vs Dubai Marina",
        ]
    },
    "buyer_journey": {
        "name": "Buying Process (Should summon Buyer Journey Agent)",
        "questions": [
            "How do I buy property in Dubai?",
            "What documents do I need to buy property?",
            "Can foreigners buy property in Dubai?",
            "What are the steps to purchase a property?",
            "How long does it take to buy property in Dubai?",
        ]
    },
    "market_research": {
        "name": "Market Research (Should summon Research Agent)",
        "questions": [
            "What are the Dubai real estate market trends?",
            "Is Dubai property market growing?",
            "What are the best areas for investment in Dubai?",
            "Dubai property market forecast 2024",
            "Rental yields in Dubai",
        ]
    },
    "user_context": {
        "name": "User Context & Memory (Should remember Walid)",
        "questions": [
            "What's my name?",
            "Do you remember me?",
            "What have we discussed before?",
            "Remember I'm interested in Dubai Marina",
            "What did I ask about earlier?",
        ]
    },
    "edge_cases": {
        "name": "Edge Cases & Error Handling",
        "questions": [
            "What is the meaning of life?",  # Off-topic
            "asdfghjkl",  # Gibberish
            "",  # Empty
            "Tell me a joke",  # Off-topic but friendly
            "How can I apply for a job?",  # No careers page
        ]
    },
    "multi_step": {
        "name": "Multi-Step Reasoning",
        "questions": [
            "I'm a first-time buyer with 500k AED budget. What are my options in Dubai Marina?",
            "I want to invest 2 million AED. Compare Dubai Marina and Downtown and recommend the best option.",
            "What's the complete process and cost of buying a 1BR apartment in Dubai as a foreigner?",
            "I want high ROI and good rental yields. What area and property type do you recommend?",
            "Compare payment plans for 2BR apartments in Dubai Marina vs Business Bay with ROI analysis",
        ]
    },
    "specificity": {
        "name": "Specific vs Generic Responses",
        "questions": [
            "What's the exact address of Laguna Residence?",
            "How many units does Laguna Residence have?",
            "What is the exact price of a 2BR in Laguna Residence?",
            "What amenities does DO Dubai Islands have?",
            "When will Al Marjan Islands project be completed?",
        ]
    }
}


# ============================================================================
# TEST EXECUTION
# ============================================================================

class LunaTestSuite:
    def __init__(self):
        print("=" * 80)
        print("🧪 LUNA COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print()
        
        # Initialize Luna
        print("Initializing Luna...")
        try:
            self.luna = get_luna_agent()
            print("✅ Luna initialized successfully")
            print()
        except Exception as e:
            print(f"❌ Failed to initialize Luna: {e}")
            sys.exit(1)
        
        self.results = {}
        self.session_id = f"test_walid_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def analyze_response(self, question: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single response for quality metrics."""
        response_text = response.get("response", "")
        tools_used = response.get("tools_used", [])
        
        analysis = {
            "question": question,
            "response_length": len(response_text),
            "tools_count": len(tools_used),
            "tools_names": [t.get("tool") for t in tools_used],
            "has_knowledge_base": any("knowledge_base" in t.get("tool", "") for t in tools_used),
            "has_web_search": any("web" in t.get("tool", "").lower() or "tavily" in t.get("tool", "").lower() for t in tools_used),
            "has_subagent": any("summon" in t.get("tool", "") for t in tools_used),
            "mentions_walid": "walid" in response_text.lower(),
            "has_url": "http" in response_text or "www" in response_text,
            "is_specific": len(response_text) > 200,
            "is_generic": "I don't have" in response_text or "I couldn't" in response_text or "Unfortunately" in response_text.lower(),
            "is_proactive": "let me" in response_text.lower() or "i'll" in response_text.lower(),
        }
        
        # Calculate quality score
        score = 0
        if analysis["tools_count"] > 0:
            score += 2
        if analysis["tools_count"] > 1:
            score += 2  # Multi-tool usage
        if analysis["has_web_search"]:
            score += 2
        if analysis["has_subagent"]:
            score += 3
        if analysis["is_specific"]:
            score += 2
        if not analysis["is_generic"]:
            score += 2
        if analysis["is_proactive"]:
            score += 1
        if analysis["has_url"]:
            score += 1
        
        analysis["quality_score"] = min(score, 10)  # Cap at 10
        
        return analysis
    
    def test_category(self, category_key: str, category_data: Dict) -> List[Dict]:
        """Test a category of questions."""
        print(f"\n{'=' * 80}")
        print(f"📂 CATEGORY: {category_data['name']}")
        print(f"{'=' * 80}\n")
        
        results = []
        
        for i, question in enumerate(category_data["questions"], 1):
            print(f"Question {i}/{len(category_data['questions'])}: {question}")
            
            try:
                # Process query
                response = self.luna.process_query(
                    query=question,
                    session_id=self.session_id,
                    conversation_history=[]
                )
                
                # Analyze response
                analysis = self.analyze_response(question, response)
                
                # Print summary
                print(f"   Response length: {analysis['response_length']} chars")
                print(f"   Tools used: {analysis['tools_count']} - {analysis['tools_names'][:3]}")
                print(f"   Quality score: {analysis['quality_score']}/10")
                
                if analysis['is_generic']:
                    print(f"   ⚠️  WARNING: Generic response detected")
                if analysis['has_subagent']:
                    print(f"   🤖 Subagent summoned!")
                if analysis['has_web_search']:
                    print(f"   🌐 Web search used!")
                
                print()
                
                results.append({
                    "category": category_key,
                    "question": question,
                    "response": response.get("response", "")[:500],  # Truncate for summary
                    "analysis": analysis
                })
                
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}\n")
                results.append({
                    "category": category_key,
                    "question": question,
                    "error": str(e),
                    "analysis": {"quality_score": 0}
                })
        
        return results
    
    def run_all_tests(self):
        """Run all test categories."""
        print("Starting comprehensive testing...\n")
        
        all_results = []
        
        for category_key, category_data in TEST_CATEGORIES.items():
            results = self.test_category(category_key, category_data)
            all_results.extend(results)
            self.results[category_key] = results
        
        return all_results
    
    def analyze_weak_areas(self):
        """Analyze test results to identify weak areas."""
        print("\n" + "=" * 80)
        print("📊 WEAKNESS ANALYSIS")
        print("=" * 80 + "\n")
        
        category_scores = {}
        issues = []
        
        # Calculate scores by category
        for category_key, results in self.results.items():
            scores = [r.get("analysis", {}).get("quality_score", 0) for r in results]
            avg_score = sum(scores) / len(scores) if scores else 0
            category_scores[category_key] = {
                "avg_score": avg_score,
                "results": results
            }
        
        # Identify weak categories
        print("📈 Category Performance:\n")
        for category_key, data in sorted(category_scores.items(), key=lambda x: x[1]["avg_score"]):
            category_name = TEST_CATEGORIES[category_key]["name"]
            avg_score = data["avg_score"]
            
            if avg_score < 5:
                status = "❌ WEAK"
                issues.append(f"Category '{category_name}' has low score: {avg_score:.1f}/10")
            elif avg_score < 7:
                status = "⚠️  NEEDS IMPROVEMENT"
            else:
                status = "✅ GOOD"
            
            print(f"   {status} - {category_name}: {avg_score:.1f}/10")
        
        # Specific issues
        print("\n🔍 Specific Issues Detected:\n")
        
        generic_responses = []
        no_web_search = []
        no_subagent_when_needed = []
        no_tools = []
        
        for category_key, results in self.results.items():
            for result in results:
                analysis = result.get("analysis", {})
                
                if analysis.get("is_generic"):
                    generic_responses.append(result["question"])
                
                if category_key == "property_search" and not analysis.get("has_web_search"):
                    no_web_search.append(result["question"])
                
                if category_key in ["pricing", "comparison", "buyer_journey", "market_research"]:
                    if not analysis.get("has_subagent"):
                        no_subagent_when_needed.append((category_key, result["question"]))
                
                if analysis.get("tools_count", 0) == 0:
                    no_tools.append(result["question"])
        
        if generic_responses:
            print(f"⚠️  Generic Responses ({len(generic_responses)}):")
            for q in generic_responses[:3]:
                print(f"      - {q}")
            issues.append(f"Generic responses in {len(generic_responses)} cases")
        
        if no_web_search:
            print(f"\n⚠️  Missing Web Search ({len(no_web_search)}):")
            for q in no_web_search[:3]:
                print(f"      - {q}")
            issues.append(f"Web search not used in {len(no_web_search)} property searches")
        
        if no_subagent_when_needed:
            print(f"\n⚠️  Missing Subagent Summoning ({len(no_subagent_when_needed)}):")
            for cat, q in no_subagent_when_needed[:3]:
                print(f"      [{cat}] - {q}")
            issues.append(f"Subagents not summoned in {len(no_subagent_when_needed)} cases")
        
        if no_tools:
            print(f"\n⚠️  No Tools Used ({len(no_tools)}):")
            for q in no_tools[:3]:
                print(f"      - {q}")
            issues.append(f"No tools used in {len(no_tools)} cases")
        
        return {
            "category_scores": category_scores,
            "issues": issues,
            "summary": {
                "total_tests": sum(len(r) for r in self.results.values()),
                "avg_overall_score": sum(data["avg_score"] for data in category_scores.values()) / len(category_scores),
                "generic_count": len(generic_responses),
                "missing_web_search": len(no_web_search),
                "missing_subagents": len(no_subagent_when_needed),
                "no_tools_count": len(no_tools),
            }
        }
    
    def generate_recommendations(self, weak_areas: Dict):
        """Generate recommendations based on weak areas."""
        print("\n" + "=" * 80)
        print("💡 RECOMMENDATIONS FOR IMPROVEMENT")
        print("=" * 80 + "\n")
        
        summary = weak_areas["summary"]
        
        recommendations = []
        
        # Overall assessment
        overall_score = summary["avg_overall_score"]
        print(f"Overall Score: {overall_score:.1f}/10\n")
        
        if overall_score < 6:
            print("🚨 CRITICAL: Luna needs significant improvements\n")
        elif overall_score < 8:
            print("⚠️  Luna is functional but has room for improvement\n")
        else:
            print("✅ Luna is performing well!\n")
        
        # Specific recommendations
        print("Recommended Actions:\n")
        
        if summary["missing_web_search"] > 2:
            rec = "🌐 IMPROVE WEB SEARCH TRIGGERING: Luna is not searching the web when knowledge base fails. Strengthen the fallback logic in the system prompt."
            print(f"1. {rec}")
            recommendations.append(rec)
        
        if summary["missing_subagents"] > 3:
            rec = "🤖 IMPROVE SUBAGENT SUMMONING: Luna is not summoning subagents for complex queries. Add more explicit instructions in the system prompt about when to summon each subagent."
            print(f"2. {rec}")
            recommendations.append(rec)
        
        if summary["generic_count"] > 3:
            rec = "📝 REDUCE GENERIC RESPONSES: Too many 'I don't have information' responses. Implement stronger requirement to try multiple tools before giving up."
            print(f"3. {rec}")
            recommendations.append(rec)
        
        if summary["no_tools_count"] > 2:
            rec = "🔧 INCREASE TOOL USAGE: Luna is answering without using tools. Strengthen instruction to always use appropriate tools for research."
            print(f"4. {rec}")
            recommendations.append(rec)
        
        # Category-specific
        weak_categories = [k for k, v in weak_areas["category_scores"].items() if v["avg_score"] < 6]
        if weak_categories:
            rec = f"📂 FOCUS ON WEAK CATEGORIES: {', '.join([TEST_CATEGORIES[c]['name'] for c in weak_categories])}"
            print(f"5. {rec}")
            recommendations.append(rec)
        
        return recommendations


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run comprehensive test suite."""
    suite = LunaTestSuite()
    
    # Run all tests
    all_results = suite.run_all_tests()
    
    # Analyze weak areas
    weak_areas = suite.analyze_weak_areas()
    
    # Generate recommendations
    recommendations = suite.generate_recommendations(weak_areas)
    
    # Save results
    output_file = f"luna_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": all_results,
            "weak_areas": weak_areas,
            "recommendations": recommendations
        }, f, indent=2)
    
    print(f"\n📄 Full results saved to: {output_file}")
    
    print("\n" + "=" * 80)
    print("✅ COMPREHENSIVE TESTING COMPLETE")
    print("=" * 80)
    
    return weak_areas, recommendations


if __name__ == "__main__":
    main()

