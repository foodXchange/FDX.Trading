#!/usr/bin/env python
"""
Azure startup script that ensures database is initialized
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize database on first run
try:
    logger.info("Checking database initialization...")
    from init_db import init_database
    init_database()
except Exception as e:
    logger.error(f"Database initialization error: {e}")
    # Continue anyway - the app might work with existing DB

# Start the FastAPI app
try:
    logger.info("Starting FastAPI application...")
    from app.main import app
    
    # Run with uvicorn
    if __name__ == "__main__":
        import uvicorn
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"Starting server on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
        
except Exception as e:
    logger.error(f"Failed to start FastAPI: {e}")
    logger.info("Falling back to simple WSGI...")
    
    # Fallback WSGI app
    def application(environ, start_response):
        path = environ.get('PATH_INFO', '/')
        
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [f"""
        <html>
        <body style="font-family: Arial; padding: 50px;">
            <h1>🍎 FoodXchange</h1>
            <p style="color: red;">Application Error:</p>
            <pre>{str(e)}</pre>
            <p>Please check the logs for more details.</p>
        </body>
        </html>
        """.encode()]
    
    # For gunicorn
    app = application
    
    if __name__ == "__main__":
        from wsgiref.simple_server import make_server
        port = int(os.environ.get("PORT", 8000))
        httpd = make_server('0.0.0.0', port, application)
        httpd.serve_forever()