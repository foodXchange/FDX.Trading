#!/usr/bin/env python3
"""
Test script to verify the deployment configuration
"""
import os
import sys
import subprocess

def test_imports():
    """Test if all required imports work"""
    print("Testing imports...")
    
    try:
        import uvicorn
        print("✓ uvicorn imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import uvicorn: {e}")
        return False
    
    try:
        import fastapi
        print("✓ fastapi imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import fastapi: {e}")
        return False
    
    # Add current directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    try:
        from foodxchange.main import app
        print("✓ foodxchange.main imported successfully")
        print(f"  App type: {type(app)}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import foodxchange.main: {e}")
        
        try:
            import main
            print("✓ main module imported successfully")
            print(f"  App type: {type(main.app)}")
            return True
        except ImportError as e2:
            print(f"✗ Failed to import main: {e2}")
            return False

def test_startup_command():
    """Test the startup command"""
    print("\nTesting startup command...")
    
    # Simulate the PORT environment variable
    os.environ['PORT'] = '8000'
    
    # Test the uvicorn command
    cmd = ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--help"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Uvicorn command syntax is valid")
            return True
        else:
            print(f"✗ Uvicorn command failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Failed to run uvicorn command: {e}")
        return False

def main():
    print("FoodXchange Deployment Test")
    print("=" * 40)
    
    # Test imports
    import_success = test_imports()
    
    # Test startup command
    command_success = test_startup_command()
    
    print("\n" + "=" * 40)
    if import_success and command_success:
        print("✓ All tests passed! Deployment should work.")
    else:
        print("✗ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()