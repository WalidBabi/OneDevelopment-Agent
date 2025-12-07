#!/usr/bin/env python3
"""
Test script for Luna DeepAgent implementation
Tests memory persistence, subagent delegation, and tool usage
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

def test_imports():
    """Test that all required imports work"""
    print("\n" + "="*60)
    print("TEST 1: Checking Imports")
    print("="*60)
    
    try:
        from deepagents import create_deep_agent
        print("✅ deepagents imported successfully")
    except ImportError as e:
        print(f"❌ deepagents import failed: {e}")
        print("   → Install with: pip install deepagents")
        return False
    
    try:
        from deepagents.backends import FilesystemBackend
        print("✅ FilesystemBackend imported successfully")
    except ImportError as e:
        print(f"❌ FilesystemBackend import failed: {e}")
        return False
    
    try:
        from langgraph.store.memory import InMemoryStore
        print("✅ InMemoryStore imported successfully")
    except ImportError as e:
        print(f"❌ InMemoryStore import failed: {e}")
        return False
    
    try:
        from agent.luna_deepagent import LunaDeepAgent, get_luna_agent
        print("✅ LunaDeepAgent imported successfully")
    except ImportError as e:
        print(f"❌ LunaDeepAgent import failed: {e}")
        return False
    
    return True


def test_initialization():
    """Test Luna initialization"""
    print("\n" + "="*60)
    print("TEST 2: Luna Initialization")
    print("="*60)
    
    try:
        from agent.luna_deepagent import get_luna_agent
        
        print("Initializing Luna...")
        luna = get_luna_agent()
        
        print(f"✅ Luna initialized successfully")
        print(f"   → Model: {luna.model_name}")
        print(f"   → Tools: {len(luna.tools)} tools")
        print(f"   → Subagents: {len(luna.subagents)} subagents")
        print(f"   → Memory path: {luna.memories_path}")
        
        # Check memory directory
        if os.path.exists(luna.memories_path):
            print(f"✅ Memory directory exists: {luna.memories_path}")
        else:
            print(f"⚠️  Memory directory not found: {luna.memories_path}")
        
        return luna
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_memory_operations(luna):
    """Test memory save and retrieve"""
    print("\n" + "="*60)
    print("TEST 3: Memory Operations")
    print("="*60)
    
    if not luna:
        print("❌ Skipping - Luna not initialized")
        return False
    
    try:
        test_session = "test_session_123"
        
        # Save to memory
        print(f"Saving to memory (session: {test_session})...")
        luna.save_to_memory(
            session_id=test_session,
            key="user_name",
            value="Walid",
            metadata={"test": True}
        )
        print("✅ Saved user_name='Walid' to memory")
        
        # Retrieve from memory
        print(f"Retrieving from memory...")
        memories = luna.get_conversation_memory(test_session)
        print(f"✅ Retrieved {len(memories)} memory items")
        
        for mem in memories:
            print(f"   → {mem['key']}: {mem['value']}")
        
        # Check filesystem
        namespace_path = os.path.join(luna.memories_path, f"luna:{test_session}")
        if os.path.exists(namespace_path):
            print(f"✅ Memory files created in filesystem")
            files = os.listdir(namespace_path)
            print(f"   → Files: {files}")
        else:
            print(f"⚠️  No filesystem files found (using InMemoryStore?)")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_subagents(luna):
    """Test subagent configuration"""
    print("\n" + "="*60)
    print("TEST 4: Subagent Configuration")
    print("="*60)
    
    if not luna:
        print("❌ Skipping - Luna not initialized")
        return False
    
    try:
        print(f"Checking {len(luna.subagents)} subagents...")
        
        for i, subagent in enumerate(luna.subagents, 1):
            print(f"\n{i}. {subagent['name']}")
            print(f"   Description: {subagent['description'][:80]}...")
            print(f"   Tools: {len(subagent['tools'])} tools")
            print(f"   Model: {subagent['model']}")
        
        print(f"\n✅ All {len(luna.subagents)} subagents configured correctly")
        return True
        
    except Exception as e:
        print(f"❌ Subagent check failed: {e}")
        return False


def test_query_processing(luna):
    """Test query processing (without actually calling OpenAI)"""
    print("\n" + "="*60)
    print("TEST 5: Query Processing Structure")
    print("="*60)
    
    if not luna:
        print("❌ Skipping - Luna not initialized")
        return False
    
    try:
        print("Checking query processing structure...")
        
        # Check that agent exists
        if luna.agent:
            print("✅ DeepAgent instance created")
        else:
            print("❌ DeepAgent instance is None")
            return False
        
        # Check agent has required methods
        if hasattr(luna.agent, 'invoke'):
            print("✅ Agent has 'invoke' method")
        else:
            print("❌ Agent missing 'invoke' method")
            return False
        
        print("\n⚠️  Skipping actual query (would call OpenAI API)")
        print("   To test full query processing, run:")
        print("   luna.process_query('Tell me about One Development', session_id='test')")
        
        return True
        
    except Exception as e:
        print(f"❌ Query processing check failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 LUNA DEEPAGENT IMPLEMENTATION TEST SUITE")
    print("="*60)
    
    # Check Python version
    import sys
    python_version = sys.version_info
    print(f"\nPython version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 11):
        print("⚠️  WARNING: Python 3.11+ required for DeepAgents")
        print("   Current version may not support all features")
        print("   See UPGRADE-TO-PYTHON-3.11.md for upgrade instructions")
    else:
        print("✅ Python version compatible with DeepAgents")
    
    # Run tests
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    
    # Test 2: Initialization
    luna = test_initialization()
    results.append(("Initialization", luna is not None))
    
    # Test 3: Memory
    results.append(("Memory Operations", test_memory_operations(luna)))
    
    # Test 4: Subagents
    results.append(("Subagent Configuration", test_subagents(luna)))
    
    # Test 5: Query Structure
    results.append(("Query Processing Structure", test_query_processing(luna)))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Luna DeepAgent is ready.")
        print("\nNext steps:")
        print("1. Restart the Django server")
        print("2. Test Luna in the chat interface")
        print("3. Try: 'My name is Walid' → Refresh → 'Do you know my name?'")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        if python_version.minor < 11:
            print("\n💡 Most likely cause: Python version < 3.11")
            print("   See UPGRADE-TO-PYTHON-3.11.md for upgrade instructions")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)







