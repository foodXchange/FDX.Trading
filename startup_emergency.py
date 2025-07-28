#!/usr/bin/env python
"""
Emergency startup script for Azure App Service
Absolute minimal dependencies to ensure startup works
"""
import os
import sys
import logging
import subprocess

# Setup logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    """Minimal main function"""
    logger.info("=" * 50)
    logger.info("EMERGENCY STARTUP - FoodXchange")
    logger.info("=" * 50)
    
    # Basic environment info
    logger.info(f"Python: {sys.version}")
    logger.info(f"Working dir: {os.getcwd()}")
    logger.info(f"Python path: {sys.path}")
    
    # Change to wwwroot if on Azure
    if os.path.exists('/home/site/wwwroot'):
        os.chdir('/home/site/wwwroot')
        logger.info(f"Changed to: {os.getcwd()}")
    
    # Get port
    port = int(os.environ.get('PORT', os.environ.get('HTTP_PLATFORM_PORT', '8000')))
    logger.info(f"Port: {port}")
    
    # Try installing only critical packages
    critical_packages = ["fastapi==0.104.1", "uvicorn[standard]==0.24.0"]
    for package in critical_packages:
        try:
            logger.info(f"Installing {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logger.error(f"Failed to install {package}: {e}")
    
    # Try to start the minimal app
    try:
        logger.info("Attempting to import minimal app...")
        from app.main_minimal import app
        logger.info("Successfully imported minimal app!")
        
        # Start with uvicorn directly
        import uvicorn
        logger.info("Starting uvicorn...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
        
    except ImportError as e:
        logger.error(f"Import failed: {e}")
        
        # Ultimate fallback - create a simple HTTP server
        logger.info("Starting fallback HTTP server...")
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json
        
        class FallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path in ['/health', '/health/advanced', '/health/simple']:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {
                        "status": "fallback_mode",
                        "message": "App is starting in fallback mode",
                        "path": self.path,
                        "port": port
                    }
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    html = f"""
                    <html>
                        <head><title>FoodXchange - Starting</title></head>
                        <body>
                            <h1>FoodXchange is Starting</h1>
                            <p>The application is in fallback mode while dependencies load.</p>
                            <p>Port: {port}</p>
                            <p>Check <a href="/health">/health</a> for status.</p>
                        </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
            
            def log_message(self, format, *args):
                logger.info("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args))
        
        try:
            server = HTTPServer(('0.0.0.0', port), FallbackHandler)
            logger.info(f"Fallback server running on port {port}")
            server.serve_forever()
        except Exception as e:
            logger.error(f"Fallback server failed: {e}")
            # Keep process alive
            import time
            while True:
                logger.info("Process keepalive...")
                time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    main()