#!/usr/bin/env python
"""
Test script for Luna DeepAgent implementation
Run this to verify the migration was successful
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from agent import get_luna_agent, chat_with_luna
from agent.luna_deepagent import LunaDeepAgent


def test_agent_initialization():
    """Test 1: Agent initializes correctly"""
    print("🧪 Test 1: Agent Initialization")
    print("-" * 50)
    
    try:
        agent = get_luna_agent()
        print(f"✅ Agent initialized: {type(agent).__name__}")
        print(f"✅ Tools available: {len(agent.tools)}")
        
        # Check it's the DeepAgent
        assert isinstance(agent, LunaDeepAgent), "Should be LunaDeepAgent instance"
        print("✅ Using DeepAgent implementation")
        
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


def test_simple_query():
    """Test 2: Process a simple query"""
    print("\n🧪 Test 2: Simple Query")
    print("-" * 50)
    
    try:
        agent = get_luna_agent()
        
        # Test with a simple greeting
        result = agent.process_query(
            query="Hello! Who are you?",
            session_id="test_session_1"
        )
        
        print(f"✅ Query processed successfully")
        print(f"✅ Response received: {len(result['response'])} chars")
        print(f"✅ Reasoning steps: {result.get('reasoning_steps', 0)}")
        print(f"✅ Tools used: {result.get('tools_used', 0)}")
        print(f"\nResponse preview:")
        print(result['response'][:200] + "..." if len(result['response']) > 200 else result['response'])
        
        return True
    except Exception as e:
        print(f"❌ Query processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_usage():
    """Test 3: Query that should use tools"""
    print("\n🧪 Test 3: Tool Usage")
    print("-" * 50)
    
    try:
        agent = get_luna_agent()
        
        # Query that should trigger tool usage
        result = agent.process_query(
            query="What projects does One Development have?",
            session_id="test_session_2"
        )
        
        print(f"✅ Query processed")
        print(f"✅ Tools used: {result.get('tools_used', 0)}")
        
        if result.get('tools_info'):
            print("\n📊 Tools called:")
            for tool in result['tools_info']:
                print(f"  - {tool['friendly_name']}")
        
        if result.get('thinking'):
            print(f"\n💭 Thinking steps: {len(result['thinking'])}")
            for step in result['thinking'][:3]:  # Show first 3 steps
                print(f"  - {step.get('description', step.get('type', 'Unknown'))}")
        
        print(f"\nResponse preview:")
        print(result['response'][:200] + "..." if len(result['response']) > 200 else result['response'])
        
        return True
    except Exception as e:
        print(f"❌ Tool usage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_convenience_function():
    """Test 4: Convenience chat function"""
    print("\n🧪 Test 4: Convenience Function")
    print("-" * 50)
    
    try:
        response = chat_with_luna("What is One Development?")
        
        print(f"✅ chat_with_luna() works")
        print(f"✅ Response: {len(response)} chars")
        print(f"\nResponse preview:")
        print(response[:200] + "..." if len(response) > 200 else response)
        
        return True
    except Exception as e:
        print(f"❌ Convenience function failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conversation_history():
    """Test 5: Conversation with history"""
    print("\n🧪 Test 5: Conversation History")
    print("-" * 50)
    
    try:
        agent = get_luna_agent()
        session_id = "test_session_history"
        
        # First message
        result1 = agent.process_query(
            query="I'm interested in luxury properties",
            session_id=session_id
        )
        print(f"✅ First message processed")
        
        # Build history
        history = [
            {'message_type': 'human', 'content': "I'm interested in luxury properties"},
            {'message_type': 'ai', 'content': result1['response']}
        ]
        
        # Second message with context
        result2 = agent.process_query(
            query="What do you recommend?",
            session_id=session_id,
            conversation_history=history
        )
        print(f"✅ Follow-up message processed")
        print(f"\nResponse preview:")
        print(result2['response'][:200] + "..." if len(result2['response']) > 200 else result2['response'])
        
        return True
    except Exception as e:
        print(f"❌ Conversation history test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("🌙 Luna DeepAgent Migration Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("Initialization", test_agent_initialization),
        ("Simple Query", test_simple_query),
        ("Tool Usage", test_tool_usage),
        ("Convenience Function", test_convenience_function),
        ("Conversation History", test_conversation_history),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Migration successful!")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed. Review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)




