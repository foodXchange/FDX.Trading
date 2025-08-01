#!/usr/bin/env python3
"""
FoodXchange Development Server
Starts the development server with auto-reload on port 9000
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import uvicorn
        print("✅ uvicorn is installed")
    except ImportError:
        print("❌ uvicorn not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "uvicorn[standard]"], check=True)
        print("✅ uvicorn installed successfully")

def setup_environment():
    """Setup development environment variables"""
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')
    os.environ.setdefault('PORT', '9000')
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent.absolute()
    sys.path.insert(0, str(current_dir))
    
    print(f"✅ Environment setup complete")
    print(f"   - FLASK_ENV: {os.environ.get('FLASK_ENV')}")
    print(f"   - FLASK_DEBUG: {os.environ.get('FLASK_DEBUG')}")
    print(f"   - PORT: {os.environ.get('PORT')}")

def start_fastapi_server(port=9000, host="0.0.0.0", reload=True):
    """Start FastAPI server with uvicorn"""
    print(f"🚀 Starting FastAPI server on {host}:{port}")
    print(f"   - Auto-reload: {'enabled' if reload else 'disabled'}")
    print(f"   - Server URL: http://localhost:{port}")
    print("   - Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        import uvicorn
        uvicorn.run(
            "foodxchange.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def start_flask_server(port=9000, host="0.0.0.0", debug=True):
    """Start Flask server"""
    print(f"🚀 Starting Flask server on {host}:{port}")
    print(f"   - Debug mode: {'enabled' if debug else 'disabled'}")
    print(f"   - Server URL: http://localhost:{port}")
    print("   - Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        os.environ['PORT'] = str(port)
        os.environ['FLASK_DEBUG'] = '1' if debug else '0'
        
        # Import and run Flask app
        from app import app
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Start FoodXchange development server")
    parser.add_argument("--port", type=int, default=9000, help="Port to run server on (default: 9000)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    parser.add_argument("--flask", action="store_true", help="Use Flask instead of FastAPI")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("FoodXchange Development Server")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not args.flask:
        check_dependencies()
    
    # Start appropriate server
    if args.flask:
        start_flask_server(port=args.port, host=args.host, debug=not args.no_reload)
    else:
        start_fastapi_server(port=args.port, host=args.host, reload=not args.no_reload)

if __name__ == "__main__":
    main() 