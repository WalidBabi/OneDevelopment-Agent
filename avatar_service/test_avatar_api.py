"""
Test Luna Avatar API - Talk to Luna!
"""
import requests
import json
import time

API_URL = "http://localhost:8000"

def test_avatar(text, quality='fast'):
    """Test avatar generation"""
    print(f"\n{'='*70}")
    print(f"🎤 Talking to Luna: '{text[:50]}...'")
    print(f"{'='*70}\n")
    
    # Check server health
    try:
        health = requests.get(f"{API_URL}/health", timeout=5)
        if health.status_code == 200:
            health_data = health.json()
            print("✓ Server is healthy")
            print(f"  GPU: {health_data.get('gpu_info', {}).get('name', 'Unknown')}")
            print(f"  Video available: {health_data.get('video_available', False)}")
            print(f"  Quality mode: {health_data.get('quality_mode', 'unknown')}")
        else:
            print("⚠️  Server health check failed")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure the server is running: python avatar_server_final.py")
        return False
    
    # Generate avatar
    print(f"\n📨 Sending request...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/generate",
            json={
                "text": text,
                "quality": quality,
                "voice_id": "default"
            },
            timeout=300  # 5 minutes max
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS! ({elapsed:.1f}s)")
            print(f"   Status: {data.get('status')}")
            print(f"   Video URL: {data.get('video_url', 'None')}")
            print(f"   Audio URL: {data.get('audio_url', 'None')}")
            print(f"   Duration: {data.get('duration', 0):.1f}s")
            print(f"   Generation time: {data.get('generation_time', 0):.1f}s")
            print(f"   Message: {data.get('message', '')}")
            
            if data.get('video_url'):
                print(f"\n🎬 Video ready! Open in browser:")
                print(f"   {data['video_url']}")
            
            return True
        else:
            print(f"\n❌ FAILED ({elapsed:.1f}s)")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.Timeout:
        print(f"\n⏱️  Request timed out after {elapsed:.1f}s")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("🎭 Luna Avatar API Tester")
    print("=" * 70)
    print("\nMake sure the server is running:")
    print("  python avatar_server_final.py")
    print("\nOr use:")
    print("  .\\START_AVATAR_SERVER.ps1")
    print()
    
    # Test with a simple message
    test_text = "Hello! I am Luna, your intelligent AI assistant from One Development. How can I help you today?"
    
    print("Testing with sample text...")
    success = test_avatar(test_text, quality='fast')
    
    if success:
        print("\n" + "=" * 70)
        print("✅ Test completed successfully!")
        print("=" * 70)
        print("\nYou can now talk to Luna by modifying the 'test_text' variable")
        print("or by calling test_avatar() with your own text.")
    else:
        print("\n" + "=" * 70)
        print("❌ Test failed - check server logs")
        print("=" * 70)

