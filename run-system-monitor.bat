@echo off
echo ========================================
echo FoodXchange System Monitoring Tools
echo ========================================
echo.

:menu
echo Choose monitoring option:
echo 1. Quick System Check (30 seconds)
echo 2. Standard Monitoring (5 minutes)
echo 3. Extended Monitoring (15 minutes)
echo 4. Continuous Monitoring (background)
echo 5. Python System Monitor (comprehensive)
echo 6. Exit
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto quick
if "%choice%"=="2" goto standard
if "%choice%"=="3" goto extended
if "%choice%"=="4" goto continuous
if "%choice%"=="5" goto python
if "%choice%"=="6" goto exit
echo Invalid choice. Please try again.
goto menu

:quick
echo.
echo Running quick system check (30 seconds)...
powershell -ExecutionPolicy Bypass -File "quick-monitor.ps1" -Interval 10 -Duration 30
goto end

:standard
echo.
echo Running standard monitoring (5 minutes)...
powershell -ExecutionPolicy Bypass -File "quick-monitor.ps1" -Interval 30 -Duration 300
goto end

:extended
echo.
echo Running extended monitoring (15 minutes)...
powershell -ExecutionPolicy Bypass -File "quick-monitor.ps1" -Interval 60 -Duration 900
goto end

:continuous
echo.
echo Starting continuous monitoring in background...
echo This will run until you stop it manually.
echo Check the logs in continuous_monitor.log
echo.
powershell -ExecutionPolicy Bypass -Command "Start-Process python -ArgumentList 'continuous_monitor.py --interval 5' -WindowStyle Hidden"
echo Continuous monitoring started in background.
echo To stop it, run: taskkill /f /im python.exe
goto end

:python
echo.
echo Running comprehensive Python system monitor...
python system_monitor.py
goto end

:end
echo.
echo Monitoring completed!
echo Check the logs for detailed information.
echo.
pause

:exit
echo Goodbye! 