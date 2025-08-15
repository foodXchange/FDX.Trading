import json

# Load supplier data
with open('products_check.json', 'r') as f:
    data = json.load(f)

print(f'Suppliers with products: {len(data)}')

if data:
    total_products = sum(s.get('productCount', 0) for s in data)
    print(f'Total products in database: {total_products}')
    
    # Show top suppliers by product count
    print('\nTop suppliers by product count:')
    sorted_suppliers = sorted(data, key=lambda x: x.get('productCount', 0), reverse=True)
    for i, supplier in enumerate(sorted_suppliers[:5], 1):
        print(f"  {i}. {supplier.get('companyName', 'Unknown')}: {supplier.get('productCount', 0)} products")