@echo off
echo ========================================
echo   Automated Azure Deployment
echo ========================================
echo.
echo This will deploy the fixed FoodXchange app to Azure
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.12 or later
    pause
    exit /b 1
)

REM Check if Azure CLI is available
az --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Azure CLI not found in PATH
    echo The script will try to use the full path to Azure CLI
    echo.
)

echo Starting automated deployment...
echo.

REM Run the deployment script
python deploy_to_azure_automated.py

echo.
echo Deployment script completed.
pause 