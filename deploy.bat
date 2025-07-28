@echo off
echo 🚀 FoodXchange Azure Deployment
echo ================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if Azure CLI is installed
az version >nul 2>&1
if errorlevel 1 (
    echo ❌ Azure CLI is not installed
    echo Please install Azure CLI from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
    pause
    exit /b 1
)

REM Check if logged in to Azure
az account show >nul 2>&1
if errorlevel 1 (
    echo ❌ Not logged in to Azure
    echo Please run: az login
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed
echo.

REM Run the deployment script
python azure_deploy.py

echo.
echo Deployment script completed
pause 