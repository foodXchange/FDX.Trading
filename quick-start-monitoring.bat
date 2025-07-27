@echo off
echo ========================================
echo Food Xchange Monitoring Quick Start
echo ========================================
echo.

echo Step 1: Installing Azure Monitor dependencies...
pip install opencensus-ext-azure==1.1.12 opencensus-ext-fastapi==0.1.0 opencensus-ext-logging==0.1.0 opencensus-ext-requests==0.1.0 opencensus-ext-sqlalchemy==0.1.0

echo.
echo Step 2: Setting up Azure Monitor...
echo Please run the Azure Monitor setup script:
echo   .\setup_azure_monitor.ps1
echo.

echo Step 3: Testing the monitoring system...
echo Starting the application for testing...
echo.

REM Start the application in the background
start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

REM Wait for the app to start
timeout /t 5 /nobreak >nul

echo.
echo Testing monitoring endpoints...
echo.

REM Test health endpoint
echo Testing /health endpoint:
curl -s http://localhost:8000/health | python -m json.tool

echo.
echo Testing /monitoring/azure endpoint:
curl -s http://localhost:8000/monitoring/azure | python -m json.tool

echo.
echo Testing /monitoring/test endpoint:
curl -s http://localhost:8000/monitoring/test | python -m json.tool

echo.
echo ========================================
echo Quick Start Complete!
echo ========================================
echo.
echo Your monitoring system is now set up.
echo.
echo Available endpoints:
echo   - http://localhost:8000/system-status (Visual status dashboard)
echo   - http://localhost:8000/health (Health check)
echo   - http://localhost:8000/monitoring/azure (Azure Monitor status)
echo   - http://localhost:8000/monitoring/test (Test all monitoring)
echo.
echo To run system monitoring:
echo   .\run-system-monitor.bat
echo.
echo To stop the application, press Ctrl+C in the application window.
echo.
pause 