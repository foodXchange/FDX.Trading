@echo off
echo ========================================
echo    FoodXchange VM Quick Access
echo ========================================
echo.
echo Choose an option:
echo 1. SSH to VM
echo 2. Open FastAPI App (FoodXchange)
echo 3. Open FDX Crawler (Supplier Database)
echo 4. Open Monitoring Tools (Grafana + Netdata via SSH tunnel)
echo 5. Open Quick Access Dashboard
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo Connecting to VM via SSH...
    ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15
) else if "%choice%"=="2" (
    echo Opening FastAPI App...
    start http://4.206.1.15
) else if "%choice%"=="3" (
    echo Opening FDX Crawler...
    start http://4.206.1.15:8003
) else if "%choice%"=="4" (
    echo Opening Monitoring Tools with SSH tunnel...
    call monitoring_tunnels.bat
) else if "%choice%"=="5" (
    echo Opening Quick Access Dashboard...
    start quick_vm_access.html
) else if "%choice%"=="6" (
    echo Goodbye!
    exit
) else (
    echo Invalid choice. Please try again.
    pause
    goto :eof
)

pause 