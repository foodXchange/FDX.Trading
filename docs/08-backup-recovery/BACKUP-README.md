# FoodXchange Backup & Recovery Guide

## 🚀 Quick Start

### 1. Initial Setup (One-time)
```bash
# Windows users:
./backup-setup.bat  # Run as Administrator

# Linux/Mac users:
chmod +x *.sh
crontab -e
# Add these lines:
0 2 * * * /path/to/daily-backup.sh >> /var/log/foodxchange-backup.log 2>&1
0 3 * * 0 /path/to/weekly-backup.sh >> /var/log/foodxchange-backup.log 2>&1
```

### 2. Manual Backup (Anytime)
```bash
# Windows:
run-backup-now.bat

# Linux/Mac:
./daily-backup.sh
```

### 3. Test Your Backups (Monthly)
```bash
./test-backup-recovery.sh
```

## 📁 Backup Locations

- **Database backups**: `./backups/database/`
- **Infrastructure configs**: `./backups/infrastructure/`
- **Logs**: `./backups/logs/`
- **Azure backups**: Automatic (14-day retention)
- **GitHub**: Your repository (code + configs)

## 🆘 Emergency Recovery

### Database Corruption
```bash
# Option 1: Azure point-in-time (last 14 days)
./disaster-recovery.sh  # Choose option 1

# Option 2: Local backup file
./disaster-recovery.sh  # Choose option 2
```

### Complete System Loss
```bash
# Rebuild everything from scratch
./disaster-recovery.sh  # Choose option 3
```

## 📊 What Gets Backed Up

### Daily (Automatic at 2 AM)
- ✅ PostgreSQL database (compressed)
- ✅ Code changes (Git commit & push)
- ✅ Azure backup verification

### Weekly (Sundays at 3 AM)
- ✅ Everything from daily backup
- ✅ Infrastructure configuration export
- ✅ Git release tag
- ✅ Database schema dump
- ✅ Environment template

### Azure (Continuous)
- ✅ Automatic daily backups
- ✅ Point-in-time recovery (14 days)
- ✅ Geographic redundancy

## 🔧 Key Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `backup-db.sh` | Database backup only | Testing or manual backup |
| `daily-backup.sh` | Full daily backup routine | Automated daily (2 AM) |
| `weekly-backup.sh` | Deep backup with configs | Automated weekly (Sundays) |
| `disaster-recovery.sh` | System recovery | When disaster strikes |
| `test-backup-recovery.sh` | Health check | Monthly verification |
| `recreate-infrastructure.sh` | Rebuild Azure resources | Complete system loss |

## 💰 Cost Breakdown

- **Azure PostgreSQL backups**: Free (included)
- **Azure Blob Storage**: ~$2/month (100GB)
- **GitHub**: Free (private repos)
- **Total**: ~$2-5/month

## ⚡ Recovery Times

- **Minor issue**: 5-10 minutes (recent backup)
- **Database restore**: 15-30 minutes (Azure)
- **Complete rebuild**: 2-4 hours (full infrastructure)

## 🔐 Security Notes

1. **Never commit secrets** to Git
2. **Store passwords** in Azure Key Vault
3. **Use SSL** for all connections
4. **Test recovery** monthly
5. **Keep `.env` file** backed up securely

## 📞 Troubleshooting

### Backup Failed
1. Check database connection: `./test-backup-recovery.sh`
2. Verify credentials in `.env`
3. Check disk space
4. Review logs in `./backups/logs/`

### Can't Connect to Database
1. Check firewall rules
2. Verify SSL is enabled
3. Test with: `psql "postgresql://fdxadmin:PASSWORD@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require"`

### Git Push Failed
1. Check authentication: `git remote -v`
2. Verify network connection
3. Try manual push: `git push origin main`

## 📅 Maintenance Checklist

### Daily
- ✅ Automated backup runs at 2 AM
- ✅ Check for any error emails/alerts

### Weekly
- ✅ Automated deep backup on Sundays
- ✅ Review backup sizes and counts

### Monthly
- ✅ Run `./test-backup-recovery.sh`
- ✅ Test restore procedure
- ✅ Update documentation if needed
- ✅ Clean old logs: `find ./backups/logs -mtime +30 -delete`

### Quarterly
- ✅ Full disaster recovery drill
- ✅ Review and update scripts
- ✅ Check Azure costs
- ✅ Update credentials if needed

---

Remember: **A backup is only as good as your last successful restore!** Test regularly.