# Start Luna Avatar Server with SadTalker
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Starting Luna Avatar Service with Video Generation" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to avatar service directory
cd C:\Users\Walid\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service

# Activate environment
Write-Host "Activating Python environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Add FFmpeg to PATH
Write-Host "Adding FFmpeg to PATH..." -ForegroundColor Yellow
$env:Path += ";C:\Users\Walid\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"

# Set quality mode
$env:VIDEO_QUALITY = "high"

# Force NVIDIA GPU
$env:CUDA_VISIBLE_DEVICES = "0"
$env:CUDA_DEVICE_ORDER = "PCI_BUS_ID"

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Green
Write-Host "  Video Quality: high (512px + GFPGAN)" -ForegroundColor Cyan
Write-Host "  GPU: NVIDIA (forced)" -ForegroundColor Cyan
Write-Host "  Expected video time: 30-40 seconds" -ForegroundColor Cyan
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Starting server on http://localhost:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Start server
python avatar_server_final.py

