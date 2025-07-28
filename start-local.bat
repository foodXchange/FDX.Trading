@echo off
echo Starting FoodXchange Local Development Server
echo ================================================
echo.
echo Loading local environment...
set ENV_FILE=.env.local
echo.
echo Starting server with auto-reload...
python -m uvicorn foodxchange.main:app --reload --host 0.0.0.0 --port 8000
pause
