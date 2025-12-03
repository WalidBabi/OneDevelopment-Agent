"""
Test SadTalker generation directly
"""
from sadtalker_generator import SadTalkerGenerator
from pathlib import Path

print("Testing SadTalker video generation...")
print()

# Initialize (use fast preset for maximum speed in tests)
gen = SadTalkerGenerator(quality='fast')
print("✓ Generator initialized")
print()

# Test files
audio = "generated_audio/94becd13-7848-4650-b245-19f481b74c4c.mp3"
image = "luna_base.png"
output = "test_video_output.mp4"

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

print("Generating video...")
print()

success, video_path, duration = gen.generate_video(
    audio_path=audio,
    image_path=image,
    output_dir="test_output_dir"
)

print()
if success:
    print(f"✓ SUCCESS!")
    print(f"  Video: {video_path}")
    print(f"  Time: {duration:.1f}s")
else:
    print(f"✗ FAILED")
    print(f"  Check logs above for errors")

