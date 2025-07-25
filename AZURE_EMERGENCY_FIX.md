# Azure Emergency Deployment Fix

## Files Created (in order of priority):

1. **main.py** - Simplest possible WSGI app
2. **application.py** - Standard WSGI application  
3. **wsgi.py** - Gunicorn-compatible WSGI
4. **hostingstart.py** - Azure default file
5. **diagnose.py** - Diagnostic tool
6. **index.php** - PHP fallback to test server
7. **server.js** - Node.js fallback

## Startup Commands to Try (in Azure Configuration):

1. `gunicorn --bind=0.0.0.0:8000 main:application`
2. `python main.py`
3. `python application.py`
4. `gunicorn --bind=0.0.0.0:8000 wsgi:application`
5. `python -m http.server 8000` (ultra fallback)

## Azure Portal Settings Required:

### Configuration > General settings:
- **Stack**: Python
- **Major version**: Python 3
- **Minor version**: Python 3.12
- **Startup Command**: `gunicorn --bind=0.0.0.0:8000 main:application`

### Configuration > Application settings:
Add these:
- `SCM_DO_BUILD_DURING_DEPLOYMENT` = `true`
- `WEBSITE_RUN_FROM_PACKAGE` = `0`
- `WEBSITES_ENABLE_APP_SERVICE_STORAGE` = `true`
- `WEBSITES_PORT` = `8000`

## Quick Test Steps:

1. **Push all files** to your repository
2. **In Azure Portal**:
   - Go to your App Service
   - Deployment Center > Logs
   - Check if deployment succeeded
   
3. **If deployment succeeded but app won't start**:
   - Go to "Advanced Tools" > "Go"
   - In Kudu, select "Debug console" > "CMD"
   - Navigate to `site/wwwroot`
   - Run: `python main.py`
   - See what error appears

4. **Check Log Stream**:
   - In Azure Portal > Log stream
   - Look for specific Python errors

## If Nothing Works:

1. In Azure Portal, try changing the startup command to just:
   ```
   python -c "from http.server import HTTPServer, BaseHTTPRequestHandler; HTTPServer(('', 8000), BaseHTTPRequestHandler).serve_forever()"
   ```

2. This will run a basic HTTP server to confirm Python works

3. Then gradually work up to the full app

## The main.py file is the most basic possible - it SHOULD work if:
- Python is installed
- Port 8000 is accessible  
- The file is in the right location