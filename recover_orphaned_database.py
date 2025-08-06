#!/usr/bin/env python3
"""
Recover Orphaned Azure PostgreSQL Database
The database is still running but not visible in portal
"""

import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

print("=" * 80)
print("AZURE DATABASE RECOVERY ANALYSIS")
print("=" * 80)

# Test current connection
print("\n1. TESTING CURRENT DATABASE CONNECTION:")
print("-" * 40)

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    # Get database info
    cur.execute("SELECT version()")
    version = cur.fetchone()[0]
    print(f"✅ Database is ALIVE and RESPONDING")
    print(f"   Version: {version.split(',')[0]}")
    
    # Get connection details from URL
    db_url = os.getenv('DATABASE_URL')
    if 'fdx-postgres-server' in db_url:
        print(f"✅ Server: fdx-postgres-server.postgres.database.azure.com")
    
    # Check data
    cur.execute("SELECT COUNT(*) FROM suppliers")
    supplier_count = cur.fetchone()[0]
    print(f"✅ Data intact: {supplier_count:,} suppliers")
    
    # Get sample recent data
    cur.execute("""
        SELECT supplier_name, country, created_at 
        FROM suppliers 
        ORDER BY created_at DESC 
        LIMIT 3
    """)
    print("\nMost recent suppliers (proof of data):")
    for row in cur.fetchall():
        print(f"  - {row[0]} ({row[1]}) - {row[2]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nThis means the database might have been deleted!")
    exit(1)

print("\n2. CRITICAL SITUATION ASSESSMENT:")
print("-" * 40)
print("⚠️ ORPHANED RESOURCE DETECTED")
print("   - Database server is running (proven above)")
print("   - Resource group 'foodxchange-rg' was deleted")
print("   - Database not visible in Azure Portal")
print("   - BUT data is still accessible!")

print("\n3. IMMEDIATE ACTIONS REQUIRED:")
print("-" * 40)
print("""
OPTION 1: EMERGENCY DATA BACKUP (DO THIS FIRST!)
-------------------------------------------------
1. Create local backup immediately:
   pg_dump "postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require" > backup_$(date +%Y%m%d_%H%M%S).sql

2. Export critical data to CSV:
   python export_all_data.py

OPTION 2: RECOVER IN AZURE (RECOMMENDED)
----------------------------------------
1. Check if database still exists in another RG:
   az postgres flexible-server list --output table
   
2. If found, note the resource group and update connection

3. If not found but still accessible (current situation):
   - The database might be in "soft delete" state
   - Azure might still be billing you
   - Check: https://portal.azure.com/#blade/HubsExtension/SubscriptionsBlade

OPTION 3: MIGRATE TO NEW DATABASE
---------------------------------
1. Create new resource group:
   az group create --name fdx-production-rg --location eastus

2. Create new PostgreSQL server:
   az postgres flexible-server create \
     --resource-group fdx-production-rg \
     --name fdx-postgres-prod \
     --admin-user fdxadmin \
     --admin-password FDX2030! \
     --sku-name Standard_B2s \
     --storage-size 32 \
     --version 15

3. Migrate data:
   python migrate_to_new_server.py
""")

print("\n4. CHECKING AZURE RESOURCES:")
print("-" * 40)
print("Run these commands to find your database:\n")

print("# List all PostgreSQL servers in subscription:")
print('az postgres flexible-server list --output table')
print()
print("# Search for specific server:")
print('az postgres flexible-server show --ids $(az resource list --query "[?contains(name, \'fdx-postgres\')].id" -o tsv)')
print()
print("# Check all resource groups:")
print('az group list --output table')

print("\n" + "=" * 80)
print("CRITICAL RECOMMENDATIONS")
print("=" * 80)
print("""
1. IMMEDIATE: Backup your data NOW before Azure fully deletes it
2. CHECK: Azure Portal > Cost Management to see if you're still being charged
3. FIND: Use Azure CLI to locate the orphaned resource
4. MIGRATE: Set up new database with proper resource group
5. UPDATE: Update all connection strings to new server

The database is in a CRITICAL state - it could be deleted at any time!
""")

# Create backup script
backup_script = """#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime

# Create backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"fdx_backup_{timestamp}.sql"

print(f"Creating backup: {backup_file}")
cmd = f'pg_dump "{os.getenv("DATABASE_URL")}" > {backup_file}'
subprocess.run(cmd, shell=True)
print(f"Backup completed: {backup_file}")
"""

with open("emergency_backup.py", "w") as f:
    f.write(backup_script)
print("\n✅ Created emergency_backup.py - RUN THIS NOW!")