# 📥 Download Wav2Lip Model - Interactive Helper
Write-Host "=" -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "📥 Wav2Lip Model Download Helper" -ForegroundColor Green
Write-Host "=" -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

$checkpoints_dir = "C:\Users\Walid\Downloads\Wav2Lip\checkpoints"
$model_path = "$checkpoints_dir\wav2lip_gan.pth"

# Create directory
if (-not (Test-Path $checkpoints_dir)) {
    New-Item -ItemType Directory -Path $checkpoints_dir -Force | Out-Null
}

# Check if exists
if (Test-Path $model_path) {
    $size = (Get-Item $model_path).Length / 1MB
    if ($size -gt 100) {
        Write-Host "✓ Model already exists: $([math]::Round($size, 2)) MB" -ForegroundColor Green
        Write-Host ""
        Write-Host "You're all set! Restart the server to use Wav2Lip." -ForegroundColor Green
        exit 0
    }
}

Write-Host "Opening download page in your browser..." -ForegroundColor Cyan
Write-Host ""

# Open multiple sources
Start-Process "https://github.com/Rudrabha/Wav2Lip/releases"
Start-Sleep -Seconds 2
Start-Process "https://drive.google.com/file/d/1FWhIZQKjLQjXFR1Kh8dKJ_xT4l8Xv0jQ/view"

Write-Host "=" * 70 -ForegroundColor Yellow
Write-Host "DOWNLOAD INSTRUCTIONS:" -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Yellow
Write-Host ""
Write-Host "I've opened 2 browser tabs for you:" -ForegroundColor White
Write-Host ""
Write-Host "Tab 1: GitHub Releases" -ForegroundColor Cyan
Write-Host "  → Look for 'wav2lip_gan.pth' file (~400MB)" -ForegroundColor White
Write-Host "  → Click to download" -ForegroundColor White
Write-Host ""
Write-Host "Tab 2: Google Drive (Alternative)" -ForegroundColor Cyan
Write-Host "  → Click 'Download' button" -ForegroundColor White
Write-Host "  → If it says 'Download quota exceeded', wait a few minutes" -ForegroundColor Yellow
Write-Host ""
Write-Host "SAVE THE FILE TO:" -ForegroundColor Green
Write-Host "  $model_path" -ForegroundColor Yellow
Write-Host ""
Write-Host "After downloading, I'll verify it for you!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key when you've finished downloading..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Verify download
Write-Host ""
Write-Host "Checking for downloaded file..." -ForegroundColor Cyan

if (Test-Path $model_path) {
    $size = (Get-Item $model_path).Length / 1MB
    if ($size -gt 100) {
        Write-Host ""
        Write-Host ("=" * 70) -ForegroundColor Green
        Write-Host "✅ SUCCESS! Model downloaded!" -ForegroundColor Green
        Write-Host ("=" * 70) -ForegroundColor Green
        Write-Host ""
        Write-Host "File: $model_path" -ForegroundColor Green
        Write-Host "Size: $([math]::Round($size, 2)) MB" -ForegroundColor Green
        Write-Host ""
        Write-Host "Wav2Lip is now ready for 8-12 second generation! ⚡" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next: Restart your avatar server!" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "⚠️  File found but too small: $([math]::Round($size, 2)) MB" -ForegroundColor Yellow
        Write-Host "   Expected: ~400 MB" -ForegroundColor Yellow
        Write-Host "   Please re-download the file" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "❌ File not found at: $model_path" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure you saved it to the correct location!" -ForegroundColor Yellow
    Write-Host "Path: $model_path" -ForegroundColor Yellow
}

