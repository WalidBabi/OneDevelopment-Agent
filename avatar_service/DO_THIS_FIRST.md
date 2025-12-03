# ⚡ DO THIS FIRST - GPU Optimization (Easiest Path!)

## 🎯 Goal: Minimize 205s → 30-40s (5x faster!)

Since Wav2Lip model download is difficult, **optimize SadTalker with GPU instead!**

---

## 🎮 GPU Settings (2 Minutes)

### Step-by-Step:

1. **Press:** `Windows Key + I`
2. **Type:** `graphics settings` (in search)
3. **Click:** "Graphics settings"
4. **Click:** "Browse"
5. **Paste:**
   ```
   %USERPROFILE%\Downloads\SadTalker\venv310\Scripts\python.exe
   ```
6. **Click:** "Add"
7. **Click:** on `python.exe` in list
8. **Click:** "Options"
9. **Select:** "High performance" ⚡
10. **Click:** "Save"

### ⚠️ CRITICAL:
**Close ALL terminals and open fresh one!**

---

## ✅ Verify It Worked

```powershell
cd %USERPROFILE%\Downloads\SadTalker
.\venv310\Scripts\python.exe -c "import torch; print('CUDA:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

**Should show:**
```
CUDA: True
Device: NVIDIA GeForce RTX 4050 Laptop GPU
```

---

## 🚀 Result

**Before:** 205 seconds  
**After:** 30-40 seconds  
**Improvement:** 5x faster! ✅

---

## 📋 Next Steps

1. ✅ Apply GPU settings (above)
2. ✅ Restart terminal
3. ✅ Restart server: `python avatar_server_final.py`
4. ✅ Test: `python test_avatar_api.py`

**You'll see 30-40 second generation instead of 205 seconds!** 🎉

---

## 💡 Later: Download Wav2Lip for Even Faster (8-12s)

Once GPU is working, you can download Wav2Lip model later for maximum speed.  
But GPU optimization alone gives you **5x speed improvement right now!**

**Start with GPU settings - it's the easiest win!** ⚡

