import json

# Load supplier data
with open('supplier_search.json', 'r') as f:
    data = json.load(f)

# Basic statistics
total = len(data)
with_products = [s for s in data if s.get('productCount', 0) > 0]
without_products = [s for s in data if s.get('productCount', 0) == 0]

# Country statistics
countries = {}
for supplier in data:
    country = supplier.get('country', 'Unknown')
    if country:
        countries[country] = countries.get(country, 0) + 1

# Print results
print(f"=== SUPPLIER DATABASE STATISTICS ===")
print(f"Total Suppliers: {total}")
print(f"Suppliers with Products: {len(with_products)}")
print(f"Suppliers without Products: {len(without_products)}")

if with_products:
    total_products = sum(s.get('productCount', 0) for s in data)
    avg_products = total_products / len(with_products) if with_products else 0
    print(f"Total Products in System: {total_products}")
    print(f"Average Products per Supplier (with products): {avg_products:.1f}")

print(f"\nCountries Represented: {len(countries)}")
print(f"\nTop 10 Countries by Supplier Count:")
sorted_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)
for i, (country, count) in enumerate(sorted_countries[:10], 1):
    print(f"  {i}. {country}: {count} suppliers")

# Check data quality
verified = [s for s in data if s.get('verification', 0) > 0]
with_website = [s for s in data if s.get('website')]
with_category = [s for s in data if s.get('category') or s.get('businessType')]

print(f"\n=== DATA QUALITY ===")
print(f"Verified Suppliers: {len(verified)} ({len(verified)*100/total:.1f}%)")
print(f"With Website: {len(with_website)} ({len(with_website)*100/total:.1f}%)")
print(f"With Category/Business Type: {len(with_category)} ({len(with_category)*100/total:.1f}%)")