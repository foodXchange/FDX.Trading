@echo off
echo ========================================
echo FoodXchange Production Server
echo ========================================
echo.
echo WARNING: This will start the server in PRODUCTION mode
echo Make sure all environment variables are properly configured
echo.
pause

REM Set production environment
set ENVIRONMENT=production
set DEBUG=False

REM Activate virtual environment
if exist "foodxchange-env\Scripts\activate.bat" (
    call foodxchange-env\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv foodxchange-env
    pause
    exit /b 1
)

REM Check for .env file
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please create .env file with proper configuration
    pause
    exit /b 1
)

REM Set Python path
set PYTHONPATH=%cd%

REM Start server without reload in production
python -c "import uvicorn; uvicorn.run('foodxchange.main:app', host='0.0.0.0', port=8003, reload=False, log_level='warning')"

pause