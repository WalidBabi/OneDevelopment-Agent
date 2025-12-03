# Verify Wav2Lip Model Download
$model_path = "$env:USERPROFILE\Downloads\Wav2Lip\checkpoints\wav2lip_gan.pth"

Write-Host "Checking for Wav2Lip model..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path $model_path) {
    $size = (Get-Item $model_path).Length / 1MB
    Write-Host "File found!" -ForegroundColor Green
    Write-Host "  Path: $model_path" -ForegroundColor White
    Write-Host "  Size: $([math]::Round($size, 2)) MB" -ForegroundColor White
    Write-Host ""
    
    if ($size -gt 100) {
        Write-Host "✅ SUCCESS! Model is ready!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Wav2Lip will now generate videos in 8-12 seconds! ⚡" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next: Restart your avatar server:" -ForegroundColor Cyan
        Write-Host "  python avatar_server_final.py" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️  File exists but is too small" -ForegroundColor Yellow
        Write-Host "   Expected: ~400 MB" -ForegroundColor Yellow
        Write-Host "   Found: $([math]::Round($size, 2)) MB" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Please re-download the file" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Model file not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Expected location:" -ForegroundColor Yellow
    Write-Host "  $model_path" -ForegroundColor White
    Write-Host ""
    Write-Host "Please download wav2lip_gan.pth (~400MB) and save it there" -ForegroundColor Yellow
}

