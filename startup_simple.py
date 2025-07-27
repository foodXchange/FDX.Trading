#!/usr/bin/env python
"""
Simple startup script for Azure App Service
Uses uvicorn directly for easier startup
"""
import os
import sys
import uvicorn

if __name__ == "__main__":
    # Get port from environment variable
    port = int(os.environ.get("PORT", 8000))
    
    # Import the FastAPI app
    from app.main import app
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 