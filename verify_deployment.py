#!/usr/bin/env python3
"""
Deployment Verification Script for FoodXchange
Checks if the application is running correctly on Azure
"""

import requests
import json
import sys
import time
from urllib.parse import urljoin

def check_endpoint(base_url, endpoint, expected_status=200, timeout=30):
    """Check if an endpoint is responding correctly"""
    url = urljoin(base_url, endpoint)
    try:
        response = requests.get(url, timeout=timeout)
        print(f"✅ {endpoint}: {response.status_code}")
        if response.status_code == expected_status:
            return True
        else:
            print(f"   Expected {expected_status}, got {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {endpoint}: {e}")
        return False

def check_health_endpoint(base_url):
    """Check the health endpoint and return detailed status"""
    url = urljoin(base_url, "/health/advanced")
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data.get('status', 'unknown')}")
            print(f"   Service: {data.get('service', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Environment: {data.get('environment', 'unknown')}")
            print(f"   Database: {data.get('database', 'unknown')}")
            return True
        else:
            print(f"❌ Health Check: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check: {e}")
        return False

def check_api_docs(base_url):
    """Check if API documentation is accessible"""
    url = urljoin(base_url, "/docs")
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            print("✅ API Documentation: Accessible")
            return True
        else:
            print(f"❌ API Documentation: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Documentation: {e}")
        return False

def check_ssl(base_url):
    """Check if HTTPS is working"""
    if base_url.startswith("https://"):
        try:
            response = requests.get(base_url, timeout=30)
            print("✅ HTTPS: Working correctly")
            return True
        except requests.exceptions.SSLError as e:
            print(f"❌ HTTPS: SSL Error - {e}")
            return False
        except Exception as e:
            print(f"❌ HTTPS: {e}")
            return False
    else:
        print("⚠️ HTTPS: Not using HTTPS")
        return False

def main():
    print("🔍 FoodXchange Deployment Verification")
    print("=" * 40)
    
    # Get the app URL
    if len(sys.argv) > 1:
        app_url = sys.argv[1]
    else:
        app_url = input("Enter your Azure app URL (e.g., https://foodxchange-app.azurewebsites.net): ").strip()
    
    if not app_url:
        print("❌ No URL provided")
        return
    
    # Ensure URL has protocol
    if not app_url.startswith(('http://', 'https://')):
        app_url = 'https://' + app_url
    
    print(f"🌐 Checking: {app_url}")
    print()
    
    # Wait a moment for app to be ready
    print("⏳ Waiting for app to be ready...")
    time.sleep(5)
    
    # Check various endpoints
    checks = [
        ("/", "Homepage"),
        ("/health", "Basic Health"),
        ("/health/simple", "Simple Health"),
        ("/health/advanced", "Advanced Health"),
        ("/docs", "API Documentation"),
        ("/metrics", "Metrics"),
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for endpoint, description in checks:
        if check_endpoint(app_url, endpoint):
            passed_checks += 1
        print()
    
    # Additional checks
    print("🔧 Additional Checks:")
    print("-" * 20)
    
    if check_health_endpoint(app_url):
        passed_checks += 1
    print()
    
    if check_api_docs(app_url):
        passed_checks += 1
    print()
    
    if check_ssl(app_url):
        passed_checks += 1
    print()
    
    # Summary
    print("📊 Verification Summary")
    print("=" * 25)
    print(f"Passed: {passed_checks}/{total_checks + 3}")
    print(f"Success Rate: {(passed_checks/(total_checks + 3)*100):.1f}%")
    
    if passed_checks == total_checks + 3:
        print("🎉 All checks passed! Your deployment is successful!")
        print(f"🌐 Your app is running at: {app_url}")
        print("\n📋 Next steps:")
        print("1. Test your application functionality")
        print("2. Set up monitoring and alerts")
        print("3. Configure your custom domain")
        print("4. Set up database backups")
    else:
        print("⚠️ Some checks failed. Please review the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Check Azure App Service logs")
        print("2. Verify environment variables")
        print("3. Check database connectivity")
        print("4. Review application startup logs")

if __name__ == "__main__":
    main()