@echo off
echo Starting FoodXchange Server...
cd /d "%~dp0"
set PYTHONPATH=%cd%
python start_server_fixed.py
pause