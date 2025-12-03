"""
Real-world test with long text about One Development projects
"""
import requests
import time

TEXT = """Certainly! Here's an introduction to One Development's projects, showcasing their active and upcoming developments:

Current Active Projects

Laguna Residence

Location: Dubai
Type: Luxury residential development
Status: Active
Features: Premium apartments equipped with modern amenities.

Do Dubai Islands

Location: Dubai Islands
Type: Hospitality-led development
Status: Active
Features: Beachfront living with world-class facilities.

Do New Cairo

Location: New Cairo, Egypt
Type: Mixed-use development
Status: Active
Features: Expanding One Development's presence in Egypt.

Upcoming Projects (Coming Soon)

Al Marjan Islands
Location: Al Marjan Islands, RAK
Status: Coming Soon

Al Reem Islands
Location: Abu Dhabi
Status: Coming Soon

Do Riyadh
Location: Riyadh, Saudi Arabia
Status: Coming Soon
Features: Expansion into the KSA market.

Do Athens
Location: Athens, Greece
Status: Coming Soon
Features: European expansion.

W55 Waterway
Location: Egypt
Status: Coming Soon

Company Overview

One Development is a premier real estate developer based in Dubai, specializing in luxurious residential and commercial properties. They are known for their commitment to quality construction, modern design, and sustainable practices, ensuring exceptional living spaces.

Key Features Across Projects

Premium Quality Construction: High standards in materials and finishes.
Modern Architectural Design: Innovative and appealing aesthetics.
Comprehensive Amenities: Including pools, gyms, parking, and security.
Flexible Payment Plans: Tailored options for buyers.
Freehold Ownership: Available for all nationalities.

If you have any specific questions or need further assistance, feel free to ask!"""

print("\n" + "="*70)
print("🧪 REAL-WORLD TEST: One Development Projects")
print("="*70)
print(f"\nText length: {len(TEXT)} characters")
print(f"Estimated audio: ~{len(TEXT) / 15:.0f} seconds")
print("\nStarting generation...")
print("="*70)

start_time = time.time()

try:
    response = requests.post(
        "http://localhost:8000/generate",
        json={
            "text": TEXT,
            "quality": "fast",
            "voice_id": "en-US-AvaMultilingualNeural"  # Shimmer-like voice
        },
        timeout=300  # 5 minutes max
    )
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*70)
    print("✅ RESULTS")
    print("="*70)
    
    if response.status_code == 200:
        data = response.json()
        gen_time = data.get('generation_time', 0) or 0
        audio_duration = data.get('audio_duration', 0) or 0
        
        print(f"\n✓ Generation successful!")
        print(f"\n📊 TIMING:")
        print(f"  • Audio duration: {audio_duration:.1f}s")
        print(f"  • Video generation: {gen_time:.1f}s")
        print(f"  • Total time: {elapsed:.1f}s")
        print(f"  • Speed ratio: {gen_time/audio_duration:.1f}x realtime" if audio_duration > 0 else "")
        
        print(f"\n📁 FILES:")
        print(f"  • Video: {data.get('video_url', 'N/A')}")
        print(f"  • Audio: {data.get('audio_url', 'N/A')}")
        
        print(f"\n⚡ PERFORMANCE:")
        if gen_time < 30:
            print(f"  🎉 EXCELLENT! Under 30 seconds!")
        elif gen_time < 60:
            print(f"  ✅ GOOD! Under 1 minute")
        elif gen_time < 120:
            print(f"  ⚠️  OK. Under 2 minutes but could be faster")
        else:
            print(f"  ❌ SLOW. Over 2 minutes - needs optimization")
        
        print()
    else:
        print(f"\n❌ Request failed: {response.status_code}")
        print(response.text)

except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n❌ ERROR after {elapsed:.1f}s:")
    print(f"  {type(e).__name__}: {e}")

print()

