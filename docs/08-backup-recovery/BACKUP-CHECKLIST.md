# FoodXchange Backup System Checklists

## ✅ Daily Checklist (Automated at 2 AM)
- [ ] Database backup created (`backup_YYYYMMDD_*.sql.gz`)
- [ ] Backup compressed successfully
- [ ] Old backups rotated (keeping last 10)
- [ ] Git changes committed
- [ ] Code pushed to GitHub
- [ ] Azure backup status verified
- [ ] Log file created in `backups/logs/`

## 📅 Weekly Checklist (Sundays at 3 AM)
- [ ] All daily backup tasks completed
- [ ] Weekly Git tag created (`weekly-YYYY-MM-DD`)
- [ ] Infrastructure configuration exported
- [ ] Database schema backup created
- [ ] Recovery documentation updated
- [ ] Old logs cleaned (>30 days)
- [ ] Backup report generated

## 🔍 Monthly Maintenance Checklist

### Week 1 - System Health
- [ ] Run `./test-backup-recovery.sh`
- [ ] Review all backup logs from past month
- [ ] Check backup file sizes for anomalies
- [ ] Verify Azure backup retention settings
- [ ] Test database connection manually

### Week 2 - Recovery Testing  
- [ ] Perform test restore to temporary database
- [ ] Verify data integrity after restore
- [ ] Test point-in-time recovery in Azure
- [ ] Document any issues found
- [ ] Update recovery time estimates

### Week 3 - Storage & Costs
- [ ] Check local storage usage
- [ ] Review Azure storage costs
- [ ] Clean unnecessary files
- [ ] Archive old backups if needed
- [ ] Verify compression is working

### Week 4 - Documentation & Security
- [ ] Update documentation if needed
- [ ] Review access permissions
- [ ] Check for security updates
- [ ] Rotate passwords if scheduled
- [ ] Update emergency contacts

## 🎯 Quarterly Review Checklist

### Q1 - Disaster Recovery Drill
- [ ] Schedule maintenance window
- [ ] Create test environment
- [ ] Execute full recovery scenario
- [ ] Time each recovery step
- [ ] Test application functionality
- [ ] Document lessons learned
- [ ] Update procedures based on findings

### Q2 - Infrastructure Review
- [ ] Review Azure resource configuration
- [ ] Check for available updates
- [ ] Optimize resource sizing
- [ ] Review firewall rules
- [ ] Update infrastructure scripts
- [ ] Test infrastructure recreation

### Q3 - Security Audit
- [ ] Rotate all passwords
- [ ] Review access logs
- [ ] Update SSL certificates
- [ ] Check for vulnerabilities
- [ ] Review backup encryption
- [ ] Update security documentation

### Q4 - Annual Planning
- [ ] Review yearly costs
- [ ] Plan next year's budget
- [ ] Evaluate backup strategy
- [ ] Plan system upgrades
- [ ] Update contact information
- [ ] Schedule next year's reviews

## 🚀 New Setup Checklist

### Initial Configuration
- [ ] `.env` file created with correct values
- [ ] All scripts made executable (`chmod +x *.sh`)
- [ ] Backup directories created
- [ ] Git repository initialized
- [ ] GitHub remote configured

### Testing
- [ ] Run `./test-backup-recovery.sh`
- [ ] Create manual backup with `./backup-db.sh`
- [ ] Verify backup file created and compressed
- [ ] Test restore to temporary database
- [ ] Verify Git commits working

### Automation Setup
- [ ] Windows: Run `backup-setup.bat` as Administrator
- [ ] Linux/Mac: Configure crontab entries
- [ ] Verify scheduled tasks created
- [ ] Test automation runs successfully
- [ ] Check log files being created

### Documentation
- [ ] Read all documentation files
- [ ] Update contact information
- [ ] Note any custom configurations
- [ ] Share docs with team members
- [ ] Create local notes for specifics

## 🔧 Pre-Recovery Checklist

### Before Starting Recovery
- [ ] Document current issue clearly
- [ ] Notify stakeholders
- [ ] Stop application if needed
- [ ] Create current backup if possible
- [ ] Identify recovery scenario
- [ ] Gather necessary credentials
- [ ] Open recovery documentation

### During Recovery
- [ ] Follow specific scenario steps
- [ ] Document each action taken
- [ ] Test at each major step
- [ ] Keep stakeholders updated
- [ ] Monitor progress closely
- [ ] Have rollback plan ready

### After Recovery
- [ ] Verify all data recovered
- [ ] Test application thoroughly
- [ ] Check all integrations
- [ ] Monitor for issues
- [ ] Document incident fully
- [ ] Schedule review meeting
- [ ] Update procedures

## 📱 Quick Status Checks

### Is My Backup Working?
```bash
# Check last backup
ls -la backups/database/ | tail -1

# Check today's log
tail backups/logs/daily-backup-$(date +%Y%m%d).log

# Count backup files
ls -1 backups/database/*.gz | wc -l
```

### Is My Database Healthy?
```bash
# Test connection
psql "postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require" -c "SELECT version();"

# Check record count
psql "connection-string" -c "SELECT COUNT(*) FROM suppliers;"

# Check latest activity
psql "connection-string" -c "SELECT MAX(created_at) FROM suppliers;"
```

### Is Azure Backup Working?
```bash
# Check backup configuration
az postgres server show --resource-group foodxchange-rg --name fdx-postgres-server --query "storageProfile"

# Check earliest restore point
az postgres server show --resource-group foodxchange-rg --name fdx-postgres-server --query "earliestRestoreDate"
```

## 📋 Backup Verification Matrix

| Component | Daily | Weekly | Monthly | Quarterly |
|-----------|-------|--------|---------|-----------|
| Database Dump | ✅ | ✅ | Test Restore | Full DR Drill |
| Git Backup | ✅ | Tag | Review | Archive |
| Azure Backup | Check | Verify | Test | Validate |
| Logs | Create | Rotate | Review | Archive |
| Infrastructure | - | Export | Verify | Update |

---

**Pro Tip**: Print these checklists and keep physical copies in multiple locations. During a crisis, paper doesn't need passwords or internet!