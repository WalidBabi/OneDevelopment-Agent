# 🔧 Fix Avatar Service to Use OpenAI TTS Audio

## Issue
The avatar service is using gTTS instead of OpenAI TTS because it's not handling the `audio_url` parameter sent by the backend.

## Problem Location
The avatar service (`avatar_server_sadtalker.py` on your laptop) receives `audio_url` from the backend but doesn't use it. Instead, it generates audio using its own TTS (gTTS).

## Solution

### On Your Local Laptop

Edit `avatar_service/avatar_server_sadtalker.py` and modify the `generate_avatar` function:

**Current code (around line 124-150):**
```python
@app.post("/generate", response_model=AvatarResponse)
async def generate_avatar(request: AvatarRequest, background_tasks: BackgroundTasks):
    """Generate avatar video using SadTalker"""
    
    if not AVATAR_IMAGE.exists():
        raise HTTPException(status_code=500, detail="luna_base.png not found")
    
    if not sadtalker_generator:
        raise HTTPException(status_code=503, detail="SadTalker not initialized")
    
    video_id = str(uuid.uuid4())
    
    try:
        logger.info(f"📨 New request: {request.text[:50]}...")
        logger.info(f"   Quality: {request.quality}")
        logger.info(f"   Voice: {request.voice_id}")
        
        # Generate video using SadTalker
        result = sadtalker_generator.generate(
            text=request.text,
            source_image=str(AVATAR_IMAGE),
            video_id=video_id,
            quality=request.quality,
            output_dir=str(OUTPUT_DIR),
            audio_dir=str(AUDIO_DIR),
            temp_dir=str(TEMP_DIR)
        )
```

**Replace with:**
```python
@app.post("/generate", response_model=AvatarResponse)
async def generate_avatar(request: AvatarRequest, background_tasks: BackgroundTasks):
    """Generate avatar video using SadTalker"""
    
    if not AVATAR_IMAGE.exists():
        raise HTTPException(status_code=500, detail="luna_base.png not found")
    
    if not sadtalker_generator:
        raise HTTPException(status_code=503, detail="SadTalker not initialized")
    
    video_id = str(uuid.uuid4())
    audio_path = AUDIO_DIR / f"{video_id}.mp3"
    
    try:
        logger.info(f"📨 New request: {request.text[:50]}...")
        logger.info(f"   Quality: {request.quality}")
        logger.info(f"   Voice: {request.voice_id}")
        logger.info(f"   Audio URL: {request.audio_url}")
        
        # Step 1: Get audio (download from backend if provided, otherwise generate)
        if request.audio_url:
            # Download OpenAI TTS audio from backend
            logger.info(f"📥 Downloading OpenAI TTS audio from: {request.audio_url}")
            import requests
            try:
                response = requests.get(request.audio_url, timeout=30)
                response.raise_for_status()
                audio_path.write_bytes(response.content)
                logger.info(f"✅ Downloaded OpenAI TTS audio: {audio_path}")
                
                # Get duration from audio file
                try:
                    from mutagen.mp3 import MP3
                    audio = MP3(str(audio_path))
                    duration = audio.info.length
                except:
                    # Estimate: ~150 words per minute
                    words = len(request.text.split())
                    duration = (words / 150) * 60
            except Exception as e:
                logger.warning(f"Failed to download audio_url, falling back to TTS: {e}")
                # Fall through to generate audio with TTS
                request.audio_url = None
        
        # Step 2: Generate video using SadTalker
        # Check if SadTalkerGenerator supports audio_path parameter
        # If it does, pass audio_path instead of text
        if request.audio_url and audio_path.exists():
            # Use downloaded audio
            logger.info(f"🎬 Generating video with downloaded audio: {audio_path}")
            result = sadtalker_generator.generate(
                audio_path=str(audio_path),  # Pass audio path if generator supports it
                text=request.text,  # Keep text as fallback
                source_image=str(AVATAR_IMAGE),
                video_id=video_id,
                quality=request.quality,
                output_dir=str(OUTPUT_DIR),
                audio_dir=str(AUDIO_DIR),
                temp_dir=str(TEMP_DIR)
            )
        else:
            # Generate audio with TTS (fallback)
            logger.info(f"🎤 Generating audio with TTS (no audio_url provided)")
            result = sadtalker_generator.generate(
                text=request.text,
                source_image=str(AVATAR_IMAGE),
                video_id=video_id,
                quality=request.quality,
                output_dir=str(OUTPUT_DIR),
                audio_dir=str(AUDIO_DIR),
                temp_dir=str(TEMP_DIR)
            )
```

**Note:** You may need to check the `SadTalkerGenerator.generate()` method signature to see if it accepts `audio_path`. If not, you might need to modify the generator class or use a different approach.

### Alternative: Check SadTalkerGenerator Class

If `SadTalkerGenerator.generate()` doesn't support `audio_path`, you may need to:

1. Check `avatar_service/sadtalker_generator.py` to see the method signature
2. Modify it to accept `audio_path` parameter
3. Or modify the generation logic to use the downloaded audio file directly

## Testing

After making the change:

1. Restart your avatar service on your laptop
2. Test from the frontend - it should now use OpenAI TTS voice
3. Check the logs to confirm it's downloading and using the audio_url

## Expected Behavior

- Backend generates OpenAI TTS audio
- Backend sends `audio_url` to avatar service
- Avatar service downloads the audio file
- Avatar service uses the downloaded audio for video generation
- Video plays with OpenAI voice instead of gTTS








