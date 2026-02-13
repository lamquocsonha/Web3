@echo off
title Unilab - Running on port 7000

REM Kill any existing Python processes using port 7000
echo 🔍 Checking for existing processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
timeout /t 1 /nobreak >nul

if not exist venv (
    echo [ERROR] Run install.bat first!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo ==========================================
echo   UNILAB - Server running
echo.
echo   Admin:   http://localhost:7000/admin
echo   Car:     http://localhost:7000/car
echo.
echo   Press Ctrl+C to stop
echo ==========================================
echo.

start http://localhost:7000/admin
python app.py

REM Pause if app exits with error
if errorlevel 1 pause
