#!/bin/bash

# Update VM with new database connection string

echo "=================================================="
echo "UPDATING VM WITH NEW DATABASE CONNECTION"
echo "=================================================="

# New connection string
NEW_DB="postgresql://fdxadmin:FoodXchange2024@fdx-postgres-production.postgres.database.azure.com/foodxchange?sslmode=require"

# Connect to VM and update
ssh azureuser@4.206.1.15 << 'ENDSSH'

echo "Updating database connection on VM..."

# Backup current .env
cp ~/fdx/.env ~/fdx/.env.backup.$(date +%Y%m%d_%H%M%S)

# Update DATABASE_URL in .env
cd ~/fdx
if [ -f .env ]; then
    # Remove old DATABASE_URL line and add new one
    grep -v "^DATABASE_URL=" .env > .env.tmp
    echo "DATABASE_URL=postgresql://fdxadmin:FoodXchange2024@fdx-postgres-production.postgres.database.azure.com/foodxchange?sslmode=require" >> .env.tmp
    mv .env.tmp .env
    echo "✓ Updated .env file"
else
    echo "DATABASE_URL=postgresql://fdxadmin:FoodXchange2024@fdx-postgres-production.postgres.database.azure.com/foodxchange?sslmode=require" > .env
    echo "✓ Created .env file"
fi

# Test new connection
echo "Testing new database connection..."
python3 -c "
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM suppliers')
    count = cur.fetchone()[0]
    print(f'✓ Connected to new database: {count:,} suppliers')
    cur.close()
    conn.close()
except Exception as e:
    print(f'✗ Connection failed: {e}')
"

# Restart the application
echo "Restarting application with new database..."
pkill -f "uvicorn"
sleep 2

# Start the app with new database
nohup python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &

echo "✓ Application restarted"
echo ""
echo "VM UPDATE COMPLETE!"
echo "New database: fdx-postgres-production"
echo "Check website: https://www.fdx.trading"

ENDSSH

echo ""
echo "=================================================="
echo "VM DATABASE UPDATE COMPLETE"
echo "=================================================="