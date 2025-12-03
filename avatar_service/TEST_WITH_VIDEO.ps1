# Test Avatar Server with Video Generation
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Testing Luna Avatar with Video Generation" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Sending request to generate avatar..." -ForegroundColor Yellow
Write-Host "This will:" -ForegroundColor Cyan
Write-Host "  1. Generate high-quality audio (2-3 seconds)" -ForegroundColor White
Write-Host "  2. Generate video with SadTalker (30-40 seconds)" -ForegroundColor White
Write-Host "  3. Return video URL" -ForegroundColor White
Write-Host ""

$json = '{"text":"Hello! I am Luna, your AI assistant from One Development. I can help you find your perfect property!","voice_id":"default"}'

Write-Host "Requesting generation..." -ForegroundColor Yellow
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/generate" -Method Post -Body $json -ContentType "application/json"
    
    $stopwatch.Stop()
    $elapsed = [math]::Round($stopwatch.Elapsed.TotalSeconds, 1)
    
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "RESPONSE RECEIVED!" -ForegroundColor Green
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Total time: $elapsed seconds" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Status: $($response.status)" -ForegroundColor $(if($response.status -eq 'video_ready'){'Green'}else{'Yellow'})
    Write-Host "Quality: $($response.quality)" -ForegroundColor Cyan
    
    if ($response.generation_time) {
        Write-Host "Video generation: $($response.generation_time) seconds" -ForegroundColor Cyan
    }
    
    Write-Host ""
    Write-Host "Audio URL: $($response.audio_url)" -ForegroundColor White
    
    if ($response.video_url) {
        Write-Host "Video URL: $($response.video_url)" -ForegroundColor Green
        Write-Host ""
        Write-Host "======================================================================" -ForegroundColor Green
        Write-Host "SUCCESS! Video generated!" -ForegroundColor Green
        Write-Host "======================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Opening video..." -ForegroundColor Cyan
        
        # Extract video ID from URL
        $videoId = $response.video_id
        $videoPath = "generated_videos/$videoId.mp4"
        
        if (Test-Path $videoPath) {
            Start-Process $videoPath
        } else {
            Write-Host "Playing from URL..." -ForegroundColor Yellow
            Start-Process $response.video_url
        }
    } else {
        Write-Host "Video URL: (not generated)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Message: $($response.message)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Playing audio only..." -ForegroundColor Cyan
        Start-Process $response.audio_url
    }
    
} catch {
    $stopwatch.Stop()
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Red
    Write-Host "ERROR" -ForegroundColor Red
    Write-Host "======================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host ""

