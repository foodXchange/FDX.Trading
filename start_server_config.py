#!/usr/bin/env python3
"""
Configurable server startup script for FoodXchange
"""

import os
import sys
from pathlib import Path
import argparse

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ.setdefault("PYTHONPATH", str(project_root))

# Import and run the FastAPI app
from foodxchange.main import app

if __name__ == "__main__":
    import uvicorn
    
    parser = argparse.ArgumentParser(description='Start FoodXchange Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8003, help='Port to bind to (default: 8003)')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--production', action='store_true', help='Run in production mode')
    
    args = parser.parse_args()
    
    if args.production:
        os.environ["ENVIRONMENT"] = "production"
        reload = False
        log_level = "warning"
    else:
        os.environ["ENVIRONMENT"] = "development"
        reload = args.reload
        log_level = "info"
    
    print(f"Starting FoodXchange Server ({os.environ['ENVIRONMENT']} mode)...")
    print(f"Project root: {project_root}")
    print(f"Server will be available at: http://{args.host}:{args.port}")
    print(f"Health check: http://{args.host}:{args.port}/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(
        "foodxchange.main:app",
        host=args.host,
        port=args.port,
        reload=reload,
        log_level=log_level
    )