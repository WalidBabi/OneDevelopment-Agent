# 🎮 Verify Windows Graphics Settings for SadTalker

## Quick Check Script

Run this to verify GPU settings are configured:

```powershell
# Check if SadTalker Python is configured for GPU
cd %USERPROFILE%\Downloads\SadTalker
.\venv310\Scripts\python.exe -c "import torch; print('CUDA:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

## Manual Verification Steps

### 1. Open Graphics Settings
- Press `Windows Key + I`
- Search for "graphics settings"
- Click "Graphics settings"

### 2. Check if SadTalker Python is Added
Look for this path in the list:
```
%USERPROFILE%\Downloads\SadTalker\venv310\Scripts\python.exe
```

### 3. If NOT Found - Add It:
1. Click **"Browse"**
2. Navigate to: `%USERPROFILE%\Downloads\SadTalker\venv310\Scripts`
3. Select **python.exe**
4. Click **"Add"**
5. Click on the python.exe entry
6. Click **"Options"**
7. Select **"High performance"** (NVIDIA GPU)
8. Click **"Save"**

### 4. Restart Terminal
**CRITICAL:** Close and reopen PowerShell/Terminal for changes to take effect!

## Expected Result

After restarting, when you run SadTalker, Task Manager should show:
- **GPU 1 (NVIDIA RTX 4050):** High utilization (50-100%)
- **GPU 0 (Intel Arc):** Low utilization

## Current Status Check

Run this test:
```powershell
cd %USERPROFILE%\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service
python test_sadtalker_direct.py
```

**While it's running:**
1. Open Task Manager (Ctrl+Shift+Esc)
2. Go to "Performance" tab
3. Click "GPU 1" (NVIDIA)
4. Watch the utilization graph

**If GPU 1 shows 0%:** GPU settings not applied - follow steps above
**If GPU 1 shows 50-100%:** GPU is working! ✅

