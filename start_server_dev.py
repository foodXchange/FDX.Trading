#!/usr/bin/env python3
"""
Development server startup script for FoodXchange
Binds to localhost only for security
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ.setdefault("PYTHONPATH", str(project_root))
os.environ.setdefault("ENVIRONMENT", "development")

# Import and run the FastAPI app
from foodxchange.main import app

if __name__ == "__main__":
    import uvicorn
    
    print("Starting FoodXchange Development Server...")
    print("Project root:", project_root)
    print("Server will be available at: http://localhost:8003")
    print("Health check: http://localhost:8003/health")
    print("Dashboard: http://localhost:8003/dashboard")
    print("Product Analysis: http://localhost:8003/product-analysis/")
    print("Search API: http://localhost:8003/api/search/")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(
        "foodxchange.main:app",
        host="127.0.0.1",  # Localhost only for development
        port=8003,
        reload=True,
        log_level="info"
    )