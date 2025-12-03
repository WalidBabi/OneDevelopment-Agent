# Force NVIDIA GPU for Avatar Service
# This ensures SadTalker uses the NVIDIA RTX 4050, not Intel integrated GPU

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "🎮 FORCING NVIDIA GPU" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Set environment variables to force NVIDIA GPU
$env:CUDA_VISIBLE_DEVICES = "0"
$env:CUDA_DEVICE_ORDER = "PCI_BUS_ID"
$env:FORCE_CUDA = "1"
$env:TORCH_CUDA_ARCH_LIST = "8.9"

# Disable Intel GPU preference
$env:DISABLE_LAYER_AMD_SWITCHABLE_GRAPHICS_1 = "1"

# Configure FFmpeg for SadTalker (required by pydub)
$ffmpegBin = "C:\Users\Walid\Downloads\SadTalker\ffmpeg\ffmpeg-master-latest-win64-gpl\bin"
if (Test-Path $ffmpegBin) {
    $env:FFMPEG_BINARY = "$ffmpegBin\ffmpeg.exe"
    $env:FFPROBE_BINARY = "$ffmpegBin\ffprobe.exe"
    $env:PATH = "$ffmpegBin;$env:PATH"
    Write-Host "✓ FFmpeg configured" -ForegroundColor Green
} else {
    Write-Host "⚠ Warning: FFmpeg not found. Run setup_ffmpeg.ps1 first!" -ForegroundColor Yellow
}

Write-Host "Environment variables set:" -ForegroundColor Yellow
Write-Host "  CUDA_VISIBLE_DEVICES = 0" -ForegroundColor White
Write-Host "  CUDA_DEVICE_ORDER = PCI_BUS_ID" -ForegroundColor White
Write-Host "  FORCE_CUDA = 1" -ForegroundColor White
Write-Host "  FFMPEG_BINARY = $env:FFMPEG_BINARY" -ForegroundColor White
Write-Host "  FFPROBE_BINARY = $env:FFPROBE_BINARY" -ForegroundColor White
Write-Host ""

# Verify GPU
Write-Host "Verifying NVIDIA GPU..." -ForegroundColor Cyan
nvidia-smi --query-gpu=index,name,utilization.gpu --format=csv

Write-Host ""
Write-Host "Starting Avatar Server with NVIDIA GPU..." -ForegroundColor Green
Write-Host ""

# Start the server
cd C:\Users\Walid\Downloads\OneDevelopment-Agent-main\OneDevelopment-Agent-main\avatar_service
.\venv\Scripts\python.exe avatar_server_simple.py

