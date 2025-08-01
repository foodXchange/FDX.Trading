@echo off
echo Restarting FoodXchange Server on Port 9000...
echo.

REM Kill any existing Python processes on port 9000
echo Stopping existing server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :9000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)

timeout /t 2 /nobreak >nul

REM Activate virtual environment
echo Activating virtual environment...
call foodxchange-env\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install fastapi uvicorn[standard] jinja2 python-multipart python-dotenv

REM Set Python path
set PYTHONPATH=%cd%

echo Starting server...
python -m uvicorn foodxchange.main:app --host 0.0.0.0 --port 9000 --reload

pause