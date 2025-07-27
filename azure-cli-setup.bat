@echo off
echo 🚀 Azure CLI Local Setup for FoodXchange
echo ======================================

REM Check if Azure CLI is installed
az --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Azure CLI not found. Installing...
    echo Please download and install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
    echo After installation, restart this script.
    pause
    exit /b 1
)

echo ✅ Azure CLI found

REM Check if logged in
echo Checking login status...
az account show >nul 2>&1
if errorlevel 1 (
    echo 🔐 Not logged in. Starting login process...
    az login
) else (
    echo ✅ Already logged in
)

REM Show current subscription
echo.
echo 📋 Current Azure Subscription:
az account show --query "name" -o tsv

REM Show FoodXchange resources
echo.
echo 🏗️  FoodXchange Resources:
az resource list --resource-group foodxchange-rg --query "[].{Name:name, Type:type, Location:location}" -o table

echo.
echo 🎯 Quick Commands:
echo   - View resources: az resource list --resource-group foodxchange-rg
echo   - View app service: az webapp show --name foodxchange-app --resource-group foodxchange-rg
echo   - View database: az postgres flexible-server show --name foodxchangepgfr --resource-group foodxchange-rg
echo   - Deploy app: az webapp deployment source config-zip --resource-group foodxchange-rg --name foodxchange-app --src app.zip

pause 