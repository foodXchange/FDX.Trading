@echo off
title FDX VM Control Center
color 0A
cls

:MENU
cls
echo.
echo    ============================================================
echo                    FDX VM CONTROL CENTER                    
echo    ============================================================
echo.
echo    VM IP: 4.206.1.15
echo    Status: ONLINE
echo.
echo    [APPLICATIONS]
echo    1. FoodXchange App....................... http://4.206.1.15
echo    2. FDX Crawler (23,206 Suppliers)........ http://4.206.1.15:8003
echo.
echo    [MONITORING] (Requires SSH Tunnel)
echo    3. Grafana Dashboard..................... Port 3000
echo    4. Netdata Real-time..................... Port 19999
echo    5. Setup Monitoring Access (SSH Tunnel)
echo.
echo    [DEVELOPMENT]
echo    6. SSH Terminal.......................... Direct SSH Access
echo    7. VS Code Remote........................ Open in VS Code
echo    8. File Manager (SFTP)................... Browse VM Files
echo.
echo    [MANAGEMENT]
echo    9. VM Control Panel...................... Local Dashboard
echo    0. Quick Access Dashboard................ HTML Interface
echo.
echo    X. Exit
echo.
echo    ============================================================
echo.
set /p choice="Select option: "

if "%choice%"=="1" goto APP
if "%choice%"=="2" goto CRAWLER
if "%choice%"=="3" goto GRAFANA
if "%choice%"=="4" goto NETDATA
if "%choice%"=="5" goto TUNNEL
if "%choice%"=="6" goto SSH
if "%choice%"=="7" goto VSCODE
if "%choice%"=="8" goto SFTP
if "%choice%"=="9" goto CONTROL
if "%choice%"=="0" goto DASHBOARD
if /i "%choice%"=="X" goto EXIT
goto MENU

:APP
echo.
echo Opening FoodXchange App...
start http://4.206.1.15
timeout /t 2 >nul
goto MENU

:CRAWLER
echo.
echo Opening FDX Crawler...
start http://4.206.1.15:8003
timeout /t 2 >nul
goto MENU

:GRAFANA
echo.
echo Checking for SSH tunnel...
netstat -an | find "3000" | find "LISTENING" >nul
if %errorlevel%==0 (
    echo Tunnel active. Opening Grafana...
    start http://localhost:3000
) else (
    echo No tunnel detected. Please run option 5 first.
    pause
)
goto MENU

:NETDATA
echo.
echo Checking for SSH tunnel...
netstat -an | find "19999" | find "LISTENING" >nul
if %errorlevel%==0 (
    echo Tunnel active. Opening Netdata...
    start http://localhost:19999
) else (
    echo No tunnel detected. Please run option 5 first.
    pause
)
goto MENU

:TUNNEL
echo.
echo Setting up SSH tunnels for monitoring...
call monitoring_tunnels.bat
goto MENU

:SSH
echo.
echo Connecting to VM via SSH...
start cmd /k ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15
goto MENU

:VSCODE
echo.
echo Opening VS Code with Remote SSH...
code --remote ssh-remote+fdxfounder@4.206.1.15 /home/fdxfounder
goto MENU

:SFTP
echo.
echo Opening SFTP connection...
start "" "C:\Program Files\PuTTY\psftp.exe" -i "%USERPROFILE%\.ssh\fdx_founders_key.ppk" fdxfounder@4.206.1.15
if %errorlevel% neq 0 (
    echo.
    echo PuTTY not found. Opening Windows Explorer SFTP...
    start "" "sftp://fdxfounder@4.206.1.15"
)
goto MENU

:CONTROL
echo.
echo Starting VM Control Panel...
cd /d "%~dp0"
if exist vm_control_fastapi.py (
    start cmd /k python vm_control_fastapi.py
    timeout /t 3 >nul
    start http://localhost:5555
) else (
    echo Control panel not found.
    pause
)
goto MENU

:DASHBOARD
echo.
echo Opening Quick Access Dashboard...
start quick_vm_access.html
goto MENU

:EXIT
echo.
echo Goodbye!
timeout /t 1 >nul
exit