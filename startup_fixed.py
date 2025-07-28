#!/usr/bin/env python3
import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("=== FoodXchange Starting ===")
logger.info(f"Python: {sys.version}")
logger.info(f"Working Directory: {os.getcwd()}")

# Ensure we're in the right directory
if os.path.exists("/home/site/wwwroot"):
    os.chdir("/home/site/wwwroot")
    sys.path.insert(0, "/home/site/wwwroot")
    logger.info("Changed to /home/site/wwwroot")

# Install critical packages if missing
def ensure_package(package_name, package_spec):
    try:
        __import__(package_name)
        logger.info(f"✓ {package_name} is available")
    except ImportError:
        logger.info(f"Installing {package_spec}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_spec])

# Ensure critical packages
ensure_package("fastapi", "fastapi==0.104.1")
ensure_package("uvicorn", "uvicorn[standard]==0.24.0")
ensure_package("jinja2", "jinja2==3.1.2")
ensure_package("dotenv", "python-dotenv==1.0.0")

# Import the app
try:
    # Add app directory to path
    app_path = os.path.join(os.getcwd(), "app")
    if os.path.exists(app_path):
        sys.path.insert(0, app_path)
    
    from app.main import app
    logger.info("✓ Successfully imported app")
    
    # Verify Azure OpenAI configuration
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if api_key and endpoint and deployment:
        logger.info(f"✓ Azure OpenAI configured: {endpoint}")
    else:
        logger.warning("⚠ Azure OpenAI not fully configured")
    
    # Run with uvicorn
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    
except Exception as e:
    logger.error(f"Failed to start main app: {e}")
    import traceback
    traceback.print_exc()
    
    # Create minimal fallback app
    logger.info("Starting fallback app...")
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return JSONResponse({
            "status": "fallback",
            "message": "FoodXchange is starting up",
            "error": str(e)
        })
    
    @app.get("/health")
    async def health():
        return JSONResponse({
            "status": "fallback",
            "healthy": False,
            "error": str(e)
        })
    
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)