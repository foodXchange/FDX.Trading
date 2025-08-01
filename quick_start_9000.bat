@echo off
echo ========================================
echo FoodXchange Quick Start (Port 9000)
echo ========================================

cd /d "%~dp0"

REM Use virtual environment Python directly
if exist "foodxchange-env\Scripts\python.exe" (
    echo Using existing virtual environment...
    set PYTHON_EXE=foodxchange-env\Scripts\python.exe
) else (
    echo Creating virtual environment...
    python -m venv foodxchange-env
    set PYTHON_EXE=foodxchange-env\Scripts\python.exe
    echo Installing dependencies...
    %PYTHON_EXE% -m pip install -r requirements.txt
)

REM Set environment variables
set FLASK_ENV=development
set FLASK_DEBUG=1
set PORT=9000
set PYTHONPATH=%cd%

echo Starting FastAPI server on port 9000 with auto-reload...
echo Server will be available at: http://localhost:9000
echo Press Ctrl+C to stop the server
echo.

%PYTHON_EXE% -m uvicorn foodxchange.main:app --host 0.0.0.0 --port 9000 --reload --log-level info

pause 