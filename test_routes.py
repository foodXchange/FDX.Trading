import requests

# Test various routes
routes = ['/blog', '/pricing', '/features', '/about', '/contact']

for route in routes:
    try:
        response = requests.get(f'http://localhost:9000{route}')
        print(f"{route}: Status {response.status_code}")
        if response.status_code == 404:
            print(f"  Response: {response.text[:200]}...")
    except Exception as e:
        print(f"{route}: Error - {e}")

# Test if routes are registered
try:
    response = requests.get('http://localhost:9000/debug-routes')
    if response.status_code == 200:
        routes_data = response.json()
        print("\nRegistered routes containing 'blog', 'pricing', or 'features':")
        for route in routes_data:
            if any(term in route.get('path', '').lower() for term in ['blog', 'pricing', 'features']):
                print(f"  {route.get('path')} - {route.get('name')}")
except Exception as e:
    print(f"\nError getting debug routes: {e}")