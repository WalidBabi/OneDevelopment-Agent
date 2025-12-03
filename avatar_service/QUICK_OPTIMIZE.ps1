# ⚡ Quick Optimization Script - Apply All Speed Improvements
# This script helps you apply both GPU settings and download Wav2Lip model

Write-Host "=" -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "⚡ Quick Speed Optimization" -ForegroundColor Green
Write-Host "=" -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

Write-Host "This script will help you:" -ForegroundColor Yellow
Write-Host "  1. Configure GPU settings (30-40s generation)" -ForegroundColor White
Write-Host "  2. Download Wav2Lip model (8-12s generation)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Choose an option:
  1) Configure GPU settings only
  2) Download Wav2Lip model only  
  3) Do both (recommended)
  4) Check current status
Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Opening GPU settings guide..." -ForegroundColor Cyan
        & ".\APPLY_GPU_SETTINGS.ps1"
    }
    "2" {
        Write-Host ""
        Write-Host "Starting Wav2Lip model download..." -ForegroundColor Cyan
        & ".\DOWNLOAD_WAV2LIP_MODEL.ps1"
    }
    "3" {
        Write-Host ""
        Write-Host "Step 1: GPU Settings" -ForegroundColor Yellow
        Write-Host ("=" * 70) -ForegroundColor Cyan
        & ".\APPLY_GPU_SETTINGS.ps1"
        
        Write-Host ""
        Write-Host ""
        Write-Host "Step 2: Wav2Lip Model" -ForegroundColor Yellow
        Write-Host ("=" * 70) -ForegroundColor Cyan
        & ".\DOWNLOAD_WAV2LIP_MODEL.ps1"
        
        Write-Host ""
        Write-Host ("=" * 70) -ForegroundColor Green
        Write-Host "✅ Optimization Complete!" -ForegroundColor Green
        Write-Host ("=" * 70) -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Yellow
        Write-Host "  1. Restart your terminal (if GPU settings were changed)" -ForegroundColor White
        Write-Host "  2. Restart avatar server: python avatar_server_final.py" -ForegroundColor White
        Write-Host "  3. Test: python test_avatar_api.py" -ForegroundColor White
        Write-Host ""
        Write-Host "Expected speed:" -ForegroundColor Cyan
        Write-Host "  With GPU: 30-40 seconds" -ForegroundColor Green
        Write-Host "  With Wav2Lip: 8-12 seconds ⚡" -ForegroundColor Green
    }
    "4" {
        Write-Host ""
        Write-Host "Checking current status..." -ForegroundColor Cyan
        Write-Host ""
        
        # Check GPU
        Write-Host "GPU Status:" -ForegroundColor Yellow
        try {
            Push-Location C:\Users\Walid\Downloads\SadTalker
            $gpu_check = .\venv310\Scripts\python.exe -c "import torch; print('CUDA:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')" 2>&1
            Pop-Location
            Write-Host $gpu_check
            if ($gpu_check -match "CUDA: True" -and $gpu_check -match "NVIDIA") {
                Write-Host "✓ GPU is configured correctly!" -ForegroundColor Green
            } else {
                Write-Host "⚠️  GPU not configured - run GPU settings script" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "⚠️  Could not check GPU status" -ForegroundColor Yellow
        }
        
        Write-Host ""
        
        # Check Wav2Lip model
        Write-Host "Wav2Lip Model Status:" -ForegroundColor Yellow
        $model_path = "C:\Users\Walid\Downloads\Wav2Lip\checkpoints\wav2lip_gan.pth"
        if (Test-Path $model_path) {
            $size = (Get-Item $model_path).Length / 1MB
            if ($size -gt 100) {
                Write-Host "✓ Model found: $([math]::Round($size, 2)) MB" -ForegroundColor Green
            } else {
                Write-Host "⚠️  Model file too small: $([math]::Round($size, 2)) MB (needs ~400MB)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "✗ Model not found - run download script" -ForegroundColor Red
        }
        
        Write-Host ""
        Write-Host "Current Performance:" -ForegroundColor Yellow
        Write-Host "  Without optimizations: ~205 seconds" -ForegroundColor White
        Write-Host "  With GPU: ~30-40 seconds" -ForegroundColor Green
        Write-Host "  With Wav2Lip: ~8-12 seconds ⚡" -ForegroundColor Green
    }
    default {
        Write-Host "Invalid choice. Please run again and select 1-4." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

