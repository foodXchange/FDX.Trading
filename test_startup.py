#!/usr/bin/env python3
"""Test if the application can start successfully"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing FoodXchange startup...")
    
    # Test imports
    print("1. Testing imports...")
    from app.main import app
    print("✓ Main app imported successfully")
    
    from app.database import engine
    print("✓ Database module imported successfully")
    
    from app.config import get_settings
    settings = get_settings()
    print(f"✓ Settings loaded successfully (environment: {settings.environment})")
    
    # Test database connection
    print("\n2. Testing database connection...")
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✓ Database connection successful")
    
    print("\n✅ All startup tests passed!")
    print("\nApplication should be able to start on Azure.")
    
except Exception as e:
    print(f"\n❌ Startup test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)