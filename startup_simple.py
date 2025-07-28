#!/usr/bin/env python3
"""
Simple Azure App Service Startup Script
"""

import os
import sys
import subprocess

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Start the FastAPI application using subprocess"""
    
    # Get port from environment variable (Azure sets this)
    port = os.environ.get("PORT", "8000")
    
    # Set environment variables for production
    os.environ.setdefault("ENVIRONMENT", "production")
    os.environ.setdefault("DEBUG", "False")
    
    print(f"Starting FoodXchange server on port {port}")
    
    # Run uvicorn as a subprocess
    cmd = [
        sys.executable, "-m", "uvicorn",
        "foodxchange.main:app",
        "--host", "0.0.0.0",
        "--port", port,
        "--log-level", "info"
    ]
    
    subprocess.run(cmd)

if __name__ == "__main__":
    main()