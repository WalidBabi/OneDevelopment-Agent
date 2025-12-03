"""
Test Wav2Lip generation directly - FAST MODE for 10-second goal
"""
from wav2lip_generator import Wav2LipGenerator
from pathlib import Path

print("Testing Wav2Lip video generation (FAST MODE)...")
print()

# Initialize
gen = Wav2LipGenerator()
print("✓ Generator initialized")
print()

# Test files
audio = "generated_audio/94becd13-7848-4650-b245-19f481b74c4c.mp3"
image = "luna_base.png"
output = "test_wav2lip_output.mp4"

print(f"Audio: {Path(audio).exists()}")
print(f"Image: {Path(image).exists()}")
print()

if not Path(audio).exists():
    print("ERROR: Audio file doesn't exist!")
    print(f"Looking for: {Path(audio).absolute()}")
    exit(1)

if not Path(image).exists():
    print("ERROR: Image file doesn't exist!")  
    exit(1)

print("Generating video (FAST mode - targeting ~10 seconds)...")
print()

success, video_path, duration = gen.generate_video(
    audio_path=audio,
    image_path=image,
    output_path=output,
    quality='fast'  # Fast mode for 8-12 seconds
)

print()
if success:
    print(f"✓ SUCCESS!")
    print(f"  Video: {video_path}")
    print(f"  Time: {duration:.1f}s")
    if duration <= 12:
        print(f"  🎉 GOAL ACHIEVED! Under 12 seconds!")
    elif duration <= 20:
        print(f"  ✅ Good! Under 20 seconds")
    else:
        print(f"  ⚠️  Still slower than target, but working")
else:
    print(f"✗ FAILED")
    print(f"  Check logs above for errors")

