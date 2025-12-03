# 📥 Wav2Lip Model Download Guide

## Model File Location
The model should be saved to:
```
%USERPROFILE%\Downloads\Wav2Lip\checkpoints\wav2lip_gan.pth
```

## Download Methods

### Method 1: Direct Download (Recommended)
1. Open browser
2. Go to: https://github.com/Rudrabha/Wav2Lip/releases
3. Download: `wav2lip_gan.pth` (~400MB)
4. Save to: `%USERPROFILE%\Downloads\Wav2Lip\checkpoints\wav2lip_gan.pth`

### Method 2: Using gdown (if installed)
```powershell
cd %USERPROFILE%\Downloads\Wav2Lip
pip install gdown
gdown https://drive.google.com/uc?id=1FWhIZQKjLQjXFR1Kh8dKJ_xT4l8Xv0jQ -O checkpoints/wav2lip_gan.pth
```

### Method 3: Manual from Google Drive
1. Go to: https://drive.google.com/file/d/1FWhIZQKjLQjXFR1Kh8dKJ_xT4l8Xv0jQ/view
2. Download the file
3. Rename to: `wav2lip_gan.pth`
4. Move to: `%USERPROFILE%\Downloads\Wav2Lip\checkpoints\`

## Verify Download
```powershell
Test-Path "%USERPROFILE%\Downloads\Wav2Lip\checkpoints\wav2lip_gan.pth"
# Should return: True

# Check file size (should be ~400MB)
(Get-Item "%USERPROFILE%\Downloads\Wav2Lip\checkpoints\wav2lip_gan.pth").Length / 1MB
# Should show: ~400
```

## After Download
Run the test:
```powershell
cd %USERPROFILE%\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service
python test_wav2lip_direct.py
```

Expected: 8-12 seconds generation time! ⚡

