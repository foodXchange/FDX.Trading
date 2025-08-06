import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Poland database connection
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

def search_products(search_term):
    """Search for products across all tables"""
    print("\n" + "="*60)
    print(f"SEARCHING FOR: {search_term.upper()}")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    results = {
        'suppliers': [],
        'products': [],
        'prices': [],
        'proposals': []
    }
    
    # 1. Search in Suppliers
    print(f"\n1. Searching Suppliers for '{search_term}'...")
    cur.execute("""
        SELECT 
            supplier_name,
            country,
            company_email,
            products,
            product_categories
        FROM suppliers
        WHERE products ILIKE %s 
           OR product_categories ILIKE %s
           OR supplier_name ILIKE %s
        LIMIT 20
    """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
    
    suppliers = cur.fetchall()
    print(f"   Found {len(suppliers)} suppliers")
    for s in suppliers[:5]:
        print(f"   - {s['supplier_name'][:40]:40} | {s['country'][:15] if s['country'] else 'N/A':15} | {s['company_email'] if s['company_email'] else 'No email'}")
        results['suppliers'].append(s)
    
    # 2. Search in Products
    print(f"\n2. Searching Products for '{search_term}'...")
    cur.execute("""
        SELECT 
            data->>'Product Name' as product_name,
            data->>'Supplier' as supplier,
            data->>'Unit Wholesale Price (latest)' as price,
            data->>'Currency for price' as currency,
            data->>'Unit of Measure' as unit
        FROM products_raw
        WHERE data::text ILIKE %s
        LIMIT 20
    """, (f'%{search_term}%',))
    
    products = cur.fetchall()
    print(f"   Found {len(products)} products")
    for p in products[:5]:
        price = f"{p['currency'] or '$'} {p['price'] or 'N/A'}"
        print(f"   - {p['product_name'][:35] if p['product_name'] else 'N/A':35} | {p['supplier'][:20] if p['supplier'] else 'N/A':20} | {price}")
        results['products'].append(p)
    
    # 3. Search in Price Book
    print(f"\n3. Searching Price Book for '{search_term}'...")
    cur.execute("""
        SELECT 
            data->>'Product' as product,
            data->>'Supplier' as supplier,
            data->>'Price' as price,
            data->>'Currency' as currency
        FROM price_book_raw
        WHERE data::text ILIKE %s
        LIMIT 20
    """, (f'%{search_term}%',))
    
    prices = cur.fetchall()
    print(f"   Found {len(prices)} price entries")
    for p in prices[:5]:
        if p['product']:
            price = f"{p['currency'] or '$'} {p['price'] or 'N/A'}"
            print(f"   - {p['product'][:35]:35} | {price}")
            results['prices'].append(p)
    
    # 4. Search in Active Proposals
    print(f"\n4. Searching Active Proposals for '{search_term}'...")
    cur.execute("""
        SELECT 
            rp.request_name,
            rp.supplier_name,
            rp.status,
            pp.product_name,
            pp.unit_price
        FROM request_proposals rp
        LEFT JOIN proposal_products pp ON pp.proposal_id = rp.proposal_id
        WHERE rp.request_name ILIKE %s
           OR rp.supplier_name ILIKE %s
           OR pp.product_name ILIKE %s
        LIMIT 20
    """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
    
    proposals = cur.fetchall()
    if proposals:
        print(f"   Found {len(proposals)} related proposals")
        for p in proposals[:5]:
            if p['request_name']:
                print(f"   - Request: {p['request_name'][:30]:30} | Status: {p['status']}")
                results['proposals'].append(p)
    
    cur.close()
    conn.close()
    
    return results

def find_best_price(product_name):
    """Find the best price for a specific product"""
    print("\n" + "="*60)
    print(f"FINDING BEST PRICE FOR: {product_name.upper()}")
    print("="*60)
    
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Search all price sources
    cur.execute("""
        WITH all_prices AS (
            -- From products
            SELECT 
                data->>'Product Name' as product,
                data->>'Supplier' as supplier,
                data->>'Supplier Country' as country,
                CAST(NULLIF(data->>'Unit Wholesale Price (latest)', '') AS DECIMAL) as price,
                data->>'Currency for price' as currency,
                'products' as source
            FROM products_raw
            WHERE data->>'Product Name' ILIKE %s
            
            UNION ALL
            
            -- From price book
            SELECT 
                data->>'Product' as product,
                data->>'Supplier' as supplier,
                NULL as country,
                CAST(NULLIF(data->>'Price', '') AS DECIMAL) as price,
                data->>'Currency' as currency,
                'price_book' as source
            FROM price_book_raw
            WHERE data->>'Product' ILIKE %s
        )
        SELECT * FROM all_prices
        WHERE price IS NOT NULL
        ORDER BY price ASC
        LIMIT 10
    """, (f'%{product_name}%', f'%{product_name}%'))
    
    prices = cur.fetchall()
    
    if prices:
        print(f"\nFound {len(prices)} prices for '{product_name}':")
        print("-" * 60)
        print(f"{'Product':30} {'Supplier':20} {'Price':10} {'Source':10}")
        print("-" * 60)
        
        for p in prices:
            product = p['product'][:30] if p['product'] else 'N/A'
            supplier = p['supplier'][:20] if p['supplier'] else 'N/A'
            price = f"{p['currency'] or '$'} {p['price']:.2f}" if p['price'] else 'N/A'
            print(f"{product:30} {supplier:20} {price:10} {p['source']:10}")
        
        if prices[0]['price']:
            print("\n" + "="*60)
            print(f"BEST PRICE: {prices[0]['currency'] or '$'} {prices[0]['price']:.2f}")
            print(f"Supplier: {prices[0]['supplier']}")
            print(f"Product: {prices[0]['product']}")
            print("="*60)
    else:
        print(f"No prices found for '{product_name}'")
    
    cur.close()
    conn.close()

def quick_search_menu():
    """Interactive search menu"""
    print("\n" + "="*60)
    print("PRODUCT SEARCH SYSTEM")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1. Search for a product")
        print("2. Find best price")
        print("3. Common searches")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            term = input("Enter search term: ").strip()
            if term:
                search_products(term)
        
        elif choice == '2':
            product = input("Enter product name: ").strip()
            if product:
                find_best_price(product)
        
        elif choice == '3':
            print("\nCommon Searches:")
            print("1. Olive Oil")
            print("2. Pasta")
            print("3. Tomatoes")
            print("4. Rice")
            print("5. Tuna")
            
            sub_choice = input("Select (1-5): ").strip()
            searches = {
                '1': 'olive oil',
                '2': 'pasta',
                '3': 'tomato',
                '4': 'rice',
                '5': 'tuna'
            }
            if sub_choice in searches:
                search_products(searches[sub_choice])
        
        elif choice == '4':
            print("Exiting search system...")
            break
        
        else:
            print("Invalid choice. Please try again.")

def main():
    # Run some example searches
    print("\n=== PRODUCT SEARCH DEMONSTRATION ===")
    
    # Example 1: Search for olive oil
    results = search_products("olive oil")
    
    # Example 2: Find best pasta price
    find_best_price("pasta")
    
    # Example 3: Search for tomatoes
    search_products("tomato")
    
    print("\n" + "="*60)
    print("SEARCH SYSTEM READY!")
    print("="*60)
    print("\nYou can now:")
    print("1. Search for any product")
    print("2. Find suppliers for specific items")
    print("3. Compare prices across suppliers")
    print("4. View related proposals")
    
    # Uncomment to run interactive menu
    # quick_search_menu()

if __name__ == "__main__":
    main()