#!/usr/bin/env python
"""
Azure startup script with Alembic migration support
"""
import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_migrations():
    """Run Alembic migrations"""
    try:
        logger.info("Running database migrations...")
        
        # Check if migrations directory exists
        if not os.path.exists("migrations"):
            logger.warning("Migrations directory not found, skipping migrations")
            return
        
        # Run alembic upgrade to latest revision
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("Migrations completed successfully")
            logger.info(f"Output: {result.stdout}")
        else:
            logger.error(f"Migration failed: {result.stderr}")
            # Don't fail the startup - the app might still work
            
    except Exception as e:
        logger.error(f"Migration error: {e}")
        # Continue anyway - migrations might not be critical

def init_database_if_needed():
    """Initialize database tables if they don't exist"""
    try:
        logger.info("Checking database initialization...")
        from app.database import engine, Base
        from app.models import user, supplier, rfq, quote, email, product, activity_log
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created")
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        # Continue anyway - the app might work with existing DB

# Main startup sequence
try:
    # Step 1: Run migrations (if available)
    run_migrations()
    
    # Step 2: Ensure tables exist (fallback if migrations fail)
    init_database_if_needed()
    
    # Step 3: Start the FastAPI app
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
            <hr>
            <p>Environment:</p>
            <ul>
                <li>DATABASE_URL: {'Set' if os.getenv('DATABASE_URL') else 'Not Set'}</li>
                <li>Python Version: {sys.version}</li>
                <li>Working Directory: {os.getcwd()}</li>
            </ul>
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