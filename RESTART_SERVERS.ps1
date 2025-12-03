# Restart Frontend and Backend Servers
# This script restarts servers with the new fixes applied

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

# Find and stop frontend (port 3000)
Write-Host "Stopping frontend..." -ForegroundColor Yellow
$frontend = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -First 1
if ($frontend) {
    Stop-Process -Id $frontend -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Stopped frontend (PID: $frontend)" -ForegroundColor Green
} else {
    Write-Host "  ℹ Frontend not running" -ForegroundColor Gray
}

Start-Sleep -Seconds 2

# Start frontend
Write-Host ""
Write-Host "Starting frontend..." -ForegroundColor Green
$frontendDir = Join-Path $PSScriptRoot "frontend"
if (Test-Path $frontendDir) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendDir'; `$env:AVATAR_SERVICE_URL='$env:AVATAR_SERVICE_URL'; npm start" -WindowStyle Minimized
    Write-Host "  ✓ Frontend starting on port 3000" -ForegroundColor Green
} else {
    Write-Host "  ✗ Frontend directory not found" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Find and stop backend Django server
Write-Host ""
Write-Host "Stopping backend..." -ForegroundColor Yellow
$backend = Get-Process | Where-Object {$_.CommandLine -like "*manage.py*" -or $_.CommandLine -like "*runserver*"} | Select-Object -First 1
if ($backend) {
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Stopped backend (PID: $($backend.Id))" -ForegroundColor Green
} else {
    Write-Host "  ℹ Backend not running" -ForegroundColor Gray
}

Start-Sleep -Seconds 2

# Start backend
Write-Host ""
Write-Host "Starting backend..." -ForegroundColor Green
$backendDir = Join-Path $PSScriptRoot "backend"
if (Test-Path $backendDir) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; `$env:AVATAR_SERVICE_URL='$env:AVATAR_SERVICE_URL'; python manage.py runserver 0.0.0.0:8001" -WindowStyle Minimized
    Write-Host "  ✓ Backend starting on port 8001" -ForegroundColor Green
} else {
    Write-Host "  ✗ Backend directory not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "✅ RESTART COMPLETE!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host ""
Write-Host "Servers are restarting..." -ForegroundColor Cyan
Write-Host "Wait 10-15 seconds, then test at: http://localhost:3000/" -ForegroundColor Yellow
Write-Host ""
Write-Host "Note: Avatar service (port 8000) was not restarted" -ForegroundColor Gray
Write-Host ""

