# FoodXchange Backup & Recovery - Quick Reference

## 🚨 Emergency Numbers
- **Database Server**: fdx-postgres-server.postgres.database.azure.com
- **Resource Group**: foodxchange-rg
- **Backup Schedule**: Daily 2 AM, Weekly Sundays 3 AM

## ⚡ Quick Commands

### 🔥 EMERGENCY RECOVERY
```bash
# System is down - Full recovery
./disaster-recovery.sh   # Interactive menu

# Quick database restore (last backup)
gunzip -c ./backups/database/$(ls -t backups/database/backup_*.gz | head -1) | \
  psql "postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require"
```

### 📊 Daily Operations
```bash
# Manual backup NOW
./daily-backup.sh

# Check backup status
ls -la backups/database/ | tail -5

# Test system health
./test-backup-recovery.sh

# View today's log
tail -f backups/logs/daily-backup-$(date +%Y%m%d).log
```

### 🔧 Common Tasks
```bash
# Database backup only
./backup-db.sh

# Check connection
psql "postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require" -c "SELECT 1;"

# Count suppliers
psql "postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require" -c "SELECT COUNT(*) FROM suppliers;"

# Check Azure backup status
az postgres server show --resource-group foodxchange-rg --name fdx-postgres-server --query "earliestRestoreDate"
```

## 📁 Important Locations
```
backups/
├── database/        # SQL backups (.sql.gz files)
├── infrastructure/  # Azure configs
└── logs/           # Backup logs

docs/backup-recovery/  # This documentation
```

## 🔄 Recovery Times
- **Point-in-time (Azure)**: 15-30 min
- **Local backup restore**: 30-60 min  
- **Full rebuild**: 2-4 hours

## ⚠️ Before Any Recovery
1. **STOP** - Don't panic
2. **ASSESS** - What's broken?
3. **BACKUP** - Save current state if possible
4. **COMMUNICATE** - Inform stakeholders
5. **EXECUTE** - Follow recovery procedure
6. **VERIFY** - Test everything works
7. **DOCUMENT** - What happened?

## 🔐 Connection Info
```bash
Server: fdx-postgres-server.postgres.database.azure.com
Database: foodxchange
Username: fdxadmin
Port: 5432
SSL: Required
```

## 📱 Windows Quick Start
```batch
# Run backup now (Windows)
run-backup-now.bat

# Setup automation (Run as Admin)
backup-setup.bat
```

## 🆘 If Nothing Works
1. Check `.env` file exists and has correct values
2. Verify internet connection
3. Check firewall allows your IP
4. Try Azure portal recovery
5. Contact Azure support: 1-800-642-7676

---
**Remember**: A calm mind solves problems faster. You have backups!