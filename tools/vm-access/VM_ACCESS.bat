@echo off
title FoodXchange VM Access - Poland Central
color 0A

echo.
echo ========================================
echo    FOODXCHANGE VM ACCESS PANEL
echo    Poland Central - 74.248.141.31
echo ========================================
echo.

echo Current VM Details:
echo    VM IP: 74.248.141.31
echo    Location: Poland Central
echo    Performance: 30ms latency from Israel
echo.

echo Available Services:
echo    1. FoodXchange App....................... http://74.248.141.31
echo    2. Email CRM System...................... http://74.248.141.31:8003
echo    3. API Endpoint.......................... http://74.248.141.31:8000
echo    4. Grafana Monitoring................... http://74.248.141.31:3000
echo    5. Netdata Monitoring.................. http://74.248.141.31:19999
echo.

echo SSH Access:
echo    User: azureuser
echo    Key: ~/.ssh/fdx_poland_key
echo    Command: ssh -i ~/.ssh/fdx_poland_key azureuser@74.248.141.31
echo.

echo ========================================
echo    QUICK ACTIONS
echo ========================================
echo.

:menu
echo Choose an action:
echo.
echo [1] Open FoodXchange App
echo [2] Open Email CRM System
echo [3] Open API Documentation
echo [4] Open Grafana Monitoring
echo [5] Open Netdata Monitoring
echo [6] SSH to VM (PowerShell)
echo [7] SSH to VM (Command Prompt)
echo [8] VS Code Remote SSH
echo [9] SFTP File Transfer
echo [10] Open SFTP in Explorer
echo [11] Check VM Status
echo [12] View All Services
echo [0] Exit
echo.

set /p choice="Enter your choice (0-12): "

if "%choice%"=="1" goto open_app
if "%choice%"=="2" goto open_email
if "%choice%"=="3" goto open_api
if "%choice%"=="4" goto open_grafana
if "%choice%"=="5" goto open_netdata
if "%choice%"=="6" goto ssh_powershell
if "%choice%"=="7" goto ssh_cmd
if "%choice%"=="8" goto vscode_ssh
if "%choice%"=="9" goto sftp
if "%choice%"=="10" goto sftp_explorer
if "%choice%"=="11" goto check_status
if "%choice%"=="12" goto view_all
if "%choice%"=="0" goto exit
goto menu

:open_app
echo Opening FoodXchange App...
start http://74.248.141.31
goto menu

:open_email
echo Opening Email CRM System...
start http://74.248.141.31:8003
goto menu

:open_api
echo Opening API Documentation...
start http://74.248.141.31:8000/docs
goto menu

:open_grafana
echo Opening Grafana Monitoring...
start http://74.248.141.31:3000
goto menu

:open_netdata
echo Opening Netdata Monitoring...
start http://74.248.141.31:19999
goto menu

:ssh_powershell
echo Opening PowerShell SSH connection...
powershell -Command "ssh -i ~/.ssh/fdx_poland_key azureuser@74.248.141.31"
goto menu

:ssh_cmd
echo Opening Command Prompt SSH connection...
start cmd /k ssh -i ~/.ssh/fdx_poland_key azureuser@74.248.141.31
goto menu

:vscode_ssh
echo Opening VS Code with Remote SSH...
code --remote ssh-remote+azureuser@74.248.141.31 /home/azureuser
goto menu

:sftp
echo Opening SFTP connection...
start "" "C:\Program Files\PuTTY\psftp.exe" -i "%USERPROFILE%\.ssh\fdx_poland_key.ppk" azureuser@74.248.141.31
goto menu

:sftp_explorer
echo Opening SFTP in Windows Explorer...
start "" "sftp://azureuser@74.248.141.31"
goto menu

:check_status
echo Checking VM status...
powershell -Command "Test-NetConnection -ComputerName 74.248.141.31 -Port 22"
echo.
echo Testing web services...
powershell -Command "try { Invoke-WebRequest -Uri 'http://74.248.141.31:8000/health' -TimeoutSec 5 | Select-Object StatusCode } catch { Write-Host 'App not responding' }"
echo.
pause
goto menu

:view_all
echo Opening all services in browser...
start http://74.248.141.31
timeout /t 2 /nobreak >nul
start http://74.248.141.31:8003
timeout /t 2 /nobreak >nul
start http://74.248.141.31:8000
timeout /t 2 /nobreak >nul
start http://74.248.141.31:3000
timeout /t 2 /nobreak >nul
start http://74.248.141.31:19999
goto menu

:exit
echo.
echo Thank you for using FoodXchange VM Access!
echo.
pause
exit