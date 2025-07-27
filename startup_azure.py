#!/usr/bin/env python
"""Simple startup script for Azure App Service"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger.info("Starting FoodXchange application...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")

# Import and run with gunicorn
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    
    # Use gunicorn directly
    os.system(f"gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:{port} --timeout 600")