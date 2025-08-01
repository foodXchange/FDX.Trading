@echo off
echo ========================================
echo Starting FoodXchange Dev Server (Port 9000)
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

REM Check if uvicorn is installed
%PYTHON_EXE% -c "import uvicorn" 2>nul
if errorlevel 1 (
    echo Installing uvicorn...
    %PYTHON_EXE% -m pip install uvicorn[standard]
)

REM Set environment variables for development
set FLASK_ENV=development
set FLASK_DEBUG=1
set PYTHONPATH=%cd%

echo Starting server with auto-reload on port 9000...
echo Server will be available at: http://localhost:9000
echo Press Ctrl+C to stop the server
echo.

%PYTHON_EXE% -m uvicorn foodxchange.main:app --host 0.0.0.0 --port 9000 --reload --log-level info

pause