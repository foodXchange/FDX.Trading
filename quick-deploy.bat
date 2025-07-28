@echo off
echo Quick Deploy to Azure
echo =======================
echo.
echo This will deploy your current code to Azure for testing
echo.
set /p confirm="Continue? (y/N): "
if /i "%confirm%"=="y" (
    python azure_deploy.py
) else (
    echo Deployment cancelled.
)
pause
