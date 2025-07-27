@echo off
echo === FoodXchange Fixed Deployment ===
echo.
echo This will deploy the fixed application to Azure.
echo Make sure you have Azure CLI installed and are logged in.
echo.
pause

python deploy_azure_fixed.py

echo.
echo Deployment completed!
pause 