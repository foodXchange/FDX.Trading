#!/usr/bin/env python
"""Minimal startup script for Azure App Service"""
import os
import sys
import subprocess

print("Starting minimal FoodXchange app...")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")

# Ensure we're in the right directory
if os.path.exists('/home/site/wwwroot'):
    os.chdir('/home/site/wwwroot')
    print(f"Changed to: {os.getcwd()}")

# Install minimal requirements
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "gunicorn"])
    print("Installed minimal requirements")
except Exception as e:
    print(f"Failed to install packages: {e}")

# Start with gunicorn
port = int(os.environ.get('PORT', os.environ.get('HTTP_PLATFORM_PORT', '8000')))
print(f"Starting on port {port}")

try:
    # Use gunicorn with uvicorn worker
    cmd = [
        sys.executable, "-m", "gunicorn",
        "--bind", f"0.0.0.0:{port}",
        "--worker-class", "uvicorn.workers.UvicornWorker",
        "--workers", "1",
        "--timeout", "600",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "app.main:app"
    ]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)
except Exception as e:
    print(f"Failed to start: {e}")
    # Keep process alive
    import time
    while True:
        time.sleep(60)