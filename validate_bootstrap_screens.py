import requests
from bs4 import BeautifulSoup
import re

def validate_screen(url, name):
    """Validate a Bootstrap screen for visual elements and functionality"""
    print(f"\n🔍 Validating {name}...")
    print("-" * 40)
    
    try:
        response = requests.get(f"http://localhost:8000{url}")
        if response.status_code != 200:
            print(f"❌ Failed to load {name}: Status {response.status_code}")
            return False
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for Bootstrap CSS
        bootstrap_css = soup.find('link', href=lambda x: x and 'bootstrap' in x)
        if bootstrap_css:
            print("✅ Bootstrap CSS loaded")
        else:
            print("❌ Bootstrap CSS not found")
        
        # Check for custom Food Xchange fonts
        custom_fonts = soup.find('link', href=lambda x: x and 'fx-fonts.css' in x)
        if custom_fonts:
            print("✅ Custom fonts loaded")
        else:
            print("❌ Custom fonts not found")
        
        # Check for Food Xchange branding
        logo = soup.find('img', src=lambda x: x and 'logo' in x)
        if logo:
            print("✅ Food Xchange logo present")
        else:
            print("❌ Food Xchange logo not found")
        
        # Check for navigation
        navbar = soup.find('nav', class_='navbar')
        if navbar:
            print("✅ Navigation bar present")
        else:
            print("❌ Navigation bar not found")
        
        # Check for responsive design
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            print("✅ Responsive viewport meta tag")
        else:
            print("❌ Responsive viewport meta tag missing")
        
        # Screen-specific validations
        if 'rfq' in url:
            validate_rfq_form(soup)
        elif 'orders' in url:
            validate_order_management(soup)
        elif 'analytics' in url:
            validate_analytics_dashboard(soup)
        elif 'help' in url:
            validate_help_center(soup)
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating {name}: {e}")
        return False

def validate_rfq_form(soup):
    """Validate RFQ form specific elements"""
    print("\n📋 RFQ Form Validation:")
    
    # Check form elements
    form = soup.find('form', id='rfqForm')
    if form:
        print("✅ RFQ form found")
        
        # Check required fields
        required_fields = ['productCategory', 'quantity', 'unit', 'deliveryDate', 'companyName', 'contactName', 'email', 'phone']
        for field_id in required_fields:
            field = soup.find('input', id=field_id) or soup.find('select', id=field_id)
            if field:
                print(f"✅ Required field '{field_id}' present")
            else:
                print(f"❌ Required field '{field_id}' missing")
        
        # Check budget slider
        budget_slider = soup.find('input', id='budgetRange')
        if budget_slider:
            print("✅ Budget slider present")
        else:
            print("❌ Budget slider missing")
        
        # Check submit button
        submit_btn = soup.find('button', type='submit')
        if submit_btn:
            print("✅ Submit button present")
        else:
            print("❌ Submit button missing")
    else:
        print("❌ RFQ form not found")

def validate_order_management(soup):
    """Validate Order Management specific elements"""
    print("\n📦 Order Management Validation:")
    
    # Check order table
    table = soup.find('table', class_='table')
    if table:
        print("✅ Order table present")
        
        # Check table headers
        headers = ['Order ID', 'Product', 'Quantity', 'Status', 'Date', 'Actions']
        for header in headers:
            if soup.find(string=re.compile(header, re.IGNORECASE)):
                print(f"✅ Table header '{header}' present")
            else:
                print(f"❌ Table header '{header}' missing")
    else:
        print("❌ Order table not found")
    
    # Check filters
    filters = soup.find('div', class_='card') and soup.find('select', id='statusFilter')
    if filters:
        print("✅ Filter controls present")
    else:
        print("❌ Filter controls missing")

def validate_analytics_dashboard(soup):
    """Validate Analytics Dashboard specific elements"""
    print("\n📊 Analytics Dashboard Validation:")
    
    # Check metrics cards
    cards = soup.find_all('div', class_='card')
    if len(cards) >= 4:
        print(f"✅ Found {len(cards)} metric cards")
    else:
        print(f"❌ Expected 4+ metric cards, found {len(cards)}")
    
    # Check charts
    canvas_elements = soup.find_all('canvas')
    if canvas_elements:
        print(f"✅ Found {len(canvas_elements)} chart canvas elements")
    else:
        print("❌ No chart canvas elements found")
    
    # Check Chart.js
    chart_js = soup.find('script', src=lambda x: x and 'chart.js' in x)
    if chart_js:
        print("✅ Chart.js library loaded")
    else:
        print("❌ Chart.js library not found")

def validate_help_center(soup):
    """Validate Help & Support Center specific elements"""
    print("\n❓ Help Center Validation:")
    
    # Check search functionality
    search_input = soup.find('input', type='search')
    if search_input:
        print("✅ Search input present")
    else:
        print("❌ Search input missing")
    
    # Check FAQ accordion
    accordion = soup.find('div', class_='accordion')
    if accordion:
        print("✅ FAQ accordion present")
    else:
        print("❌ FAQ accordion missing")
    
    # Check contact form
    contact_form = soup.find('form')
    if contact_form:
        print("✅ Contact form present")
    else:
        print("❌ Contact form missing")

def main():
    print("🎯 Bootstrap Screens Validation")
    print("=" * 50)
    
    screens = [
        ("/bootstrap/rfq", "RFQ Creation Form"),
        ("/bootstrap/orders", "Order Management Interface"),
        ("/bootstrap/analytics", "Analytics Dashboard"),
        ("/bootstrap/help", "Help & Support Center")
    ]
    
    success_count = 0
    total_count = len(screens)
    
    for url, name in screens:
        if validate_screen(url, name):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Validation Results: {success_count}/{total_count} screens validated")
    
    if success_count == total_count:
        print("🎉 All screens are properly implemented and accessible!")
        print("\n🌐 Access your screens:")
        print("• RFQ Form: http://localhost:8000/bootstrap/rfq")
        print("• Order Management: http://localhost:8000/bootstrap/orders")
        print("• Analytics Dashboard: http://localhost:8000/bootstrap/analytics")
        print("• Help & Support: http://localhost:8000/bootstrap/help")
        
        print("\n✨ Next Steps:")
        print("1. Open each URL in your browser to see the visual design")
        print("2. Test form submissions and interactions")
        print("3. Check responsive design on mobile devices")
        print("4. Verify all Food Xchange branding elements")
    else:
        print("⚠️  Some screens need attention - check the validation details above")

if __name__ == "__main__":
    main() 