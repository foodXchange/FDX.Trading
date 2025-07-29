@echo off
echo Starting FoodXchange Server...
echo Server will be available at: http://localhost:8080
echo Admin access: http://localhost:8080/admin
echo.
py -m uvicorn test_server:app --host 127.0.0.1 --port 8080 --reload
pause