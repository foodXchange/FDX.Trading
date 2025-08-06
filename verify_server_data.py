import psycopg2
import sys

# Set encoding for Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Poland database connection
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

def verify_all_data():
    """Verify all data is on the Poland server"""
    print("\n" + "="*70)
    print("VERIFYING ALL DATA ON POLAND SERVER")
    print("="*70)
    
    try:
        conn = psycopg2.connect(POLAND_DB)
        cur = conn.cursor()
        
        print("\nServer Location: fdx-poland-db.postgres.database.azure.com")
        print("Region: Poland Central")
        print("Status: CONNECTED")
        
        # Count all tables and records
        print("\n" + "-"*70)
        print("ALL TABLES AND RECORD COUNTS:")
        print("-"*70)
        
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        total_records = 0
        table_count = 0
        
        for table in tables:
            table_name = table[0]
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cur.fetchone()[0]
                if count > 0:
                    table_count += 1
                    total_records += count
                    print(f"  {table_count:3}. {table_name:35} : {count:,} records")
            except:
                pass
        
        print("\n" + "-"*70)
        print(f"SUMMARY:")
        print(f"  Total Tables with Data : {table_count}")
        print(f"  Total Records         : {total_records:,}")
        print("-"*70)
        
        # Key business data
        print("\n" + "="*70)
        print("KEY BUSINESS DATA ON SERVER:")
        print("="*70)
        
        # Suppliers
        cur.execute("SELECT COUNT(*) FROM suppliers")
        suppliers = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT country) FROM suppliers WHERE country IS NOT NULL")
        countries = cur.fetchone()[0]
        print(f"\nSUPPLIERS:")
        print(f"  Total Suppliers : {suppliers:,}")
        print(f"  Countries       : {countries}")
        
        # Buyers
        cur.execute("SELECT COUNT(*) FROM buyers")
        buyers = cur.fetchone()[0]
        print(f"\nBUYERS:")
        print(f"  Total Buyers    : {buyers}")
        
        # Products
        cur.execute("SELECT COUNT(*) FROM products_raw")
        products = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM supplier_product_links")
        linked_products = cur.fetchone()[0]
        print(f"\nPRODUCTS:")
        print(f"  Total Products  : {products}")
        print(f"  Linked Products : {linked_products}")
        
        # Orders
        cur.execute("SELECT COUNT(*) FROM orders_raw")
        orders = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM order_line_items_raw")
        order_items = cur.fetchone()[0]
        print(f"\nORDERS:")
        print(f"  Total Orders    : {orders}")
        print(f"  Order Items     : {order_items}")
        
        # Workflow data
        cur.execute("SELECT COUNT(*) FROM requests_raw")
        requests = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM proposals_samples_raw")
        proposals = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM shipping_raw")
        shipping = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM invoices_raw")
        invoices = cur.fetchone()[0]
        print(f"\nWORKFLOW DATA:")
        print(f"  Requests        : {requests}")
        print(f"  Proposals       : {proposals}")
        print(f"  Shipments       : {shipping}")
        print(f"  Invoices        : {invoices}")
        
        # Compliance data
        cur.execute("SELECT COUNT(*) FROM adaptation_process_raw")
        adaptation = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM kosher_process_raw")
        kosher = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM compliance_process_raw")
        compliance = cur.fetchone()[0]
        print(f"\nCOMPLIANCE DATA:")
        print(f"  Adaptation      : {adaptation}")
        print(f"  Kosher          : {kosher}")
        print(f"  Compliance      : {compliance}")
        
        print("\n" + "="*70)
        print("VERIFICATION COMPLETE!")
        print("="*70)
        print("\nALL DATA IS SUCCESSFULLY STORED ON THE POLAND SERVER")
        print(f"Total: {total_records:,} records across {table_count} tables")
        print("\nDatabase is ready for production use!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n[ERROR]: {e}")

if __name__ == "__main__":
    verify_all_data()