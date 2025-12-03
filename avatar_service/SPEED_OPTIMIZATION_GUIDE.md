# 🚀 SadTalker Speed Optimization Guide

## 🎯 Goal: Generate Videos in < 10 Seconds

Current "fast" mode: **10-20 seconds**  
Target: **< 10 seconds**

---

## ⚡ Super-Fast Mode Configuration

To achieve <10 second generation, create a new "super_fast" quality mode:

### Update `avatar_service/avatar_server_aws.py` (or your active server file)

```python
# Quality settings
settings = {
    "super_fast": {
        "size": 256, 
        "preprocess": "crop",  # Fastest preprocessing
        "still": True,         # Minimal head movement
        "enhancer": None,      # NO face enhancement (saves 3-5s!)
    },
    "fast": {
        "size": 256, 
        "preprocess": "crop", 
        "still": True,
        "enhancer": "gfpgan",  # Face enhancement adds time
    },
    "standard": {
        "size": 256, 
        "preprocess": "full", 
        "still": False,
        "enhancer": "gfpgan",
    },
    "high": {
        "size": 512, 
        "preprocess": "full", 
        "still": False,
        "enhancer": "gfpgan",
    },
}

cfg = settings.get(quality, settings["super_fast"])

# Build command
cmd = [
    "python", str(SADTALKER_DIR / "inference.py"),
    "--driven_audio", str(audio_path),
    "--source_image", str(image_path),
    "--result_dir", str(output_path.parent),
    "--size", str(cfg["size"]),
    "--preprocess", cfg["preprocess"],
]

# Only add enhancer if specified
if cfg.get("enhancer"):
    cmd.extend(["--enhancer", cfg["enhancer"]])

if cfg["still"]:
    cmd.append("--still")
```

---

## 🔥 Speed Optimization Techniques

### 1. **Remove Face Enhancement** (saves 3-5 seconds)
```python
# Don't use --enhancer flag in super_fast mode
# Quality is still good for real-time applications
```

### 2. **Use Crop Preprocessing** (saves 2-3 seconds)
```python
"preprocess": "crop"  # vs "full" which analyzes entire image
```

### 3. **Enable Still Mode** (saves 1-2 seconds)
```python
"still": True  # Minimal head movement, faster processing
```

### 4. **Use Lower Resolution** (already doing this)
```python
"size": 256  # vs 512 (saves ~5 seconds)
```

### 5. **GPU Optimization** (critical!)

Make sure your Windows Graphics Settings are configured for High Performance:

```powershell
# Run this PowerShell script to verify GPU is being used
nvidia-smi

# You should see Python process using GPU
# If not, configure Windows Graphics Settings:
# Settings > System > Display > Graphics Settings
# Add Python.exe from SadTalker venv
# Set to "High Performance"
```

### 6. **Pre-cache Face Landmarks** (saves 2-3 seconds)

Cache the face landmarks for luna_base.png once:

```python
# Run this once when server starts
import subprocess
subprocess.run([
    "python", "inference.py",
    "--source_image", "luna_base.png",
    "--preprocess", "crop"
])
# This creates cached landmarks in temp folder
# Subsequent generations will be faster!
```

---

## 📊 Expected Speeds

| Mode | Resolution | Enhancer | Preprocess | Still | Expected Time |
|------|------------|----------|------------|-------|---------------|
| **super_fast** | 256px | None | crop | Yes | **6-10s** ⚡⚡⚡ |
| **fast** | 256px | gfpgan | crop | Yes | 10-15s ⚡⚡ |
| **standard** | 256px | gfpgan | full | No | 20-30s ⚡ |
| **high** | 512px | gfpgan | full | No | 30-40s |

---

## 🎬 Implementation Steps

### Step 1: Update Avatar Server

```python
# In your avatar_server file (avatar_server_aws.py or similar)
# Add super_fast mode as shown above
```

### Step 2: Test Locally

```bash
cd avatar_service
python avatar_server_aws.py

# Test with curl or browser:
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, I am Luna", "quality": "super_fast"}'
```

### Step 3: Update Frontend (Optional)

If you want to default to super_fast mode:

```javascript
// In frontend/src/components/LunaFreeInterface.js
const avatarResult = await chatService.generateAvatar(
    responseText, 
    null, 
    'default', 
    'super_fast'  // Use super_fast mode
);
```

---

## ⚠️ Quality Trade-offs

### Super-Fast Mode
- ✅ **Pros:** 
  - 6-10 second generation
  - Still looks good for real-time chat
  - Low resolution works well on most screens
  - Smooth lip-sync
  
- ❌ **Cons:**
  - No face enhancement (slightly less refined)
  - Lower resolution (256px vs 512px)
  - Minimal head movement (more static)

### Recommendation
Use **super_fast** mode for:
- ✅ Real-time conversations
- ✅ Live demos
- ✅ Interactive experiences
- ✅ When speed > quality

Use **high** mode for:
- ✅ Presentations
- ✅ Marketing videos
- ✅ Saved/cached responses
- ✅ When quality > speed

---

## 🔧 Troubleshooting

### Generation Still Slow?

1. **Check GPU Usage:**
   ```bash
   nvidia-smi
   # Should show Python process using GPU
   ```

2. **Verify Windows Graphics Settings:**
   - Windows Settings > System > Display > Graphics
   - Add Python.exe from SadTalker venv
   - Set to "High Performance"

3. **Close Other GPU Apps:**
   - Chrome/browsers with hardware acceleration
   - Other AI tools
   - Video editors

4. **Update GPU Drivers:**
   ```bash
   # Download latest from NVIDIA website
   # Your RTX 4050 should have latest drivers
   ```

5. **Check Disk Speed:**
   - SadTalker saves temp files
   - Use SSD for temp directories
   - Clear old temp files

---

## 🚀 Advanced: Even Faster

### Use Video Caching for Common Responses

```python
# Pre-generate videos for common FAQ
CACHED_RESPONSES = {
    "tell me about one development": "video_001.mp4",
    "what projects are available": "video_002.mp4",
    "what are the payment plans": "video_003.mp4",
}

# In generate_avatar():
if text.lower() in CACHED_RESPONSES:
    # Return cached video instantly!
    return cached_video_path
```

### Use Smaller Model Checkpoints

```python
# SadTalker has different checkpoint sizes
# Try using the "light" version if available
# Download from SadTalker releases
```

---

## 📈 Benchmark Your System

Run this to measure actual speeds:

```python
import time

start = time.time()
# Generate video
elapsed = time.time() - start

print(f"Generation time: {elapsed:.1f}s")
```

Target on RTX 4050:
- Super-Fast: 6-10s
- Fast: 10-15s

---

## 💡 Pro Tips

1. **Keep Server Running:** First generation is always slower (model loading)
2. **Use Still Mode:** Less computation, faster results
3. **Monitor GPU Temp:** Ensure good cooling for consistent speeds
4. **Batch Processing:** If generating multiple videos, do them sequentially
5. **Test Different Settings:** Your specific setup might vary

---

## ✅ Summary

To achieve <10 second generation:

1. ✅ Create "super_fast" quality mode
2. ✅ Remove face enhancement
3. ✅ Use crop preprocessing
4. ✅ Enable still mode
5. ✅ Use 256px resolution
6. ✅ Ensure GPU is being used
7. ✅ Pre-cache face landmarks
8. ✅ Close other GPU apps

Expected result: **6-10 seconds per video!** 🎉

---

**Ready to test? Update your local avatar server and measure the speeds!**

