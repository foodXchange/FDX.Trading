@echo off
echo Quick Azure Deployment Fix
echo ==================================================

echo.
echo Deploying to Azure...
az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path azure_quick_fix.zip --type zip --restart true

if %ERRORLEVEL% == 0 (
    echo [SUCCESS] Deployment successful!
    
    echo.
    echo Setting startup command...
    az webapp config set --name foodxchange-app --resource-group foodxchange-rg --startup-file "python -m uvicorn app:app --host 0.0.0.0 --port 8000"
    
    echo.
    echo Restarting app...
    az webapp restart --name foodxchange-app --resource-group foodxchange-rg
    
    echo.
    echo Deployment complete!
    echo URL: https://foodxchange-app.azurewebsites.net
    echo Health: https://foodxchange-app.azurewebsites.net/health
) else (
    echo [ERROR] Deployment failed!
)