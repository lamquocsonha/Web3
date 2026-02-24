@echo off
title Unilab - Install

echo ==========================================
echo   UNILAB - Setup
echo ==========================================
echo.

REM --- Detect Python command ---
set PYTHON_CMD=

REM 1) Check PATH first: python, python3, py
where python >nul 2>&1 && (
    set PYTHON_CMD=python
    goto :found_python
)
where python3 >nul 2>&1 && (
    set PYTHON_CMD=python3
    goto :found_python
)
where py >nul 2>&1 && (
    set PYTHON_CMD=py
    goto :found_python
)

REM 2) Scan common install locations (for when PATH is not set)
echo [*] Python not in PATH, scanning common locations...

REM --- AppData Local (default user install) ---
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_CMD=%%D\python.exe"
        goto :found_python
    )
)

REM --- Program Files (system-wide install) ---
for /d %%D in ("%ProgramFiles%\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_CMD=%%D\python.exe"
        goto :found_python
    )
)
for /d %%D in ("%ProgramFiles(x86)%\Python3*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_CMD=%%D\python.exe"
        goto :found_python
    )
)

REM --- WindowsApps (Microsoft Store install) ---
for /f "delims=" %%F in ('dir /b /s "%LOCALAPPDATA%\Microsoft\WindowsApps\python*.exe" 2^>nul') do (
    set "PYTHON_CMD=%%F"
    goto :found_python
)

REM --- Scoop ---
if exist "%USERPROFILE%\scoop\apps\python\current\python.exe" (
    set "PYTHON_CMD=%USERPROFILE%\scoop\apps\python\current\python.exe"
    goto :found_python
)

REM --- Chocolatey ---
if exist "C:\Python313\python.exe" set "PYTHON_CMD=C:\Python313\python.exe" && goto :found_python
if exist "C:\Python312\python.exe" set "PYTHON_CMD=C:\Python312\python.exe" && goto :found_python
if exist "C:\Python311\python.exe" set "PYTHON_CMD=C:\Python311\python.exe" && goto :found_python
if exist "C:\Python310\python.exe" set "PYTHON_CMD=C:\Python310\python.exe" && goto :found_python

echo.
echo [ERROR] Python not found anywhere!
echo.
echo   Please install Python 3.10+ from https://www.python.org/downloads/
echo   IMPORTANT: Check "Add Python to PATH" during installation!
echo.
echo   Or if Python is already installed, add it to PATH manually:
echo     1. Open Settings ^> System ^> About ^> Advanced system settings
echo     2. Click Environment Variables
echo     3. Edit PATH ^> Add your Python folder (e.g. C:\Users\YourName\AppData\Local\Programs\Python\Python313)
echo.
pause
exit /b 1

:found_python
for /f "delims=" %%V in ('"%PYTHON_CMD%" --version 2^>^&1') do set PYTHON_VER=%%V
echo [OK] Found %PYTHON_VER%
echo      Path: %PYTHON_CMD%
echo.

echo [1/4] Creating virtual environment...
if exist venv (
    echo       Already exists, skipping.
) else (
    "%PYTHON_CMD%" -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        echo         Try: "%PYTHON_CMD%" -m pip install --upgrade pip
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
