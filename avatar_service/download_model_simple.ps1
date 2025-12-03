# Download Wav2Lip Model Helper
$checkpoints_dir = "C:\Users\Walid\Downloads\Wav2Lip\checkpoints"
$model_path = "$checkpoints_dir\wav2lip_gan.pth"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "📥 Wav2Lip Model Download" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Create directory
if (-not (Test-Path $checkpoints_dir)) {
    New-Item -ItemType Directory -Path $checkpoints_dir -Force | Out-Null
}

# Check if exists
if (Test-Path $model_path) {
    $size = (Get-Item $model_path).Length / 1MB
    if ($size -gt 100) {
        Write-Host "✓ Model already exists: $([math]::Round($size, 2)) MB" -ForegroundColor Green
        exit 0
    }
}

Write-Host "Opening download pages..." -ForegroundColor Cyan
Start-Process "https://github.com/Rudrabha/Wav2Lip/releases"
Start-Sleep -Seconds 1
Start-Process "https://drive.google.com/file/d/1FWhIZQKjLQjXFR1Kh8dKJ_xT4l8Xv0jQ/view"

Write-Host ""
Write-Host "DOWNLOAD INSTRUCTIONS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. In the browser tabs that opened:" -ForegroundColor White
Write-Host "   - Try GitHub Releases first" -ForegroundColor Gray
Write-Host "   - Or use Google Drive link" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Download: wav2lip_gan.pth (~400MB)" -ForegroundColor White
Write-Host ""
Write-Host "3. Save to:" -ForegroundColor White
Write-Host "   $model_path" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Come back here and press Enter when done..." -ForegroundColor Cyan
Read-Host

# Verify
if (Test-Path $model_path) {
    $size = (Get-Item $model_path).Length / 1MB
    if ($size -gt 100) {
        Write-Host ""
        Write-Host "✅ SUCCESS! Model ready: $([math]::Round($size, 2)) MB" -ForegroundColor Green
        Write-Host "Restart server to use Wav2Lip (8-12s generation)!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠️  File too small. Please re-download." -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "❌ File not found. Make sure you saved it to:" -ForegroundColor Red
    Write-Host "   $model_path" -ForegroundColor Yellow
}

