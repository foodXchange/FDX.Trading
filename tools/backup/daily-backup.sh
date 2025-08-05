#!/bin/bash
# FoodXchange Daily Backup Script
# Runs database backup, code backup, and status checks

LOG_FILE="./backups/logs/daily-backup-$(date +%Y%m%d).log"
mkdir -p ./backups/logs

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "==============================================="
log "🚀 Starting FoodXchange daily backup routine..."
log "==============================================="

# 1. Backup database
log "📊 Backing up database..."
if ./backup-db.sh >> "$LOG_FILE" 2>&1; then
    log "✅ Database backup completed successfully"
else
    log "❌ Database backup failed!"
    exit 1
fi

# 2. Commit code changes to Git
log "💻 Backing up code to Git..."
if [ -d .git ]; then
    # Add all changes
    git add . >> "$LOG_FILE" 2>&1
    
    # Commit with timestamp
    if git diff --staged --quiet; then
        log "No changes to commit"
    else
        git commit -m "Auto backup: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1
        log "✅ Changes committed"
        
        # Push to remote
        if git push origin main >> "$LOG_FILE" 2>&1; then
            log "✅ Code pushed to GitHub"
        else
            log "⚠️ Failed to push to GitHub - will retry next time"
        fi
    fi
else
    log "⚠️ Git repository not initialized - skipping code backup"
fi

# 3. Check Azure backup status
log "☁️ Checking Azure automated backups..."
if command -v az &> /dev/null; then
    EARLIEST_RESTORE=$(az postgres server show \
      --resource-group foodxchange-founders-rg \
      --name fdx-postgres-server \
      --query "earliestRestoreDate" -o tsv 2>/dev/null)
    
    if [ -n "$EARLIEST_RESTORE" ]; then
        log "✅ Azure backups available from: $EARLIEST_RESTORE"
    else
        log "⚠️ Could not verify Azure backup status"
    fi
else
    log "⚠️ Azure CLI not installed - skipping Azure backup check"
fi

# 4. Check backup storage usage
log "💾 Checking backup storage..."
BACKUP_COUNT=$(ls -1 ./backups/database/backup_*.gz 2>/dev/null | wc -l)
BACKUP_SIZE=$(du -sh ./backups/database 2>/dev/null | cut -f1)
log "Local backups: $BACKUP_COUNT files, Total size: $BACKUP_SIZE"

# 5. Create daily summary
log "==============================================="
log "📋 Daily Backup Summary:"
log "- Database backup: ✅ Completed"
log "- Code backup: $(git log --oneline -1 2>/dev/null || echo 'N/A')"
log "- Local backups: $BACKUP_COUNT files ($BACKUP_SIZE)"
log "- Azure restore point: $EARLIEST_RESTORE"
log "==============================================="
log "✅ Daily backup routine completed!"

# Send notification (optional - requires mail setup)
# echo "Daily backup completed at $(date)" | mail -s "FoodXchange Backup Report" your@email.com

exit 0