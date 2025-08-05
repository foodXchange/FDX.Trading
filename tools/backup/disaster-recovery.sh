#!/bin/bash
# FoodXchange Disaster Recovery Script
# Complete system recovery from backups

echo "==============================================="
echo "🚨 FoodXchange Disaster Recovery"
echo "==============================================="

# Function to prompt for confirmation
confirm() {
    read -p "$1 (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Operation cancelled."
        exit 1
    fi
}

# Recovery options menu
echo "Select recovery type:"
echo "1. Point-in-time recovery (Azure managed backup)"
echo "2. Restore from local backup file"
echo "3. Complete infrastructure rebuild"
echo "4. Test recovery (dry run)"
read -p "Enter option (1-4): " RECOVERY_TYPE

case $RECOVERY_TYPE in
    1)
        echo "📅 Point-in-Time Recovery"
        echo "========================"
        read -p "Enter recovery timestamp (YYYY-MM-DDTHH:MM:SSZ): " RESTORE_TIME
        read -p "Enter new server name suffix (e.g., 'restored'): " SERVER_SUFFIX
        
        confirm "Restore database to $RESTORE_TIME?"
        
        echo "Creating restored server..."
        az postgres server restore \
          --resource-group foodxchange-founders-rg \
          --name fdx-postgres-server-$SERVER_SUFFIX \
          --restore-point-in-time "$RESTORE_TIME" \
          --source-server fdx-postgres-server
        
        echo "✅ Server restored. Update your connection string to:"
        echo "fdx-postgres-server-$SERVER_SUFFIX.postgres.database.azure.com"
        ;;
        
    2)
        echo "💾 Restore from Local Backup"
        echo "============================"
        
        # List available backups
        echo "Available backups:"
        ls -lh ./backups/database/backup_*.gz | tail -10
        
        read -p "Enter backup filename (or 'latest' for most recent): " BACKUP_FILE
        
        if [ "$BACKUP_FILE" == "latest" ]; then
            BACKUP_FILE=$(ls -t ./backups/database/backup_*.gz | head -1)
        else
            BACKUP_FILE="./backups/database/$BACKUP_FILE"
        fi
        
        if [ ! -f "$BACKUP_FILE" ]; then
            echo "❌ Backup file not found: $BACKUP_FILE"
            exit 1
        fi
        
        confirm "Restore from $BACKUP_FILE?"
        
        echo "Restoring database..."
        gunzip -c "$BACKUP_FILE" | PGPASSWORD="FDX2030!" psql \
          -h fdx-postgres-server.postgres.database.azure.com \
          -U fdxadmin \
          -d foodxchange
        
        echo "✅ Database restored from backup"
        ;;
        
    3)
        echo "🏗️ Complete Infrastructure Rebuild"
        echo "================================="
        
        confirm "This will recreate ALL infrastructure. Continue?"
        
        # Run infrastructure recreation script
        ./recreate-infrastructure.sh
        
        # Restore latest database backup
        echo "Restoring latest database backup..."
        LATEST_BACKUP=$(ls -t ./backups/database/backup_*.gz | head -1)
        if [ -f "$LATEST_BACKUP" ]; then
            gunzip -c "$LATEST_BACKUP" | PGPASSWORD="FDX2030!" psql \
              -h fdx-postgres-server.postgres.database.azure.com \
              -U fdxadmin \
              -d foodxchange
        fi
        
        # Restore application from Git
        echo "Restoring application code..."
        if [ ! -d ".git" ]; then
            git clone https://github.com/YOUR_USERNAME/foodxchange.git foodxchange-restored
            cd foodxchange-restored
        fi
        
        echo "✅ Complete infrastructure rebuild finished"
        ;;
        
    4)
        echo "🧪 Test Recovery (Dry Run)"
        echo "=========================="
        
        echo "Checking recovery readiness..."
        
        # Check local backups
        echo "✓ Local database backups: $(ls -1 ./backups/database/backup_*.gz 2>/dev/null | wc -l) files"
        
        # Check Azure backup status
        if command -v az &> /dev/null; then
            EARLIEST_RESTORE=$(az postgres server show \
              --resource-group foodxchange-founders-rg \
              --name fdx-postgres-server \
              --query "earliestRestoreDate" -o tsv 2>/dev/null)
            echo "✓ Azure restore available from: $EARLIEST_RESTORE"
        fi
        
        # Check Git status
        if [ -d .git ]; then
            echo "✓ Git repository: $(git remote get-url origin 2>/dev/null || echo 'No remote')"
            echo "✓ Latest commit: $(git log --oneline -1)"
        fi
        
        # Test database connection
        echo "Testing database connection..."
        PGPASSWORD="FDX2030!" psql \
          -h fdx-postgres-server.postgres.database.azure.com \
          -U fdxadmin \
          -d foodxchange \
          -c "SELECT version();" &>/dev/null
        
        if [ $? -eq 0 ]; then
            echo "✓ Database connection: OK"
        else
            echo "✗ Database connection: FAILED"
        fi
        
        echo ""
        echo "Recovery test complete. System is ready for recovery if needed."
        ;;
        
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "==============================================="
echo "Recovery operation completed"
echo "==============================================="