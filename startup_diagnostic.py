#!/usr/bin/env python
"""Diagnostic startup script for Azure"""
import os
import sys
import subprocess

print("=== FoodXchange Diagnostic Startup ===")
print(f"Python: {sys.version}")
print(f"Working Directory: {os.getcwd()}")

# Set environment variable to track deployment
os.environ["DEPLOYMENT_TIME"] = "2025-07-27T16:30:00Z"

# Try to run the diagnostic app
try:
    port = int(os.environ.get("PORT", 8000))
    cmd = f"gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main_diagnostic:app --bind 0.0.0.0:{port} --timeout 300"
    print(f"Starting with command: {cmd}")
    subprocess.run(cmd, shell=True)
except Exception as e:
    print(f"ERROR: Failed to start - {e}")
    # Fallback to simple uvicorn
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main_diagnostic:app", "--host", "0.0.0.0", "--port", str(port)])