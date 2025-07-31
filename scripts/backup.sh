#!/bin/sh
# Automated Backup Script for Production
# This script runs in the backup container via cron

# Configuration
BACKUP_DIR="/backups"
RETENTION_DAYS=7
DB_HOST="db"
DB_NAME="foodxchange_prod"
DB_USER="foodxchange"

# Create timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/automated_backup_${TIMESTAMP}.sql.gz"

# Create backup
echo "[$(date)] Starting automated backup..."
pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "[$(date)] Backup completed: $BACKUP_FILE"
    
    # Check file size
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "[$(date)] Backup size: $SIZE"
    
    # Clean old backups
    echo "[$(date)] Cleaning backups older than ${RETENTION_DAYS} days..."
    find "$BACKUP_DIR" -name "automated_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    
    # List remaining backups
    echo "[$(date)] Current backups:"
    ls -lh "$BACKUP_DIR"/automated_backup_*.sql.gz
else
    echo "[$(date)] ERROR: Backup failed!"
    exit 1
fi

echo "[$(date)] Automated backup process completed"