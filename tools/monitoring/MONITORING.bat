@echo off
title VM Monitoring Dashboard
color 0E
cls

echo ============================================================
echo              VM MONITORING DASHBOARD
echo ============================================================
echo.
echo This will set up access to both monitoring tools:
echo.
echo 📊 GRAFANA - System dashboards and metrics
echo ⚡ NETDATA - Real-time performance monitoring
echo.
echo ============================================================
echo.

REM Kill any existing SSH tunnels
echo Cleaning up existing connections...
taskkill /F /IM ssh.exe 2>nul

echo.
echo Setting up secure tunnels...
echo.

REM Create Grafana tunnel
echo [1/2] Setting up Grafana access (port 3000)...
start /B ssh -i ~/.ssh/fdx_founders_key -L 3000:localhost:3000 -N fdxfounder@4.206.1.15

REM Create Netdata tunnel
echo [2/2] Setting up Netdata access (port 19999)...
start /B ssh -i ~/.ssh/fdx_founders_key -L 19999:localhost:19999 -N fdxfounder@4.206.1.15

REM Wait for tunnels
echo.
echo Establishing connections...
timeout /t 3 /nobreak >nul

REM Check if tunnels are active
set GRAFANA_OK=0
set NETDATA_OK=0

netstat -an | find "3000" | find "LISTENING" >nul
if %errorlevel%==0 set GRAFANA_OK=1

netstat -an | find "19999" | find "LISTENING" >nul
if %errorlevel%==0 set NETDATA_OK=1

cls
echo ============================================================
echo              MONITORING ACCESS READY
echo ============================================================
echo.

if %GRAFANA_OK%==1 (
    echo ✅ GRAFANA:  http://localhost:3000
    echo    Username: admin
    echo    Password: admin
) else (
    echo ❌ GRAFANA:  Failed to establish tunnel
)

echo.

if %NETDATA_OK%==1 (
    echo ✅ NETDATA:  http://localhost:19999
    echo    No login required
) else (
    echo ❌ NETDATA:  Failed to establish tunnel
)

echo.
echo ============================================================
echo.
echo What would you like to open?
echo.
echo 1. Grafana Dashboard
echo 2. Netdata Real-time
echo 3. Both
echo 4. Exit (keep tunnels active)
echo.
set /p choice="Select option (1-4): "

if "%choice%"=="1" (
    if %GRAFANA_OK%==1 (
        start http://localhost:3000
    ) else (
        echo Grafana tunnel not active!
        pause
    )
) else if "%choice%"=="2" (
    if %NETDATA_OK%==1 (
        start http://localhost:19999
    ) else (
        echo Netdata tunnel not active!
        pause
    )
) else if "%choice%"=="3" (
    if %GRAFANA_OK%==1 start http://localhost:3000
    if %NETDATA_OK%==1 start http://localhost:19999
) else if "%choice%"=="4" (
    exit
)

echo.
echo ============================================================
echo Monitoring tools are now accessible!
echo.
echo You can close this window - the tunnels will remain active.
echo To stop tunnels, close all SSH processes.
echo ============================================================
echo.
pause