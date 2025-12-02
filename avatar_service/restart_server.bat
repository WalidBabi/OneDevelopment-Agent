@echo off
echo Stopping any existing avatar server...
taskkill /F /FI "WINDOWTITLE eq Luna Avatar*" /T 2>nul
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *avatar_server*" /T 2>nul
timeout /t 2 /nobreak >nul

echo Starting avatar server...
cd /d "%~dp0"
call venv\Scripts\activate.bat
set PATH=%PATH%;C:\Users\Walid\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin
python avatar_server_working.py

