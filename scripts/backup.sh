#!/bin/bash

# PostgreSQL backup script for FoodXchange
# Runs daily in production environment

BACKUP_DIR="/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="foodxchange"
DB_USER="postgres"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform database backup
echo "Starting backup at $(date)"
PGPASSWORD=$POSTGRES_PASSWORD pg_dump \
    -h postgres \
    -U $DB_USER \
    -d $DB_NAME \
    -f "$BACKUP_DIR/foodxchange_backup_$TIMESTAMP.sql"

# Compress the backup
gzip "$BACKUP_DIR/foodxchange_backup_$TIMESTAMP.sql"

# Remove backups older than 7 days
find "$BACKUP_DIR" -name "foodxchange_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed at $(date)"
echo "Backup file: foodxchange_backup_$TIMESTAMP.sql.gz"

# Optional: Upload to cloud storage (Azure Blob Storage)
# Uncomment and configure if needed
# az storage blob upload \
#     --account-name $AZURE_STORAGE_ACCOUNT \
#     --container-name backups \
#     --name "foodxchange_backup_$TIMESTAMP.sql.gz" \
#     --file "$BACKUP_DIR/foodxchange_backup_$TIMESTAMP.sql.gz"