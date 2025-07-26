#!/usr/bin/env python3
"""
Check Python Architecture Script
This script helps determine if you're running 32-bit or 64-bit Python
"""

import platform
import sys
import struct

def check_python_architecture():
    """Check and display Python architecture information"""
    print("=== Python Architecture Check ===")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    
    # Check if it's 32-bit or 64-bit
    is_64bit = struct.calcsize("P") * 8 == 64
    print(f"\n=== Result ===")
    if is_64bit:
        print("✅ You are running 64-bit Python")
        print("   This is optimal for cryptography operations")
    else:
        print("⚠️  You are running 32-bit Python")
        print("   Consider upgrading to 64-bit Python for better performance")
        print("   with cryptography operations")
    
    print(f"\n=== Recommendation ===")
    if not is_64bit:
        print("1. Download 64-bit Python from https://www.python.org/downloads/")
        print("2. Create a new virtual environment with 64-bit Python")
        print("3. Reinstall your dependencies")
        print("4. This will eliminate the cryptography warning and improve performance")
    else:
        print("Your Python installation is optimal for cryptography operations!")

if __name__ == "__main__":
    check_python_architecture() 