@echo off
REM Startup script for Agentic Honeypot System
echo ============================================================
echo   Agentic Honeypot for Scam Detection System
echo ============================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/3] Checking Python installation...
python --version
echo.

REM Install dependencies
echo [2/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

REM Run the application
echo [3/3] Starting the application...
echo.
echo API will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
