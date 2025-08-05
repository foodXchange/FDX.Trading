@echo off
echo ===================================
echo Claude Code VM Connection Helper
echo ===================================
echo.
echo Choose connection method:
echo 1. Connect to fdxfounder (main app)
echo 2. Connect to azureuser
echo 3. Open specific folder on VM
echo 4. Run command on VM
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo Connecting to fdxfounder@4.206.1.15...
    claude --ssh fdx-vm
) else if "%choice%"=="2" (
    echo Connecting to azureuser@4.206.1.15...
    echo Note: You may need to add azureuser to SSH config
    claude --ssh fdx-vm-azureuser
) else if "%choice%"=="3" (
    set /p folder="Enter remote folder path (e.g., /home/fdxfounder/fdx/app): "
    echo Opening %folder% on VM...
    claude --remote-folder fdx-vm:%folder%
) else if "%choice%"=="4" (
    set /p cmd="Enter command to run on VM: "
    echo Running command on VM...
    claude --ssh fdx-vm --exec "%cmd%"
) else (
    echo Invalid choice!
)

pause