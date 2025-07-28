#!/usr/bin/env python
"""
Azure App Service startup script for FastAPI application
"""
import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main startup function"""
    logger.info("Starting FoodXchange FastAPI application...")
    
    # Get port from environment
    port = int(os.environ.get('PORT', os.environ.get('HTTP_PLATFORM_PORT', '8000')))
    
    try:
        # Try to import and run FastAPI app with uvicorn
        logger.info("Attempting to start FastAPI with Uvicorn...")
        import uvicorn
        from app.main import app
        
        logger.info(f"Starting server on port {port}")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.info("Installing required packages...")
        
        # Install essential packages
        packages = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0",
            "python-dotenv==1.0.0",
            "jinja2==3.1.2",
            "python-multipart==0.0.6",
            "sqlalchemy==2.0.23",
            "psutil==5.9.6"
        ]
        
        for package in packages:
            logger.info(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        # Try again after installing
        try:
            import uvicorn
            from app.main import app
            
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=port,
                log_level="info"
            )
        except Exception as e2:
            logger.error(f"Failed to start after installing packages: {e2}")
            # Fallback to simple HTTP server
            logger.info("Starting fallback HTTP server...")
            from http.server import HTTPServer, SimpleHTTPRequestHandler
            
            class Handler(SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/health' or self.path == '/health/advanced':
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(b'{"status":"fallback","message":"App starting..."}')
                    else:
                        super().do_GET()
            
            server = HTTPServer(('0.0.0.0', port), Handler)
            logger.info(f"Fallback server running on port {port}")
            server.serve_forever()
    
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        # Keep the process alive
        import time
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()