@echo off
echo Emergency Azure Deployment Fix
echo ==============================

echo Creating deployment package...
powershell -Command "Remove-Item emergency_fix.zip -ErrorAction SilentlyContinue"
powershell -Command "Compress-Archive -Path emergency_fix.py,requirements.txt -DestinationPath emergency_fix.zip"

echo Deploying to Azure...
az webapp deployment source config-zip --resource-group foodxchange-rg --name foodxchange-app --src emergency_fix.zip

echo Setting startup command...
az webapp config set --resource-group foodxchange-rg --name foodxchange-app --startup-file "python emergency_fix.py"

echo Restarting app...
az webapp restart --resource-group foodxchange-rg --name foodxchange-app

echo Done! Check https://www.fdx.trading in 2 minutes