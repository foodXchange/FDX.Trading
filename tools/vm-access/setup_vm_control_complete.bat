@echo off
title FDX VM Control Panel - Complete Setup
color 0A

echo ============================================================
echo         FDX VM CONTROL PANEL - COMPLETE SETUP
echo ============================================================
echo.
echo This script will:
echo   1. Test SSH connection to your VM
echo   2. Upload the control panel files
echo   3. Install and configure the control panel
echo   4. Set up Cursor IDE integration
echo.
echo ============================================================
echo.

REM Check for required files
if not exist vm_control_fastapi.py (
    echo ERROR: vm_control_fastapi.py not found!
    echo Please ensure all files are in the current directory.
    pause
    exit /b 1
)

if not exist templates\dashboard_fastapi.html (
    echo ERROR: templates\dashboard_fastapi.html not found!
    pause
    exit /b 1
)

REM Set variables
set VM_HOST=4.206.1.15
set VM_USER=fdxfounder
set SSH_KEY=%USERPROFILE%\.ssh\fdx_founders_key
set REMOTE_DIR=/home/fdxfounder/vm-control-panel

echo.
echo Step 1: Testing SSH connection...
ssh -i %SSH_KEY% -o ConnectTimeout=5 %VM_USER%@%VM_HOST% "echo 'SSH connection successful!'"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: SSH connection failed!
    echo Please check:
    echo   - VM is running
    echo   - SSH key is at %SSH_KEY%
    echo   - Network connection
    pause
    exit /b 1
)

echo.
echo Step 2: Creating remote directories...
ssh -i %SSH_KEY% %VM_USER%@%VM_HOST% "mkdir -p %REMOTE_DIR%/templates %REMOTE_DIR%/static"

echo.
echo Step 3: Uploading control panel files...
echo   - Uploading Python application...
scp -i %SSH_KEY% vm_control_fastapi.py %VM_USER%@%VM_HOST%:%REMOTE_DIR%/

echo   - Uploading HTML template...
scp -i %SSH_KEY% templates\dashboard_fastapi.html %VM_USER%@%VM_HOST%:%REMOTE_DIR%/templates/

echo   - Uploading deployment script...
scp -i %SSH_KEY% deploy_vm_control_panel.sh %VM_USER%@%VM_HOST%:%REMOTE_DIR%/

echo.
echo Step 4: Making deployment script executable...
ssh -i %SSH_KEY% %VM_USER%@%VM_HOST% "chmod +x %REMOTE_DIR%/deploy_vm_control_panel.sh"

echo.
echo Step 5: Running deployment script...
echo This will install dependencies and configure the service.
echo Please wait...
echo.
ssh -i %SSH_KEY% -t %VM_USER%@%VM_HOST% "cd %REMOTE_DIR% && ./deploy_vm_control_panel.sh"

echo.
echo ============================================================
echo          SETUP COMPLETE - NEXT STEPS
echo ============================================================
echo.
echo 1. VM Control Panel should now be accessible at:
echo    - http://%VM_HOST%:5555
echo.
echo 2. Configure Azure credentials on the VM:
echo    ssh -i %SSH_KEY% %VM_USER%@%VM_HOST%
echo    nano %REMOTE_DIR%/.env
echo.
echo 3. To use with Cursor IDE:
echo    - Run: cursor_vm_control.bat
echo    - Or: cursor --folder-uri "vscode-remote://ssh-remote+fdx-vm%REMOTE_DIR%"
echo.
echo 4. Quick commands:
echo    - Check status: ssh fdx-vm "sudo systemctl status vm-control-panel"
echo    - View logs: ssh fdx-vm "sudo journalctl -u vm-control-panel -f"
echo    - Restart: ssh fdx-vm "sudo systemctl restart vm-control-panel"
echo.
echo 5. Local tunnel (if port 5555 is blocked):
echo    ssh -i %SSH_KEY% -L 5555:localhost:5555 %VM_USER%@%VM_HOST%
echo    Then visit: http://localhost:5555
echo.
echo ============================================================
echo.

REM Open the control panel
echo Opening VM Control Panel in browser...
timeout /t 3 >nul
start http://%VM_HOST%:5555

echo.
echo Would you like to open Cursor IDE connected to the control panel? (Y/N)
set /p open_cursor=
if /i "%open_cursor%"=="Y" (
    echo Opening Cursor IDE...
    cursor --folder-uri "vscode-remote://ssh-remote+fdx-vm%REMOTE_DIR%"
)

echo.
echo Setup script completed!
pause