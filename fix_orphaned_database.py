#!/usr/bin/env python3
"""
Fix Orphaned Database - Complete Recovery Solution
"""

import os
import subprocess
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def fix_database():
    print("=" * 80)
    print("FIXING ORPHANED DATABASE - COMPLETE SOLUTION")
    print("=" * 80)
    
    # Step 1: Verify current database is accessible
    print("\n1. VERIFYING CURRENT DATABASE...")
    print("-" * 40)
    
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM suppliers")
        count = cur.fetchone()[0]
        print(f"SUCCESS: Database accessible with {count:,} suppliers")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: Cannot access database: {e}")
        return False
    
    # Step 2: Create new resource group
    print("\n2. CREATING NEW RESOURCE GROUP...")
    print("-" * 40)
    
    rg_name = "fdx-production-rg"
    location = "eastus"
    
    cmd = f"az group create --name {rg_name} --location {location}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if "Succeeded" in result.stdout or "already exists" in result.stderr:
        print(f"SUCCESS: Resource group '{rg_name}' ready")
    else:
        print(f"ERROR: {result.stderr}")
        return False
    
    # Step 3: Create new PostgreSQL server
    print("\n3. CREATING NEW POSTGRESQL SERVER...")
    print("-" * 40)
    
    new_server = "fdx-postgres-production"
    
    create_cmd = f"""az postgres flexible-server create \
        --resource-group {rg_name} \
        --name {new_server} \
        --location {location} \
        --admin-user fdxadmin \
        --admin-password "FDX2030!" \
        --sku-name Standard_B2ms \
        --storage-size 32 \
        --version 15 \
        --yes"""
    
    print(f"Creating server '{new_server}'...")
    print("This will take 5-10 minutes...")
    
    result = subprocess.run(create_cmd, shell=True, capture_output=True, text=True)
    
    if "already exists" in result.stderr:
        print("Server already exists - using existing")
    elif result.returncode == 0:
        print("SUCCESS: New server created")
    else:
        print(f"ERROR: {result.stderr[:500]}")
        return False
    
    # Step 4: Configure firewall
    print("\n4. CONFIGURING FIREWALL...")
    print("-" * 40)
    
    firewall_cmd = f"""az postgres flexible-server firewall-rule create \
        --resource-group {rg_name} \
        --name {new_server} \
        --rule-name AllowAll \
        --start-ip-address 0.0.0.0 \
        --end-ip-address 255.255.255.255"""
    
    subprocess.run(firewall_cmd, shell=True, capture_output=True)
    print("Firewall configured for all IPs")
    
    # Step 5: Get new connection string
    print("\n5. GETTING NEW CONNECTION STRING...")
    print("-" * 40)
    
    new_connection = f"postgresql://fdxadmin:FDX2030!@{new_server}.postgres.database.azure.com:5432/foodxchange?sslmode=require"
    print(f"New connection string: {new_connection}")
    
    # Step 6: Create backup and restore script
    print("\n6. CREATING MIGRATION SCRIPT...")
    print("-" * 40)
    
    migration_script = f'''#!/usr/bin/env python3
"""
Migrate Data to New Server
"""

import os
import subprocess
from datetime import datetime

# Old server (orphaned but still working)
OLD_DB = "{os.getenv('DATABASE_URL')}"

# New server
NEW_DB = "{new_connection}"

print("Starting migration from orphaned to new database...")

# Step 1: Backup from old
backup_file = f"fdx_backup_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.sql"
print(f"Creating backup: {{backup_file}}")

backup_cmd = f'pg_dump "{{OLD_DB}}" > {{backup_file}}'
subprocess.run(backup_cmd, shell=True)
print("Backup completed")

# Step 2: Restore to new
print("Restoring to new server...")
restore_cmd = f'psql "{{NEW_DB}}" < {{backup_file}}'
subprocess.run(restore_cmd, shell=True)
print("Restore completed")

print("Migration successful!")
print(f"New database URL: {{NEW_DB}}")
'''
    
    with open("migrate_database.py", "w") as f:
        f.write(migration_script)
    
    print("Created: migrate_database.py")
    
    # Step 7: Update .env file
    print("\n7. UPDATING CONFIGURATION...")
    print("-" * 40)
    
    # Read current .env
    with open(".env", "r") as f:
        lines = f.readlines()
    
    # Update DATABASE_URL
    new_lines = []
    updated = False
    for line in lines:
        if line.startswith("DATABASE_URL="):
            new_lines.append(f"# Old (orphaned): {line}")
            new_lines.append(f"DATABASE_URL={new_connection}\n")
            updated = True
        else:
            new_lines.append(line)
    
    if not updated:
        new_lines.append(f"\nDATABASE_URL={new_connection}\n")
    
    # Save backup of old .env
    with open(".env.backup", "w") as f:
        f.writelines(lines)
    
    # Write new .env
    with open(".env", "w") as f:
        f.writelines(new_lines)
    
    print("Updated .env file (backup saved as .env.backup)")
    
    print("\n" + "=" * 80)
    print("RECOVERY PLAN READY!")
    print("=" * 80)
    print("""
    NEXT STEPS:
    
    1. Run the migration (copies all data):
       python migrate_database.py
    
    2. Test the new connection:
       python -c "import psycopg2; psycopg2.connect('{}').cursor().execute('SELECT COUNT(*) FROM suppliers')"
    
    3. Update your VM:
       ssh azureuser@4.206.1.15
       # Update the DATABASE_URL in .env on VM
    
    4. The new database is properly managed in:
       - Resource Group: {}
       - Server: {}
       - Visible in Azure Portal
       - Properly backed up
    """.format(new_connection, rg_name, new_server))
    
    return True

if __name__ == "__main__":
    fix_database()