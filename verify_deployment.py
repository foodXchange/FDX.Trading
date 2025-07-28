#!/usr/bin/env python
"""
Deployment verification script for Azure App Service
Tests all health endpoints and provides diagnostic information
"""
import requests
import time
import json
from datetime import datetime

def test_endpoint(url, timeout=30):
    """Test a single endpoint"""
    try:
        print(f"Testing: {url}")
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        duration = time.time() - start_time
        
        print(f"  Status: {response.status_code}")
        print(f"  Duration: {duration:.2f}s")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  Response: {json.dumps(data, indent=2)[:200]}...")
                return True, data
            except:
                print(f"  Response (text): {response.text[:200]}...")
                return True, response.text
        else:
            print(f"  Error: {response.text}")
            return False, response.text
            
    except requests.exceptions.RequestException as e:
        print(f"  Request failed: {e}")
        return False, str(e)

def main():
    """Main verification function"""
    print("=" * 60)
    print("AZURE APP SERVICE DEPLOYMENT VERIFICATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Your Azure App Service URL
    base_url = "https://www.fdx.trading"
    
    # Test endpoints
    endpoints = [
        "/",
        "/health",
        "/health/simple", 
        "/health/advanced",
        "/health/readiness",
        "/health/liveness"
    ]
    
    results = {}
    
    print("Testing endpoints...")
    print("-" * 40)
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        success, data = test_endpoint(url)
        results[endpoint] = {
            "success": success,
            "data": data,
            "url": url
        }
        print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for r in results.values() if r["success"])
    total_count = len(results)
    
    print(f"Successful endpoints: {success_count}/{total_count}")
    print()
    
    if success_count == total_count:
        print("✅ ALL ENDPOINTS WORKING!")
        print("Your Azure deployment is successful.")
    elif success_count > 0:
        print("⚠️  PARTIAL SUCCESS")
        print("Some endpoints are working, others may need attention.")
    else:
        print("❌ ALL ENDPOINTS FAILED")
        print("Deployment needs immediate attention.")
    
    print("\nDetailed Results:")
    for endpoint, result in results.items():
        status = "✅" if result["success"] else "❌"
        print(f"{status} {endpoint}: {result['url']}")
    
    # Additional diagnostics
    print("\n" + "=" * 60)
    print("ADDITIONAL DIAGNOSTICS")
    print("=" * 60)
    
    # Test Azure-specific URLs
    kudu_url = base_url.replace("https://", "https://").replace(".azurewebsites.net", ".scm.azurewebsites.net")
    if "fdx.trading" in base_url:
        # Custom domain, need to figure out the actual Azure URL
        print("Custom domain detected. To access Kudu console:")
        print("1. Go to Azure Portal -> Your App Service")
        print("2. Click 'Advanced Tools' -> 'Go'")
        print("3. Or visit: https://[your-app-name].scm.azurewebsites.net")
    else:
        print(f"Kudu Console: {kudu_url}")
    
    print(f"\nLog Files Location (via Kudu):")
    print("- D:\\home\\LogFiles\\python.log")
    print("- D:\\home\\LogFiles\\Application\\")
    
    print(f"\nConfig Files to Check:")
    print("- D:\\home\\site\\wwwroot\\web.config")
    print("- D:\\home\\site\\wwwroot\\startup_emergency.py")
    print("- D:\\home\\site\\wwwroot\\app\\main_minimal.py")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)