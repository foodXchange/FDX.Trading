@echo off
echo Starting Azure Continuous Monitor...
echo ==================================================
echo.
echo The monitor will check your app every 60 seconds and automatically:
echo - Restart the app if it crashes
echo - Scale up if memory issues occur
echo - Fix deployment issues
echo - Send notifications on critical errors
echo.
echo Press Ctrl+C to stop monitoring
echo.
python azure_continuous_monitor.py