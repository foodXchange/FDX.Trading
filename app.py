"""
Azure App Service entry point for FoodXchange
This file is used by Azure to start the application
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the FastAPI app
    from app.main import app
    logger.info("Successfully imported FastAPI app")
except Exception as e:
    logger.error(f"Failed to import app: {e}")
    # Create a minimal app if import fails
    from fastapi import FastAPI
    app = FastAPI(title="FoodXchange")
    
    @app.get("/")
    async def root():
        return {"error": f"Application failed to load: {str(e)}", "status": "error"}
    
    @app.get("/health")
    async def health():
        return {"status": "unhealthy", "error": str(e)}

# This allows Azure to find the app
application = app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting app on port {port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False) 