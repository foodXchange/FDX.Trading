"""Test the main app with minimal configuration"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Disable middlewares for testing
os.environ["SECURITY_HEADERS_ENABLED"] = "false"
os.environ["RATE_LIMIT_ENABLED"] = "false"

from foodxchange.main import app
import uvicorn

# Remove all middlewares except CORS
print("Testing with minimal middleware configuration...")

if __name__ == "__main__":
    print("Starting server on http://localhost:8005")
    uvicorn.run(app, host="127.0.0.1", port=8005, log_level="debug")