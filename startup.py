#!/usr/bin/env python3
"""
Azure App Service Startup Script for FoodXchange
This script is used by Azure to start the FastAPI application
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Start the FastAPI application"""
    
    # Get port from environment variable (Azure sets this)
    port = int(os.environ.get("PORT", 8000))
    
    # Set environment variables for production
    os.environ.setdefault("ENVIRONMENT", "production")
    os.environ.setdefault("DEBUG", "False")
    
    # Import the FastAPI app
    try:
        from foodxchange.main import app
        print(f"✅ FastAPI app imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import FastAPI app: {e}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        sys.exit(1)
    
    # Start the server
    print(f"🚀 Starting FoodXchange server on port {port}")
    uvicorn.run(
        "foodxchange.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )

if __name__ == "__main__":
    main() 