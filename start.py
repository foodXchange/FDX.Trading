#!/usr/bin/env python3
"""
FoodXchange - AI-Powered B2B Food Sourcing Platform
Simple startup script
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Start the FoodXchange application"""
    
    # Change to the foodxchange directory
    foodxchange_dir = Path(__file__).parent / "foodxchange"
    if not foodxchange_dir.exists():
        print("❌ Error: foodxchange directory not found!")
        print("Please run this script from the project root directory.")
        sys.exit(1)
    
    os.chdir(foodxchange_dir)
    
    print("🚀 Starting FoodXchange - AI-Powered B2B Food Sourcing Platform")
    print("=" * 60)
    print("📍 Application will be available at:")
    print("   • Main App: http://localhost:8000")
    print("   • AI Analysis: http://localhost:8000/product-analysis")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Dashboard: http://localhost:8000/dashboard")
    print("=" * 60)
    print("💡 Try the AI Product Analysis feature!")
    print("   Upload an image or search for products like 'Organic dried cranberries'")
    print("=" * 60)
    
    try:
        # Start the FastAPI application
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 FoodXchange stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()