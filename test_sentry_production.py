import requests
import time

# Test the production Sentry integration
print("Testing Sentry integration on production site...")

# Test endpoints
base_url = "https://www.fdx.trading"
endpoints = [
    "/health",
    "/sentry-debug",  # This will trigger an error
    "/test-sentry",   # This will send a test error
    "/monitoring/test" # This will test all monitoring systems
]

for endpoint in endpoints:
    url = f"{base_url}{endpoint}"
    print(f"\nTesting {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        elif response.status_code == 500:
            print("Error triggered successfully (expected for /sentry-debug)")
        else:
            print(f"Unexpected status: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    
    time.sleep(2)  # Wait between requests

print("\n✅ Test complete! Check your Sentry dashboard at:")
print("https://foodxchange.sentry.io/issues/")
print("\nYou should see:")
print("- Division by zero error from /sentry-debug")
print("- Test error from /test-sentry")
print("- Monitoring test event from /monitoring/test")