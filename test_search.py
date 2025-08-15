import requests
import json
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost:53812/api"

def test_search(query, description):
    """Test a search query"""
    print(f"\n{description}")
    print(f"Query: {query}")
    
    response = requests.get(
        f"{BASE_URL}/Products/search",
        params={"query": query},
        verify=False
    )
    
    if response.status_code == 200:
        products = response.json()
        print(f"Results: {len(products)} products found")
        
        # Show first 3 results
        for i, product in enumerate(products[:3], 1):
            print(f"  {i}. {product.get('productName', 'N/A')} - {product.get('supplierName', 'Unknown Supplier')}")
            if product.get('category'):
                print(f"     Category: {product.get('category')}")
    else:
        print(f"Error: {response.status_code}")

# Test various search scenarios
print("=== TESTING PRODUCT SEARCH FUNCTIONALITY ===")

# Basic searches
test_search("oil", "1. Basic search: 'oil'")
test_search("pasta", "2. Basic search: 'pasta'")
test_search("chocolate", "3. Basic search: 'chocolate'")
test_search("cheese", "4. Basic search: 'cheese'")
test_search("bread", "5. Basic search: 'bread'")

# Complex searches
test_search("olive oil", "6. Multi-word search: 'olive oil'")
test_search("organic", "7. Attribute search: 'organic'")
test_search("premium", "8. Quality search: 'premium'")

# Category-based search
print("\n=== TESTING CATEGORY FILTERS ===")
response = requests.get(f"{BASE_URL}/Products", verify=False)
if response.status_code == 200:
    products = response.json()
    categories = {}
    for product in products:
        cat = product.get('category', 'Uncategorized')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"Total products: {len(products)}")
    print(f"Categories found: {len(categories)}")
    print("\nTop 5 categories by product count:")
    sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    for i, (cat, count) in enumerate(sorted_cats[:5], 1):
        print(f"  {i}. {cat}: {count} products")