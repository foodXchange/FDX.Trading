#!/usr/bin/env python3
"""
Simple Azure App Service Startup Script
Direct import without module path issues
"""
import os
import sys
import logging
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
logger.info(f"Added {current_dir} to Python path")

try:
    # Get port from environment
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Using port: {port}")
    
    # Import the FastAPI app directly
    from foodxchange.main import app
    logger.info("Successfully imported FastAPI app")
    
    # Run uvicorn server
    logger.info(f"Starting Uvicorn server on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.info("Trying alternative import...")
    
    try:
        # Try importing from a flat structure
        import main
        app = main.app
        logger.info("Successfully imported app using alternative method")
        
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
        
    except Exception as e2:
        logger.error(f"Alternative import also failed: {e2}")
        
        # Start a minimal health check server
        logger.info("Starting minimal health check server...")
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json
        
        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "error",
                    "message": "Application failed to start - module import error",
                    "error": str(e),
                    "path": self.path
                }
                self.wfile.write(json.dumps(response).encode())
        
        port = int(os.environ.get('PORT', 8000))
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        logger.info(f"Health check server listening on port {port}")
        server.serve_forever()
        
except Exception as e:
    logger.error(f"Failed to start application: {e}", exc_info=True)
    raise