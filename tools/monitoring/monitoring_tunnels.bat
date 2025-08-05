@echo off
echo ========================================
echo    VM Monitoring Access Setup
echo ========================================
echo.
echo Azure firewall blocks monitoring ports.
echo This script creates SSH tunnels to access them.
echo.

REM Kill any existing SSH tunnels
echo Cleaning up existing tunnels...
taskkill /F /IM ssh.exe 2>nul

echo.
echo Starting SSH tunnels...
echo.

REM Create Grafana tunnel (port 3000)
echo [1/2] Creating Grafana tunnel (port 3000)...
start /B ssh -i ~/.ssh/fdx_founders_key -L 3000:localhost:3000 fdxfounder@4.206.1.15 -N

REM Create Netdata tunnel (port 19999)
echo [2/2] Creating Netdata tunnel (port 19999)...
start /B ssh -i ~/.ssh/fdx_founders_key -L 19999:localhost:19999 fdxfounder@4.206.1.15 -N

REM Wait for tunnels to establish
echo.
echo Waiting for tunnels to establish...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Tunnels created successfully!
echo ========================================
echo.
echo You can now access:
echo.
echo 📊 Grafana:   http://localhost:3000
echo    Username:  admin
echo    Password:  admin
echo.
echo ⚡ Netdata:   http://localhost:19999
echo    (No login required)
echo.
echo ========================================
echo.
echo Choose an option:
echo 1. Open Grafana
echo 2. Open Netdata
echo 3. Open Both
echo 4. Exit (tunnels remain active)
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    start http://localhost:3000
) else if "%choice%"=="2" (
    start http://localhost:19999
) else if "%choice%"=="3" (
    start http://localhost:3000
    start http://localhost:19999
) else if "%choice%"=="4" (
    exit
)

echo.
echo Press any key to exit...
pause >nul