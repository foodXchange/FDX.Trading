"""
Azure App Service Startup Script for FoodXchange
This script ensures proper initialization and startup on Azure
"""
import os
import sys
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {current_dir}")
logger.info(f"Python path: {sys.path}")

# Check if running on Azure
is_azure = os.environ.get('WEBSITE_INSTANCE_ID') is not None
logger.info(f"Running on Azure: {is_azure}")

# Load environment variables
try:
    from dotenv import load_dotenv
    
    if os.path.exists('.env'):
        load_dotenv('.env', override=False)
        logger.info("Loaded .env file")
    
    if os.path.exists('.env.blob'):
        load_dotenv('.env.blob', override=True)
        logger.info("Loaded .env.blob file")
except ImportError:
    logger.warning("python-dotenv not available, skipping .env files")

# Verify critical environment variables
env_vars = {
    'DATABASE_URL': os.getenv('DATABASE_URL'),
    'AZURE_STORAGE_CONNECTION_STRING': os.getenv('AZURE_STORAGE_CONNECTION_STRING'),
    'AZURE_OPENAI_API_KEY': os.getenv('AZURE_OPENAI_API_KEY'),
    'SENTRY_DSN': os.getenv('SENTRY_DSN'),
    'SENTRY_ENVIRONMENT': os.getenv('SENTRY_ENVIRONMENT', 'production')
}

for var, value in env_vars.items():
    if value:
        logger.info(f"[OK] {var} is configured")
    else:
        logger.warning(f"[MISSING] {var} is NOT configured")

# Get port from environment
port = os.environ.get('PORT', os.environ.get('HTTP_PLATFORM_PORT', '8000'))
logger.info(f"Starting application on port {port}")

# Ensure gunicorn is available
try:
    import gunicorn
    logger.info("Gunicorn is available")
except ImportError:
    logger.error("Gunicorn is not installed!")
    sys.exit(1)

# Run the FastAPI app with gunicorn
cmd = [
    sys.executable, "-m", "gunicorn",
    "-w", "2",  # 2 workers for better performance
    "-k", "uvicorn.workers.UvicornWorker",
    "app.main:app",
    "--bind", f"0.0.0.0:{port}",
    "--timeout", "600",  # 10 minutes timeout
    "--access-logfile", "-",
    "--error-logfile", "-",
    "--log-level", "info",
    "--preload"  # Preload app for faster worker startup
]

logger.info(f"Starting Gunicorn with command: {' '.join(cmd)}")

try:
    # Use exec to replace the current process
    os.execvp(sys.executable, cmd)
except Exception as e:
    logger.error(f"Failed to start application: {e}", exc_info=True)
    sys.exit(1)