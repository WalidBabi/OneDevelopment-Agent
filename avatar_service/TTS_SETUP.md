# 🎤 High-Quality TTS Setup for Luna

This guide helps you set up the best open-source TTS voices for Luna.

## Quick Start (Recommended)

Install edge-tts for Microsoft's high-quality neural voices:

```bash
cd avatar_service
.\venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Linux/Mac

pip install edge-tts==6.1.10
```

**That's it!** You now have access to 400+ Microsoft neural voices.

## Testing TTS

```python
import asyncio
import edge_tts

async def test():
    text = "Hello, I'm Luna, your AI assistant."
    output_file = "test_luna.mp3"
    
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save(output_file)
    print(f"✓ Audio saved to {output_file}")

asyncio.run(test())
```

## Available Voices for Luna

### 🌟 Recommended Voices

| Voice ID | Description | Best For |
|----------|-------------|----------|
| `en-US-AriaNeural` | Young, friendly, energetic | Default Luna personality |
| `en-US-JennyNeural` | Professional, warm, clear | Business interactions |
| `en-GB-SoniaNeural` | British, sophisticated | Elegant, refined |
| `en-US-MichelleNeural` | Casual, conversational | Friendly chat |
| `en-US-SaraNeural` | Soft, caring, empathetic | Support, guidance |

### Test Different Voices

```bash
# Test Aria (default)
edge-tts --voice "en-US-AriaNeural" --text "Hello, I'm Luna" --write-media test_aria.mp3

# Test Jenny (professional)
edge-tts --voice "en-US-JennyNeural" --text "Hello, I'm Luna" --write-media test_jenny.mp3

# Test Sonia (British)
edge-tts --voice "en-GB-SoniaNeural" --text "Hello, I'm Luna" --write-media test_sonia.mp3
```

### List ALL Available Voices

```bash
edge-tts --list-voices
```

## Advanced Options

### Option 1: Piper TTS (Fast, Offline)

Best for: Offline use, ultra-low latency

```bash
pip install piper-tts

# Download a model
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-en-us-lessac-medium.onnx
```

### Option 2: Coqui TTS (Voice Cloning)

Best for: Creating a custom Luna voice from audio samples

```bash
pip install TTS

# Test it
tts --text "Hello, I'm Luna" --model_name "tts_models/en/ljspeech/tacotron2-DDC" --out_path luna_test.wav
```

**Voice Cloning:**
If you have 5-10 minutes of clean audio samples of your desired Luna voice:

```python
from TTS.api import TTS

# Clone a voice
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
tts.tts_to_file(
    text="Hello, I'm Luna",
    file_path="output.wav",
    speaker_wav="path/to/luna_voice_sample.wav",  # Your reference audio
    language="en"
)
```

### Option 3: StyleTTS2 (Highest Quality)

Best for: Maximum naturalness (but slower)

```bash
git clone https://github.com/yl4579/StyleTTS2.git
cd StyleTTS2
pip install -r requirements.txt
# Download models as per their README
```

## Using the TTS Manager

The avatar server includes a TTS manager that automatically uses the best available engine:

```python
from tts_manager import get_tts_manager

tts = get_tts_manager()

# Generate speech with automatic fallback
await tts.generate_speech(
    text="Hello, I'm Luna",
    output_path="output.mp3",
    voice="default"  # or "professional", "british", "casual"
)
```

## Comparison

| Engine | Speed | Quality | GPU Required | Offline | Voice Options |
|--------|-------|---------|--------------|---------|---------------|
| **edge-tts** | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ❌ | ❌ | 400+ |
| **Piper** | ⚡⚡⚡ | ⭐⭐⭐⭐ | ❌ | ✅ | 50+ |
| **Coqui XTTS** | ⚡⚡ | ⭐⭐⭐⭐ | ✅ | ✅ | Clone any |
| **StyleTTS2** | ⚡ | ⭐⭐⭐⭐⭐ | ✅ | ✅ | Clone any |
| **gTTS** | ⚡⚡ | ⭐⭐⭐ | ❌ | ❌ | 1 |

## Update Avatar Server

To use the new TTS system:

```bash
cd avatar_service

# Install updated requirements
pip install -r requirements.txt

# Use the improved server
python avatar_server_improved.py
```

The server will automatically detect and use the best available TTS engine.

## Troubleshooting

### edge-tts not working

```bash
# Update
pip install --upgrade edge-tts

# Test directly
edge-tts --text "test" --voice "en-US-AriaNeural" --write-media test.mp3
```

### "No module named 'edge_tts'"

```bash
# Make sure you're in the virtual environment
.\venv\Scripts\activate  # Windows
pip install edge-tts
```

### Want even more voices?

Check out:
- [edge-tts voice list](https://github.com/rany2/edge-tts#voice-list)
- [Coqui TTS models](https://github.com/coqui-ai/TTS#released-models)
- [Piper voices](https://github.com/rhasspy/piper/blob/master/VOICES.md)

## Next Steps

1. ✅ Install edge-tts (done!)
2. 🎤 Test different voices
3. 🎬 Install SadTalker for full video generation (see `INSTALL_SADTALKER.md`)
4. 🚀 Deploy to production

## Resources

- [edge-tts GitHub](https://github.com/rany2/edge-tts)
- [Piper TTS](https://github.com/rhasspy/piper)
- [Coqui TTS](https://github.com/coqui-ai/TTS)
- [StyleTTS2](https://github.com/yl4579/StyleTTS2)

