@echo off
echo ========================================
echo Cursor Remote SSH Connection to FDX VM
echo ========================================
echo.
echo Choose connection type:
echo 1. Connect to fdx-vm (general access)
echo 2. Connect to fdx-dev (with port forwarding)
echo 3. Open specific folder on VM
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Connecting to fdx-vm...
    echo Opening folder: /home/fdxfounder/fdx/app
    cursor --remote ssh-remote+fdx-vm /home/fdxfounder/fdx/app
) else if "%choice%"=="2" (
    echo.
    echo Connecting to fdx-dev with port forwarding...
    echo Forwarded ports:
    echo   - localhost:8000 = VM port 80 (main app)
    echo   - localhost:8003 = VM port 8003
    echo   - localhost:3000 = VM port 3000
    echo Opening folder: /home/fdxfounder/fdx/app
    cursor --remote ssh-remote+fdx-dev /home/fdxfounder/fdx/app
) else if "%choice%"=="3" (
    echo.
    echo Available folders:
    echo   /home/fdxfounder/fdx/app (main application)
    echo   /home/fdxfounder/fdx/scripts (utility scripts)
    echo   /home/fdxfounder/FDX-Crawler (crawler app)
    echo.
    set /p folder="Enter folder path: "
    echo.
    echo Connecting to fdx-vm...
    echo Opening folder: %folder%
    cursor --remote ssh-remote+fdx-vm %folder%
) else (
    echo Invalid choice!
    pause
    exit /b 1
)

echo.
echo If Cursor doesn't open, make sure:
echo 1. Cursor is installed and in PATH
echo 2. Remote-SSH extension is installed
echo 3. SSH connection works: ssh fdx-vm
echo.
pause