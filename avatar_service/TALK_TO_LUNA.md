# 🎭 Talk to Luna - Quick Start Guide

## 🚀 Server is Running!

The Luna Avatar server should now be running on: **http://localhost:8000**

## 🎤 How to Talk to Luna

### Method 1: Using the Test Script (Easiest)

```powershell
cd %USERPROFILE%\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service
python test_avatar_api.py
```

This will send a test message to Luna and generate a video!

### Method 2: Using curl (Command Line)

```powershell
curl -X POST http://localhost:8000/generate `
  -H "Content-Type: application/json" `
  -d '{\"text\": \"Hello! I am Luna, your AI assistant.\", \"quality\": \"fast\"}'
```

### Method 3: Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/generate",
    json={
        "text": "Hello! I am Luna, your AI assistant. How can I help you?",
        "quality": "fast"
    }
)

data = response.json()
print(f"Video URL: {data['video_url']}")
print(f"Audio URL: {data['audio_url']}")
```

### Method 4: Using Browser (GET requests only)

Open in browser:
- **Server info:** http://localhost:8000/
- **Health check:** http://localhost:8000/health
- **Video:** http://localhost:8000/videos/{video_id}.mp4
- **Audio:** http://localhost:8000/audio/{audio_id}.mp3

## 📊 API Endpoints

### POST /generate
Generate a talking avatar video from text.

**Request:**
```json
{
  "text": "Your message here",
  "quality": "fast",  // fast | standard | high | ultra
  "voice_id": "default"
}
```

**Response:**
```json
{
  "video_url": "http://localhost:8000/videos/{id}.mp4",
  "audio_url": "http://localhost:8000/audio/{id}.mp3",
  "video_id": "...",
  "duration": 5.2,
  "status": "video_ready",
  "quality": "fast",
  "generation_time": 168.4,
  "message": "High-quality video generated (fast mode)"
}
```

### GET /health
Check server status and GPU availability.

### GET /videos/{filename}
Download a generated video.

### GET /audio/{filename}
Download generated audio.

## ⚡ Quality Modes

- **fast**: 256px, no enhancement (~10-20s expected)
- **standard**: 256px + GFPGAN (~20-30s expected)
- **high**: 512px + GFPGAN (~30-40s expected)
- **ultra**: 512px + GFPGAN + RealESRGAN (~60s expected)

## 🎯 Current Status

- ✅ **Server:** Running
- ✅ **TTS:** Microsoft Neural Voices (edge-tts)
- ✅ **Progress Bar:** Shows real-time steps
- ⚠️ **Video Generation:** SadTalker (168s currently, can be optimized to 30-40s)
- ⏳ **Wav2Lip:** Ready (needs model download for 8-12s)

## 🐛 Troubleshooting

### Server not responding?
1. Check if it's running: `curl http://localhost:8000/health`
2. Restart: `python avatar_server_final.py`

### Video generation slow?
- Current: ~168 seconds (CPU mode)
- With GPU: ~30-40 seconds (need Windows Graphics Settings)
- With Wav2Lip: ~8-12 seconds (need model download)

### No video generated?
- Check server logs for errors
- Verify `luna_base.png` exists
- Check SadTalker is installed correctly

## 🎉 Enjoy Talking to Luna!

The server is ready - start chatting! 🚀

