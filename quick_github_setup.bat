@echo off
echo === Quick GitHub Actions Setup for FoodXchange ===
echo.

echo Step 1: Download Publish Profile
echo --------------------------------
echo 1. Go to: https://portal.azure.com
echo 2. Navigate to: App Services - foodxchange-app
echo 3. Click "Get publish profile" and save the file
echo.
echo Press any key when you have the publish profile file...
pause > nul

echo.
echo Step 2: Initialize Git Repository
echo ---------------------------------
git init
git add .
git commit -m "Initial commit with GitHub Actions workflow"

echo.
echo Step 3: Create GitHub Repository
echo --------------------------------
echo 1. Go to: https://github.com/new
echo 2. Repository name: FoodXchange
echo 3. Keep it Public or Private as you prefer
echo 4. DON'T initialize with README
echo 5. Click "Create repository"
echo.
set /p username="Enter your GitHub username: "

echo.
echo Adding GitHub remote...
git remote add origin https://github.com/%username%/FoodXchange.git
git branch -M main

echo.
echo Step 4: Add Publish Profile to GitHub
echo -------------------------------------
echo 1. Go to: https://github.com/%username%/FoodXchange/settings/secrets/actions/new
echo 2. Name: AZURE_WEBAPP_PUBLISH_PROFILE
echo 3. Value: Paste entire XML content from publish profile
echo 4. Click "Add secret"
echo.
echo Press any key when you've added the secret...
pause > nul

echo.
echo Step 5: Push to GitHub
echo ----------------------
git push -u origin main

echo.
echo === Setup Complete! ===
echo.
echo Your deployment will start automatically.
echo Monitor it at: https://github.com/%username%/FoodXchange/actions
echo.
echo Once deployed, check:
echo - https://foodxchange-app.azurewebsites.net/health
echo - https://www.fdx.trading/health
echo.
pause