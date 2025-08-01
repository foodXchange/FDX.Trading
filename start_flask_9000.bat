@echo off
echo ========================================
echo Starting FoodXchange Flask Dev Server (Port 9000)
echo ========================================

cd /d "%~dp0"
echo Current directory: %cd%

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

REM Check if Flask is installed
%PYTHON_EXE% -c "import flask" 2>nul
if errorlevel 1 (
    echo Installing Flask...
    %PYTHON_EXE% -m pip install flask flask-mail flask-wtf
)

REM Set environment variables for development
set FLASK_ENV=development
set FLASK_DEBUG=1
set PORT=9000
set PYTHONPATH=%cd%

echo Starting Flask server with auto-reload on port 9000...
echo Server will be available at: http://localhost:9000
echo Press Ctrl+C to stop the server
echo.

%PYTHON_EXE% app.py

pause 