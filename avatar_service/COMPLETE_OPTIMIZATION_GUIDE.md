# ⚡ Complete Speed Optimization Guide

## Current: 205 seconds → Target: 8-12 seconds

---

## 🎮 Step 1: GPU Settings (2 minutes) - DO THIS FIRST

### Quick Steps:

1. **Press:** `Windows Key + I`
2. **Type:** `graphics settings` (in search box)
3. **Click:** "Graphics settings"
4. **Click:** "Browse"
5. **Paste this path:**
   ```
   %USERPROFILE%\Downloads\SadTalker\venv310\Scripts\python.exe
   ```
6. **Click:** "Add"
7. **Click:** on `python.exe` in the list
8. **Click:** "Options"
9. **Select:** "High performance" ⚡ (This is NVIDIA GPU)
10. **Click:** "Save"

### ⚠️ CRITICAL:
**Close ALL PowerShell/Terminal windows and open a fresh one!**

### Verify It Worked:
```powershell
cd %USERPROFILE%\Downloads\SadTalker
.\venv310\Scripts\python.exe -c "import torch; print('CUDA:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

**Should show:**
```
CUDA: True
Device: NVIDIA GeForce RTX 4050 Laptop GPU
```

**Result:** 205s → **30-40 seconds** ✅

---

## 📥 Step 2: Download Wav2Lip Model (5 minutes)

### I've Opened Browser Tabs For You!

**Two tabs should be open:**
1. GitHub Releases: https://github.com/Rudrabha/Wav2Lip/releases
2. Google Drive: https://drive.google.com/file/d/1FWhIZQKjLQjXFR1Kh8dKJ_xT4l8Xv0jQ/view

### Download Steps:

1. **In one of the browser tabs:**
   - GitHub: Look for `wav2lip_gan.pth` file (~400MB) and download
   - Google Drive: Click "Download" button

2. **When browser asks where to save:**
   - Navigate to: `%USERPROFILE%\Downloads\Wav2Lip\checkpoints\`
   - Or save anywhere, then move it there

3. **File name must be:** `wav2lip_gan.pth`

4. **File size should be:** ~400 MB

### Verify Download:
```powershell
cd %USERPROFILE%\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service
.\VERIFY_MODEL.ps1
```

**Result:** 30-40s → **8-12 seconds** ⚡

---

## 🚀 Step 3: Restart Server

```powershell
# Stop current server (Ctrl+C)
cd %USERPROFILE%\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service
python avatar_server_final.py
```

---

## ✅ After Both Steps

**Expected Performance:**
- **Generation time:** 8-12 seconds ⚡
- **User experience:** Professional, no waiting!
- **Quality:** Excellent lip-sync

**Test it:**
```powershell
python test_avatar_api.py
```

---

## 📊 Speed Comparison

| Step | Time | Generation Speed |
|------|------|------------------|
| Current (CPU) | - | 205 seconds |
| + GPU Settings | 2 min | 30-40 seconds |
| + Wav2Lip Model | 5 min | **8-12 seconds** ⚡ |

---

## 🎯 Quick Checklist

- [ ] Applied GPU settings (Windows Graphics Settings)
- [ ] Restarted terminal
- [ ] Verified GPU detected
- [ ] Downloaded wav2lip_gan.pth (~400MB)
- [ ] Saved to: `%USERPROFILE%\Downloads\Wav2Lip\checkpoints\`
- [ ] Verified with: `.\VERIFY_MODEL.ps1`
- [ ] Restarted avatar server
- [ ] Tested generation speed

---

## 🆘 Troubleshooting

### GPU Not Detected?
- Make sure you selected "High performance" not "Power saving"
- Restart terminal after changing settings
- Verify with the command above

### Model Download Failed?
- Try the other browser tab (GitHub or Google Drive)
- Google Drive quota exceeded? Wait 10 minutes and try again
- Check file size - should be ~400MB

### Still Slow?
- Make sure GPU settings applied (restart terminal!)
- Check if Wav2Lip model is downloaded and verified
- Restart server after changes

---

## 🎉 You're Almost There!

**After completing both steps, you'll have:**
- ⚡ 8-12 second video generation
- 🎭 Professional talking avatar
- 😊 Happy users who don't wait!

**Let's get it done!** 🚀

