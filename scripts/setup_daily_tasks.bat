@echo off
echo.
echo ====================================
echo   FoodXchange Daily Task Setup
echo ====================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

set TASK_NAME=FoodXchange_Daily_Maintenance
set PYTHON_PATH=python
set SCRIPT_PATH=%~dp0daily_maintenance.py

echo Creating scheduled task for daily maintenance...
echo.

REM Delete existing task if it exists
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

REM Create new task to run daily at 2 AM
schtasks /create ^
    /tn "%TASK_NAME%" ^
    /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\"" ^
    /sc daily ^
    /st 02:00 ^
    /ru SYSTEM ^
    /rl HIGHEST ^
    /f

if %errorlevel% equ 0 (
    echo SUCCESS: Daily maintenance task created!
    echo.
    echo Task Details:
    echo - Name: %TASK_NAME%
    echo - Schedule: Daily at 2:00 AM
    echo - Script: %SCRIPT_PATH%
    echo.
    echo You can manage this task in Task Scheduler.
) else (
    echo ERROR: Failed to create scheduled task.
)

echo.
echo Creating additional scheduled tasks...
echo.

REM Create Redis monitoring task (every hour)
set MONITOR_TASK=FoodXchange_Redis_Monitor
schtasks /create ^
    /tn "%MONITOR_TASK%" ^
    /tr "\"%PYTHON_PATH%\" \"%~dp0redis_monitor.py\"" ^
    /sc hourly ^
    /mo 1 ^
    /ru SYSTEM ^
    /f

if %errorlevel% equ 0 (
    echo SUCCESS: Redis monitoring task created (runs hourly)
)

REM Create weekly comprehensive backup task
set BACKUP_TASK=FoodXchange_Weekly_Backup
schtasks /create ^
    /tn "%BACKUP_TASK%" ^
    /tr "\"%~dp0..\fx.bat\" backup" ^
    /sc weekly ^
    /d SUN ^
    /st 03:00 ^
    /ru SYSTEM ^
    /f

if %errorlevel% equ 0 (
    echo SUCCESS: Weekly backup task created (Sundays at 3:00 AM)
)

echo.
echo ====================================
echo   Setup Complete!
echo ====================================
echo.
echo Scheduled Tasks Created:
echo 1. Daily Maintenance - 2:00 AM daily
echo 2. Redis Monitoring - Every hour
echo 3. Weekly Backup - Sundays 3:00 AM
echo.
echo To view or modify tasks:
echo - Open Task Scheduler
echo - Look for tasks starting with "FoodXchange_"
echo.
pause