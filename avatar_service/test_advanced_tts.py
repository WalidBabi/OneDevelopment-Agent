"""
Test Advanced TTS Options - Parler-TTS
Quick test of ElevenLabs-quality open-source TTS
"""

import sys

print("=" * 70)
print("🎯 ADVANCED TTS QUICK TEST - Parler-TTS")
print("=" * 70)
print()

# Check if Parler-TTS is installed
try:
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer
    import torch
    import scipy.io.wavfile
    print("✓ Parler-TTS is installed")
except ImportError as e:
    print("❌ Parler-TTS not installed")
    print()
    print("Install with:")
    print("  pip install git+https://github.com/huggingface/parler-tts.git")
    print("  pip install scipy")
    sys.exit(1)

# Check GPU
if torch.cuda.is_available():
    device = "cuda"
    print(f"✓ Using GPU: {torch.cuda.get_device_name(0)}")
else:
    device = "cpu"
    print("⚠  Using CPU (will be slower)")

print()
print("=" * 70)
print("Loading Parler-TTS model...")
print("(First time will download ~1GB model)")
print("=" * 70)
print()

try:
    # Load model (use mini for faster testing)
    model = ParlerTTSForConditionalGeneration.from_pretrained(
        "parler-tts/parler-tts-mini-v1"
    ).to(device)
    tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-v1")
    
    print("✓ Model loaded successfully")
    print()
    
    # Test different voice descriptions for Luna
    test_cases = [
        {
            "name": "Luna - Energetic",
            "description": "A young female voice, clear and energetic, speaking at a moderate pace with a friendly tone",
            "text": "Hello! I'm Luna, your intelligent AI assistant from One Development. How can I help you today?"
        },
        {
            "name": "Luna - Professional",
            "description": "A professional female voice, clear and warm, speaking confidently with a business-like tone",
            "text": "Welcome to One Development. I'm Luna, and I'm here to assist you with all your property inquiries."
        },
        {
            "name": "Luna - Casual",
            "description": "A friendly young woman's voice, casual and conversational, speaking naturally with a warm smile",
            "text": "Hey there! Luna here. Let's chat about your dream home!"
        }
    ]
    
    print("=" * 70)
    print("Generating voices...")
    print("=" * 70)
    print()
    
    for i, test in enumerate(test_cases, 1):
        print(f"{i}. {test['name']}")
        print(f"   Description: {test['description']}")
        print(f"   Text: {test['text'][:50]}...")
        
        try:
            # Tokenize
            input_ids = tokenizer(test['description'], return_tensors="pt").input_ids.to(device)
            prompt_input_ids = tokenizer(test['text'], return_tensors="pt").input_ids.to(device)
            
            # Generate
            with torch.no_grad():
                generation = model.generate(
                    input_ids=input_ids,
                    prompt_input_ids=prompt_input_ids
                )
            
            # Save
            audio_arr = generation.cpu().numpy().squeeze()
            output_file = f"voice_tests/parler_luna_{i}_{test['name'].lower().replace(' - ', '_').replace(' ', '_')}.wav"
            
            import os
            os.makedirs("voice_tests", exist_ok=True)
            
            scipy.io.wavfile.write(
                output_file,
                model.config.sampling_rate,
                audio_arr
            )
            
            print(f"   ✓ Saved: {output_file}")
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        print()
    
    print("=" * 70)
    print("✅ TEST COMPLETE!")
    print("=" * 70)
    print()
    print("Listen to the generated files in: voice_tests/")
    print()
    print("Next steps:")
    print("  1. Listen to the samples")
    print("  2. Choose your favorite voice description")
    print("  3. Integrate into avatar server")
    print()
    print("For even better quality, try:")
    print("  - parler-tts/parler-tts-large-v1 (bigger model, better quality)")
    print("  - Fish Audio (voice cloning)")
    print("  - F5-TTS (state-of-the-art)")
    print()
    print("See ADVANCED_TTS_GUIDE.md for full details!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

