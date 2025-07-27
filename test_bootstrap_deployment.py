import requests
import sys

def test_endpoint(url, name):
    try:
        response = requests.get(f"http://localhost:8000{url}", timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: {url} - Status: {response.status_code}")
            return True
        else:
            print(f"❌ {name}: {url} - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: {url} - Error: {e}")
        return False

def main():
    print("Testing all Bootstrap screens...")
    print("=" * 50)
    
    endpoints = [
        ("/bootstrap/rfq", "RFQ Creation Form"),
        ("/bootstrap/orders", "Order Management Interface"),
        ("/bootstrap/analytics", "Analytics Dashboard"),
        ("/bootstrap/help", "Help & Support Center")
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for url, name in endpoints:
        if test_endpoint(url, name):
            success_count += 1
    
    print("=" * 50)
    print(f"Results: {success_count}/{total_count} screens accessible")
    
    if success_count == total_count:
        print("🎉 All Bootstrap screens are working!")
        print("\nAccess your screens at:")
        print("• RFQ Form: http://localhost:8000/bootstrap/rfq")
        print("• Order Management: http://localhost:8000/bootstrap/orders")
        print("• Analytics Dashboard: http://localhost:8000/bootstrap/analytics")
        print("• Help & Support: http://localhost:8000/bootstrap/help")
    else:
        print("⚠️  Some screens may need attention")
        sys.exit(1)

if __name__ == "__main__":
    main()
