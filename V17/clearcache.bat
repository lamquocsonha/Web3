@echo off
echo ======================================
echo   CLEAR PYTHON CACHE
echo ======================================
echo.

echo [1/3] Clearing __pycache__ directories...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo Done!

echo.
echo [2/3] Clearing .pyc files...
del /s /q *.pyc 2>nul
echo Done!

echo.
echo [3/3] Clearing .pyo files...
del /s /q *.pyo 2>nul
echo Done!

echo.
echo ======================================
echo   CACHE CLEARED SUCCESSFULLY!
echo ======================================
echo.
echo Next steps:
echo 1. Restart Flask server (Ctrl+C then run.bat)
echo 2. Hard refresh browser (Ctrl+Shift+R)
echo.
pause
