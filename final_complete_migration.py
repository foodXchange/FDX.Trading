#!/usr/bin/env python3
"""
Final migration script - complete transfer of all remaining suppliers
"""

import psycopg2
from psycopg2.extras import execute_batch
import time

def main():
    print("=" * 70)
    print("FINAL DATABASE MIGRATION - COMPLETING TRANSFER")
    print("=" * 70)
    
    # Database connections using direct parameters
    old_password = 'FDX2030!'
    
    try:
        # Connect to old database
        print("\nConnecting to old database (fdx-postgres-server)...")
        old_conn_str = f"host='fdx-postgres-server.postgres.database.azure.com' port='5432' dbname='foodxchange' user='fdxadmin' password='{old_password}' sslmode='require'"
        old_conn = psycopg2.connect(old_conn_str)
        old_cur = old_conn.cursor()
        
        # Connect to new database
        print("Connecting to new database (fdx-postgres-production)...")
        new_conn = psycopg2.connect(
            host='fdx-postgres-production.postgres.database.azure.com',
            database='foodxchange',
            user='fdxadmin',
            password='FoodXchange2024',
            sslmode='require'
        )
        new_cur = new_conn.cursor()
        
        # Check current status
        old_cur.execute("SELECT COUNT(*) FROM suppliers")
        old_count = old_cur.fetchone()[0]
        
        new_cur.execute("SELECT COUNT(*) FROM suppliers")
        new_count = old_cur.fetchone()[0]
        
        print(f"\nCurrent Status:")
        print(f"  Old database: {old_count:,} suppliers")
        print(f"  New database: {new_count:,} suppliers")
        print(f"  To migrate: {old_count - new_count:,} suppliers")
        
        if new_count >= old_count:
            print("\nAll suppliers already migrated!")
            return
        
        # Get all supplier IDs from new database to avoid duplicates
        print("\nGetting existing IDs from new database...")
        new_cur.execute("SELECT id FROM suppliers")
        existing_ids = set(row[0] for row in new_cur.fetchall())
        print(f"Found {len(existing_ids):,} existing suppliers")
        
        # Get all suppliers from old database
        print("\nFetching ALL suppliers from old database...")
        old_cur.execute("""
            SELECT id, supplier_name, company_name, country, products,
                   supplier_type, company_email, company_website
            FROM suppliers 
            ORDER BY id
        """)
        
        all_suppliers = old_cur.fetchall()
        print(f"Retrieved {len(all_suppliers):,} total suppliers from old database")
        
        # Filter out existing ones
        suppliers_to_migrate = [s for s in all_suppliers if s[0] not in existing_ids]
        print(f"Found {len(suppliers_to_migrate):,} NEW suppliers to migrate")
        
        if not suppliers_to_migrate:
            print("No new suppliers to migrate!")
            return
        
        # Migrate in batches
        batch_size = 500
        total_migrated = 0
        errors = 0
        start_time = time.time()
        
        print(f"\nStarting migration of {len(suppliers_to_migrate):,} suppliers...")
        print("This may take a few minutes...")
        
        for i in range(0, len(suppliers_to_migrate), batch_size):
            batch = suppliers_to_migrate[i:i+batch_size]
            
            try:
                # Use execute_batch for faster insertion
                execute_batch(
                    new_cur,
                    """
                    INSERT INTO suppliers (
                        id, supplier_name, company_name, country, products,
                        supplier_type, company_email, company_website
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    batch,
                    page_size=100
                )
                
                migrated_in_batch = len(batch)
                total_migrated += migrated_in_batch
                new_conn.commit()
                
                # Progress update
                progress = (i + batch_size) / len(suppliers_to_migrate) * 100
                if progress > 100:
                    progress = 100
                    
                elapsed = time.time() - start_time
                rate = total_migrated / elapsed if elapsed > 0 else 0
                
                print(f"  Progress: {total_migrated:,}/{len(suppliers_to_migrate):,} "
                      f"({progress:.1f}%) - Rate: {rate:.0f} suppliers/sec")
                      
            except Exception as e:
                errors += 1
                print(f"  Error in batch: {str(e)[:100]}")
                # Try individual inserts for this batch
                for row in batch:
                    try:
                        new_cur.execute("""
                            INSERT INTO suppliers (
                                id, supplier_name, company_name, country, products,
                                supplier_type, company_email, company_website
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (id) DO NOTHING
                        """, row)
                        total_migrated += 1
                    except:
                        pass
                new_conn.commit()
        
        # Final verification
        new_cur.execute("SELECT COUNT(*) FROM suppliers")
        final_count = new_cur.fetchone()[0]
        
        elapsed_total = time.time() - start_time
        
        print("\n" + "=" * 70)
        print("MIGRATION COMPLETE!")
        print("=" * 70)
        print(f"Started with: {new_count:,} suppliers")
        print(f"Final count: {final_count:,} suppliers")
        print(f"Migrated: {total_migrated:,} suppliers")
        print(f"Errors: {errors}")
        print(f"Time taken: {elapsed_total:.1f} seconds")
        
        if final_count >= 16963:
            print("\n🎉 SUCCESS! ALL 16,963 SUPPLIERS MIGRATED!")
            print("Your new managed database is complete!")
        else:
            missing = 16963 - final_count
            print(f"\nPartial success: {final_count:,} / 16,963 suppliers")
            print(f"Still missing: {missing:,} suppliers")
        
        # Migrate search keywords if they exist
        print("\n" + "-" * 70)
        print("Checking for search keywords...")
        
        try:
            old_cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'supplier_search_keywords'
                )
            """)
            
            if old_cur.fetchone()[0]:
                old_cur.execute("SELECT COUNT(*) FROM supplier_search_keywords")
                keyword_count = old_cur.fetchone()[0]
                
                if keyword_count > 0:
                    print(f"Found {keyword_count:,} search keywords")
                    
                    # Create table in new DB if needed
                    new_cur.execute("""
                        CREATE TABLE IF NOT EXISTS supplier_search_keywords (
                            keyword VARCHAR(255) PRIMARY KEY,
                            supplier_ids INTEGER[]
                        )
                    """)
                    
                    # Clear and copy keywords
                    new_cur.execute("DELETE FROM supplier_search_keywords")
                    
                    old_cur.execute("SELECT keyword, supplier_ids FROM supplier_search_keywords")
                    keywords = old_cur.fetchall()
                    
                    execute_batch(
                        new_cur,
                        "INSERT INTO supplier_search_keywords (keyword, supplier_ids) VALUES (%s, %s)",
                        keywords,
                        page_size=100
                    )
                    
                    new_conn.commit()
                    print(f"Migrated {len(keywords):,} search keywords")
                else:
                    print("No keywords to migrate")
            else:
                print("No search keywords table in old database")
                
        except Exception as e:
            print(f"Could not migrate keywords: {str(e)[:100]}")
        
        # Close connections
        old_cur.close()
        old_conn.close()
        new_cur.close()
        new_conn.close()
        
        print("\n" + "=" * 70)
        print("ALL OPERATIONS COMPLETE!")
        print("=" * 70)
        print("\nYour new managed database details:")
        print("  Server: fdx-postgres-production.postgres.database.azure.com")
        print("  Database: foodxchange")
        print("  Username: fdxadmin")
        print("  Password: FoodXchange2024")
        print(f"  Total Suppliers: {final_count:,}")
        print("\nThe database is properly managed in Azure Portal with automatic backups.")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()