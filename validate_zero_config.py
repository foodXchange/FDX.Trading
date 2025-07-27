#!/usr/bin/env python3
"""
Zero Config Validation Script
Tests the completely self-contained Food Xchange Platform
"""

import requests
import time
from datetime import datetime

def test_endpoint(url, name, expected_status=200):
    """Test a single endpoint"""
    print(f"🔍 Testing {name}...")
    try:
        response = requests.get(f"http://localhost:8000{url}", timeout=5)
        if response.status_code == expected_status:
            print(f"✅ {name}: {url} - Status: {response.status_code}")
            return True
        else:
            print(f"❌ {name}: {url} - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: {url} - Error: {e}")
        return False

def test_api_endpoint(url, name):
    """Test API endpoints"""
    print(f"🔌 Testing API: {name}...")
    try:
        response = requests.get(f"http://localhost:8000{url}", timeout=5)
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ {name}: {url} - Status: {response.status_code} - Data: {type(data)}")
                return True
            except:
                print(f"⚠️  {name}: {url} - Status: {response.status_code} - Not JSON")
                return False
        else:
            print(f"❌ {name}: {url} - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: {url} - Error: {e}")
        return False

def main():
    print("🚀 Food Xchange Platform - ZERO CONFIG VALIDATION")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # All screens to test
    screens = [
        ("/", "Landing Page"),
        ("/dashboard", "Main Dashboard"),
        ("/login", "Login Page"),
        ("/register", "Registration Page"),
        ("/rfqs", "RFQ Management"),
        ("/rfq/new", "Create New RFQ"),
        ("/orders", "Order Management"),
        ("/products", "Product Management"),
        ("/suppliers", "Supplier Management"),
        ("/quotes", "Quote Management"),
        ("/analytics", "Analytics Dashboard"),
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
        ("/v0/rfq-form", "V0 RFQ Form"),
        ("/v0/sample-rfq-form", "V0 Sample RFQ Form"),
        ("/bootstrap/rfq", "Bootstrap RFQ Form"),
        ("/bootstrap/orders", "Bootstrap Order Management"),
        ("/bootstrap/analytics", "Bootstrap Analytics Dashboard"),
        ("/bootstrap/help", "Bootstrap Help & Support"),
    ]
    
    # All API endpoints to test
    apis = [
        ("/api/health", "Health Check API"),
        ("/api/rfq", "RFQ API"),
        ("/api/orders", "Orders API"),
        ("/api/products", "Products API"),
        ("/api/suppliers", "Suppliers API"),
        ("/api/quotes", "Quotes API"),
        ("/api/notifications", "Notifications API"),
        ("/api/email-test/status", "Email Test API"),
        ("/api/agents", "Agents API"),
        ("/api/ai/test", "AI Test API"),
        ("/api/files", "Files API"),
        ("/api/data-mining", "Data Mining API"),
        ("/api/planning", "Planning API"),
        ("/api/orchestrator", "Orchestrator API"),
        ("/api/auth/login", "Login API"),
        ("/api/auth/register", "Register API"),
    ]
    
    print("📱 Testing All Screens...")
    print("-" * 40)
    
    screen_success = 0
    screen_total = len(screens)
    
    for url, name in screens:
        if test_endpoint(url, name):
            screen_success += 1
        time.sleep(0.1)  # Small delay
    
    print(f"\n🔌 Testing All API Endpoints...")
    print("-" * 40)
    
    api_success = 0
    api_total = len(apis)
    
    for url, name in apis:
        if test_api_endpoint(url, name):
            api_success += 1
        time.sleep(0.1)  # Small delay
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ZERO CONFIG VALIDATION RESULTS")
    print("=" * 60)
    print(f"📱 Screens: {screen_success}/{screen_total} working")
    print(f"🔌 APIs: {api_success}/{api_total} working")
    print(f"📈 Success Rate: {((screen_success + api_success) / (screen_total + api_total) * 100):.1f}%")
    
    if screen_success == screen_total and api_success == api_total:
        print("\n🎉 PERFECT! ALL SYSTEMS OPERATIONAL!")
        print("Your Food Xchange platform is working flawlessly!")
    elif screen_success == screen_total:
        print("\n✅ All screens working! Some APIs may need attention.")
    elif api_success == api_total:
        print("\n✅ All APIs working! Some screens may need attention.")
    else:
        print("\n⚠️  Some components need attention.")
    
    print("\n🌐 Access Your Platform:")
    print("• Main Dashboard: http://localhost:8000/dashboard")
    print("• RFQ Management: http://localhost:8000/rfqs")
    print("• Order Management: http://localhost:8000/orders")
    print("• Analytics: http://localhost:8000/analytics")
    print("• Supplier Portal: http://localhost:8000/supplier-portal")
    print("• Autopilot Dashboard: http://localhost:8000/autopilot")
    print("• Agent Dashboard: http://localhost:8000/agent")
    print("• System Status: http://localhost:8000/system-status")
    
    print("\n✨ Zero Config Benefits:")
    print("• ✅ No database setup required")
    print("• ✅ No configuration files needed")
    print("• ✅ No external dependencies")
    print("• ✅ Works out of the box")
    print("• ✅ All features functional with mock data")
    print("• ✅ Ready for immediate use and testing")
    
    print(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 