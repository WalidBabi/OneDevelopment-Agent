# Install LivePortrait for Photorealistic Avatars

## Step-by-Step Installation

### 1. Download LivePortrait

```powershell
cd %USERPROFILE%\Downloads
git clone https://github.com/KwaiVGI/LivePortrait.git
cd LivePortrait
```

### 2. Install LivePortrait Dependencies

```powershell
# Activate your avatar service venv
cd %USERPROFILE%\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service
.\venv\Scripts\activate

# Install LivePortrait requirements
pip install -r %USERPROFILE%\Downloads\LivePortrait\requirements.txt

# Install additional packages
pip install gTTS opencv-python
```

### 3. Download Model Weights

LivePortrait needs pretrained weights. Run this:

```powershell
cd %USERPROFILE%\Downloads\LivePortrait

# Download weights (this will take a few minutes)
python scripts/download_models.py
```

If that doesn't work, manually download from:
https://huggingface.co/KwaiVGI/LivePortrait/tree/main

Put the files in: `%USERPROFILE%\Downloads\LivePortrait\pretrained_weights\`

### 4. Get a Photorealistic Luna Image

You need a high-quality female portrait photo:

**Option A: Generate with AI**
- Use Midjourney, DALL-E, or Stable Diffusion
- Prompt: "professional headshot photo of a beautiful female AI assistant, front facing, neutral expression, soft lighting, 4k, photorealistic"
- Save as: `%USERPROFILE%\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service\luna_base.png`

**Option B: Use a stock photo**
- Get from Unsplash/Pexels (free)
- Make sure it's:
  - Square (512x512 or 1024x1024)
  - Front-facing
  - Good lighting
  - Neutral expression

**Option C: I can help you generate one**
- Tell me and I'll give you a prompt for Midjourney/DALL-E

### 5. Test LivePortrait

```powershell
cd %USERPROFILE%\Downloads\LivePortrait

# Test with example
python inference.py --source assets/examples/source/s6.jpg --driving assets/examples/driving/d0.mp4
```

This should generate a test video in `animations/`.

### 6. Update Avatar Service

Copy the new server file:

```powershell
cd %USERPROFILE%\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service

# Backup old file
copy avatar_server.py avatar_server_backup.py

# You'll need to download the new file from AWS or I can give it to you
```

### 7. Restart Avatar Service

```powershell
# Stop the current server (Ctrl+C in that window)

# Start with new code
python avatar_server_liveportrait.py
```

### 8. Test End-to-End

- Go to Luna in browser
- Click Avatar Only mode
- Speak to Luna
- Should now get PHOTOREALISTIC video!

## Troubleshooting

### "Module not found" errors
```powershell
pip install <missing-module>
```

### Out of memory
- Reduce image size to 512x512
- Close other applications
- Restart your laptop

### Slow generation
- First generation is slow (model loading)
- Subsequent ones should be 3-5 seconds
- Check GPU usage: `nvidia-smi`

## Alternative: Use SadTalker Instead

If LivePortrait doesn't work, try SadTalker:

```powershell
cd %USERPROFILE%\Downloads
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker
pip install -r requirements.txt
```

Then I'll give you the integration code for SadTalker.

## Next Steps

1. Install LivePortrait
2. Get photorealistic Luna image
3. Test LivePortrait works
4. Update avatar service
5. Test with Luna!





