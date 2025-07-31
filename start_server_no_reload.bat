@echo off
echo Starting FoodXchange Server (No Auto-Reload)...
cd /d "%~dp0"
set PYTHONPATH=%cd%
python -m uvicorn foodxchange.main:app --host 0.0.0.0 --port 8003 --reload=False
pause