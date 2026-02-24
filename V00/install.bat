@echo off
title Unilab - Install

echo ==========================================
echo   UNILAB - Setup
echo ==========================================
echo.

REM --- Detect Python command ---
set PYTHON_CMD=
where python >nul 2>&1 && (
    for /f "delims=" %%V in ('python --version 2^>^&1') do set PYTHON_VER=%%V
    set PYTHON_CMD=python
    goto :found_python
)
where python3 >nul 2>&1 && (
    for /f "delims=" %%V in ('python3 --version 2^>^&1') do set PYTHON_VER=%%V
    set PYTHON_CMD=python3
    goto :found_python
)
where py >nul 2>&1 && (
    for /f "delims=" %%V in ('py --version 2^>^&1') do set PYTHON_VER=%%V
    set PYTHON_CMD=py
    goto :found_python
)

echo [ERROR] Python not found!
echo.
echo   Please install Python 3.10+ from https://www.python.org/downloads/
echo   IMPORTANT: Check "Add Python to PATH" during installation!
echo.
pause
exit /b 1

:found_python
echo [OK] Found %PYTHON_VER% (%PYTHON_CMD%)
echo.

echo [1/4] Creating virtual environment...
if exist venv (
    echo       Already exists, skipping.
) else (
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        echo         Try: %PYTHON_CMD% -m pip install --upgrade pip
        pause
        exit /b 1
    )
    echo       Done!
)

echo [2/4] Activating venv...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)

echo [3/4] Installing packages...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [WARNING] Some packages may have failed to install.
    echo          Check requirements.txt for compatibility.
)

echo [4/4] Complete!
echo.
echo ==========================================
echo   Setup OK!
echo.
echo   Run project:  run.bat
echo.
echo   Admin:   http://localhost:7000/admin
echo   Shop:    http://localhost:7000/shop
echo   Car:     http://localhost:7000/car
echo   Travel:  http://localhost:7000/travel
echo ==========================================
pause
