#!/bin/bash
# FoodXchange Backup & Recovery Test Script
# Monthly health check for backup systems

echo "==============================================="
echo "🔍 FoodXchange Backup System Health Check"
echo "Date: $(date)"
echo "==============================================="

ERRORS=0

# Function to check and report status
check_status() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2: PASS"
    else
        echo "❌ $2: FAIL"
        ERRORS=$((ERRORS + 1))
    fi
}

# 1. Test database connectivity
echo ""
echo "1. Testing Database Connectivity..."
PGPASSWORD="FDX2030!" psql \
  -h fdx-postgres-server.postgres.database.azure.com \
  -U fdxadmin \
  -d foodxchange \
  -c "SELECT current_timestamp;" &>/dev/null
check_status $? "Database connection"

# 2. Test backup creation
echo ""
echo "2. Testing Backup Creation..."
TEST_BACKUP="./backups/database/test_backup_$(date +%Y%m%d_%H%M%S).sql"
PGPASSWORD="FDX2030!" pg_dump \
  -h fdx-postgres-server.postgres.database.azure.com \
  -U fdxadmin \
  -d foodxchange \
  --table=suppliers \
  --data-only \
  > "$TEST_BACKUP" 2>/dev/null
check_status $? "Backup creation"

# Check backup file size
if [ -f "$TEST_BACKUP" ]; then
    SIZE=$(stat -f%z "$TEST_BACKUP" 2>/dev/null || stat -c%s "$TEST_BACKUP" 2>/dev/null)
    if [ $SIZE -gt 0 ]; then
        echo "✅ Backup file size: $(ls -lh $TEST_BACKUP | awk '{print $5}')"
        rm "$TEST_BACKUP"
    else
        echo "❌ Backup file is empty"
        ERRORS=$((ERRORS + 1))
    fi
fi

# 3. Check Azure CLI availability
echo ""
echo "3. Testing Azure CLI..."
if command -v az &> /dev/null; then
    az --version &>/dev/null
    check_status $? "Azure CLI installed"
    
    # Test Azure authentication
    az account show &>/dev/null
    check_status $? "Azure authentication"
else
    echo "⚠️ Azure CLI not installed"
fi

# 4. Check Git repository
echo ""
echo "4. Testing Git Repository..."
if [ -d .git ]; then
    git status &>/dev/null
    check_status $? "Git repository"
    
    # Check remote
    git remote -v &>/dev/null
    check_status $? "Git remote configured"
else
    echo "⚠️ Git repository not initialized"
fi

# 5. Check backup directories
echo ""
echo "5. Checking Backup Directories..."
DIRS=("./backups/database" "./backups/infrastructure" "./backups/logs")
for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ Directory exists: $dir"
    else
        echo "❌ Directory missing: $dir"
        ERRORS=$((ERRORS + 1))
    fi
done

# 6. Check backup rotation
echo ""
echo "6. Checking Backup Rotation..."
DB_BACKUP_COUNT=$(ls -1 ./backups/database/backup_*.gz 2>/dev/null | wc -l)
echo "📊 Database backups: $DB_BACKUP_COUNT files"
if [ $DB_BACKUP_COUNT -gt 20 ]; then
    echo "⚠️ Warning: Too many backup files. Consider cleanup."
fi

# 7. Test backup restoration (small table only)
echo ""
echo "7. Testing Backup Restoration..."
# Create a test table
PGPASSWORD="FDX2030!" psql \
  -h fdx-postgres-server.postgres.database.azure.com \
  -U fdxadmin \
  -d foodxchange \
  -c "CREATE TABLE IF NOT EXISTS backup_test (id SERIAL PRIMARY KEY, test_data TEXT, created_at TIMESTAMP DEFAULT NOW());" &>/dev/null

# Insert test data
PGPASSWORD="FDX2030!" psql \
  -h fdx-postgres-server.postgres.database.azure.com \
  -U fdxadmin \
  -d foodxchange \
  -c "INSERT INTO backup_test (test_data) VALUES ('Test backup data $(date)');" &>/dev/null

# Backup the test table
TEST_RESTORE="./backups/database/test_restore_$(date +%Y%m%d).sql"
PGPASSWORD="FDX2030!" pg_dump \
  -h fdx-postgres-server.postgres.database.azure.com \
  -U fdxadmin \
  -d foodxchange \
  --table=backup_test \
  > "$TEST_RESTORE" 2>/dev/null

# Drop and restore
PGPASSWORD="FDX2030!" psql \
  -h fdx-postgres-server.postgres.database.azure.com \
  -U fdxadmin \
  -d foodxchange \
  -c "DROP TABLE backup_test;" &>/dev/null

PGPASSWORD="FDX2030!" psql \
  -h fdx-postgres-server.postgres.database.azure.com \
  -U fdxadmin \
  -d foodxchange \
  < "$TEST_RESTORE" &>/dev/null

check_status $? "Backup restoration"

# Cleanup
PGPASSWORD="FDX2030!" psql \
  -h fdx-postgres-server.postgres.database.azure.com \
  -U fdxadmin \
  -d foodxchange \
  -c "DROP TABLE IF EXISTS backup_test;" &>/dev/null
rm -f "$TEST_RESTORE"

# Summary
echo ""
echo "==============================================="
echo "📊 Health Check Summary"
echo "==============================================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ All backup systems operational!"
    echo "Your backup strategy is working correctly."
else
    echo "❌ Found $ERRORS issues that need attention!"
    echo "Please review the errors above and take action."
fi
echo "==============================================="

exit $ERRORS