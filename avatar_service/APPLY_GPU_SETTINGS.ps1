# 🎮 Apply GPU Settings - Automated Guide
# This script helps you configure Windows Graphics Settings for maximum speed

Write-Host "=" -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "🎮 GPU Settings Configuration Guide" -ForegroundColor Green
Write-Host "=" -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

Write-Host "This will help you configure Windows to use NVIDIA GPU for faster generation." -ForegroundColor Yellow
Write-Host ""

# Check if paths exist
$sadtalker_python = "C:\Users\Walid\Downloads\SadTalker\venv310\Scripts\python.exe"
$wav2lip_python = "C:\Users\Walid\Downloads\Wav2Lip\venv\Scripts\python.exe"

Write-Host "Checking Python executables..." -ForegroundColor Cyan
if (Test-Path $sadtalker_python) {
    Write-Host "✓ SadTalker Python found" -ForegroundColor Green
} else {
    Write-Host "✗ SadTalker Python not found: $sadtalker_python" -ForegroundColor Red
}

if (Test-Path $wav2lip_python) {
    Write-Host "✓ Wav2Lip Python found" -ForegroundColor Green
} else {
    Write-Host "✗ Wav2Lip Python not found: $wav2lip_python" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "MANUAL STEPS (Windows Settings):" -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Press Windows Key + I (opens Settings)" -ForegroundColor White
Write-Host ""
Write-Host "2. In the search box, type: graphics settings" -ForegroundColor White
Write-Host "   Then click 'Graphics settings'" -ForegroundColor White
Write-Host ""
Write-Host "3. Under 'Graphics performance preference', click 'Browse'" -ForegroundColor White
Write-Host ""
Write-Host "4. Copy and paste this path:" -ForegroundColor Cyan
Write-Host "   $sadtalker_python" -ForegroundColor Yellow
Write-Host ""
Write-Host "5. Select 'python.exe' and click 'Add'" -ForegroundColor White
Write-Host ""
Write-Host "6. Click on 'python.exe' in the list" -ForegroundColor White
Write-Host ""
Write-Host "7. Click 'Options' button" -ForegroundColor White
Write-Host ""
Write-Host "8. Select 'High performance' (this is NVIDIA GPU)" -ForegroundColor Green
Write-Host ""
Write-Host "9. Click 'Save'" -ForegroundColor White
Write-Host ""

if (Test-Path $wav2lip_python) {
    Write-Host "10. Repeat steps 3-9 for Wav2Lip:" -ForegroundColor White
    Write-Host "    Path: $wav2lip_python" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "11. IMPORTANT: Close ALL PowerShell/Terminal windows" -ForegroundColor Red
Write-Host "    Then open a fresh terminal for changes to take effect!" -ForegroundColor Red
Write-Host ""

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "After restarting terminal, verify GPU is working:" -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "Run this command:" -ForegroundColor White
Write-Host "cd C:\Users\Walid\Downloads\SadTalker" -ForegroundColor Cyan
Write-Host ".\venv310\Scripts\python.exe -c `"import torch; print('CUDA:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')`"" -ForegroundColor Cyan
Write-Host ""
Write-Host "You should see:" -ForegroundColor White
Write-Host "  CUDA: True" -ForegroundColor Green
Write-Host "  Device: NVIDIA GeForce RTX 4050 Laptop GPU" -ForegroundColor Green
Write-Host ""

Write-Host "Press any key to open Windows Settings..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Try to open Graphics Settings
try {
    Start-Process "ms-settings:display-advancedgraphics"
    Write-Host ""
    Write-Host "✓ Opened Windows Settings - follow the steps above!" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "⚠️  Could not open Settings automatically" -ForegroundColor Yellow
    Write-Host "   Please open manually: Windows Key + I, then search 'graphics settings'" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "After configuring, restart your terminal and test!" -ForegroundColor Cyan

