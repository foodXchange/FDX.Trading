#!/usr/bin/env python3
"""
Azure App Service Startup Script - Simplified for Azure
This ensures proper module imports and starts the FastAPI app
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
logger.info(f"Added {current_dir} to Python path")

# Import and run the app
try:
    logger.info("Starting FoodXchange application...")
    
    # Get port from environment
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Using port: {port}")
    
    # Import uvicorn and the app
    import uvicorn
    from foodxchange.main import app
    
    logger.info("Successfully imported FastAPI app")
    
    # Configure uvicorn
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True,
        use_colors=False  # Disable colors for Azure logs
    )
    
    # Create and run server
    server = uvicorn.Server(config)
    logger.info(f"Starting Uvicorn server on 0.0.0.0:{port}")
    server.run()
    
except Exception as e:
    logger.error(f"Failed to start application: {e}", exc_info=True)
    
    # Fallback to a simple server to prevent 503
    logger.info("Starting fallback server...")
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    
    class FallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "error",
                "message": f"Main application failed to start: {str(e)}",
                "startup_error": True,
                "path": self.path
            }
            self.wfile.write(json.dumps(response).encode())
        
        def log_message(self, format, *args):
            logger.info("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format%args))
    
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), FallbackHandler)
    logger.info(f"Fallback server listening on port {port}")
    server.serve_forever()