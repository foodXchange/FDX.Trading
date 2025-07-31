#!/usr/bin/env python3
"""
Fixed server startup script for FoodXchange
This script handles import issues and starts the server properly
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ.setdefault("PYTHONPATH", str(project_root))

# Import and run the FastAPI app
from foodxchange.main import app

if __name__ == "__main__":
    import uvicorn
    
    print("Starting FoodXchange Server...")
    print("Project root:", project_root)
    print("Python path:", sys.path[:3])
    print("Server will be available at: http://localhost:8003")
    print("Health check: http://localhost:8003/health")
    print("Dashboard: http://localhost:8003/dashboard")
    print("Product Analysis: http://localhost:8003/product-analysis/")
    print("Search API: http://localhost:8003/api/search/")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(
        "foodxchange.main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )