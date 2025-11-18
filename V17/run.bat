@echo off
chcp 65001 > nul
echo ========================================
echo  TRADING DASHBOARD - STARTING
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

echo Starting Flask Server...
echo Dashboard: http://127.0.0.1:5555
echo.

REM Open browser after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5555"

REM Start server
python app.py

pause
