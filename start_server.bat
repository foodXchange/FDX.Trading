@echo off
echo Starting FoodXchange Server...
cd /d "%~dp0"
set PYTHONPATH=%cd%
cd foodxchange
"C:\Users\foodz\AppData\Local\Programs\Python\Python312\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8003
pause