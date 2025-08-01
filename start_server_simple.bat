@echo off
echo ========================================
echo Starting FoodXchange Dev Server (Port 9000)
echo ========================================

cd /d "%~dp0"
echo Current directory: %cd%

REM Set environment variables for development
set FLASK_ENV=development
set FLASK_DEBUG=1
set PYTHONPATH=%cd%

echo Starting server with auto-reload on port 9000...
echo Server will be available at: http://localhost:9000
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn foodxchange.main:app --host 0.0.0.0 --port 9000 --reload --log-level info

pause