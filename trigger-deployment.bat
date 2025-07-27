@echo off
echo Triggering GitHub Actions Deployment
echo ===================================
echo.
echo This will commit changes and push to trigger deployment.
echo.
pause

git add .
git commit -m "Configure CI/CD pipeline with consolidated workflow"
git push origin main

echo.
echo Deployment triggered! Check progress at:
echo https://github.com/foodxchange/foodxchange-app/actions
echo.
pause