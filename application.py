#!/usr/bin/env python
"""
Azure App Service emergency application starter with WSGI compatibility
"""
import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_emergency_app():
    """Create emergency WSGI application"""
    def application(environ, start_response):
        status = '200 OK'
        headers = [('Content-Type', 'text/html')]
        start_response(status, headers)
        
        html = b'''<!DOCTYPE html>
<html>
<head>
    <title>FoodXchange - Starting Up</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; }
        .status { color: #ff6b35; }
    </style>
</head>
<body>
    <h1>FoodXchange</h1>
    <p class="status">Application is starting up...</p>
    <p>This page will refresh automatically.</p>
</body>
</html>'''
        return [html]
    
    return application

# Install critical dependencies
try:
    logger.info("Checking dependencies...")
    import fastapi
    import uvicorn
except ImportError:
    logger.info("Installing missing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn[standard]", "gunicorn"])

# Try to create the application
try:
    logger.info("Loading FastAPI application...")
    from app.main import app
    logger.info("FastAPI app loaded successfully")
    
    # For WSGI compatibility
    application = app
    
except Exception as e:
    logger.error(f"Failed to load main app: {e}")
    logger.info("Running emergency fallback application")
    application = create_emergency_app()

# Direct execution
if __name__ == "__main__":
    logger.info("Starting application...")
    port = int(os.environ.get('PORT', os.environ.get('HTTP_PLATFORM_PORT', 8000)))
    
    if hasattr(application, '__call__') and not hasattr(application, 'run'):
        # WSGI app
        from wsgiref.simple_server import make_server
        with make_server('', port, application) as httpd:
            logger.info(f"Serving WSGI app on port {port}")
            httpd.serve_forever()
    else:
        # ASGI app
        import uvicorn
        uvicorn.run(application, host="0.0.0.0", port=port)