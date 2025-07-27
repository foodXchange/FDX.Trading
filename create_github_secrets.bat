@echo off
echo Creating Azure Service Principal for GitHub Actions...
echo.

REM Create service principal and capture output
az ad sp create-for-rbac --name "github-actions-foodxchange" --role contributor --scopes "/subscriptions/88931ed0-52df-42fb-a09c-e024c9586f8a/resourceGroups/foodxchange-rg" > sp_output.json

REM Check if successful
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create service principal!
    exit /b 1
)

echo.
echo Service Principal created successfully!
echo.
echo ========================================
echo Add these secrets to your GitHub repository:
echo ========================================
echo.
echo 1. AZURE_CLIENT_ID: (see appId in sp_output.json)
echo 2. AZURE_TENANT_ID: (see tenant in sp_output.json)
echo 3. AZURE_SUBSCRIPTION_ID: 88931ed0-52df-42fb-a09c-e024c9586f8a
echo.
echo The credentials are saved in sp_output.json
echo KEEP THIS FILE SECURE - it contains sensitive credentials!
echo.
type sp_output.json
echo.
echo ========================================
pause