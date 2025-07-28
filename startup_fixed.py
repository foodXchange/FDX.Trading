#!/usr/bin/env python3
"""
Azure App Service Startup Script - Fixed version that properly activates virtual environment
"""
import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def activate_virtual_environment():
    """Activate the antenv virtual environment created by Oryx"""
    venv_path = "/home/site/wwwroot/antenv"
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    # Add virtual environment site-packages to Python path
    site_packages = os.path.join(venv_path, "lib", f"python{python_version}", "site-packages")
    
    if os.path.exists(site_packages):
        logger.info(f"Adding {site_packages} to Python path")
        sys.path.insert(0, site_packages)
        return True
    else:
        logger.error(f"Virtual environment site-packages not found at: {site_packages}")
        # Try alternative paths
        alt_paths = [
            os.path.join(venv_path, "Lib", "site-packages"),  # Windows-style
            os.path.join(venv_path, "lib", "python3.12", "site-packages"),  # Hardcoded version
            "/opt/python/3.12.11/lib/python3.12/site-packages",  # System packages
        ]
        
        for path in alt_paths:
            if os.path.exists(path):
                logger.info(f"Found alternative path: {path}")
                sys.path.insert(0, path)
                return True
        
        return False

def main():
    """Main startup function"""
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    logger.info(f"Current directory: {current_dir}")
    
    # Activate virtual environment
    if not activate_virtual_environment():
        logger.warning("Could not activate virtual environment, proceeding with system packages")
    
    # Get port from environment
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Using port: {port}")
    
    try:
        # First try to import the minimal app (fallback)
        logger.info("Attempting to start minimal app...")
        import minimal_app
        
        # Run with uvicorn
        import uvicorn
        config = uvicorn.Config(
            app=minimal_app.app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True,
            use_colors=False
        )
        
        server = uvicorn.Server(config)
        logger.info(f"Starting minimal app on 0.0.0.0:{port}")
        server.run()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        
        # Ultimate fallback - basic HTTP server
        logger.info("Starting basic HTTP fallback server...")
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json
        
        class FallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "fallback",
                    "message": "Application running in fallback mode",
                    "error": str(e),
                    "path": self.path,
                    "python_path": sys.path
                }
                self.wfile.write(json.dumps(response, indent=2).encode())
            
            def do_HEAD(self):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
            
            def log_message(self, format, *args):
                logger.info("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format%args))
        
        server = HTTPServer(('0.0.0.0', port), FallbackHandler)
        logger.info(f"Fallback server listening on port {port}")
        server.serve_forever()

if __name__ == "__main__":
    main()