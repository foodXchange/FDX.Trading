@echo off
echo === Pushing FoodXchange to GitHub ===

REM Pull latest changes first
echo Pulling latest changes...
git pull origin main --allow-unrelated-histories

REM Add all files except nul
echo Adding files...
git add -A

REM Commit changes
echo Committing changes...
git commit -m "Fix Azure deployment - add minimal WSGI apps and diagnostic tools"

REM Push to GitHub
echo Pushing to GitHub...
git push -u origin main

echo === Push complete! ===
echo.
echo Now go to Azure Portal and:
echo 1. Go to Deployment Center
echo 2. Click "Sync" to pull latest changes from GitHub
echo 3. Check Log Stream for any errors
pause