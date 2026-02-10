@echo off
title Unilab - Install

echo ==========================================
echo   UNILAB - Setup
echo ==========================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.10+ from python.org
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
if exist venv (
    echo       Already exists, skipping.
) else (
    python -m venv venv
    echo       Done!
)

echo [2/4] Activating venv...
call venv\Scripts\activate.bat

echo [3/4] Installing packages...
pip install -r requirements.txt -q

echo [4/4] Complete!
echo.
echo ==========================================
echo   Setup OK!
echo.
echo   Run project:  run.bat
echo.
echo   Admin:   http://localhost:7000/admin
echo   UniCar:  http://localhost:7000/car
echo ==========================================
pause
