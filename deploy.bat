@echo off
echo 🚀 Starting Azure deployment for FoodXchange...

REM Check if logged in
echo Checking Azure login status...
az account show >nul 2>&1
if errorlevel 1 (
    echo ❌ Not logged in to Azure. Please run 'az login' first.
    pause
    exit /b 1
)

echo ✅ Logged in to Azure

REM Configuration
set RESOURCE_GROUP_NAME=foodxchange-rg
set LOCATION=East US
set APP_NAME=foodxchange-app
set PLAN_NAME=foodxchange-plan

REM Create Resource Group
echo Creating resource group: %RESOURCE_GROUP_NAME%
az group create --name %RESOURCE_GROUP_NAME% --location "%LOCATION%"

REM Create App Service Plan
echo Creating App Service Plan: %PLAN_NAME%
az appservice plan create --name %PLAN_NAME% --resource-group %RESOURCE_GROUP_NAME% --sku B1 --is-linux

REM Create Web App
echo Creating Web App: %APP_NAME%
az webapp create --resource-group %RESOURCE_GROUP_NAME% --plan %PLAN_NAME% --name %APP_NAME% --runtime "PYTHON:3.12"

REM Configure startup command
echo Configuring startup command...
az webapp config set --resource-group %RESOURCE_GROUP_NAME% --name %APP_NAME% --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app"

REM Create deployment package
echo Creating deployment package...
powershell -Command "Compress-Archive -Path 'app', 'requirements.txt', 'startup.txt' -DestinationPath 'app.zip' -Force"

REM Deploy the app
echo Deploying application...
az webapp deployment source config-zip --resource-group %RESOURCE_GROUP_NAME% --name %APP_NAME% --src app.zip

echo ✅ Deployment completed!
echo 🌐 Your app is available at: https://%APP_NAME%.azurewebsites.net
pause 