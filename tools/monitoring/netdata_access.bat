@echo off
title Netdata Real-time Monitoring
color 0B
cls

echo ============================================
echo         NETDATA REAL-TIME MONITORING
echo ============================================
echo.
echo Netdata provides real-time system metrics:
echo - CPU, Memory, Disk usage
echo - Network traffic
echo - Process monitoring
echo - System performance
echo.

REM Check if tunnel already exists
netstat -an | find "19999" | find "LISTENING" >nul
if %errorlevel%==0 (
    echo [OK] SSH tunnel already active!
    goto OPEN_NETDATA
)

echo Creating SSH tunnel for Netdata access...
echo.

REM Kill any existing SSH processes on port 19999
for /f "tokens=5" %%i in ('netstat -ano ^| find "19999" ^| find "LISTENING"') do (
    taskkill /F /PID %%i 2>nul
)

REM Create SSH tunnel
echo Starting SSH tunnel on port 19999...
start /B ssh -i ~/.ssh/fdx_founders_key -L 19999:localhost:19999 -N fdxfounder@4.206.1.15

REM Wait for tunnel to establish
echo Waiting for tunnel to establish...
timeout /t 3 /nobreak >nul

REM Verify tunnel is working
netstat -an | find "19999" | find "LISTENING" >nul
if %errorlevel%==0 (
    echo.
    echo [SUCCESS] SSH tunnel established!
) else (
    echo.
    echo [ERROR] Failed to create tunnel. Trying alternative method...
    start cmd /k "ssh -i ~/.ssh/fdx_founders_key -L 19999:localhost:19999 fdxfounder@4.206.1.15"
    timeout /t 5 /nobreak >nul
)

:OPEN_NETDATA
echo.
echo ============================================
echo Opening Netdata in your browser...
echo.
echo URL: http://localhost:19999
echo.
echo Features available:
echo - Real-time CPU usage
echo - Memory consumption
echo - Disk I/O
echo - Network traffic
echo - Process list
echo - System logs
echo ============================================
echo.

REM Open in default browser
start http://localhost:19999

echo.
echo Netdata is now accessible at: http://localhost:19999
echo.
echo Press any key to close this window.
echo (Netdata will remain accessible)
pause >nul