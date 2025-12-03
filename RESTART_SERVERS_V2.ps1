# Restart Frontend and Backend Servers - Fixed
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "🔄 Restarting Servers" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Check if AVATAR_SERVICE_URL is set
if ([string]::IsNullOrWhiteSpace($env:AVATAR_SERVICE_URL)) {
    Write-Host "❌ Error: AVATAR_SERVICE_URL environment variable is not set!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please set your ngrok URL first:" -ForegroundColor Yellow
    Write-Host "  1. Start ngrok: ngrok http 8000" -ForegroundColor White
    Write-Host "  2. Copy the HTTPS forwarding URL" -ForegroundColor White
    Write-Host "  3. Run: .\SET_AVATAR_URL.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "OR set manually:" -ForegroundColor Yellow
    Write-Host '  $env:AVATAR_SERVICE_URL = "https://YOUR_URL.ngrok-free.app"' -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✅ Using AVATAR_SERVICE_URL: $env:AVATAR_SERVICE_URL" -ForegroundColor Green
Write-Host ""

# Frontend
Write-Host "Stopping frontend..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.CommandLine -like "*npm*start*" -or $_.CommandLine -like "*react-scripts*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "Starting frontend..." -ForegroundColor Green
$frontendDir = Join-Path $PSScriptRoot "frontend"
if (Test-Path $frontendDir) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendDir'; `$env:AVATAR_SERVICE_URL='$env:AVATAR_SERVICE_URL'; npm start" -WindowStyle Minimized
    Write-Host "  ✓ Frontend restarting on port 3000" -ForegroundColor Green
}

Start-Sleep -Seconds 2

# Backend
Write-Host ""
Write-Host "Stopping backend..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.CommandLine -like "*manage.py*" -or $_.CommandLine -like "*runserver*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "Starting backend..." -ForegroundColor Green
$backendDir = Join-Path $PSScriptRoot "backend"
if (Test-Path $backendDir) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; `$env:AVATAR_SERVICE_URL='$env:AVATAR_SERVICE_URL'; python manage.py runserver 0.0.0.0:8001" -WindowStyle Minimized
    Write-Host "  ✓ Backend restarting on port 8001" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "✅ RESTART COMPLETE!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host ""
Write-Host "STATUS:" -ForegroundColor Cyan
Write-Host "  • Timeout increased to 600s (10 mins)" -ForegroundColor White
Write-Host "  • SadTalker batch size = 4 (faster GPU)" -ForegroundColor White
Write-Host "  • Old audio/video issue fixed" -ForegroundColor White
Write-Host ""
Write-Host "TEST:" -ForegroundColor Yellow
Write-Host "  1. Wait 15 seconds" -ForegroundColor White
Write-Host "  2. Go to: http://localhost:3000/" -ForegroundColor White
Write-Host "  3. Ask Luna a question" -ForegroundColor White

