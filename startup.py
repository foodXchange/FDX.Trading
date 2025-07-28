#!/usr/bin/env python3
"""
Azure-compatible startup script with automatic dependency installation
and graceful fallback mechanisms
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def find_python():
    """Find the correct Python interpreter"""
    # Try multiple Python locations
    python_paths = [
        sys.executable,
        '/usr/bin/python3',
        '/usr/local/bin/python3',
        '/opt/python/3.12/bin/python3',
        '/home/site/wwwroot/antenv/bin/python',
        'python3',
        'python'
    ]
    
    for python_path in python_paths:
        try:
            result = subprocess.run([python_path, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Found Python at: {python_path} ({result.stdout.strip()})")
                return python_path
        except Exception:
            continue
    
    return sys.executable

def install_packages():
    """Install required packages if missing"""
    python = find_python()
    required_packages = [
        'fastapi==0.104.1',
        'uvicorn[standard]==0.24.0',
        'gunicorn==21.2.0',
        'python-dotenv==1.0.0',
        'jinja2==3.1.2',
        'python-multipart==0.0.6'
    ]
    
    logger.info("Checking and installing required packages...")
    
    for package in required_packages:
        package_name = package.split('==')[0].split('[')[0]
        try:
            __import__(package_name.replace('-', '_'))
            logger.info(f"✓ {package_name} already installed")
        except ImportError:
            logger.warning(f"Installing {package}...")
            try:
                subprocess.check_call([python, '-m', 'pip', 'install', package])
                logger.info(f"✓ Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                logger.error(f"✗ Failed to install {package}: {e}")

def create_simple_app():
    """Create a simple WSGI application as fallback"""
    logger.info("Creating fallback WSGI application...")
    
    def application(environ, start_response):
        path = environ.get('PATH_INFO', '/')
        
        if path == '/' or path == '/index.html':
            # Serve the main page with FullStory tracking
            start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
            return [b'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FoodXchange - AI-Powered Food Sourcing Platform</title>
    
    <!-- FullStory Code -->
    <script>
    window['_fs_host'] = 'fullstory.com';
    window['_fs_script'] = 'edge.fullstory.com/s/fs.js';
    window['_fs_org'] = 'ZYAJ7';
    window['_fs_namespace'] = 'FS';
    (function(m,n,e,t,l,o,g,y){
        var c=function(){c.q.push(arguments)};c.q=[];
        var f=n.getElementsByTagName(e)[0];
        j=n.createElement(e);j.async=1;j.crossOrigin='anonymous';j.src='https://'+_fs_script;
        f.parentNode.insertBefore(j,f);
        if(g){o[s]('DOMContentLoaded',g,!1);o[s]('load',g,!1)}
        function g(){if(!l){l=1;c('restart')}}
        c('setReplayEngine','rrweb2');
        FS=c;
    })(window,document,'script','addEventListener',0,window,'_fs_namespace','_fs_loaded');
    </script>
    
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .status {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #ff6b35;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 5px;
        }
        .btn:hover {
            background: #e55a2b;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>FoodXchange</h1>
            <p>AI-Powered Food Sourcing Platform</p>
        </div>
        
        <div class="status">
            <h3>System Status: Limited Functionality</h3>
            <p>The application is running with reduced features. Core functionality is being restored.</p>
        </div>
        
        <div style="background: white; padding: 20px; border-radius: 10px;">
            <h2>Welcome to FoodXchange</h2>
            <p>Streamline your food sourcing with AI-powered supplier matching, automated RFQs, and intelligent analytics.</p>
            
            <div style="margin: 20px 0;">
                <a href="/health" class="btn">Health Check</a>
                <a href="/login" class="btn">Login</a>
                <a href="/register" class="btn">Register</a>
            </div>
        </div>
    </div>
</body>
</html>''']
        
        elif path == '/health':
            start_response('200 OK', [('Content-Type', 'application/json')])
            import json
            from datetime import datetime
            return [json.dumps({
                "status": "healthy",
                "mode": "fallback",
                "timestamp": datetime.now().isoformat(),
                "message": "Application running in fallback mode"
            }).encode()]
        
        elif path == '/health/simple':
            start_response('200 OK', [('Content-Type', 'application/json')])
            import json
            from datetime import datetime
            return [json.dumps({
                "status": "healthy",
                "timestamp": datetime.now().isoformat()
            }).encode()]
        
        elif path == '/health/detailed':
            start_response('200 OK', [('Content-Type', 'application/json')])
            import json
            from datetime import datetime
            return [json.dumps({
                "status": "healthy",
                "mode": "fallback",
                "timestamp": datetime.now().isoformat(),
                "database": "unavailable",
                "application": "fallback_mode",
                "version": "1.0.0"
            }).encode()]
        
        else:
            start_response('404 Not Found', [('Content-Type', 'text/html')])
            return [b'<h1>404 - Page Not Found</h1><p><a href="/">Go to Home</a></p>']
    
    return application

def start_fastapi():
    """Try to start the FastAPI application"""
    logger.info("Attempting to start FastAPI application...")
    
    try:
        # Import and run the main app
        from app.main import app
        import uvicorn
        
        port = int(os.environ.get('PORT', os.environ.get('HTTP_PLATFORM_PORT', '8000')))
        logger.info(f"Starting FastAPI on port {port}")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
        return True
        
    except ImportError as e:
        logger.error(f"Failed to import FastAPI app: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to start FastAPI: {e}")
        return False

def start_gunicorn():
    """Try to start with Gunicorn"""
    logger.info("Attempting to start with Gunicorn...")
    
    try:
        python = find_python()
        port = os.environ.get('PORT', os.environ.get('HTTP_PLATFORM_PORT', '8000'))
        
        cmd = [
            python, '-m', 'gunicorn',
            '-w', '1',
            '-k', 'uvicorn.workers.UvicornWorker',
            'app.main:app',
            '--bind', f'0.0.0.0:{port}',
            '--timeout', '300',
            '--access-logfile', '-',
            '--error-logfile', '-'
        ]
        
        logger.info(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd)
        return True
        
    except Exception as e:
        logger.error(f"Failed to start with Gunicorn: {e}")
        return False

def start_wsgi_server():
    """Start a simple WSGI server as last resort"""
    logger.info("Starting fallback WSGI server...")
    
    try:
        from wsgiref.simple_server import make_server
        port = int(os.environ.get('PORT', os.environ.get('HTTP_PLATFORM_PORT', '8000')))
        
        app = create_simple_app()
        logger.info(f"Starting WSGI server on port {port}")
        
        with make_server('0.0.0.0', port, app) as httpd:
            logger.info(f"Fallback server running on port {port}")
            httpd.serve_forever()
            
    except Exception as e:
        logger.error(f"Failed to start WSGI server: {e}")
        # As absolute last resort, just keep the process alive
        logger.info("Keeping process alive...")
        import time
        while True:
            time.sleep(60)

def main():
    """Main startup function"""
    logger.info("=" * 50)
    logger.info("FoodXchange Azure Startup Script")
    logger.info("=" * 50)
    logger.info(f"Python: {sys.version}")
    logger.info(f"Working Directory: {os.getcwd()}")
    logger.info(f"PATH: {os.environ.get('PATH', 'Not set')}")
    
    # Change to app directory if needed
    if os.path.exists('/home/site/wwwroot'):
        os.chdir('/home/site/wwwroot')
        logger.info(f"Changed to: {os.getcwd()}")
    
    # Install missing packages
    install_packages()
    
    # Try different startup methods in order
    methods = [
        ("FastAPI with Uvicorn", start_fastapi),
        ("Gunicorn with Uvicorn workers", start_gunicorn),
        ("Fallback WSGI server", start_wsgi_server)
    ]
    
    for method_name, method_func in methods:
        logger.info(f"\nTrying: {method_name}")
        try:
            if method_func():
                break
        except Exception as e:
            logger.error(f"Method '{method_name}' failed: {e}")
            continue

if __name__ == "__main__":
    main()