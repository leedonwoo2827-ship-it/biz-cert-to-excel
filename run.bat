@echo off
setlocal
cd /d "%~dp0"

REM --- Check virtual environment ---
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Not set up yet. Please run setup.bat first.
    pause
    exit /b 1
)

echo ============================================================
echo   Tax Invoice to Excel  -  starting...
echo   Your browser will open automatically.
echo   If not, copy the Local URL shown below into your browser.
echo ============================================================
echo.

".venv\Scripts\python.exe" -m streamlit run app.py

pause
