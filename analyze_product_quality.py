import json
import urllib.request
import ssl

# Disable SSL verification for localhost
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Get products
url = "https://localhost:53812/api/Products"
req = urllib.request.Request(url)
response = urllib.request.urlopen(req, context=ssl_context)
products = json.loads(response.read().decode())

print("=== PRODUCT DATA QUALITY ANALYSIS ===")
print(f"Total Products: {len(products)}")

# Analyze completeness
fields_stats = {
    'productName': 0,
    'description': 0,
    'category': 0,
    'subCategory': 0,
    'price': 0,
    'unit': 0,
    'brand': 0,
    'sku': 0,
    'imageUrl': 0,
    'certifications': 0,
    'origin': 0,
    'isAvailable': 0
}

# Count field completeness
for product in products:
    for field in fields_stats:
        if product.get(field) and str(product.get(field)).strip():
            fields_stats[field] += 1

print("\n=== FIELD COMPLETENESS ===")
for field, count in fields_stats.items():
    percentage = (count / len(products)) * 100 if products else 0
    print(f"{field:20} {count:4}/{len(products)} ({percentage:.1f}%)")

# Check for duplicates
product_names = [p.get('productName', '') for p in products]
unique_names = set(product_names)
duplicates = len(product_names) - len(unique_names)
print(f"\n=== DUPLICATES ===")
print(f"Duplicate products: {duplicates}")

# Category distribution
categories = {}
for product in products:
    cat = product.get('category', 'Uncategorized')
    if cat and cat.strip():
        categories[cat] = categories.get(cat, 0) + 1
    else:
        categories['Uncategorized'] = categories.get('Uncategorized', 0) + 1

print(f"\n=== CATEGORY DISTRIBUTION ===")
print(f"Total categories: {len(categories)}")
sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
for cat, count in sorted_cats[:10]:
    print(f"  {cat[:50]:50} {count:4} products")

# Products without critical fields
missing_critical = []
for product in products:
    if not product.get('productName') or not product.get('description'):
        missing_critical.append(product)

print(f"\n=== DATA ISSUES ===")
print(f"Products missing name or description: {len(missing_critical)}")

# Products with price
with_price = [p for p in products if p.get('price') and p.get('price') > 0]
print(f"Products with price: {len(with_price)} ({len(with_price)*100/len(products):.1f}%)")

# Products with images
with_images = [p for p in products if p.get('imageUrl')]
print(f"Products with images: {len(with_images)} ({len(with_images)*100/len(products):.1f}%)")

# Recommendations
print("\n=== RECOMMENDATIONS ===")
if len(with_price) < len(products) * 0.5:
    print("• Add pricing information for more products")
if len(with_images) < len(products) * 0.3:
    print("• Add product images for better user experience")
if categories.get('Uncategorized', 0) > len(products) * 0.3:
    print("• Improve category assignment for uncategorized products")
if duplicates > 0:
    print("• Remove duplicate products")
print("• Enrich product descriptions for better search results")
print("• Add certifications and origin information where applicable")