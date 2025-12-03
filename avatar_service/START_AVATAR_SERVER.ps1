# 🚀 Start Luna Avatar Server
# This will start the server so you can talk to Luna!

Write-Host "=" -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "🚀 Starting Luna Avatar Server" -ForegroundColor Green
Write-Host "=" -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "avatar_server_final.py")) {
    Write-Host "❌ Error: avatar_server_final.py not found!" -ForegroundColor Red
    Write-Host "   Please run this script from the avatar_service directory" -ForegroundColor Yellow
    exit 1
}

# Check if luna_base.png exists
if (-not (Test-Path "luna_base.png")) {
    Write-Host "❌ Error: luna_base.png not found!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Avatar server found" -ForegroundColor Green
Write-Host "✓ Luna base image found" -ForegroundColor Green
Write-Host ""

Write-Host "Starting server on http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Once started, you can:" -ForegroundColor Yellow
Write-Host "  1. Test: http://localhost:8000/" -ForegroundColor White
Write-Host "  2. Generate video: POST http://localhost:8000/generate" -ForegroundColor White
Write-Host "  3. Health check: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
python avatar_server_final.py

