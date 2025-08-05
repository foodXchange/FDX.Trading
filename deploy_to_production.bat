@echo off
echo ======================================
echo FDX.trading Production Deployment
echo ======================================
echo.

echo Deploying to www.fdx.trading...
echo.

REM Copy the updated AI search system file
echo 1. Copying ai_search_system.py to VM...
scp -i C:\Users\foodz\.ssh\fdx_founders_key ai_search_system.py fdxfounder@4.206.1.15:~/fdx/app/

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Could not copy files to VM
    echo Please check SSH key permissions
    pause
    exit /b 1
)

echo.
echo 2. Restarting application on VM...
ssh -i C:\Users\foodz\.ssh\fdx_founders_key fdxfounder@4.206.1.15 "cd ~/fdx/app && sudo systemctl restart gunicorn && sudo systemctl restart nginx"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Could not restart services
    pause
    exit /b 1
)

echo.
echo ======================================
echo DEPLOYMENT COMPLETE!
echo ======================================
echo.
echo The AI search system has been deployed to www.fdx.trading
echo.
echo Test the deployment:
echo - https://www.fdx.trading
echo - https://www.fdx.trading/suppliers (AI Search)
echo.
pause