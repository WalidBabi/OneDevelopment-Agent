# ⚡ Step-by-Step Speed Optimization Guide

## Goal: Minimize generation time from 205s to 8-12s

---

## 🎮 Step 1: Apply GPU Settings (2 minutes)

### Quick Method:
1. **Press:** `Windows Key + I` (opens Settings)
2. **Search:** Type "graphics settings" and click it
3. **Click:** "Browse" button
4. **Paste this path:**
   ```
   %USERPROFILE%\Downloads\SadTalker\venv310\Scripts\python.exe
   ```
5. **Select:** `python.exe` and click "Add"
6. **Click:** on the `python.exe` entry in the list
7. **Click:** "Options" button
8. **Select:** "High performance" (NVIDIA GPU)
9. **Click:** "Save"

### Also Add Wav2Lip Python (if you want):
Repeat steps 3-9 with this path:
```
%USERPROFILE%\Downloads\Wav2Lip\venv\Scripts\python.exe
```

### ⚠️ IMPORTANT:
**Close ALL PowerShell/Terminal windows and open a fresh one!**

### Verify GPU is Working:
```powershell
cd %USERPROFILE%\Downloads\SadTalker
.\venv310\Scripts\python.exe -c "import torch; print('CUDA:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

**Expected output:**
```
CUDA: True
Device: NVIDIA GeForce RTX 4050 Laptop GPU
```

**Result:** Generation time drops from 205s → **30-40 seconds** ✅

---

## 📥 Step 2: Download Wav2Lip Model (5 minutes)

### Option A: Manual Download (Recommended)

1. **Open browser** and go to:
   ```
   https://github.com/Rudrabha/Wav2Lip/releases
   ```

2. **Find and download:** `wav2lip_gan.pth` (~400MB)
   - Look for the latest release
   - Download the `.pth` file

3. **Save to:**
   ```
   %USERPROFILE%\Downloads\Wav2Lip\checkpoints\wav2lip_gan.pth
   ```
   - Create the `checkpoints` folder if it doesn't exist

4. **Verify:** File should be ~400MB

### Option B: Try Automated Download

Run this in PowerShell:
```powershell
cd %USERPROFILE%\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service
.\DOWNLOAD_WAV2LIP_MODEL.ps1
```

**Result:** Generation time drops to **8-12 seconds** ⚡

---

## 🚀 Step 3: Restart Server

1. **Stop current server** (Ctrl+C if running)

2. **Restart:**
   ```powershell
   cd %USERPROFILE%\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service
   python avatar_server_final.py
   ```

3. **Test:**
   ```powershell
   python test_avatar_api.py
   ```

---

## 📊 Expected Results

| Configuration | Time | Status |
|---------------|------|--------|
| Current (CPU) | ~120-150s | ✅ Already optimized |
| With GPU | ~30-40s | ⏳ Apply GPU settings |
| With Wav2Lip | ~8-12s | ⏳ Download model |
| Both | ~8-12s | ⏳ Do both steps |

---

## ✅ Quick Checklist

- [ ] Applied GPU settings in Windows
- [ ] Restarted terminal
- [ ] Verified GPU is detected
- [ ] Downloaded Wav2Lip model (~400MB)
- [ ] Restarted avatar server
- [ ] Tested generation speed

---

## 🎯 After Optimization

**You'll be able to:**
- Generate videos in **8-12 seconds** ⚡
- Talk to Luna in real-time
- Users won't get bored waiting
- Professional experience!

**Ready to optimize? Follow the steps above!** 🚀

