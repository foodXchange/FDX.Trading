@echo off
echo ========================================
echo    Cursor VM Connection Setup
echo ========================================
echo.

REM Create SSH config for VM
echo Creating SSH configuration...
(
echo Host fdx-vm
echo     HostName 4.206.1.15
echo     User fdxfounder
echo     Port 22
echo     IdentityFile ~/.ssh/fdx_founders_key
echo     StrictHostKeyChecking no
echo     UserKnownHostsFile /dev/null
echo     ForwardAgent yes
echo.
echo Host fdx-vm-app
echo     HostName 4.206.1.15
echo     User fdxfounder
echo     Port 22
echo     IdentityFile ~/.ssh/fdx_founders_key
echo     StrictHostKeyChecking no
echo     UserKnownHostsFile /dev/null
echo     ForwardAgent yes
echo     RemoteCommand cd /home/fdxfounder/fdx/app && exec bash
) > "%USERPROFILE%\.ssh\config"

echo SSH config created at %USERPROFILE%\.ssh\config
echo.

REM Check if SSH key exists
if not exist "%USERPROFILE%\.ssh\fdx_founders_key" (
    echo WARNING: SSH key not found at %USERPROFILE%\.ssh\fdx_founders_key
    echo Please ensure your SSH key is in the correct location
    echo.
)

REM Test SSH connection
echo Testing SSH connection...
ssh -o ConnectTimeout=5 fdx-vm "echo 'SSH connection successful!'"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo SSH connection failed. Please check:
    echo 1. Your SSH key is at %USERPROFILE%\.ssh\fdx_founders_key
    echo 2. The VM is running
    echo 3. Your internet connection
    echo.
) else (
    echo SSH connection test passed!
    echo.
)

REM Open Cursor with remote connection
echo.
echo Opening Cursor with VM connection...
echo.
echo Choose an option:
echo 1. Connect to VM root directory
echo 2. Connect to FDX app directory
echo 3. Just open Cursor (connect manually)
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo Connecting to VM root...
    cursor --folder-uri "vscode-remote://ssh-remote+fdx-vm/home/fdxfounder"
) else if "%choice%"=="2" (
    echo Connecting to FDX app directory...
    cursor --folder-uri "vscode-remote://ssh-remote+fdx-vm/home/fdxfounder/fdx/app"
) else (
    echo Opening Cursor...
    cursor
    echo.
    echo To connect to VM in Cursor:
    echo 1. Press Ctrl+Shift+P to open command palette
    echo 2. Type "Remote-SSH: Connect to Host"
    echo 3. Select "fdx-vm" from the list
    echo 4. Choose the folder you want to open
)

echo.
echo ========================================
echo Setup complete!
echo.
echo Quick tips:
echo - Use Ctrl+Shift+P to open command palette
echo - Type "Remote" to see all remote commands
echo - Your VM apps are at:
echo   * Main app: /home/fdxfounder/fdx/app
echo   * Port 80: FastAPI main app
echo   * Port 8003: FDX Crawler with 23,206 suppliers
echo ========================================
pause