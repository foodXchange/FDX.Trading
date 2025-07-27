@echo off
echo === Simple Azure Deployment ===
echo.

REM Check if Azure CLI is installed
az version >nul 2>&1
if errorlevel 1 (
    echo Azure CLI not found. Please install it first:
    echo https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
    pause
    exit /b 1
)

REM Check if logged in
az account show >nul 2>&1
if errorlevel 1 (
    echo Not logged in to Azure. Please run 'az login' first
    pause
    exit /b 1
)

echo Azure CLI found and logged in!
echo.

REM Get deployment info
set /p resourceGroup="Enter your Azure resource group name (e.g., foodxchange-rg): "
set /p appName="Enter your Azure Web App name (e.g., foodxchange-app): "

echo.
echo === Installing Dependencies ===
pip install -r requirements.txt

echo.
echo === Deploying to Azure ===
echo Deploying to %appName%...

REM Deploy using Azure CLI
az webapp deployment source config-zip --resource-group %resourceGroup% --name %appName% --src .

echo.
echo === Deployment Complete! ===
echo Your app should be available at: https://%appName%.azurewebsites.net

echo.
set /p restart="Do you want to restart the app? (y/n): "
if /i "%restart%"=="y" (
    echo Restarting app...
    az webapp restart --name %appName% --resource-group %resourceGroup%
    echo App restarted!
)

echo.
echo Deployment complete! 🎉
pause 