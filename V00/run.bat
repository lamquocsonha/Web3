@echo off
chcp 65001 >nul 2>&1
title Unilab - Running on port 7000

REM Kill any existing process using port 7000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":7000 " ^| findstr "LISTENING"') do (
    echo [*] Killing PID %%a on port 7000...
    taskkill /F /PID %%a >nul 2>&1
)

if not exist venv (
    echo [ERROR] Run install.bat first!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)

echo ==========================================
echo   UNILAB - Server running
echo.
echo   Admin:   http://localhost:7000/admin
echo   Car:     http://localhost:7000/car
echo   Travel:  http://localhost:7000/travel
echo.
echo   Press Ctrl+C to stop
echo ==========================================
echo.

python app.py

REM Pause if app exits with error
if errorlevel 1 (
    echo.
    echo [ERROR] Server exited with an error!
    pause
)
