@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   Business Registration Cert to Excel  -  Setup
echo ============================================================
echo.

REM --- 1. Check Python ---
python --version >nul 2>&1
if errorlevel 1 goto NOPYTHON
echo [OK] Python found
python --version

REM --- 2. Create virtual environment ---
if not exist ".venv" (
    echo.
    echo [STEP] Creating virtual environment .venv ...
    python -m venv .venv
)

REM --- 3. Install packages ---
echo.
echo [STEP] Installing Python packages - first time may take a few minutes...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto PIPFAIL
echo [OK] Packages installed

REM --- 4. Prepare .env ---
if not exist ".env" copy ".env.example" ".env" >nul

echo.
echo ============================================================
echo   Setup complete!
echo   Now double-click run.bat, then enter the proxy URL and API key
echo   in the left sidebar of the app.
echo ============================================================
pause
exit /b 0

:NOPYTHON
echo [ERROR] Python is not installed.
echo         Install from https://www.python.org/downloads/
echo         Check "Add Python to PATH" during install.
pause
exit /b 1

:PIPFAIL
echo [ERROR] Package install failed. Check your internet connection.
pause
exit /b 1
