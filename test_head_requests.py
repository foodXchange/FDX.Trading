#!/usr/bin/env python3
"""
Test script to verify HEAD request handling locally before Azure deployment
"""
import subprocess
import time
import requests
import sys

def test_endpoints():
    """Test all endpoints with both GET and HEAD methods"""
    base_url = "http://localhost:8000"
    
    endpoints = [
        ("/", ["GET", "HEAD"]),
        ("/health", ["GET", "HEAD"]),
        ("/health/simple", ["GET", "HEAD"]),
        ("/health/detailed", ["GET", "HEAD"]),
        ("/health/advanced", ["GET", "HEAD"])
    ]
    
    print("Testing endpoints...")
    print("-" * 60)
    
    all_passed = True
    
    for path, methods in endpoints:
        for method in methods:
            try:
                if method == "GET":
                    response = requests.get(f"{base_url}{path}", timeout=5)
                else:
                    response = requests.head(f"{base_url}{path}", timeout=5)
                
                status = "PASS" if response.status_code == 200 else "FAIL"
                color = "\033[92m" if status == "PASS" else "\033[91m"
                
                print(f"{color}{method:6} {path:20} Status: {response.status_code} {status}\033[0m")
                
                if status == "FAIL":
                    all_passed = False
                    
            except requests.exceptions.RequestException as e:
                print(f"\033[91m{method:6} {path:20} ERROR: {str(e)}\033[0m")
                all_passed = False
    
    print("-" * 60)
    return all_passed

def main():
    print("Starting local FastAPI server for testing...")
    
    # Start the server
    server_process = subprocess.Popen(
        [sys.executable, "minimal_app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    try:
        # Test endpoints
        all_passed = test_endpoints()
        
        if all_passed:
            print("\n\033[92mAll tests passed! ✓\033[0m")
            print("Your app is ready for Azure deployment.")
        else:
            print("\n\033[91mSome tests failed! ✗\033[0m")
            print("Fix the issues before deploying to Azure.")
            
    finally:
        # Stop the server
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    main()