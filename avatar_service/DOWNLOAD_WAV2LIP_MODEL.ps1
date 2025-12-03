# 📥 Download Wav2Lip Model - Automated Script
# This script downloads the Wav2Lip model for 8-12 second generation

Write-Host "=" -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "📥 Wav2Lip Model Download" -ForegroundColor Green
Write-Host "=" -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

$checkpoints_dir = "C:\Users\Walid\Downloads\Wav2Lip\checkpoints"
$model_path = "$checkpoints_dir\wav2lip_gan.pth"

# Create directory if needed
if (-not (Test-Path $checkpoints_dir)) {
    Write-Host "Creating checkpoints directory..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $checkpoints_dir -Force | Out-Null
}

# Check if model already exists
if (Test-Path $model_path) {
    $size = (Get-Item $model_path).Length / 1MB
    if ($size -gt 100) {
        Write-Host "✓ Model already exists: $([math]::Round($size, 2)) MB" -ForegroundColor Green
        Write-Host ""
        Write-Host "Model is ready! You can use Wav2Lip now." -ForegroundColor Green
        exit 0
    } else {
        Write-Host "⚠️  Model file exists but is too small: $([math]::Round($size, 2)) MB" -ForegroundColor Yellow
        Write-Host "   Deleting and re-downloading..." -ForegroundColor Yellow
        Remove-Item $model_path -Force
    }
}

Write-Host "Model file: $model_path" -ForegroundColor Cyan
Write-Host "Size: ~400 MB" -ForegroundColor Cyan
Write-Host ""

Write-Host "Download Options:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Option 1: Manual Download (Recommended - Most Reliable)" -ForegroundColor Green
Write-Host "  1. Open browser and go to:" -ForegroundColor White
Write-Host "     https://github.com/Rudrabha/Wav2Lip/releases" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Download: wav2lip_gan.pth (~400MB)" -ForegroundColor White
Write-Host ""
Write-Host "  3. Save to: $model_path" -ForegroundColor Yellow
Write-Host ""

Write-Host "Option 2: Try Automated Download" -ForegroundColor Green
Write-Host "  Attempting to download using Python..." -ForegroundColor White
Write-Host ""

# Try downloading with Python requests
$download_script = @"
import requests
import os
from pathlib import Path

url = 'https://github.com/Rudrabha/Wav2Lip/releases/download/v0.0.1/wav2lip_gan.pth'
output_path = r'$model_path'

print(f'Downloading Wav2Lip model (~400MB)...')
print(f'This may take 5-10 minutes depending on your internet speed.')
print(f'')

try:
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f'\rProgress: {percent:.1f}% ({downloaded / 1024 / 1024:.1f} MB / {total_size / 1024 / 1024:.1f} MB)', end='')
    
    print(f'\n')
    print(f'✓ Download complete!')
    print(f'  File: {output_path}')
    print(f'  Size: {downloaded / 1024 / 1024:.2f} MB')
except Exception as e:
    print(f'\n❌ Download failed: {e}')
    print(f'')
    print(f'Please download manually from:')
    print(f'  https://github.com/Rudrabha/Wav2Lip/releases')
    print(f'')
    print(f'Save to: {output_path}')
"@

try {
    python -c $download_script
    
    if (Test-Path $model_path) {
        $size = (Get-Item $model_path).Length / 1MB
        if ($size -gt 100) {
            Write-Host ""
            Write-Host ("=" * 70) -ForegroundColor Green
            Write-Host "✅ SUCCESS! Model downloaded!" -ForegroundColor Green
            Write-Host ("=" * 70) -ForegroundColor Green
            Write-Host ""
            Write-Host "Model ready: $model_path" -ForegroundColor Green
            Write-Host "Size: $([math]::Round($size, 2)) MB" -ForegroundColor Green
            Write-Host ""
            Write-Host "Wav2Lip is now ready for 8-12 second generation! ⚡" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "⚠️  Download completed but file seems too small" -ForegroundColor Yellow
            Write-Host "   Please try manual download" -ForegroundColor Yellow
        }
    } else {
        Write-Host ""
        Write-Host "⚠️  Download failed - please use manual download" -ForegroundColor Yellow
    }
} catch {
    Write-Host ""
    Write-Host "⚠️  Automated download not available" -ForegroundColor Yellow
    Write-Host "   Please use manual download (Option 1)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "After downloading, restart the avatar server to use Wav2Lip!" -ForegroundColor Cyan

