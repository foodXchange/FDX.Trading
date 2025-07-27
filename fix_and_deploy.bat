@echo off
echo ========================================
echo    FoodXchange Azure Fix & Deploy
echo ========================================
echo.

echo Creating deployment package...
python create_deployment_package.py

echo.
echo ========================================
echo    NEXT STEPS:
echo ========================================
echo.
echo 1. Go to Azure Portal: https://portal.azure.com
echo 2. Navigate to: foodxchange-app
echo 3. Go to Deployment Center
echo 4. Upload: foodxchange_deployment.zip
echo 5. Follow the guide in: FINAL_AZURE_FIX_GUIDE.md
echo.
echo ========================================
pause 