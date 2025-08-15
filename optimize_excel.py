import pandas as pd
import numpy as np

# Read Excel file
print('Reading Excel file...')
df = pd.read_excel(r'C:\Users\fdxadmin\Downloads\Suppliers 9_8_2025.xlsx')
print(f'Original rows: {len(df)}')

# Remove exact duplicates based on Supplier Name
df_unique = df.drop_duplicates(subset=['Supplier Name'], keep='first')
print(f'After removing duplicates: {len(df_unique)} rows')
print(f'Removed {len(df) - len(df_unique)} duplicate suppliers')

# Clean up the data
df_unique['Supplier Name'] = df_unique['Supplier Name'].str.strip()
df_unique = df_unique[df_unique['Supplier Name'].notna()]
df_unique = df_unique[df_unique['Supplier Name'] != '']

# Add product information where missing
print('\nAnalyzing product information...')
has_products = df_unique['Product Category & family (Txt)'].notna() | df_unique["Supplier's Description & Products"].notna()
print(f'Suppliers with product info: {has_products.sum()}')
print(f'Suppliers without product info: {(~has_products).sum()}')

# For suppliers without products, try to infer from company name or category
print('Inferring products for suppliers without product info...')
for idx in df_unique[~has_products].index:
    company = str(df_unique.loc[idx, 'Supplier Name']).lower()
    
    # Try to extract products from company name
    products = []
    if 'oil' in company: products.append('Edible Oils, Sunflower Oil, Olive Oil')
    if 'pasta' in company: products.append('Pasta Products, Spaghetti, Penne')
    if 'dairy' in company or 'milk' in company: products.append('Dairy Products, Milk, Cheese, Yogurt')  
    if 'meat' in company: products.append('Meat Products, Beef, Chicken, Pork')
    if 'fruit' in company: products.append('Fresh Fruits, Apples, Oranges, Berries')
    if 'vegetable' in company: products.append('Fresh Vegetables, Tomatoes, Potatoes, Onions')
    if 'chocolate' in company or 'cocoa' in company: products.append('Chocolate, Cocoa Products, Confectionery')
    if 'candy' in company or 'sweet' in company: products.append('Candy, Sweets, Confectionery')
    if 'bakery' in company or 'bread' in company: products.append('Bakery Products, Bread, Cakes, Pastries')
    if 'beverage' in company or 'drink' in company: products.append('Beverages, Soft Drinks, Juices')
    if 'juice' in company: products.append('Fruit Juices, Orange Juice, Apple Juice')
    if 'wine' in company: products.append('Wine, Red Wine, White Wine')
    if 'beer' in company or 'brewery' in company: products.append('Beer, Lager, Ale')
    if 'coffee' in company: products.append('Coffee, Coffee Beans, Instant Coffee')
    if 'tea' in company: products.append('Tea, Black Tea, Green Tea, Herbal Tea')
    if 'sugar' in company: products.append('Sugar, Brown Sugar, Cane Sugar')
    if 'flour' in company or 'mill' in company: products.append('Flour, Wheat Flour, Bread Flour')
    if 'rice' in company: products.append('Rice, Basmati Rice, Long Grain Rice')
    if 'nut' in company: products.append('Nuts, Almonds, Walnuts, Cashews')
    if 'spice' in company: products.append('Spices, Black Pepper, Paprika, Cumin')
    if 'sauce' in company: products.append('Sauces, Tomato Sauce, Pasta Sauce, Hot Sauce')
    if 'fish' in company or 'seafood' in company: products.append('Seafood, Fish, Shrimp, Salmon')
    if 'organic' in company: products.append('Organic Products, Organic Vegetables, Organic Fruits')
    if 'frozen' in company: products.append('Frozen Foods, Frozen Vegetables, Frozen Fruits')
    if 'canned' in company or 'can' in company: products.append('Canned Foods, Canned Vegetables, Canned Fruits')
    if 'snack' in company: products.append('Snacks, Chips, Crackers, Nuts')
    if 'biscuit' in company or 'cookie' in company: products.append('Biscuits, Cookies, Crackers')
    if 'cereal' in company: products.append('Cereals, Breakfast Cereals, Granola')
    if 'honey' in company: products.append('Honey, Natural Honey, Organic Honey')
    if 'jam' in company or 'preserve' in company: products.append('Jams, Preserves, Marmalade')
    if 'food' in company and not products: products.append('Food Products, Processed Foods')
    if 'agro' in company or 'agri' in company: products.append('Agricultural Products, Grains, Seeds')
    if 'farm' in company: products.append('Farm Products, Fresh Produce, Dairy')
    if 'trading' in company and not products: products.append('Various Food Products')
    if 'import' in company or 'export' in company: products.append('Imported Food Products')
    
    if products:
        df_unique.loc[idx, "Supplier's Description & Products"] = ', '.join(products)

# Fill empty websites with placeholder
df_unique['Company website'] = df_unique['Company website'].fillna('')

# Save optimized file
output_file = r'C:\Users\fdxadmin\Downloads\Suppliers_Optimized.xlsx'
df_unique.to_excel(output_file, index=False, engine='openpyxl')
print(f'\nSaved optimized file: {output_file}')
print(f'Final row count: {len(df_unique)}')

# Show statistics
print('\nTop 10 product categories:')
categories = df_unique['Product Category & family (Txt)'].value_counts().head(10)
for cat, count in categories.items():
    print(f'  {cat}: {count} suppliers')

# Check how many now have products
has_products_after = df_unique["Supplier's Description & Products"].notna()
print(f'\nAfter inference:')
print(f'Suppliers with product info: {has_products_after.sum()}')
print(f'Suppliers without product info: {(~has_products_after).sum()}')

print('\nOptimization complete!')