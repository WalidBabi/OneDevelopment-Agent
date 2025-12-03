"""
Quick test to verify GPU is being used by SadTalker
"""
import requests
import time

print("\n" + "="*70)
print("🧪 TESTING GPU FIX")
print("="*70)
print("\nSending test request to avatar service...")
print("This should take ~10-30 seconds with GPU (not 20 minutes!)")
print()

start_time = time.time()

response = requests.post(
    "http://localhost:8000/generate",
    json={
        "text": "Testing GPU acceleration.",
        "quality": "fast"
    },
    timeout=120  # 2 minutes max
)

elapsed = time.time() - start_time

print("\n" + "="*70)
print("✅ RESULTS")
print("="*70)

if response.status_code == 200:
    data = response.json()
    gen_time = data.get('generation_time', 0) or 0
    
    print(f"\n✓ Generation successful!")
    print(f"  Time: {gen_time:.1f}s")
    print(f"  Total elapsed: {elapsed:.1f}s")
    print(f"  Video: {data.get('video_url', 'N/A')}")
    print(f"  Audio: {data.get('audio_url', 'N/A')}")
    print()
    
    if gen_time < 60:
        print("🎉 SUCCESS! GPU is working! (< 60s)")
    elif gen_time < 300:
        print("⚠️  PARTIAL: Faster than before but still slow")
        print("   May need more optimization")
    else:
        print("❌ FAILED: Still using CPU (> 5 minutes)")
        print("   GPU not being utilized")
else:
    print(f"\n❌ Request failed: {response.status_code}")
    print(response.text)

print()

