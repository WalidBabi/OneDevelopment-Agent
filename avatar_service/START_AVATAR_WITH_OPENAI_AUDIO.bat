@echo off
REM ===================================================================
REM Start Luna Avatar Service with OpenAI TTS Audio Support
REM ===================================================================
REM This script starts the avatar service that will:
REM 1. Listen for requests from the AWS backend
REM 2. Download OpenAI TTS audio (high quality voice)
REM 3. Generate videos with SadTalker
REM 4. Serve videos back to the frontend
REM ===================================================================

color 0B
echo ============================================================
echo   Luna Avatar Service - Starting with OpenAI TTS Support
echo ============================================================
echo.

REM Check if running in correct directory
if not exist "avatar_server_simple.py" (
    color 0C
    echo ERROR: Please run this script from the avatar_service directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo   X Python not found
    pause
    exit /b 1
)
python --version
echo   OK - Python found
echo.

REM Check GPU
echo [2/5] Checking GPU...
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    nvidia-smi --query-gpu=name --format=csv,noheader
    echo   OK - GPU Found
) else (
    echo   WARNING - No NVIDIA GPU detected, will use CPU (slow)
)
echo.

REM Check SadTalker
echo [3/5] Checking SadTalker...
set SADTALKER_PATH=C:\Users\Walid\Downloads\SadTalker
if exist "%SADTALKER_PATH%" (
    echo   OK - SadTalker found at: %SADTALKER_PATH%
) else (
    color 0E
    echo   WARNING - SadTalker not found at: %SADTALKER_PATH%
    echo   Please update the path in sadtalker_generator.py
)
echo.

REM Check Luna base image
echo [4/5] Checking Luna base image...
if exist "luna_base.png" (
    echo   OK - Luna image found
) else (
    color 0C
    echo   ERROR - luna_base.png not found!
    echo   Please add a photorealistic image of Luna
)
echo.

REM Install/update dependencies
echo [5/5] Checking dependencies...
echo   Installing/updating required packages...
python -m pip install -q fastapi uvicorn torch requests mutagen gtts edge-tts 2>nul
echo   OK - Dependencies ready
echo.

REM Start the server
color 0B
echo ============================================================
echo   Starting Avatar Service...
echo ============================================================
echo.
echo The service will:
echo   * Accept requests from the AWS backend
echo   * Download OpenAI TTS audio (shimmer voice)
echo   * Generate talking avatar videos with SadTalker
echo   * Serve videos back to the frontend
echo.
color 0E
echo IMPORTANT: Keep ngrok running in another terminal!
echo IMPORTANT: Make sure AVATAR_SERVICE_URL is set in backend .env
echo.
color 0B
echo Press Ctrl+C to stop the service
echo.

REM Start the avatar server
REM You can change this to avatar_server_sadtalker.py if that's what you're using
python avatar_server_simple.py

REM If the script exits
echo.
color 0E
echo Avatar service stopped.
pause

