# 🎬 SadTalker Installation Guide for Luna Avatar

## Overview

SadTalker creates realistic talking head videos from:
- ✅ A single image (luna_base.png)
- ✅ Audio file (from TTS)
- ✅ GPU acceleration (your RTX 4050)

**Result:** Professional talking head videos with natural lip-sync!

---

## 📋 Requirements

- ✅ Windows 11 (you have this)
- ✅ RTX 4050 GPU (you have this)
- ✅ CUDA installed (you have this)
- ✅ Python 3.8-3.10
- ✅ ~10GB free disk space (for models)

---

## 🚀 Installation Steps

### Step 1: Clone SadTalker

```bash
cd %USERPROFILE%\Downloads
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker
```

### Step 2: Create Virtual Environment

```powershell
# Create new venv for SadTalker
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

### Step 3: Install PyTorch with CUDA

```bash
# For CUDA 11.8 (adjust if you have different version)
pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118

# Verify PyTorch can see your GPU
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
```

Expected output:
```
CUDA available: True
GPU: NVIDIA GeForce RTX 4050 Laptop GPU
```

### Step 4: Install SadTalker Dependencies

```bash
pip install -r requirements.txt
```

**If you get errors**, install these individually:

```bash
pip install numpy==1.23.5
pip install opencv-python==4.8.1.78
pip install scikit-image==0.21.0
pip install imageio==2.31.1
pip install imageio-ffmpeg==0.4.8
pip install librosa==0.10.0
pip install pydub==0.25.1
pip install face-alignment==1.3.5
pip install gradio==3.41.2
pip install yacs==0.1.8
pip install pyyaml
pip install kornia==0.7.0
pip install safetensors==0.3.1
pip install basicsr==1.4.2
pip install resampy==0.4.2
```

### Step 5: Download Pre-trained Models

**Windows PowerShell:**

```powershell
# Download checkpoints (this will download ~3GB)
# Note: The bash script won't work on Windows, so we'll download manually

# Create directories
New-Item -ItemType Directory -Force -Path checkpoints

# Download models using Python
python -c "
import gdown
import os

# Download main checkpoints
print('Downloading SadTalker checkpoints...')

# Checkpoint URLs (these are the official model links)
files = {
    'checkpoints/SadTalker_V0.0.2_256.safetensors': 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors',
    'checkpoints/SadTalker_V0.0.2_512.safetensors': 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors',
    'gfpgan/weights/alignment_WFLW_4HG.pth': 'https://github.com/xinntao/facexlib/releases/download/v0.1.0/alignment_WFLW_4HG.pth',
    'gfpgan/weights/detection_Resnet50_Final.pth': 'https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth',
    'gfpgan/weights/parsing_parsenet.pth': 'https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth',
}

import urllib.request
for filepath, url in files.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not os.path.exists(filepath):
        print(f'Downloading {filepath}...')
        urllib.request.urlretrieve(url, filepath)
        print(f'✓ Downloaded {filepath}')
    else:
        print(f'✓ {filepath} already exists')

print('✓ All checkpoints downloaded!')
"
```

**Alternative: Manual Download**

If the script fails, download manually:

1. Go to: https://github.com/OpenTalker/SadTalker/releases
2. Download:
   - `SadTalker_V0.0.2_256.safetensors` → `checkpoints/`
   - `SadTalker_V0.0.2_512.safetensors` → `checkpoints/`
3. Go to: https://github.com/xinntao/facexlib/releases
4. Download GFPGAN weights to `gfpgan/weights/`

### Step 6: Test SadTalker

```bash
# Copy your Luna base image
copy %USERPROFILE%\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service\luna_base.png examples\source_image\luna_base.png

# Test with sample audio (create a test audio first)
# We'll use edge-tts to generate test audio
pip install edge-tts

# Generate test audio
python -c "
import asyncio
import edge_tts

async def generate():
    text = 'Hello! I am Luna, your intelligent AI assistant from One Development. How can I help you today?'
    communicate = edge_tts.Communicate(text, 'en-US-AriaNeural')
    await communicate.save('examples/driven_audio/test_luna.mp3')
    print('✓ Test audio generated')

asyncio.run(generate())
"

# Now run SadTalker!
python inference.py \
  --driven_audio examples/driven_audio/test_luna.mp3 \
  --source_image examples/source_image/luna_base.png \
  --result_dir results \
  --still \
  --preprocess full \
  --enhancer gfpgan
```

**Expected:** Video generated in `results/` folder!

---

## 🎯 Quick Test Script

Create `test_sadtalker.py`:

```python
"""
Quick SadTalker test for Luna
"""
import os
import subprocess
import asyncio
import sys

# Add SadTalker to path
sys.path.insert(0, r'%USERPROFILE%\Downloads\SadTalker')

async def generate_test_audio():
    """Generate test audio with edge-tts"""
    try:
        import edge_tts
        
        text = "Hello! I'm Luna, your AI assistant. This is a test of the SadTalker system."
        output = "test_luna_audio.mp3"
        
        communicate = edge_tts.Communicate(text, 'en-US-AriaNeural')
        await communicate.save(output)
        
        print(f"✓ Test audio generated: {output}")
        return output
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

def test_sadtalker(audio_path, image_path="luna_base.png"):
    """Test SadTalker generation"""
    print("=" * 70)
    print("🎬 TESTING SADTALKER")
    print("=" * 70)
    print()
    
    if not os.path.exists(audio_path):
        print(f"❌ Audio file not found: {audio_path}")
        return False
    
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return False
    
    print(f"✓ Audio: {audio_path}")
    print(f"✓ Image: {image_path}")
    print()
    print("Generating video (this may take 30-60 seconds)...")
    print()
    
    cmd = [
        "python",
        "inference.py",
        "--driven_audio", audio_path,
        "--source_image", image_path,
        "--result_dir", "test_results",
        "--still",
        "--preprocess", "full",
        "--enhancer", "gfpgan"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            print("✓ SadTalker completed successfully!")
            print()
            print("Video should be in: test_results/")
            print("Check for .mp4 files in that directory")
            return True
        else:
            print(f"❌ SadTalker failed")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ SadTalker timed out (>3 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    # Step 1: Generate audio
    audio_path = await generate_test_audio()
    
    if not audio_path:
        print("Failed to generate test audio")
        return
    
    # Step 2: Test SadTalker
    success = test_sadtalker(audio_path)
    
    if success:
        print()
        print("=" * 70)
        print("✅ SADTALKER TEST SUCCESSFUL!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Check the generated video in test_results/")
        print("  2. Integrate with avatar server")
        print("  3. Test from frontend")
    else:
        print()
        print("=" * 70)
        print("❌ SADTALKER TEST FAILED")
        print("=" * 70)
        print()
        print("Troubleshooting:")
        print("  1. Check that all checkpoints are downloaded")
        print("  2. Verify GPU is accessible (nvidia-smi)")
        print("  3. Check SadTalker logs above for errors")

if __name__ == "__main__":
    asyncio.run(main())
```

Run the test:

```bash
cd %USERPROFILE%\Downloads\SadTalker
python test_sadtalker.py
```

---

## 🔧 Troubleshooting

### "No module named 'face_alignment'"
```bash
pip install face-alignment==1.3.5
```

### "CUDA out of memory"
- Use 256px model instead of 512px
- Close other GPU applications
- Restart Python

### "FFmpeg not found"
```bash
# FFmpeg should already be in your PATH from earlier setup
# Test it:
ffmpeg -version

# If not found, add to PATH (you already did this):
$env:Path += ";%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
```

### Checkpoints not downloading
- Download manually from: https://github.com/OpenTalker/SadTalker/releases/tag/v0.0.2-rc
- Place in `checkpoints/` folder

### Slow generation
- **Normal:** First run is ~60 seconds (model loading)
- **After first:** ~20-30 seconds per video
- **With GPU:** Should be fast
- **CPU only:** Very slow (not recommended)

---

## 📊 Expected Performance

| Setting | Time | Quality | GPU Memory |
|---------|------|---------|------------|
| 256px, no enhancer | 20s | Good | 2GB |
| 256px, with gfpgan | 30s | Better | 3GB |
| 512px, no enhancer | 30s | Better | 4GB |
| 512px, with gfpgan | 45s | Best | 6GB |

**Recommendation for RTX 4050:** Use 256px with gfpgan for best speed/quality balance

---

## 🎯 Next: Integrate with Avatar Server

Once SadTalker is working, we'll integrate it with your avatar server!

See: `SADTALKER_INTEGRATION.md` (coming next)

---

## 📚 Resources

- [SadTalker GitHub](https://github.com/OpenTalker/SadTalker)
- [SadTalker Paper](https://arxiv.org/abs/2211.12194)
- [Online Demo](https://huggingface.co/spaces/vinthony/SadTalker)

---

## ✅ Checklist

- [ ] Clone SadTalker repository
- [ ] Create virtual environment
- [ ] Install PyTorch with CUDA
- [ ] Install dependencies
- [ ] Download checkpoints
- [ ] Run test script
- [ ] Verify video generation works
- [ ] Ready for integration!

---

**Ready to install? Let's do it! 🚀**

