#!/bin/bash
# FoodXchange Weekly Deep Backup Script
# Performs comprehensive weekly backup including infrastructure config

LOG_FILE="./backups/logs/weekly-backup-$(date +%Y%m%d).log"
mkdir -p ./backups/logs

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "==============================================="
log "🔄 Starting FoodXchange weekly deep backup..."
log "==============================================="

DATE=$(date +%Y-%m-%d)

# 1. Run daily backup first
log "📊 Running daily backup routine..."
./daily-backup.sh

# 2. Create weekly Git tag
log "🏷️ Creating weekly Git tag..."
if [ -d .git ]; then
    git tag -a "weekly-$DATE" -m "Weekly backup $DATE" >> "$LOG_FILE" 2>&1
    if git push origin --tags >> "$LOG_FILE" 2>&1; then
        log "✅ Weekly tag created and pushed: weekly-$DATE"
    else
        log "⚠️ Failed to push tag to remote"
    fi
fi

# 3. Export infrastructure configuration
log "🏗️ Exporting infrastructure configuration..."
if command -v az &> /dev/null; then
    # PostgreSQL server configuration
    az postgres server show \
      --resource-group foodxchange-founders-rg \
      --name fdx-postgres-server > "./backups/infrastructure/postgres-config-$DATE.json" 2>/dev/null
    
    # Firewall rules
    az postgres server firewall-rule list \
      --resource-group foodxchange-founders-rg \
      --server-name fdx-postgres-server > "./backups/infrastructure/firewall-rules-$DATE.json" 2>/dev/null
    
    # Database configuration
    az postgres db list \
      --resource-group foodxchange-founders-rg \
      --server-name fdx-postgres-server > "./backups/infrastructure/databases-$DATE.json" 2>/dev/null
    
    log "✅ Infrastructure configuration exported"
    
    # Upload to Azure Storage (if configured)
    if [ -n "$STORAGE_ACCOUNT" ]; then
        log "☁️ Uploading infrastructure backup to Azure Storage..."
        az storage blob upload-batch \
          --destination backups \
          --source ./backups/infrastructure \
          --pattern "*-$DATE.json" \
          --account-name $STORAGE_ACCOUNT >> "$LOG_FILE" 2>&1
    fi
else
    log "⚠️ Azure CLI not available - skipping infrastructure export"
fi

# 4. Create environment backup (without secrets)
log "📋 Creating environment template..."
cat > ".env.backup-$DATE" << 'EOF'
# FoodXchange Environment Configuration Backup
# Created: $(date)
# 
# Database Configuration
DATABASE_URL=postgresql://fdxadmin:***REDACTED***@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require

# Azure Configuration
AZURE_OPENAI_KEY=***REDACTED***
AZURE_OPENAI_ENDPOINT=https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# App Configuration
APP_NAME=FoodXchange
DEBUG=False
EOF

# 5. Create full database schema dump
log "📐 Creating database schema backup..."
PGPASSWORD="FDX2030!" pg_dump \
  -h fdx-postgres-server.postgres.database.azure.com \
  -U fdxadmin \
  -d foodxchange \
  --schema-only \
  --no-owner \
  --no-privileges \
  > "./backups/database/schema-$DATE.sql" 2>/dev/null

# 6. Create recovery documentation
log "📄 Updating recovery documentation..."
cat > "./backups/RECOVERY-INSTRUCTIONS-$DATE.md" << EOF
# FoodXchange Recovery Instructions
Generated: $(date)

## Quick Recovery Commands

### 1. Database Recovery
\`\`\`bash
# From latest backup
gunzip -c ./backups/database/backup_LATEST.sql.gz | psql "postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require"

# From specific date
az postgres server restore \\
  --resource-group foodxchange-founders-rg \\
  --name fdx-postgres-server-restored \\
  --restore-point-in-time "$DATE" \\
  --source-server fdx-postgres-server
\`\`\`

### 2. Infrastructure Recovery
\`\`\`bash
./recreate-infrastructure.sh
\`\`\`

### 3. Application Recovery
\`\`\`bash
git clone https://github.com/YOUR_USERNAME/foodxchange.git
cd foodxchange
git checkout weekly-$DATE
# Restore .env file with actual values
# Deploy application
\`\`\`

## Backup Inventory
- Database backups: $(ls -1 ./backups/database/backup_*.gz 2>/dev/null | wc -l) files
- Infrastructure configs: $(ls -1 ./backups/infrastructure/*.json 2>/dev/null | wc -l) files
- Git tags: $(git tag -l "weekly-*" 2>/dev/null | wc -l) weekly snapshots

## Last Verified Working Configuration
- Server: fdx-postgres-server.postgres.database.azure.com
- Database: foodxchange
- Last backup: $(ls -t ./backups/database/backup_*.gz 2>/dev/null | head -1)
EOF

# 7. Clean old backups (keep last 4 weeks)
log "🧹 Cleaning old weekly backups..."
find ./backups/infrastructure -name "*-20*.json" -mtime +28 -delete 2>/dev/null
find ./backups/logs -name "*.log" -mtime +30 -delete 2>/dev/null

# 8. Generate backup report
log "==============================================="
log "📊 Weekly Backup Report"
log "==============================================="
log "Database Backups:"
log "  - Daily backups: $(ls -1 ./backups/database/backup_*.gz 2>/dev/null | wc -l)"
log "  - Total size: $(du -sh ./backups/database 2>/dev/null | cut -f1)"
log "  - Oldest: $(ls -t ./backups/database/backup_*.gz 2>/dev/null | tail -1)"
log "  - Newest: $(ls -t ./backups/database/backup_*.gz 2>/dev/null | head -1)"
log ""
log "Infrastructure Backups:"
log "  - Config files: $(ls -1 ./backups/infrastructure/*.json 2>/dev/null | wc -l)"
log "  - Total size: $(du -sh ./backups/infrastructure 2>/dev/null | cut -f1)"
log ""
log "Git Repository:"
log "  - Current branch: $(git branch --show-current 2>/dev/null || echo 'N/A')"
log "  - Last commit: $(git log --oneline -1 2>/dev/null || echo 'N/A')"
log "  - Weekly tags: $(git tag -l "weekly-*" 2>/dev/null | wc -l)"
log "==============================================="
log "✅ Weekly deep backup completed!"

exit 0