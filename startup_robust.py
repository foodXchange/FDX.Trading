#!/usr/bin/env python
"""
Robust Azure startup script that ensures all dependencies are installed
"""
import subprocess
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def install_requirements():
    """Install all requirements from requirements.txt"""
    logger.info("Installing requirements from requirements.txt...")
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install all requirements
        if os.path.exists("requirements.txt"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            logger.info("Successfully installed all requirements")
        else:
            logger.error("requirements.txt not found!")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install requirements: {e}")
        # Try installing critical packages individually
        critical_packages = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0",
            "gunicorn==21.2.0",
            "pandas==2.2.2",
            "jinja2==3.1.2",
            "python-multipart==0.0.6",
            "python-dotenv==1.0.0"
        ]
        
        for package in critical_packages:
            try:
                logger.info(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except:
                logger.error(f"Failed to install {package}")

def verify_pandas():
    """Verify pandas is installed and working"""
    try:
        import pandas as pd
        logger.info(f"Pandas {pd.__version__} is installed and working")
        return True
    except ImportError:
        logger.error("Pandas import failed!")
        return False

def main():
    """Main startup function"""
    logger.info("=" * 60)
    logger.info("FoodXchange Robust Startup Script")
    logger.info("=" * 60)
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    # Change to correct directory if needed
    if os.path.exists('/home/site/wwwroot'):
        os.chdir('/home/site/wwwroot')
        logger.info(f"Changed to: {os.getcwd()}")
    
    # Install requirements
    install_requirements()
    
    # Verify pandas specifically
    if not verify_pandas():
        logger.error("Pandas verification failed, trying direct install...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas==2.2.2"])
            verify_pandas()
        except:
            logger.error("Failed to install pandas directly")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        if os.path.exists('.env'):
            load_dotenv('.env', override=False)
            logger.info("Loaded .env file")
    except ImportError:
        logger.warning("python-dotenv not available")
    
    # Get port
    port = int(os.environ.get('PORT', os.environ.get('HTTP_PLATFORM_PORT', '8000')))
    logger.info(f"Starting on port: {port}")
    
    # Try to start the application
    try:
        # Try importing the app first
        from app.main import app
        logger.info("Successfully imported FastAPI app")
        
        # Try with gunicorn
        logger.info("Starting with gunicorn...")
        cmd = [
            sys.executable, "-m", "gunicorn",
            "-w", "1",
            "-k", "uvicorn.workers.UvicornWorker",
            "app.main:app",
            "--bind", f"0.0.0.0:{port}",
            "--timeout", "300",
            "--access-logfile", "-",
            "--error-logfile", "-",
            "--log-level", "info"
        ]
        subprocess.run(cmd)
        
    except ImportError as e:
        logger.error(f"Failed to import app: {e}")
        logger.error("Trying direct uvicorn...")
        
        try:
            import uvicorn
            from app.main import app
            uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
        except Exception as e2:
            logger.error(f"All startup methods failed: {e2}")
            
            # Keep process alive
            logger.info("Keeping process alive for debugging...")
            import time
            while True:
                time.sleep(60)

if __name__ == "__main__":
    main()