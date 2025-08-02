import requests
import time

print("Testing FoodXchange server...")

# Wait a moment for server to fully start
time.sleep(2)

# Test endpoints
endpoints = [
    "http://localhost:8003/health",
    "http://localhost:8003/",
    "http://localhost:8003/demo",
    "http://localhost:8003/demo/test",
    "http://localhost:8003/demo/animations"
]

for endpoint in endpoints:
    try:
        response = requests.get(endpoint, timeout=5)
        print(f"✓ {endpoint} - Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"✗ {endpoint} - Connection failed")
    except requests.exceptions.Timeout:
        print(f"✗ {endpoint} - Timeout")
    except Exception as e:
        print(f"✗ {endpoint} - Error: {e}")

print("\nServer test complete!")