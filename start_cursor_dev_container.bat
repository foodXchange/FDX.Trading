@echo off
echo ========================================
echo FoodXchange Dev Container in Cursor
echo ========================================

echo.
echo This will help you start the FoodXchange development container in Cursor.
echo.
echo Prerequisites:
echo 1. Docker Desktop must be running
echo 2. Cursor must be installed
echo.
echo Steps:
echo 1. Open Cursor
echo 2. Open this project folder: %cd%
echo 3. Press Ctrl+Shift+P (or F1)
echo 4. Type "Dev Containers: Reopen in Container"
echo 5. Press Enter
echo.
echo The container will build and open automatically in Cursor.
echo.
echo Once inside the container, you can:
echo - Use Cursor's integrated terminal to run:
echo   python -m uvicorn foodxchange.main:app --host 0.0.0.0 --port 9000 --reload
echo.
echo - Or use the provided script:
echo   ./start_server_9000.sh
echo.
echo - Access the app at: http://localhost:9000
echo.
echo Cursor Benefits:
echo - AI code completion works with container environment
echo - Integrated terminal runs inside container
echo - Debugging works seamlessly
echo - All extensions pre-configured
echo.
pause 