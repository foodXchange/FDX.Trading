#!/usr/bin/env python3
"""
Test Azure Deployment without Azure CLI
"""

import urllib.request
import urllib.error
import json
import time
from datetime import datetime

def test_endpoint(url, method='GET', timeout=30):
    """Test an endpoint and return status"""
    try:
        req = urllib.request.Request(url, method=method)
        response = urllib.request.urlopen(req, timeout=timeout)
        status = response.getcode()
        data = response.read().decode('utf-8')
        return status, data, None
    except urllib.error.HTTPError as e:
        return e.code, None, str(e)
    except Exception as e:
        return None, None, str(e)

def main():
    app_name = "foodxchange-app"  # Based on the logs, this appears to be the actual app name
    base_url = f"https://{app_name}.azurewebsites.net"
    
    print("Azure App Service Deployment Test")
    print("=" * 50)
    print(f"App URL: {base_url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        ('/', 'GET', 'Root endpoint'),
        ('/health', 'GET', 'Health check'),
        ('/health', 'HEAD', 'Health check (HEAD)'),
        ('/health/simple', 'GET', 'Simple health check'),
        ('/docs', 'GET', 'API Documentation'),
    ]
    
    results = []
    
    for endpoint, method, description in endpoints:
        url = base_url + endpoint
        print(f"\n[TEST] {description}")
        print(f"  URL: {url}")
        print(f"  Method: {method}")
        
        status, data, error = test_endpoint(url, method)
        
        if status:
            print(f"  Status: {status}")
            if status == 200:
                print("  [OK] Success")
                if data and method == 'GET':
                    try:
                        json_data = json.loads(data)
                        print(f"  Response: {json.dumps(json_data, indent=2)[:200]}...")
                    except:
                        print(f"  Response: {data[:200]}...")
            else:
                print(f"  [WARN] Unexpected status code")
        else:
            print(f"  [ERROR] {error}")
        
        results.append({
            'endpoint': endpoint,
            'method': method,
            'status': status,
            'success': status == 200 if status else False
        })
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"\nTests passed: {successful}/{total}")
    
    for result in results:
        status_str = f"Status {result['status']}" if result['status'] else "Failed"
        icon = "[OK]" if result['success'] else "[FAIL]"
        print(f"  {icon} {result['method']} {result['endpoint']} - {status_str}")
    
    if successful == total:
        print(f"\n[SUCCESS] All tests passed! App is working correctly.")
        print(f"App URL: {base_url}")
    else:
        print(f"\n[WARN] Some tests failed. Please check:")
        print(f"  1. Deployment logs: https://{app_name}.scm.azurewebsites.net/api/logs/docker")
        print(f"  2. App settings in Azure Portal")
        print(f"  3. Startup command configuration")

if __name__ == "__main__":
    main()