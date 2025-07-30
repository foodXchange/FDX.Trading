#!/usr/bin/env python3
"""
FoodXchange Server Runner
Updated startup script for current configuration
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Start the FoodXchange application"""
    
    # Get the current port from main.py configuration
    current_port = 8003  # Update this if port changes
    
    print("Starting FoodXchange - AI-Powered B2B Food Sourcing Platform")
    print("=" * 60)
    print("Application will be available at:")
    print(f"   - Main App: http://localhost:{current_port}")
    print(f"   - AI Analysis: http://localhost:{current_port}/product-analysis/")
    print(f"   - Dashboard: http://localhost:{current_port}/dashboard")
    print(f"   - API Docs: http://localhost:{current_port}/docs")
    print("=" * 60)
    print("Features:")
    print("   - AI Product Analysis with Hebrew language support")
    print("   - Machine Learning from user corrections")
    print("   - Real-time field editing")
    print("   - Multi-image analysis")
    print("   - Document generation (DOCX, PDF, HTML)")
    print("   - Email integration with Azure")
    print("=" * 60)
    
    try:
        # Start the FastAPI application
        uvicorn.run(
            "foodxchange.main:app",
            host="0.0.0.0",
            port=current_port,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nFoodXchange stopped. Goodbye!")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()