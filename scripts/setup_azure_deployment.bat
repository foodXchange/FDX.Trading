@echo off
echo Setting up Azure Service Principal for GitHub Actions...
echo.

REM Set variables
set SUBSCRIPTION_ID=493477d6-57ab-49c4-8229-a99c4425c65a
set RESOURCE_GROUP=foodxchange-rg
set APP_NAME=foodxchange-github-actions

echo Creating service principal...
az ad sp create-for-rbac --name "%APP_NAME%" --role contributor --scopes /subscriptions/%SUBSCRIPTION_ID%/resourceGroups/%RESOURCE_GROUP% --sdk-auth > azure_credentials.json

echo.
echo ========================================
echo AZURE SERVICE PRINCIPAL CREATED!
echo ========================================
echo.
echo Next steps:
echo 1. Open azure_credentials.json
echo 2. Copy the entire JSON content
echo 3. Go to https://github.com/foodXchange/FDX.Trading/settings/secrets/actions
echo 4. Click "New repository secret"
echo 5. Name: AZURE_CREDENTIALS
echo 6. Value: Paste the JSON content
echo 7. Click "Add secret"
echo.
echo 8. Delete azure_credentials.json after adding to GitHub!
echo.
pause