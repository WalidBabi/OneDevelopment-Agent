# Video Not Displaying - Troubleshooting Guide

## Current Status ✅

**What's Working:**
- ✅ Speech recognition
- ✅ Auto-transcription
- ✅ TTS voice responses (shimmer)  
- ✅ Avatar service accessible through ngrok
- ✅ Django backend can reach avatar service
- ✅ Video generation completes on Windows

**What's NOT Working:**
- ❌ Videos not accessible after generation

## Problem Identified

Videos are being generated on your Windows laptop successfully, but when the AWS backend tries to fetch them through ngrok, the avatar service says "Video not found".

###Possible Causes:

1. **Videos are being deleted immediately after generation**
2. **File naming mismatch** (UUID vs UUID.mp4)
3. **Videos saved in wrong directory**
4. **Permissions issue on Windows**

## Testing Steps

### Step 1: Test the Website Now

1. Go to **http://13.62.188.127:3000/**
2. Click allow for microphone
3. Say: "Hi Luna, tell me about yourself"
4. Watch the progress bar - video should start generating

### Step 2: Check Your Windows Terminal

In the PowerShell window running `avatar_server.py`, you should see:

```
INFO:__main__:📨 New request: ...
INFO:__main__:🎤 Generating audio...
INFO:__main__:🎬 Generating fast quality video...
INFO:__main__:✓ Video ready: SOME-UUID-HERE.mp4
```

**Copy that UUID!** (e.g., `a1b2c3d4-1234-5678-abcd-123456789abc`)

### Step 3: Test Video Access from AWS

On AWS server, run:

```bash
python3 /home/ec2-user/OneDevelopment-Agent/test_video_access.py "YOUR-UUID-HERE.mp4"
```

This will tell us if the video is accessible through ngrok.

### Step 4: Check Windows File System

On your Windows PC, check these folders:

```powershell
# In PowerShell, navigate to your avatar service folder
cd C:\Users\Walid\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service

# List generated videos
dir generated_videos\

# List temp audio files  
dir generated_audio\

# List temp SadTalker files
dir temp_sadtalker\
```

**Do you see .mp4 files?** Note their names.

## Quick Fixes to Try

### Fix 1: Check Avatar Server OUTPUT_DIR

Which avatar_server file are you running? Check the terminal where you started it. Then check that file's configuration.

If using `avatar_server.py`, check line ~20-30 for:

```python
OUTPUT_DIR = Path(__file__).parent / "generated_videos"
```

### Fix 2: Ensure Videos Persist

Some avatar servers might auto-delete videos. Check for any cleanup logic or TTL settings.

### Fix 3: Test Direct File Access on Windows

On Windows, try accessing the video directly:

```powershell
# If you have Python on Windows
python -m http.server 9000

# Then access: http://localhost:9000/generated_videos/
```

## Expected Behavior (Once Fixed)

1. You speak → Transcribed
2. Message sent → Luna processes
3. Video generation starts (you see progress bar)
4. Video completes on Windows
5. **AWS backend fetches video through ngrok**
6. **Video displays on website**
7. Audio plays from video
8. Listening restarts automatically

## Current ngrok URL

```
https://5d812f2e82fa.ngrok-free.app
```

**Note:** This changes every time you restart ngrok!

## If Videos Still Don't Work

Try this alternative: **Mount a shared network drive** or use **file sync** (like Dropbox, Google Drive) to make the generated_videos folder accessible from both Windows and AWS.

Or run everything locally on Windows (recommended for testing):
- Backend on Windows: `http://localhost:8000`
- Frontend on Windows: `http://localhost:3000`
- Avatar service on Windows: `http://localhost:8000` (same port as backend, proxied)

## Need More Help?

Run these diagnostics:

```bash
# On AWS
curl -s https://5d812f2e82fa.ngrok-free.app/health | python3 -m json.tool

# Check what videos exist (if avatar service has a list endpoint)
curl -s https://5d812f2e82fa.ngrok-free.app/videos/

# Test Django backend
curl http://13.62.188.127:8000/api/avatar/health/ | python3 -m json.tool
```

Share the output and we can debug further!








