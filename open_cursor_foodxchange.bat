@echo off
echo ========================================
echo    Opening FoodXchange in Cursor IDE
echo ========================================
echo.
echo Connecting to VM at /home/fdxfounder/fdx/app
echo This is your main FoodXchange application (Port 80)
echo.

REM Check if SSH key exists
if not exist "%USERPROFILE%\.ssh\fdx_founders_key" (
    echo ERROR: SSH key not found at %USERPROFILE%\.ssh\fdx_founders_key
    echo Please ensure your SSH key is in place.
    pause
    exit /b 1
)

REM Open Cursor with FoodXchange directory
echo Starting Cursor with remote connection...
cursor --folder-uri "vscode-remote://ssh-remote+fdx-foodxchange/home/fdxfounder/fdx/app"

echo.
echo ========================================
echo Cursor should now be opening with:
echo - Remote: fdx-foodxchange (4.206.1.15)
echo - Folder: /home/fdxfounder/fdx/app
echo - App URL: http://4.206.1.15
echo.
echo If connection fails:
echo 1. Make sure VM is running
echo 2. Check your SSH key permissions
echo 3. Try: ssh fdx-foodxchange
echo ========================================
pause