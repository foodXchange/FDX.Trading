#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Server Test Script
Tests all major endpoints and functionality
"""

import requests
import json
import time
import sys
from datetime import datetime

# Base URL for the server
BASE_URL = "http://localhost:8000"

# Test results tracker
test_results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}

def test_endpoint(method, path, description, data=None, files=None, expected_status=200, headers=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{path}"
    print(f"\n🧪 Testing: {description}")
    print(f"   {method} {url}")
    
    try:
        # Make the request
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            if files:
                response = requests.post(url, data=data, files=files, headers=headers)
            else:
                response = requests.post(url, data=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print(f"   ❌ Unsupported method: {method}")
            test_results["failed"] += 1
            return None
        
        # Check status code
        if response.status_code == expected_status:
            print(f"   ✅ Status: {response.status_code} (expected)")
            test_results["passed"] += 1
            
            # Try to parse JSON response
            try:
                json_response = response.json()
                print(f"   📋 Response: {json.dumps(json_response, indent=2)[:200]}...")
            except:
                print(f"   📋 Response: {response.text[:200]}...")
            
            return response
        else:
            print(f"   ❌ Status: {response.status_code} (expected {expected_status})")
            print(f"   📋 Response: {response.text[:200]}...")
            test_results["failed"] += 1
            test_results["errors"].append({
                "endpoint": f"{method} {path}",
                "description": description,
                "status": response.status_code,
                "expected": expected_status,
                "response": response.text[:500]
            })
            return response
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error: Server not responding")
        test_results["failed"] += 1
        test_results["errors"].append({
            "endpoint": f"{method} {path}",
            "description": description,
            "error": "Connection refused - is the server running?"
        })
        return None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        test_results["failed"] += 1
        test_results["errors"].append({
            "endpoint": f"{method} {path}",
            "description": description,
            "error": str(e)
        })
        return None

def run_tests():
    """Run all server tests"""
    print("🚀 Starting FoodXchange Server Tests")
    print("=" * 60)
    print(f"Server URL: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Test 1: Health Check
    test_endpoint("GET", "/health", "Health Check")
    
    # Test 2: Main Pages
    test_endpoint("GET", "/", "Landing Page")
    test_endpoint("GET", "/dashboard", "Dashboard Page")
    test_endpoint("GET", "/login", "Login Page")
    
    # Test 3: API Documentation
    test_endpoint("GET", "/docs", "API Documentation")
    test_endpoint("GET", "/redoc", "ReDoc Documentation")
    
    # Test 4: Static Files
    test_endpoint("GET", "/static/css/main.css", "Static CSS File")
    test_endpoint("GET", "/favicon.png", "Favicon")
    
    # Test 5: Authentication
    test_endpoint("POST", "/auth/login", "Login with Invalid Credentials", 
                 data={"email": "test@example.com", "password": "wrong"}, 
                 expected_status=303)
    
    # Test 6: Profile Routes
    test_endpoint("GET", "/profile/", "Profile Page")
    test_endpoint("GET", "/profile/edit", "Profile Edit Page")
    test_endpoint("GET", "/profile/settings", "Profile Settings Page")
    
    # Test 7: Business Routes
    test_endpoint("GET", "/suppliers", "Suppliers Page")
    test_endpoint("GET", "/buyers", "Buyers Page")
    test_endpoint("GET", "/projects", "Projects Page")
    
    # Test 8: API Endpoints
    test_endpoint("GET", "/suppliers/list", "List Suppliers API")
    test_endpoint("GET", "/buyers/list", "List Buyers API")
    
    # Test 9: Product Analysis
    test_endpoint("GET", "/product-analysis/", "Product Analysis Page")
    
    # Test 10: Azure Testing Routes
    test_endpoint("GET", "/api/azure/health", "Azure Health Check")
    test_endpoint("GET", "/azure-test/api/status", "Azure API Status")
    
    # Test 11: Search Routes
    test_endpoint("GET", "/api/search/products?query=test", "Product Search API")
    
    # Test 12: Data Import Routes
    test_endpoint("GET", "/import/", "Data Import Page")
    test_endpoint("GET", "/import/template/csv", "Download CSV Template")
    
    # Print Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📈 Success Rate: {(test_results['passed'] / (test_results['passed'] + test_results['failed']) * 100):.1f}%")
    
    if test_results["errors"]:
        print("\n❌ FAILED TESTS:")
        for error in test_results["errors"]:
            print(f"\n   Endpoint: {error.get('endpoint', 'Unknown')}")
            print(f"   Description: {error.get('description', 'Unknown')}")
            if 'status' in error:
                print(f"   Status: {error['status']} (expected {error.get('expected', 'Unknown')})")
            if 'error' in error:
                print(f"   Error: {error['error']}")
            if 'response' in error:
                print(f"   Response: {error['response'][:200]}...")
    
    print("\n" + "=" * 60)
    
    # Return exit code based on results
    return 0 if test_results["failed"] == 0 else 1

def check_server_running():
    """Check if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return True
    except:
        return False

if __name__ == "__main__":
    # Check if server is running
    if not check_server_running():
        print("❌ Server is not running!")
        print(f"Please start the server first: python start_server_fixed.py")
        sys.exit(1)
    
    # Run the tests
    exit_code = run_tests()
    sys.exit(exit_code)