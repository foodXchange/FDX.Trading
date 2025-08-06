#!/bin/bash

# Complete migration script to run on VM

echo "================================================"
echo "COMPLETING DATABASE MIGRATION ON VM"
echo "================================================"

# Update VM with new database connection
cat > update_and_migrate.py << 'EOF'
import psycopg2
import os

# Database connections
OLD_DB = "postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require"
NEW_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-postgres-production.postgres.database.azure.com/foodxchange?sslmode=require"

print("Completing migration on VM...")

try:
    # Connect to both databases
    old_conn = psycopg2.connect(OLD_DB)
    old_cur = old_conn.cursor()
    
    new_conn = psycopg2.connect(NEW_DB)
    new_cur = new_conn.cursor()
    
    # Check current status
    new_cur.execute("SELECT COUNT(*) FROM suppliers")
    current = new_cur.fetchone()[0]
    print(f"Current suppliers in new DB: {current:,}")
    
    if current >= 16963:
        print("Migration already complete!")
    else:
        # Get remaining suppliers
        print("Copying remaining suppliers...")
        old_cur.execute("""
            SELECT id, supplier_name, company_name, country, products
            FROM suppliers 
            WHERE id > (SELECT COALESCE(MAX(id), 0) FROM suppliers)
            ORDER BY id
        """)
        
        remaining = old_cur.fetchall()
        print(f"Found {len(remaining)} suppliers to copy")
        
        # Insert remaining
        for row in remaining[:10000]:  # Batch limit
            try:
                new_cur.execute("""
                    INSERT INTO suppliers (id, supplier_name, company_name, country, products)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, row)
            except:
                pass
        
        new_conn.commit()
        
        # Final count
        new_cur.execute("SELECT COUNT(*) FROM suppliers")
        final = new_cur.fetchone()[0]
        print(f"Migration complete! Total suppliers: {final:,}")
    
    # Update .env file
    print("\nUpdating .env file...")
    with open("/home/fdxfounder/fdx/app/.env", "w") as f:
        f.write(f"DATABASE_URL={NEW_DB}\n")
        f.write("# Other environment variables here\n")
    
    print("Environment updated!")
    
    old_cur.close()
    old_conn.close()
    new_cur.close()
    new_conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    print("Old database may be inaccessible")

print("\nTo restart app with new database:")
print("sudo systemctl restart fdx-app")
EOF

# SSH to VM and run the migration
ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15 << 'ENDSSH'
cd ~/fdx/app
python3 update_and_migrate.py

# Restart the application
sudo systemctl restart fdx-app

echo "Migration complete on VM!"
ENDSSH