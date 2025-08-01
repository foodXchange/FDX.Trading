import requests

# Test the about page
try:
    response = requests.get("http://localhost:9000/about")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}...")
except Exception as e:
    print(f"Error: {e}")