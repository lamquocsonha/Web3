@echo off
title Unilab - Running on port 7000

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
echo   UniCar:  http://localhost:7000/car
echo.
echo   Press Ctrl+C to stop
echo ==========================================
echo.

start http://localhost:7000/admin
python app.py
