# Set AVATAR_SERVICE_URL Environment Variable
# This connects the backend to the avatar service via ngrok
#
# SECURITY WARNING: Never hardcode ngrok URLs in scripts or commit them to version control!
# ngrok URLs are publicly accessible and should be treated as secrets.

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "🔗 Setting Avatar Service URL" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Prompt user for their ngrok URL
Write-Host "⚠️  SECURITY NOTICE:" -ForegroundColor Yellow
Write-Host "   ngrok URLs should NEVER be hardcoded or committed to version control!" -ForegroundColor Yellow
Write-Host "   They are publicly accessible and should be treated as secrets." -ForegroundColor Yellow
Write-Host ""

$ngrok_url = Read-Host "Enter your ngrok URL (e.g., https://abc123.ngrok-free.app)"

if ([string]::IsNullOrWhiteSpace($ngrok_url)) {
    Write-Host "❌ Error: No URL provided!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To get your ngrok URL:" -ForegroundColor Yellow
    Write-Host "  1. Start ngrok: ngrok http 8000" -ForegroundColor White
    Write-Host "  2. Copy the HTTPS forwarding URL" -ForegroundColor White
    Write-Host "  3. Run this script again with that URL" -ForegroundColor White
    exit 1
}

# Validate URL format
if ($ngrok_url -notmatch "^https://.*\.ngrok.*\.app$") {
    Write-Host "⚠️  Warning: URL doesn't look like a valid ngrok URL" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Host "Cancelled." -ForegroundColor Gray
        exit 0
    }
}

Write-Host ""
Write-Host "Setting AVATAR_SERVICE_URL..." -ForegroundColor Cyan

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
Write-Host "  2. Test: http://localhost:3000/ (or your frontend URL)" -ForegroundColor White
Write-Host "  3. Ask Luna a question - avatar should respond!" -ForegroundColor White
Write-Host ""

Write-Host "To verify:" -ForegroundColor Yellow
Write-Host '  echo $env:AVATAR_SERVICE_URL' -ForegroundColor Gray
Write-Host ""

