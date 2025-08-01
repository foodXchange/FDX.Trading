@echo off
echo ========================================
echo FoodXchange Development Server
echo ========================================

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "foodxchange-env\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv foodxchange-env
    echo Then run: foodxchange-env\Scripts\activate
    echo Then run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Use virtual environment Python directly
echo Using virtual environment Python...
set PYTHON_EXE=foodxchange-env\Scripts\python.exe

REM Set environment variables
set PYTHONPATH=%cd%

echo Starting development server...
echo Usage options:
echo   %PYTHON_EXE% dev_server.py              - Start FastAPI server on port 9000
echo   %PYTHON_EXE% dev_server.py --flask       - Start Flask server on port 9000
echo   %PYTHON_EXE% dev_server.py --port 8000   - Start on different port
echo   %PYTHON_EXE% dev_server.py --no-reload   - Disable auto-reload
echo.

%PYTHON_EXE% dev_server.py %*

pause 