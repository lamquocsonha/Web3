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

REM --- Detect Python command ---
set PYTHON_CMD=
where python >nul 2>&1 && set PYTHON_CMD=python&& goto :run_server
where python3 >nul 2>&1 && set PYTHON_CMD=python3&& goto :run_server
where py >nul 2>&1 && set PYTHON_CMD=py&& goto :run_server

REM Scan common install locations
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" set "PYTHON_CMD=%%D\python.exe"&& goto :run_server
)
for /d %%D in ("%ProgramFiles%\Python3*") do (
    if exist "%%D\python.exe" set "PYTHON_CMD=%%D\python.exe"&& goto :run_server
)
if exist "C:\Python313\python.exe" set "PYTHON_CMD=C:\Python313\python.exe"&& goto :run_server
if exist "C:\Python312\python.exe" set "PYTHON_CMD=C:\Python312\python.exe"&& goto :run_server
if exist "C:\Python311\python.exe" set "PYTHON_CMD=C:\Python311\python.exe"&& goto :run_server

echo [ERROR] Python not found! Run install.bat first.
pause
exit /b 1

:run_server
echo ==========================================
echo   UNILAB - Server running
echo.
echo   Admin:   http://localhost:7000/admin
echo   Shop:    http://localhost:7000/shop
echo   Car:     http://localhost:7000/car
echo   Travel:  http://localhost:7000/travel
echo.
echo   Press Ctrl+C to stop
echo ==========================================
echo.

"%PYTHON_CMD%" app.py

REM Pause if app exits with error
if errorlevel 1 (
    echo.
    echo [ERROR] Server exited with an error!
    pause
)
