# Set AVATAR_SERVICE_URL Environment Variable
# This connects the backend to the avatar service via ngrok

$ngrok_url = "https://5d812f2e82fa.ngrok-free.app"

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "🔗 Setting Avatar Service URL" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Set for current session
$env:AVATAR_SERVICE_URL = $ngrok_url
Write-Host "✅ Set AVATAR_SERVICE_URL for current session" -ForegroundColor Green
Write-Host "   Value: $ngrok_url" -ForegroundColor Yellow
Write-Host ""

# Also set permanently for user
[Environment]::SetEnvironmentVariable("AVATAR_SERVICE_URL", $ngrok_url, "User")
Write-Host "✅ Set AVATAR_SERVICE_URL permanently (User level)" -ForegroundColor Green
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Restart backend server (if running)" -ForegroundColor White
Write-Host "  2. Test: http://13.62.188.127:3000/" -ForegroundColor White
Write-Host "  3. Ask Luna a question - avatar should respond!" -ForegroundColor White
Write-Host ""

Write-Host "To verify:" -ForegroundColor Yellow
Write-Host '  python -c "import os; print(os.getenv(\"AVATAR_SERVICE_URL\"))"' -ForegroundColor Gray
Write-Host ""

