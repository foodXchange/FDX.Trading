@echo off
echo 🚀 One-Click Azure Deployment
echo.

REM Hardcoded values - change these to match your setup
set RESOURCE_GROUP=foodxchange-rg
set APP_NAME=foodxchange-app

echo Deploying to: %APP_NAME%
echo Resource Group: %RESOURCE_GROUP%
echo.

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Deploy
echo 🚀 Deploying to Azure...
az webapp deployment source config-zip --resource-group %RESOURCE_GROUP% --name %APP_NAME% --src .

echo.
echo ✅ Deployment complete!
echo 🌐 Your app: https://%APP_NAME%.azurewebsites.net
echo.
pause 