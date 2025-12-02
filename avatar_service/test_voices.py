"""
Test different TTS voices for Luna
"""

import asyncio
import edge_tts
from pathlib import Path

# Create test output directory
OUTPUT_DIR = Path("./voice_tests")
OUTPUT_DIR.mkdir(exist_ok=True)

# Test text
TEST_TEXT = "Hello! I'm Luna, your intelligent AI assistant from One Development. How can I help you today?"

# Voice options to test
VOICES = {
    "aria": {
        "id": "en-US-AriaNeural",
        "description": "Young, friendly, energetic (DEFAULT)"
    },
    "jenny": {
        "id": "en-US-JennyNeural",
        "description": "Professional, warm, clear"
    },
    "sonia": {
        "id": "en-GB-SoniaNeural",
        "description": "British, sophisticated"
    },
    "michelle": {
        "id": "en-US-MichelleNeural",
        "description": "Casual, conversational"
    },
    "sara": {
        "id": "en-US-SaraNeural",
        "description": "Soft, caring, empathetic"
    }
}


async def test_voice(name, voice_info):
    """Test a single voice"""
    print(f"\n🎤 Testing: {name}")
    print(f"   Description: {voice_info['description']}")
    print(f"   Voice ID: {voice_info['id']}")
    
    output_file = OUTPUT_DIR / f"luna_{name}.mp3"
    
    try:
        communicate = edge_tts.Communicate(TEST_TEXT, voice_info['id'])
        await communicate.save(str(output_file))
        
        print(f"   ✓ Saved to: {output_file}")
        print(f"   ▶  Play it to hear this voice!")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")


async def main():
    print("=" * 70)
    print("🔊 LUNA VOICE TESTING")
    print("=" * 70)
    print(f"\nTesting text: \"{TEST_TEXT}\"")
    print(f"\nOutput directory: {OUTPUT_DIR.absolute()}")
    print("\n" + "=" * 70)
    
    # Test all voices
    for name, voice_info in VOICES.items():
        await test_voice(name, voice_info)
    
    print("\n" + "=" * 70)
    print("✅ TESTING COMPLETE!")
    print("=" * 70)
    print(f"\nListen to the generated files in: {OUTPUT_DIR.absolute()}")
    print("\nRecommendations:")
    print("  • 'aria' - Best for default Luna personality")
    print("  • 'jenny' - Best for professional business interactions")
    print("  • 'sonia' - Best for elegant, refined conversations")
    print("\nTo use a voice, update avatar_server_improved.py or pass it in the API:")
    print("  voice_id='default' (aria), 'professional' (jenny), or 'british' (sonia)")


if __name__ == "__main__":
    asyncio.run(main())

