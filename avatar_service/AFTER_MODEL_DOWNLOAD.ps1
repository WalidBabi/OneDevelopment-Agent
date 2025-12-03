# Run this after downloading Wav2Lip model
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "🔍 Verifying Wav2Lip Model" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

$model_path = "C:\Users\Walid\Downloads\Wav2Lip\checkpoints\wav2lip_gan.pth"

if (Test-Path $model_path) {
    $size = (Get-Item $model_path).Length / 1MB
    if ($size -gt 100) {
        Write-Host "✅ Model found: $([math]::Round($size, 2)) MB" -ForegroundColor Green
        Write-Host ""
        Write-Host "Restarting avatar server..." -ForegroundColor Cyan
        
        # Stop avatar server
        Get-Process | Where-Object {$_.CommandLine -like "*avatar_server_final.py*"} | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        
        # Start avatar server
        cd C:\Users\Walid\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python avatar_server_final.py" -WindowStyle Minimized
        
        Write-Host "✅ Avatar server restarted!" -ForegroundColor Green
        Write-Host ""
        Write-Host "=" * 70 -ForegroundColor Green
        Write-Host "🎉 READY FOR 8-12 SECOND GENERATION!" -ForegroundColor Green
        Write-Host "=" * 70 -ForegroundColor Green
        Write-Host ""
        Write-Host "Test now:" -ForegroundColor Cyan
        Write-Host "  1. Go to: http://13.62.188.127:3000/" -ForegroundColor White
        Write-Host "  2. Ask Luna a question" -ForegroundColor White
        Write-Host "  3. Watch video generate in 8-12 seconds! ⚡" -ForegroundColor Green
    } else {
        Write-Host "⚠️  File too small: $([math]::Round($size, 2)) MB" -ForegroundColor Yellow
        Write-Host "   Expected: ~400 MB" -ForegroundColor Yellow
        Write-Host "   Please re-download the model" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Model not found at: $model_path" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download wav2lip_gan.pth and save it to:" -ForegroundColor Yellow
    Write-Host "  $model_path" -ForegroundColor White
}

