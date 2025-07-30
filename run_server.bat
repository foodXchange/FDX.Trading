@echo off
echo ========================================
echo FoodXchange AI Product Analysis Server
echo ========================================
echo.
echo Starting server on port 8003...
echo.
echo Available at:
echo   - Main: http://localhost:8003
echo   - AI Analysis: http://localhost:8003/product-analysis/
echo   - Dashboard: http://localhost:8003/dashboard
echo.
echo Press Ctrl+C to stop the server
echo.

python run_server.py

pause