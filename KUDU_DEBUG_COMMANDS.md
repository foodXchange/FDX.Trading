# Azure Kudu Console Debug Commands

Access the Kudu console at: `https://[your-app-name].scm.azurewebsites.net/DebugConsole`

## Essential Debugging Commands

### 1. Check Current Status
```bash
# Navigate to site root
cd D:\home\site\wwwroot

# Check if files exist
dir
ls -la

# Check Python version and path
D:\home\python3125x64\python.exe --version
where python

# Check current processes
tasklist | findstr python
```

### 2. Check Log Files
```bash
# View current Python logs
type D:\home\LogFiles\python.log

# View recent application logs
type D:\home\LogFiles\Application\*.log

# View HTTP platform logs
dir D:\home\LogFiles\http*
```

### 3. Test Python Import Chain
```bash
# Test basic Python functionality
D:\home\python3125x64\python.exe -c "import sys; print(sys.version); print(sys.path)"

# Test FastAPI import
D:\home\python3125x64\python.exe -c "import fastapi; print('FastAPI OK')"

# Test minimal app import
D:\home\python3125x64\python.exe -c "from app.main_minimal import app; print('Minimal app OK')"

# Test original app import
D:\home\python3125x64\python.exe -c "from app.main import app; print('Full app OK')"
```

### 4. Check Environment Variables
```bash
# Check critical environment variables
echo %PORT%
echo %HTTP_PLATFORM_PORT%
echo %SENTRY_DSN%
echo %DATABASE_URL%

# List all environment variables
set
```

### 5. Manual Package Installation
```bash
# Install critical packages manually
D:\home\python3125x64\python.exe -m pip install fastapi==0.104.1
D:\home\python3125x64\python.exe -m pip install uvicorn[standard]==0.24.0
D:\home\python3125x64\python.exe -m pip install gunicorn==21.2.0

# List installed packages
D:\home\python3125x64\python.exe -m pip list
```

### 6. Test Health Endpoints Directly
```bash
# Start the emergency startup script manually
D:\home\python3125x64\python.exe D:\home\site\wwwroot\startup_emergency.py

# In another console window, test the endpoint
curl http://localhost:%HTTP_PLATFORM_PORT%/health
curl http://localhost:%HTTP_PLATFORM_PORT%/health/advanced
```

### 7. File Verification
```bash
# Check if required files exist
dir app\main_minimal.py
dir startup_emergency.py
dir web.config
dir requirements.txt

# Check file sizes (empty files indicate issues)
dir /S app\*.py
```

### 8. Clean Restart Process
```bash
# Kill any running Python processes
taskkill /F /IM python.exe

# Clear any cached Python files
del /S /Q __pycache__
del /S /Q *.pyc

# Restart the web app from Azure portal
# Site -> Restart
```

## Troubleshooting Common Issues

### Issue: Import Errors
**Solution**: Check if the file exists and has proper permissions
```bash
type app\main_minimal.py | head -10
icacls app\main_minimal.py
```

### Issue: Port Binding Errors
**Solution**: Check if port is available and properly set
```bash
netstat -an | findstr %HTTP_PLATFORM_PORT%
echo %HTTP_PLATFORM_PORT%
```

### Issue: Package Installation Failures
**Solution**: Use specific package versions and check pip
```bash
D:\home\python3125x64\python.exe -m pip install --upgrade pip
D:\home\python3125x64\python.exe -m pip install --no-cache-dir fastapi==0.104.1
```

## Quick Health Check Script

Create and run this script in Kudu console:

```bash
echo @echo off > quick_check.bat
echo echo === QUICK HEALTH CHECK === >> quick_check.bat
echo echo Python Version: >> quick_check.bat
echo D:\home\python3125x64\python.exe --version >> quick_check.bat
echo echo Port: %HTTP_PLATFORM_PORT% >> quick_check.bat
echo echo Files Check: >> quick_check.bat
echo dir startup_emergency.py >> quick_check.bat
echo dir app\main_minimal.py >> quick_check.bat
echo echo Recent Logs: >> quick_check.bat
echo type D:\home\LogFiles\python.log ^| tail -20 >> quick_check.bat
echo echo === END CHECK === >> quick_check.bat

quick_check.bat
```