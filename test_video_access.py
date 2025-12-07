#!/usr/bin/env python3
"""
Test script to check if videos are accessible through ngrok
"""
import requests
import sys

NGROK_URL = "https://5d812f2e82fa.ngrok-free.app"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{NGROK_URL}/health", timeout=5)
        print(f"✅ Health Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_video(video_id):
    """Test if a video is accessible"""
    print(f"\nTesting video: {video_id}")
    url = f"{NGROK_URL}/videos/{video_id}"
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10, stream=True)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            content_length = response.headers.get('content-length', 'unknown')
            print(f"✅ Video accessible! Size: {content_length} bytes")
            
            # Download first 1KB to verify it's actually a video
            chunk = next(response.iter_content(chunk_size=1024))
            if chunk[:4] == b'ftyp' or chunk[:8] == b'\x00\x00\x00\x18ftyp':
                print("✅ Confirmed: This is a valid MP4 video!")
            else:
                print(f"⚠️  Warning: Doesn't look like MP4. First bytes: {chunk[:20]}")
            
            return True
        else:
            print(f"❌ Video not accessible: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing video: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Avatar Service Video Access Test")
    print("="*60)
    
    if not test_health():
        print("\n❌ Avatar service not reachable. Check if:")
        print("   1. Avatar service is running on Windows")
        print("   2. ngrok tunnel is active")
        sys.exit(1)
    
    print("\n" + "="*60)
    
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
        test_video(video_id)
    else:
        print("\nUsage: python test_video_access.py <video_id>")
        print("Example: python test_video_access.py 34c6ed16-cb6e-4d6b-97b1-6019b5a8bb7d.mp4")
        print("\nOr generate a new video by speaking to Luna at:")
        print("http://13.62.188.127:3000/")








