@echo off
echo ========================================
echo Starting FoodXchange Server
echo ========================================
echo.

REM Kill any existing Python processes on our ports
echo Cleaning up old processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8003') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8004') do taskkill /PID %%a /F 2>nul

echo.
echo Starting server on http://localhost:8003
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

cd /d C:\Users\foodz\Desktop\FoodXchange
python -m uvicorn foodxchange.main:app --reload --port 8003 --host 127.0.0.1