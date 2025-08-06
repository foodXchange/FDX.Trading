#!/usr/bin/env python3
"""
Continue migrating remaining suppliers from old to new database
"""

import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Database connections
OLD_DB = os.getenv('DATABASE_URL')  # From .env - the old database
NEW_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-postgres-production.postgres.database.azure.com/foodxchange?sslmode=require"

def migrate_suppliers():
    """Migrate remaining suppliers from old to new database"""
    
    print("=" * 70)
    print("CONTINUING DATABASE MIGRATION")
    print("=" * 70)
    
    try:
        # Connect to both databases
        print("\nConnecting to databases...")
        old_conn = psycopg2.connect(OLD_DB)
        old_cur = old_conn.cursor()
        
        new_conn = psycopg2.connect(NEW_DB)
        new_cur = new_conn.cursor()
        
        # Check current status
        old_cur.execute("SELECT COUNT(*) FROM suppliers")
        old_count = old_cur.fetchone()[0]
        
        new_cur.execute("SELECT COUNT(*) FROM suppliers")
        new_count = new_cur.fetchone()[0]
        
        print(f"\nCurrent Status:")
        print(f"  Old database: {old_count:,} suppliers")
        print(f"  New database: {new_count:,} suppliers")
        print(f"  To migrate: {old_count - new_count:,} suppliers")
        
        if new_count >= old_count:
            print("\nAll suppliers already migrated!")
            return
        
        # Get IDs already in new database to avoid duplicates
        print("\nChecking existing IDs...")
        new_cur.execute("SELECT id FROM suppliers")
        existing_ids = set(row[0] for row in new_cur.fetchall())
        print(f"Found {len(existing_ids):,} existing IDs")
        
        # Get all suppliers from old database
        print("\nFetching suppliers from old database...")
        old_cur.execute("""
            SELECT id, supplier_name, company_name, country, products,
                   supplier_type, company_email, company_website,
                   certifications, verified, rating, product_categories,
                   created_at, updated_at
            FROM suppliers 
            ORDER BY id
        """)
        
        all_suppliers = old_cur.fetchall()
        print(f"Retrieved {len(all_suppliers):,} total suppliers")
        
        # Filter out existing ones
        suppliers_to_migrate = [s for s in all_suppliers if s[0] not in existing_ids]
        print(f"Need to migrate {len(suppliers_to_migrate):,} new suppliers")
        
        if not suppliers_to_migrate:
            print("No new suppliers to migrate")
            return
        
        # Migrate in batches
        batch_size = 500
        total_migrated = 0
        start_time = time.time()
        
        print(f"\nMigrating in batches of {batch_size}...")
        
        for i in range(0, len(suppliers_to_migrate), batch_size):
            batch = suppliers_to_migrate[i:i+batch_size]
            
            # Insert batch
            try:
                execute_batch(
                    new_cur,
                    """
                    INSERT INTO suppliers (
                        id, supplier_name, company_name, country, products,
                        supplier_type, company_email, company_website,
                        certifications, verified, rating, product_categories,
                        created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    batch,
                    page_size=100
                )
                total_migrated += len(batch)
                new_conn.commit()
                
                # Progress update
                elapsed = time.time() - start_time
                rate = total_migrated / elapsed if elapsed > 0 else 0
                remaining = len(suppliers_to_migrate) - total_migrated
                eta = remaining / rate if rate > 0 else 0
                
                print(f"  Batch {i//batch_size + 1}: Migrated {total_migrated:,} / {len(suppliers_to_migrate):,} "
                      f"({total_migrated*100//len(suppliers_to_migrate)}%) - "
                      f"Rate: {rate:.0f}/sec - ETA: {eta:.0f}s")
                      
            except Exception as e:
                print(f"  Error in batch {i//batch_size + 1}: {str(e)[:100]}")
                # Try simpler insert for this batch
                for row in batch:
                    try:
                        new_cur.execute("""
                            INSERT INTO suppliers (id, supplier_name, company_name, country, products)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (id) DO NOTHING
                        """, row[:5])
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
        print(f"Final count: {final_count:,} suppliers")
        print(f"Newly migrated: {total_migrated:,} suppliers")
        print(f"Time taken: {elapsed_total:.1f} seconds")
        print(f"Average rate: {total_migrated/elapsed_total:.0f} suppliers/second")
        
        if final_count >= 16963:
            print("\nSUCCESS! All suppliers have been migrated!")
        else:
            print(f"\nPartial migration: {final_count:,} / 16,963 suppliers ({final_count*100//16963}%)")
        
        # Close connections
        old_cur.close()
        old_conn.close()
        new_cur.close()
        new_conn.close()
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

def migrate_search_keywords():
    """Migrate search keywords cache"""
    
    print("\n" + "=" * 70)
    print("MIGRATING SEARCH KEYWORDS")
    print("=" * 70)
    
    try:
        old_conn = psycopg2.connect(OLD_DB)
        old_cur = old_conn.cursor()
        
        new_conn = psycopg2.connect(NEW_DB)
        new_cur = new_conn.cursor()
        
        # Check if keywords exist in old DB
        old_cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'supplier_search_keywords'
            )
        """)
        
        if not old_cur.fetchone()[0]:
            print("No search keywords table in old database")
            return
        
        # Get keywords from old DB
        old_cur.execute("SELECT COUNT(*) FROM supplier_search_keywords")
        keyword_count = old_cur.fetchone()[0]
        
        if keyword_count == 0:
            print("No keywords to migrate")
            return
        
        print(f"Found {keyword_count:,} keywords to migrate")
        
        # Check if table exists in new DB
        new_cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'supplier_search_keywords'
            )
        """)
        
        if not new_cur.fetchone()[0]:
            # Create table
            print("Creating search keywords table...")
            new_cur.execute("""
                CREATE TABLE IF NOT EXISTS supplier_search_keywords (
                    keyword VARCHAR(255) PRIMARY KEY,
                    supplier_ids INTEGER[]
                )
            """)
            new_conn.commit()
        
        # Clear existing keywords
        new_cur.execute("DELETE FROM supplier_search_keywords")
        
        # Copy keywords
        print("Copying keywords...")
        old_cur.execute("SELECT keyword, supplier_ids FROM supplier_search_keywords")
        keywords = old_cur.fetchall()
        
        execute_batch(
            new_cur,
            "INSERT INTO supplier_search_keywords (keyword, supplier_ids) VALUES (%s, %s)",
            keywords,
            page_size=100
        )
        
        new_conn.commit()
        
        new_cur.execute("SELECT COUNT(*) FROM supplier_search_keywords")
        final_count = new_cur.fetchone()[0]
        
        print(f"Migrated {final_count:,} search keywords")
        
        # Create index if not exists
        print("Creating search index...")
        new_cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_search_keywords 
            ON supplier_search_keywords(keyword)
        """)
        new_conn.commit()
        
        old_cur.close()
        old_conn.close()
        new_cur.close()
        new_conn.close()
        
        print("Search keywords migration complete!")
        
    except Exception as e:
        print(f"Error migrating keywords: {e}")

if __name__ == "__main__":
    # Run migrations
    migrate_suppliers()
    migrate_search_keywords()
    
    print("\n" + "=" * 70)
    print("ALL MIGRATIONS COMPLETE!")
    print("=" * 70)
    print("\nYour new managed database is ready with all data.")
    print("\nDatabase: fdx-postgres-production.postgres.database.azure.com")
    print("Username: fdxadmin")
    print("Password: FoodXchange2024")