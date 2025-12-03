# Wait and Monitor for Wav2Lip Model Download
$model_path = "C:\Users\Walid\Downloads\Wav2Lip\checkpoints\wav2lip_gan.pth"
$checkpoints_dir = "C:\Users\Walid\Downloads\Wav2Lip\checkpoints"

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "📥 Monitoring Wav2Lip Model Download" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "Waiting for file to appear at:" -ForegroundColor Yellow
Write-Host "  $model_path" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Gray
Write-Host ""

# Create directory if needed
if (-not (Test-Path $checkpoints_dir)) {
    New-Item -ItemType Directory -Path $checkpoints_dir -Force | Out-Null
    Write-Host "Created checkpoints directory" -ForegroundColor Green
}

$last_size = 0
$check_count = 0

while ($true) {
    $check_count++
    
    if (Test-Path $model_path) {
        $current_size = (Get-Item $model_path).Length / 1MB
        $size_mb = [math]::Round($current_size, 2)
        
        if ($current_size -ne $last_size) {
            Write-Host "[$check_count] File found! Size: $size_mb MB" -ForegroundColor Yellow
            
            if ($current_size -gt 100) {
                Write-Host ""
                Write-Host "=" * 70 -ForegroundColor Green
                Write-Host "✅ DOWNLOAD COMPLETE!" -ForegroundColor Green
                Write-Host "=" * 70 -ForegroundColor Green
                Write-Host ""
                Write-Host "File: $model_path" -ForegroundColor White
                Write-Host "Size: $size_mb MB" -ForegroundColor Green
                Write-Host ""
                Write-Host "Wav2Lip is ready for 8-12 second generation! ⚡" -ForegroundColor Green
                Write-Host ""
                Write-Host "Next: Restart avatar server to use Wav2Lip!" -ForegroundColor Cyan
                break
            } else {
                Write-Host "  ⚠️  File too small, still downloading..." -ForegroundColor Yellow
            }
            
            $last_size = $current_size
        } else {
            # File size hasn't changed - might be complete or stuck
            if ($current_size -gt 100) {
                Write-Host ""
                Write-Host "=" * 70 -ForegroundColor Green
                Write-Host "✅ DOWNLOAD COMPLETE!" -ForegroundColor Green
                Write-Host "=" * 70 -ForegroundColor Green
                Write-Host ""
                Write-Host "File: $model_path" -ForegroundColor White
                Write-Host "Size: $size_mb MB" -ForegroundColor Green
                Write-Host ""
                Write-Host "Wav2Lip is ready!" -ForegroundColor Green
                break
            }
        }
    } else {
        if ($check_count -eq 1 -or $check_count % 10 -eq 0) {
            Write-Host "[$check_count] Waiting for file..." -ForegroundColor Gray
        }
    }
    
    Start-Sleep -Seconds 2
}

