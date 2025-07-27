@echo off
echo === FoodXchange Azure Deployment ===
echo.
echo This script will deploy your app to Azure.
echo Make sure you have logged in to Azure CLI first!
echo.
echo Run 'az login' if you haven't logged in yet.
echo.
pause

REM Configuration
set RESOURCE_GROUP=foodxchange-rg
set APP_NAME=foodxchange-app
set PLAN_NAME=foodxchange-plan
set LOCATION=East US

echo.
echo Creating resource group...
az group create --name %RESOURCE_GROUP% --location "%LOCATION%"

echo.
echo Creating App Service Plan...
az appservice plan create --name %PLAN_NAME% --resource-group %RESOURCE_GROUP% --sku B1 --is-linux

echo.
echo Creating Web App...
az webapp create --resource-group %RESOURCE_GROUP% --plan %PLAN_NAME% --name %APP_NAME% --runtime "PYTHON:3.12"

echo.
echo Configuring startup command...
az webapp config set --resource-group %RESOURCE_GROUP% --name %APP_NAME% --startup-file "gunicorn --bind 0.0.0.0:8000 --timeout 600 --worker-class uvicorn.workers.UvicornWorker app.main:app"

echo.
echo Creating deployment package...
python create_deployment_package.py

echo.
echo Deploying application...
az webapp deployment source config-zip --resource-group %RESOURCE_GROUP% --name %APP_NAME% --src foodxchange_deployment.zip

echo.
echo Getting app URL...
for /f "tokens=*" %%i in ('az webapp show --resource-group %RESOURCE_GROUP% --name %APP_NAME% --query defaultHostName -o tsv') do set HOSTNAME=%%i

echo.
echo ====================================
echo Deployment Complete!
echo ====================================
echo App URL: https://%HOSTNAME%
echo Health Check: https://%HOSTNAME%/health
echo System Status: https://%HOSTNAME%/system-status
echo.
echo Next Steps:
echo 1. Configure Azure OpenAI settings in the Azure Portal
echo 2. Test your application
echo.
pause