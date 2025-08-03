# Test your API
import requests

# API base URL
BASE_URL = "http://localhost:8000"

print("1. Testing home endpoint:")
response = requests.get(f"{BASE_URL}/")
print(response.json())

print("\n2. Getting all users (should be empty):")
response = requests.get(f"{BASE_URL}/users")
print(response.json())

print("\n3. Adding a new user:")
response = requests.post(
    f"{BASE_URL}/users",
    params={"name": "Alice Smith", "email": "alice@example.com"}
)
print(response.json())

print("\n4. Adding another user:")
response = requests.post(
    f"{BASE_URL}/users", 
    params={"name": "Bob Jones", "email": "bob@example.com"}
)
print(response.json())

print("\n5. Getting all users again:")
response = requests.get(f"{BASE_URL}/users")
print(response.json())