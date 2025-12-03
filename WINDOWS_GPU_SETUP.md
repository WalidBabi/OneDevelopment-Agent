# 🎮 Windows GPU Settings - Force NVIDIA for Maximum Speed

## 🚨 Critical Issue

Your laptop has 2 GPUs:
- **GPU 0: Intel Arc** (Integrated, slower, power-saving)
- **GPU 1: NVIDIA RTX 4050** (Discrete, faster, high-performance)

**Problem:** Windows defaults to Intel Arc for power saving  
**Result:** 12+ minute video generation instead of 15-20 seconds  
**Solution:** Force Windows to use NVIDIA GPU for Python

---

## ✅ Solution: Windows Graphics Settings (PERMANENT FIX)

### Step 1: Open Graphics Settings

**Method A: Via Settings**
1. Press `Windows Key + I` (Opens Settings)
2. Click **"System"** in the left sidebar
3. Click **"Display"**
4. Scroll down and click **"Graphics"**

**Method B: Via Search**
1. Press `Windows Key`
2. Type: **"Graphics settings"**
3. Click the result

### Step 2: Add Wav2Lip Python to High Performance List

1. Under "Graphics performance preference", click **"Browse"**

2. Navigate to and select:
   ```
   %USERPROFILE%\Downloads\Wav2Lip\venv\Scripts\python.exe
   ```

3. Click **"Add"**

### Step 3: Configure for High Performance

1. Find **"python.exe"** in the list (you may see the full path)

2. Click on it to select it

3. Click **"Options"** button

4. Select **"High performance"** (this is the NVIDIA GPU)

5. Click **"Save"**

### Step 4: Repeat for SadTalker (Optional)

If you want to use SadTalker with NVIDIA too:

1. Click **"Browse"** again

2. Navigate to:
   ```
   %USERPROFILE%\Downloads\SadTalker\venv310\Scripts\python.exe
   ```

3. Add and set to **"High performance"**

### Step 5: Repeat for Avatar Service (Important!)

For your main avatar service:

1. Click **"Browse"** again

2. Navigate to:
   ```
   %USERPROFILE%\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service\venv\Scripts\python.exe
   ```

3. Add and set to **"High performance"**

### Step 6: Restart Terminal

**Important:** Close and reopen PowerShell/Terminal for changes to take effect!

---

## 🔍 Verify It's Working

### Method 1: Task Manager (Visual Confirmation)

1. Open **Task Manager** (`Ctrl + Shift + Esc`)

2. Go to **"Performance"** tab

3. Look for **"GPU 1"** (NVIDIA GeForce RTX 4050)

4. Run Wav2Lip generation

5. **Expected Result:**
   - **GPU 1 (NVIDIA):** 80-100% usage 🟢
   - **GPU 0 (Intel Arc):** 0-20% usage
   - **Generation time:** 15-20 seconds ⚡

### Method 2: Python Check

```powershell
cd %USERPROFILE%\Downloads\Wav2Lip
.\venv\Scripts\activate
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}')"
```

**Expected output:**
```
GPU: NVIDIA GeForce RTX 4050 Laptop GPU
```

### Method 3: nvidia-smi

While Wav2Lip is running:

```powershell
nvidia-smi
```

You should see `python.exe` in the processes list using GPU memory.

---

## 📊 Expected Performance Improvement

| Metric | Before (Intel Arc) | After (NVIDIA) | Improvement |
|--------|-------------------|----------------|-------------|
| **Generation time** | 12+ minutes | 15-20 seconds | **36-48x faster!** |
| **Frame rate** | 5 seconds/frame | 0.1 seconds/frame | **50x faster!** |
| **GPU usage** | Intel: 50-80% | NVIDIA: 80-100% | Optimal |
| **User experience** | Unusable ❌ | Professional ✅ | Huge win! |

---

## 🛠️ Alternative Method: NVIDIA Control Panel

If the above doesn't work, try NVIDIA Control Panel:

### Step 1: Open NVIDIA Control Panel

1. Right-click on **Desktop**
2. Click **"NVIDIA Control Panel"**
3. (If not showing, install/update NVIDIA drivers)

### Step 2: Manage 3D Settings

1. In left sidebar, go to: **"3D Settings"** → **"Manage 3D Settings"**

2. Click **"Program Settings"** tab

3. Click **"Add"** button

4. Click **"Browse"**

5. Navigate to:
   ```
   %USERPROFILE%\Downloads\Wav2Lip\venv\Scripts\python.exe
   ```

6. Click "Add Selected Program"

### Step 3: Set Preferred GPU

1. In "Select the preferred graphics processor" dropdown

2. Choose: **"High-performance NVIDIA processor"**

3. Click **"Apply"** at the bottom

4. Repeat for other Python installations (SadTalker, avatar_service)

---

## 🔥 Power Plan Optimization (Optional but Recommended)

For maximum performance:

### Set High Performance Power Plan

```powershell
# View available plans
powercfg /list

# Set to High Performance
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# Or via GUI: Control Panel → Power Options → High Performance
```

**Result:** GPU won't throttle, consistent 15-20s generation!

---

## 📝 Quick Reference Commands

### Check Which GPU PyTorch is Using

```powershell
cd %USERPROFILE%\Downloads\Wav2Lip
.\venv\Scripts\activate
python -c "import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No CUDA')"
```

### Monitor GPU Usage in Real-Time

```powershell
# Update every 1 second
nvidia-smi -l 1
```

### Check GPU Processes

```powershell
nvidia-smi --query-compute-apps=pid,name,used_memory --format=csv
```

---

## 🚨 Troubleshooting

### Still Using Intel Arc?

**Problem:** Task Manager shows Intel Arc at 50-80%, NVIDIA at 0%

**Solutions:**

1. **Double-check Graphics Settings**
   - Ensure python.exe is set to "High performance"
   - Restart terminal after changing

2. **Update NVIDIA Drivers**
   - Go to: https://www.nvidia.com/download/index.aspx
   - Download latest driver for RTX 4050
   - Install and restart

3. **Disable Intel GPU (Temporary Test)**
   - Open Device Manager
   - Expand "Display adapters"
   - Right-click "Intel Arc"
   - Choose "Disable device"
   - Test Wav2Lip
   - Re-enable when done

4. **Set in Environment Variables**
   ```powershell
   # Add to PowerShell profile
   $env:CUDA_VISIBLE_DEVICES = "0"
   $env:CUDA_DEVICE_ORDER = "PCI_BUS_ID"
   ```

### Still Slow Even with NVIDIA?

**Check:**

1. **GPU Temperature:** May be throttling if too hot
   ```powershell
   nvidia-smi --query-gpu=temperature.gpu --format=csv
   ```

2. **Power Limit:** Ensure not power-limited
   ```powershell
   nvidia-smi -q -d POWER
   ```

3. **Background Processes:** Close other GPU-heavy apps

4. **VRAM:** Ensure enough free memory (need ~2-3GB)
   ```powershell
   nvidia-smi --query-gpu=memory.used,memory.total --format=csv
   ```

---

## ✅ Success Checklist

After setup, verify:

- [ ] Python.exe added to Windows Graphics Settings
- [ ] Set to "High performance" (NVIDIA)
- [ ] Terminal restarted
- [ ] Task Manager shows NVIDIA GPU active during generation
- [ ] Generation time is 15-20 seconds (not minutes)
- [ ] Consistent speed across multiple generations

**When all checked:** You're optimized! 🎉

---

## 📈 Before & After

### Before GPU Fix:
```
User asks question
↓
Generate with Intel Arc
↓
Wait 12+ minutes ❌
↓
User left website 😞
```

### After GPU Fix:
```
User asks question
↓
Audio plays (2-3s) ✅
↓
Generate with NVIDIA (15-20s) ⚡
↓
Video plays (total: 17-23s) ✅
↓
User happy! 😊
```

---

## 🎯 Summary

**Issue:** Windows using slow Intel GPU  
**Fix:** Graphics Settings → High Performance  
**Result:** 36-48x faster (15-20s instead of 12+ min)  
**Time to fix:** 2 minutes  
**Benefit:** Forever!  

**Do this once, enjoy forever!** 🚀


