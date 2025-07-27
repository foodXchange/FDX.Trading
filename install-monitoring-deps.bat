@echo off
echo ========================================
echo FoodXchange Monitoring Dependencies
echo ========================================
echo.

echo Installing Python monitoring dependencies...
pip install psutil requests azure-storage-blob azure-identity

echo.
echo Installing PowerShell modules...
powershell -ExecutionPolicy Bypass -Command "Install-Module -Name Az -Force -AllowClobber"

echo.
echo Creating monitoring directories...
if not exist "monitoring_reports" mkdir monitoring_reports
if not exist "logs" mkdir logs

echo.
echo ✅ Monitoring dependencies installed successfully!
echo.
echo Available monitoring tools:
echo - run-system-monitor.bat (Interactive menu)
echo - system_monitor.py (Comprehensive Python monitor)
echo - continuous_monitor.py (Background monitoring)
echo - quick-monitor.ps1 (PowerShell quick check)
echo.
echo Run 'run-system-monitor.bat' to start monitoring.
pause 