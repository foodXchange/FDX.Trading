#!/usr/bin/env python3
"""
Root-level main.py for Azure App Service
This file imports and exposes the FastAPI app from the foodxchange module
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # Import the FastAPI app from foodxchange module
    from foodxchange.main import app
    logger.info("Successfully imported FastAPI app from foodxchange.main")
    
    # Make the app available at module level
    __all__ = ['app']
    
except ImportError as e:
    logger.error(f"Failed to import app from foodxchange.main: {e}")
    
    # Create a minimal FastAPI app as fallback
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="FoodXchange API - Startup Error")
    
    @app.get("/")
    async def root():
        return JSONResponse(
            content={
                "status": "error",
                "message": "Main application failed to load",
                "error": str(e),
                "suggestion": "Check Azure deployment logs for details"
            },
            status_code=503
        )
    
    @app.get("/health")
    async def health():
        return JSONResponse(
            content={
                "status": "unhealthy",
                "message": "Application startup failed",
                "error": str(e)
            },
            status_code=503
        )

# If running directly, start uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)