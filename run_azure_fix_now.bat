@echo off
echo Starting Azure 503 fix...

REM Stop the app
echo Stopping App Service...
az webapp stop --name foodxchange-app --resource-group foodxchange-rg

REM Check if startup_fixed.py exists and copy it
if exist startup_fixed.py (
    echo Using startup_fixed.py
    copy /Y startup_fixed.py startup.py
)

REM Deploy to Azure
echo Deploying to Azure...
az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path . --type zip

REM Start the app
echo Starting App Service...
az webapp start --name foodxchange-app --resource-group foodxchange-rg

echo Waiting 60 seconds for app to initialize...
timeout /t 60 /nobreak > nul

REM Test the endpoints
echo Testing endpoints...
curl -s -o nul -w "Azure endpoint: %%{http_code}\n" https://foodxchange-app.azurewebsites.net/
curl -s -o nul -w "Health endpoint: %%{http_code}\n" https://foodxchange-app.azurewebsites.net/health

echo Fix complete!