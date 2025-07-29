#!/usr/bin/env python3
"""
Simple server startup script
"""
import sys
import os

# Add the foodxchange directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'foodxchange'))

if __name__ == "__main__":
    try:
        import uvicorn
        from foodxchange.main import app
        
        print("Starting FoodXchange server...")
        print("Server will be available at: http://localhost:8000")
        print("Admin access: http://localhost:8000/admin")
        print("Press Ctrl+C to stop the server")
        
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError as e:
        print(f"Error: {e}")
        print("Please install required packages: pip install fastapi uvicorn")
    except Exception as e:
        print(f"Server error: {e}")