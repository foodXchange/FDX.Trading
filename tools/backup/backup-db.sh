#!/bin/bash
# FoodXchange Database Backup Script
# This script creates PostgreSQL database backups with automatic rotation

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/database"
DB_NAME="foodxchange"
SERVER="fdx-postgres-server.postgres.database.azure.com"
USERNAME="fdxadmin"
EXPORT PGPASSWORD="FDX2030!"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo "==============================================="
echo "FoodXchange Database Backup"
echo "Date: $(date)"
echo "==============================================="

# Create the backup
echo "Creating backup: backup_$DATE.sql"
pg_dump "host=$SERVER port=5432 dbname=$DB_NAME user=$USERNAME sslmode=require" \
  > "$BACKUP_DIR/backup_$DATE.sql"

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "✅ Backup completed successfully!"
    
    # Get file size
    SIZE=$(ls -lh "$BACKUP_DIR/backup_$DATE.sql" | awk '{print $5}')
    echo "Backup size: $SIZE"
    
    # Compress the backup
    echo "Compressing backup..."
    gzip "$BACKUP_DIR/backup_$DATE.sql"
    
    # Keep only last 10 backups (delete older ones)
    echo "Cleaning old backups..."
    ls -t $BACKUP_DIR/backup_*.sql.gz | tail -n +11 | xargs -r rm
    
    echo "✅ Backup process completed: backup_$DATE.sql.gz"
else
    echo "❌ Backup failed!"
    exit 1
fi

# Optional: Upload to Azure Storage
# Uncomment if you have Azure CLI configured
# echo "Uploading to Azure Storage..."
# az storage blob upload \
#   --account-name mystorageaccount \
#   --container-name backups \
#   --name "db-backup-$DATE.sql.gz" \
#   --file "$BACKUP_DIR/backup_$DATE.sql.gz"

echo "==============================================="