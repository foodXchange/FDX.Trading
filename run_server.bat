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
echo   - Search API: http://localhost:8003/api/search/
echo.
echo Press Ctrl+C to stop the server
echo.

REM Activate virtual environment if it exists
if exist "foodxchange-env\Scripts\activate.bat" (
    call foodxchange-env\Scripts\activate.bat
)

REM Set Python path
set PYTHONPATH=%cd%

REM Start the server using the fixed startup script
python start_server_fixed.py

pause