@echo off
echo ========================================
echo FoodXchange Dev Container Setup
echo ========================================

echo.
echo This will help you start the FoodXchange development container.
echo.
echo Prerequisites:
echo 1. Docker Desktop must be running
echo 2. VS Code with Dev Containers extension installed
echo.
echo Steps:
echo 1. Open VS Code
echo 2. Press F1 or Ctrl+Shift+P
echo 3. Type "Dev Containers: Reopen in Container"
echo 4. Press Enter
echo.
echo The container will build and open automatically.
echo.
echo Once inside the container, you can start the server with:
echo   python -m uvicorn foodxchange.main:app --host 0.0.0.0 --port 9000 --reload
echo.
echo Or use the provided scripts:
echo   ./start_server_9000.sh
echo.
pause 