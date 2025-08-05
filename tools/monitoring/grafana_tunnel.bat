@echo off
echo ========================================
echo    Grafana SSH Tunnel Setup
echo ========================================
echo.
echo Creating SSH tunnel to access Grafana...
echo.

REM Kill any existing SSH tunnels on port 3000
echo Cleaning up existing tunnels...
taskkill /F /IM ssh.exe /FI "WINDOWTITLE eq localhost:3000" 2>nul

REM Create new SSH tunnel
echo Starting SSH tunnel...
start /B ssh -i ~/.ssh/fdx_founders_key -L 3000:localhost:3000 fdxfounder@4.206.1.15 -N

REM Wait a moment for tunnel to establish
timeout /t 2 /nobreak >nul

REM Open Grafana in browser
echo Opening Grafana in browser...
start http://localhost:3000

echo.
echo ========================================
echo Grafana is now accessible at:
echo http://localhost:3000
echo.
echo Login credentials:
echo Username: admin
echo Password: admin
echo.
echo Press any key to close this window...
echo (Note: Grafana will remain accessible)
echo ========================================
pause >nul