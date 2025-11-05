@echo off
echo ====================================
echo FreshConnect - Starting Application
echo ====================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet
echo.

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please create .env file and add your GEMINI_API_KEY
    echo.
    echo Copy .env.example to .env and edit it:
    echo   copy .env.example .env
    echo.
    pause
    exit /b 1
)

REM Check if database exists
if not exist "marketplace.db" (
    echo Database not found. Initializing...
    python seed_data.py
    echo.
)

REM Start the application
echo Starting FreshConnect...
echo.
echo Open your browser at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ====================================
echo.
python run.py

pause
