"""Simple test to check if server is responding"""
import requests
import time

print("Testing FoodXchange server...")

# Test different endpoints
endpoints = [
    "http://localhost:8003/health",
    "http://localhost:8003/",
    "http://127.0.0.1:8003/health",
    "http://127.0.0.1:8003/"
]

for endpoint in endpoints:
    try:
        print(f"\nTesting {endpoint}...")
        response = requests.get(endpoint, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:100]}...")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
    except requests.exceptions.Timeout:
        print("Request timed out")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
    
    time.sleep(1)

print("\nTest complete.")