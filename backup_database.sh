#!/bin/bash

# Manual backup script for FDX PostgreSQL database

echo "=========================================="
echo "FDX DATABASE BACKUP SCRIPT"
echo "=========================================="

# Configuration
DB_HOST="fdx-postgres-production.postgres.database.azure.com"
DB_NAME="foodxchange"
DB_USER="fdxadmin"
DB_PASS="FoodXchange2024"
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/fdx_backup_$DATE.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo "Starting backup of $DB_NAME database..."
echo "Backup file: $BACKUP_FILE"

# Perform backup using pg_dump
PGPASSWORD=$DB_PASS pg_dump \
  -h $DB_HOST \
  -U $DB_USER \
  -d $DB_NAME \
  -f $BACKUP_FILE \
  --verbose \
  --no-owner \
  --no-acl

if [ $? -eq 0 ]; then
    # Compress the backup
    echo "Compressing backup..."
    gzip $BACKUP_FILE
    
    FINAL_FILE="$BACKUP_FILE.gz"
    SIZE=$(ls -lh $FINAL_FILE | awk '{print $5}')
    
    echo "=========================================="
    echo "BACKUP COMPLETE!"
    echo "=========================================="
    echo "File: $FINAL_FILE"
    echo "Size: $SIZE"
    echo ""
    echo "To restore this backup:"
    echo "  gunzip $FINAL_FILE"
    echo "  psql -h $DB_HOST -U $DB_USER -d $DB_NAME < $BACKUP_FILE"
else
    echo "BACKUP FAILED!"
    exit 1
fi

# Optional: Upload to Azure Blob Storage
# Uncomment and configure if you have Azure Storage account
# echo "Uploading to Azure Storage..."
# az storage blob upload \
#   --account-name YOUR_STORAGE_ACCOUNT \
#   --container-name backups \
#   --name $(basename $FINAL_FILE) \
#   --file $FINAL_FILE

# Clean up old backups (keep last 7 local backups)
echo "Cleaning old backups..."
ls -t $BACKUP_DIR/fdx_backup_*.sql.gz | tail -n +8 | xargs -r rm

echo "Done!"