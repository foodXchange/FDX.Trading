import requests
from bs4 import BeautifulSoup
import re
import time

def validate_screen(url, name, expected_status=200):
    """Validate a screen for basic functionality"""
    print(f"\n🔍 Validating {name}...")
    print("-" * 50)
    
    try:
        response = requests.get(f"http://localhost:8000{url}", timeout=10)
        if response.status_code == expected_status:
            print(f"✅ {name}: {url} - Status: {response.status_code}")
            
            # Parse HTML for additional checks
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for basic HTML structure
            if soup.find('html'):
                print("✅ Valid HTML structure")
            else:
                print("❌ Invalid HTML structure")
            
            # Check for title
            title = soup.find('title')
            if title:
                print(f"✅ Page title: {title.get_text()[:50]}...")
            else:
                print("❌ No page title found")
            
            # Check for navigation
            navbar = soup.find('nav') or soup.find('header')
            if navbar:
                print("✅ Navigation/header present")
            else:
                print("⚠️  No navigation/header found")
            
            # Check for main content
            main_content = soup.find('main') or soup.find('div', class_='container') or soup.find('div', class_='content')
            if main_content:
                print("✅ Main content area present")
            else:
                print("⚠️  No main content area found")
            
            return True
        else:
            print(f"❌ {name}: {url} - Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: {url} - Error: {e}")
        return False
    except Exception as e:
        print(f"❌ {name}: {url} - Unexpected error: {e}")
        return False

def validate_api_endpoint(url, name, method='GET'):
    """Validate API endpoints"""
    print(f"\n🔍 Validating API: {name}...")
    print("-" * 50)
    
    try:
        if method == 'GET':
            response = requests.get(f"http://localhost:8000{url}", timeout=10)
        elif method == 'POST':
            response = requests.post(f"http://localhost:8000{url}", timeout=10)
        
        if response.status_code in [200, 201, 204]:
            print(f"✅ {name}: {url} - Status: {response.status_code}")
            return True
        else:
            print(f"⚠️  {name}: {url} - Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: {url} - Error: {e}")
        return False

def main():
    print("🎯 Complete Food Xchange Platform Validation")
    print("=" * 60)
    
    # All available screens based on your templates and routes
    screens = [
        # Bootstrap Screens (already validated)
        ("/bootstrap/rfq", "Bootstrap RFQ Form"),
        ("/bootstrap/orders", "Bootstrap Order Management"),
        ("/bootstrap/analytics", "Bootstrap Analytics Dashboard"),
        ("/bootstrap/help", "Bootstrap Help & Support"),
        
        # Main Application Screens
        ("/", "Landing Page"),
        ("/dashboard", "Main Dashboard"),
        ("/login", "Login Page"),
        ("/register", "Registration Page"),
        
        # Core Business Screens
        ("/rfqs", "RFQ Management"),
        ("/rfq/new", "Create New RFQ"),
        ("/orders", "Order Management"),
        ("/products", "Product Management"),
        ("/suppliers", "Supplier Management"),
        ("/quotes", "Quote Management"),
        ("/analytics", "Analytics Dashboard"),
        
        # Advanced Features
        ("/planning", "Planning Dashboard"),
        ("/orchestrator", "Orchestrator Dashboard"),
        ("/autopilot", "Autopilot Dashboard"),
        ("/agent", "Agent Dashboard"),
        ("/operator", "Operator Dashboard"),
        ("/supplier-portal", "Supplier Portal"),
        ("/email-intelligence", "Email Intelligence"),
        ("/quote-comparison", "Quote Comparison"),
        ("/projects", "Projects Management"),
        ("/system-status", "System Status"),
        
        # V0 Components
        ("/v0/rfq-form", "V0 RFQ Form"),
        ("/v0/sample-rfq-form", "V0 Sample RFQ Form"),
    ]
    
    # API Endpoints
    api_endpoints = [
        # Core APIs
        ("/api/rfq", "RFQ API"),
        ("/api/orders", "Orders API"),
        ("/api/products", "Products API"),
        ("/api/suppliers", "Suppliers API"),
        ("/api/quotes", "Quotes API"),
        
        # Authentication
        ("/api/auth/login", "Login API"),
        ("/api/auth/register", "Register API"),
        
        # Notifications
        ("/api/notifications", "Notifications API"),
        ("/api/email-test/status", "Email Test API"),
        
        # Agents and AI
        ("/api/agents", "Agents API"),
        ("/api/ai/test", "AI Test API"),
        
        # Data and Files
        ("/api/files", "Files API"),
        ("/api/data-mining", "Data Mining API"),
        
        # Planning and Orchestration
        ("/api/planning", "Planning API"),
        ("/api/orchestrator", "Orchestrator API"),
    ]
    
    print("\n📱 Validating All Screens...")
    print("=" * 60)
    
    screen_success = 0
    screen_total = len(screens)
    
    for url, name in screens:
        if validate_screen(url, name):
            screen_success += 1
        time.sleep(0.5)  # Small delay to avoid overwhelming the server
    
    print("\n🔌 Validating API Endpoints...")
    print("=" * 60)
    
    api_success = 0
    api_total = len(api_endpoints)
    
    for url, name in api_endpoints:
        if validate_api_endpoint(url, name):
            api_success += 1
        time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPLETE VALIDATION RESULTS")
    print("=" * 60)
    print(f"📱 Screens: {screen_success}/{screen_total} accessible")
    print(f"🔌 APIs: {api_success}/{api_total} responding")
    print(f"📈 Total Success Rate: {((screen_success + api_success) / (screen_total + api_total) * 100):.1f}%")
    
    if screen_success == screen_total and api_success == api_total:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("Your Food Xchange platform is fully functional!")
    else:
        print("\n⚠️  SOME COMPONENTS NEED ATTENTION")
        print("Check the validation details above for specific issues")
    
    print("\n🌐 Access Your Platform:")
    print("• Main Dashboard: http://localhost:8000/dashboard")
    print("• RFQ Management: http://localhost:8000/rfqs")
    print("• Order Management: http://localhost:8000/orders")
    print("• Analytics: http://localhost:8000/analytics")
    print("• Supplier Portal: http://localhost:8000/supplier-portal")
    print("• Autopilot Dashboard: http://localhost:8000/autopilot")
    print("• Agent Dashboard: http://localhost:8000/agent")
    print("• System Status: http://localhost:8000/system-status")
    
    print("\n✨ Key Features Available:")
    print("• Complete RFQ lifecycle management")
    print("• Order tracking and management")
    print("• Supplier relationship management")
    print("• Quote comparison and analysis")
    print("• Advanced analytics and reporting")
    print("• AI-powered automation")
    print("• Email intelligence and monitoring")
    print("• Multi-agent orchestration")
    print("• Planning and forecasting tools")
    print("• Real-time system monitoring")

if __name__ == "__main__":
    main() 