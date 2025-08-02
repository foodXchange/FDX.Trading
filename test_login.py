"""
Test login functionality
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_login():
    """Test the login functionality"""
    
    base_url = "http://localhost:9000"
    
    # Test credentials for development mode
    test_users = [
        {"email": "admin@fdx.trading", "password": "FDX2030!", "expected": "admin"},
        {"email": "user@fdx.trading", "password": "user123", "expected": "user"},
        {"email": "demo@fdx.trading", "password": "demo123", "expected": "user"}
    ]
    
    print("Testing FoodXchange Login")
    print("=" * 50)
    print(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")
    print()
    
    for user in test_users:
        print(f"Testing login for: {user['email']}")
        
        # Create session to maintain cookies
        session = requests.Session()
        
        # Attempt login
        login_data = {
            "email": user["email"],
            "password": user["password"]
        }
        
        try:
            response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
            
            print(f"  Status Code: {response.status_code}")
            print(f"  Location: {response.headers.get('Location', 'No redirect')}")
            
            # Check if JWT token was set
            if 'access_token' in session.cookies:
                print(f"  OK JWT token set successfully")
            else:
                print(f"  X No JWT token found in cookies")
            
            # Follow redirect to dashboard
            if response.status_code == 303 and response.headers.get('Location') == '/dashboard':
                dashboard_response = session.get(f"{base_url}/dashboard", allow_redirects=False)
                if dashboard_response.status_code == 200:
                    print(f"  OK Successfully accessed dashboard")
                else:
                    print(f"  X Dashboard access failed: {dashboard_response.status_code}")
            
        except requests.exceptions.ConnectionError:
            print(f"  X Connection error - make sure server is running on port 9000")
        except Exception as e:
            print(f"  X Error: {e}")
        
        print()
    
    print("\nDevelopment Mode Login Instructions:")
    print("-" * 40)
    print("1. Make sure ENVIRONMENT=development is set in .env")
    print("2. Use one of these test credentials:")
    print("   - admin@fdx.trading / admin123")
    print("   - user@fdx.trading / user123")
    print("   - demo@fdx.trading / demo123")
    print("3. Access the optimized login page: /login?optimized=true")

if __name__ == "__main__":
    test_login()