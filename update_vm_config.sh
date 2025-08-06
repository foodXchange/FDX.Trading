#!/bin/bash

echo "=========================================="
echo "UPDATING VM WITH NEW DATABASE AND AI KEYS"
echo "=========================================="

# Create the update script locally
cat > vm_update.py << 'EOF'
#!/usr/bin/env python3
import os

print("Updating VM configuration...")

# New configuration
new_env_content = """# FDX Trading Environment Configuration

# Database - New Managed PostgreSQL
DATABASE_URL=postgresql://fdxadmin:FoodXchange2024@fdx-postgres-production.postgres.database.azure.com/foodxchange?sslmode=require

# Azure OpenAI Configuration
AZURE_OPENAI_KEY=4mSTbyKUOviCB5cxUXY7xKveMTmeRqozTJSmW61MkJzSknM8YsBLJQQJ99BDACYeBjFXJ3w3AAAAACOGtOUz
AZURE_OPENAI_ENDPOINT=https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# User Email
USER_EMAIL=udi@fdx.trading

# Other configurations can be added here
"""

# Backup existing .env
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        backup = f.read()
    with open('.env.backup', 'w') as f:
        f.write(backup)
    print("Backed up existing .env to .env.backup")

# Write new .env
with open('.env', 'w') as f:
    f.write(new_env_content)

print("Updated .env file with new configuration")
print("\nNew configuration includes:")
print("- New managed PostgreSQL database")
print("- Azure OpenAI credentials")
print("\nRestart the app with: sudo systemctl restart fdx-app")
EOF

# SSH to VM and run the update
echo "Connecting to VM and updating configuration..."
ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15 << 'ENDSSH'
cd ~/fdx/app

# Create the update script on VM
cat > vm_update.py << 'EOFPY'
#!/usr/bin/env python3
import os

print("Updating VM configuration...")

# New configuration
new_env_content = """# FDX Trading Environment Configuration

# Database - New Managed PostgreSQL
DATABASE_URL=postgresql://fdxadmin:FoodXchange2024@fdx-postgres-production.postgres.database.azure.com/foodxchange?sslmode=require

# Azure OpenAI Configuration
AZURE_OPENAI_KEY=4mSTbyKUOviCB5cxUXY7xKveMTmeRqozTJSmW61MkJzSknM8YsBLJQQJ99BDACYeBjFXJ3w3AAAAACOGtOUz
AZURE_OPENAI_ENDPOINT=https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# User Email
USER_EMAIL=udi@fdx.trading

# Other configurations can be added here
"""

# Backup existing .env
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        backup = f.read()
    with open('.env.backup', 'w') as f:
        f.write(backup)
    print("Backed up existing .env to .env.backup")

# Write new .env
with open('.env', 'w') as f:
    f.write(new_env_content)

print("Updated .env file with new configuration")
print("\nNew configuration includes:")
print("- New managed PostgreSQL database")
print("- Azure OpenAI credentials")
EOFPY

# Run the update script
python3 vm_update.py

# Test the database connection
echo ""
echo "Testing new database connection..."
python3 -c "
import psycopg2
import os

# Load the new .env
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('DATABASE_URL='):
            db_url = line.split('=', 1)[1].strip()
            break

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM suppliers')
    count = cur.fetchone()[0]
    print(f'SUCCESS! Connected to new database with {count:,} suppliers')
    cur.close()
    conn.close()
except Exception as e:
    print(f'Error connecting: {e}')
"

# Restart the application
echo ""
echo "Restarting FDX application..."
sudo systemctl restart fdx-app

# Check status
echo ""
echo "Checking application status..."
sudo systemctl status fdx-app --no-pager | head -10

echo ""
echo "=========================================="
echo "VM UPDATE COMPLETE!"
echo "=========================================="
echo ""
echo "Your VM is now using:"
echo "- New managed PostgreSQL database"
echo "- Azure OpenAI for AI features"
echo ""
echo "Access your application at: http://4.206.1.15"
echo ""
ENDSSH

echo ""
echo "VM configuration update completed!"