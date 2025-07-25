#!/usr/bin/env python
"""
Bulletproof startup script for Azure App Service
This handles all common deployment issues
"""
import os
import sys
import subprocess
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get port from environment
PORT = int(os.environ.get("PORT", 8000))
HOST = "0.0.0.0"

logger.info(f"Starting FoodXchange on {HOST}:{PORT}")

# Method 1: Try with gunicorn (production)
try:
    logger.info("Attempting to start with gunicorn...")
    cmd = [
        "gunicorn",
        "-w", "2",
        "-k", "uvicorn.workers.UvicornWorker",
        "app:app",
        "--bind", f"{HOST}:{PORT}",
        "--timeout", "600",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "--log-level", "info"
    ]
    logger.info(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
except Exception as e:
    logger.error(f"Gunicorn failed: {e}")
    
    # Method 2: Try with uvicorn directly
    try:
        logger.info("Falling back to uvicorn...")
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app:app",
            "--host", HOST,
            "--port", str(PORT),
            "--log-level", "info"
        ]
        logger.info(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except Exception as e:
        logger.error(f"Uvicorn failed: {e}")
        
        # Method 3: Run minimal app
        logger.info("Falling back to minimal app...")
        cmd = [
            sys.executable,
            "app_minimal.py"
        ]
        subprocess.run(cmd, check=True)