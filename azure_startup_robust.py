#!/usr/bin/env python
"""
Robust Azure startup script with comprehensive error handling
"""
import os
import sys
import logging
import traceback
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('startup.log')
    ]
)
logger = logging.getLogger(__name__)

def create_fallback_app():
    """Create a fallback WSGI app when FastAPI fails"""
    def application(environ, start_response):
        path = environ.get('PATH_INFO', '/')
        
        if path == '/':
            start_response('200 OK', [('Content-Type', 'text/html')])
            return ["""
            <html>
            <head>
                <title>FoodXchange - Maintenance Mode</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 50px; text-align: center; }
                    .container { max-width: 600px; margin: 0 auto; }
                    .status { background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 10px; margin: 20px 0; }
                    .error { background: #f8d7da; border: 1px solid #f5c6cb; padding: 20px; border-radius: 10px; margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>FoodXchange</h1>
                    <div class="status">
                        <h2>Application in Maintenance Mode</h2>
                        <p>The application is running but some features may be limited due to database connection issues.</p>
                        <p>Our team is working to resolve this. Please try again in a few minutes.</p>
                    </div>
                    <div class="error">
                        <h3>Technical Details:</h3>
                        <p>Database connection issues detected. Application running in fallback mode.</p>
                    </div>
                    <p><a href="/health">Health Check</a> | <a href="/status">System Status</a></p>
                </div>
            </body>
            </html>
            """.encode()]
        
        elif path == '/health':
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [b'{"status": "degraded", "message": "Application running in fallback mode", "database": "unavailable"}']
        
        elif path == '/status':
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [b'{"status": "maintenance", "database": "unavailable", "features": "limited"}']
        
        else:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'Not Found']
    
    return application

def main():
    """Main startup function with comprehensive error handling"""
    logger.info("Starting FoodXchange application...")
    
    # Step 1: Try to import and start FastAPI app
    try:
        logger.info("Attempting to start FastAPI application...")
        
        # Import the enhanced database configuration
        try:
            from app.database_enhanced import verify_database_connection
            if not verify_database_connection():
                logger.warning("Database connection failed, but continuing...")
        except Exception as e:
            logger.warning(f"Database verification failed: {e}")
        
        # Try to import the main app
        from app.main import app
        logger.info("FastAPI app imported successfully!")
        
        # Start the server
        if __name__ == "__main__":
            import uvicorn
            port = int(os.environ.get("PORT", 8000))
            logger.info(f"Starting FastAPI server on port {port}")
            uvicorn.run(app, host="0.0.0.0", port=port)
        
        return app
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.info("Falling back to WSGI application...")
        return create_fallback_app()
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        logger.info("Falling back to WSGI application...")
        return create_fallback_app()

# Create the application
app = main()

# For WSGI servers
if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting WSGI server on port {port}")
    httpd = make_server('0.0.0.0', port, app)
    httpd.serve_forever()
