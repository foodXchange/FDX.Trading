@echo off
echo ==========================================
echo UPDATING VM WITH NEW DATABASE AND AI KEYS
echo ==========================================
echo.

echo This will update your VM with:
echo - New managed PostgreSQL database
echo - Azure OpenAI credentials
echo.

echo SSH Key: ~/.ssh/fdx_founders_key
echo VM User: fdxfounder@4.206.1.15
echo.

pause

echo.
echo Connecting to VM and updating configuration...
bash update_vm_config.sh

echo.
echo ==========================================
echo UPDATE COMPLETE!
echo ==========================================
echo.
echo Your VM is now using:
echo - Database: fdx-postgres-production
echo - AI: Azure OpenAI (gpt-4o-mini)
echo.
echo Access your app at: http://4.206.1.15
echo.
pause