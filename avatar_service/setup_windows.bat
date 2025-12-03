@echo off
REM Luna Avatar Service - Windows Setup Script
REM Run this on your RTX 4050 laptop

echo ========================================
echo Luna Avatar Service Setup
echo ========================================
echo.

REM Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10 or later from python.org
    pause
    exit /b 1
)
python --version
echo.

REM Check CUDA
echo [2/6] Checking CUDA installation...
nvcc --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: CUDA not found!
    echo Please install CUDA Toolkit from NVIDIA website
    echo You can continue, but GPU won't work.
    pause
)
echo.

REM Create virtual environment
echo [3/6] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo Virtual environment created!
)
echo.

REM Activate and install dependencies
echo [4/6] Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
echo.

REM Check PyTorch CUDA
echo [5/6] Checking PyTorch CUDA support...
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A')" 2>nul
if errorlevel 1 (
    echo PyTorch not installed or has issues.
    echo.
    echo Please install PyTorch with CUDA support:
    echo Visit: https://pytorch.org/get-started/locally/
    echo.
    echo For CUDA 11.8:
    echo pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    echo.
    echo For CUDA 12.1:
    echo pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    pause
)
echo.

REM Check GPU
echo [6/6] Checking GPU...
python -c "import torch; print('GPU Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU detected'); print('GPU Memory:', round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2), 'GB' if torch.cuda.is_available() else '')"
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Add your photorealistic Luna image as: luna_base.png
echo 2. Run: python avatar_server.py
echo 3. In another terminal, run: ngrok http 8000
echo.
pause







