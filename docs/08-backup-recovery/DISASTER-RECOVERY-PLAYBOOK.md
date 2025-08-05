# FoodXchange Disaster Recovery Playbook

> **Critical Document** - Keep accessible at all times  
> **Last Updated**: August 2025  
> **Recovery Hotline**: Azure Support 1-800-642-7676  

---

## 🚨 EMERGENCY RESPONSE FLOWCHART

```
SYSTEM DOWN?
    │
    ├─→ Can access database? ──YES──→ [Go to: Data Corruption Recovery]
    │                          
    └─→ NO
        │
        ├─→ Can access Azure? ──YES──→ [Go to: Azure Recovery]
        │
        └─→ NO ─→ [Go to: Complete Rebuild]
```

---

## 📋 INITIAL ASSESSMENT (5 minutes)

### 1. System Status Check
```bash
# Test database connection
psql "postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require" -c "SELECT 1;"

# Check Azure portal
# https://portal.azure.com > foodxchange-rg

# Test application
curl http://localhost:9000/health
```

### 2. Document the Issue
- **Time discovered**: ________________
- **Symptoms**: ______________________
- **Last known good state**: __________
- **Recent changes**: _________________

---

## 🔄 RECOVERY SCENARIOS

### SCENARIO A: Data Corruption (Database Accessible)

**Symptoms**: Wrong data, missing records, but can connect

**Recovery Time**: 15-30 minutes

**Steps**:
1. **Stop all write operations**
   ```bash
   # Notify users / Stop application
   ```

2. **Identify corruption time**
   ```bash
   # Check when issue started
   psql "connection-string" -c "SELECT * FROM suppliers ORDER BY updated_at DESC LIMIT 10;"
   ```

3. **Use Azure Point-in-Time Recovery**
   ```bash
   # Restore to 1 hour before corruption
   RESTORE_TIME="2025-08-04T09:00:00Z"  # Adjust this!
   
   az postgres server restore \
     --resource-group foodxchange-rg \
     --name fdx-postgres-server-recovery \
     --restore-point-in-time "$RESTORE_TIME" \
     --source-server fdx-postgres-server
   ```

4. **Verify recovered data**
   ```bash
   # Connect to new server
   psql "postgresql://fdxadmin:FDX2030!@fdx-postgres-server-recovery.postgres.database.azure.com:5432/foodxchange?sslmode=require"
   
   # Check data
   SELECT COUNT(*) FROM suppliers;
   ```

5. **Switch application to recovered database**
   - Update `.env` with new server name
   - Restart application
   - Test functionality

6. **Clean up**
   - Delete corrupted server (after confirming recovery)
   - Rename recovered server to original name

---

### SCENARIO B: Database Inaccessible (Azure Portal Works)

**Symptoms**: Can't connect to database, Azure portal accessible

**Recovery Time**: 30-60 minutes

**Steps**:
1. **Check Azure service health**
   ```bash
   # Check Azure status
   az postgres server show --resource-group foodxchange-rg --name fdx-postgres-server
   ```

2. **Try Azure portal recovery**
   - Login to https://portal.azure.com
   - Navigate to: foodxchange-rg > fdx-postgres-server
   - Click "Restore" > Select time > Create

3. **If Azure recovery fails, use local backup**
   ```bash
   # Find latest backup
   LATEST_BACKUP=$(ls -t backups/database/backup_*.gz | head -1)
   echo "Using backup: $LATEST_BACKUP"
   
   # Create new database server (if needed)
   ./recreate-infrastructure.sh
   
   # Restore backup
   gunzip -c $LATEST_BACKUP | psql "postgresql://fdxadmin:FDX2030!@NEW-SERVER.postgres.database.azure.com:5432/foodxchange?sslmode=require"
   ```

4. **Update application configuration**
   ```bash
   # Update .env
   sed -i 's/fdx-postgres-server/NEW-SERVER/g' .env
   
   # Restart application
   ```

---

### SCENARIO C: Complete Azure Failure

**Symptoms**: No Azure access, need complete rebuild

**Recovery Time**: 2-4 hours

**Steps**:
1. **Gather resources**
   - Latest local backup: `backups/database/`
   - Infrastructure config: `backups/infrastructure/`
   - Application code: Git repository

2. **Recreate infrastructure**
   ```bash
   # Run infrastructure script
   ./recreate-infrastructure.sh
   
   # This creates:
   # - Resource group
   # - PostgreSQL server
   # - Firewall rules
   # - Storage account
   ```

3. **Restore database**
   ```bash
   # Wait for server to be ready (5-10 min)
   sleep 300
   
   # Find latest backup
   BACKUP=$(ls -t backups/database/backup_*.gz | head -1)
   
   # Restore
   gunzip -c $BACKUP | psql "postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require"
   ```

4. **Deploy application**
   ```bash
   # Get latest code
   git pull origin main
   
   # Or clone fresh
   git clone https://github.com/yourusername/foodxchange.git
   cd foodxchange
   
   # Configure environment
   cp .env.template .env
   # Edit .env with new values
   
   # Start application
   python app.py  # Or your deployment method
   ```

5. **Verify system**
   - Test database queries
   - Check all endpoints
   - Verify data integrity

---

### SCENARIO D: Ransomware/Security Breach

**Symptoms**: Encrypted files, suspicious activity

**Recovery Time**: 4-8 hours

**IMMEDIATE ACTIONS**:
1. **ISOLATE** - Disconnect from network
2. **DOCUMENT** - Screenshot everything
3. **DON'T PAY** - Contact authorities
4. **CLEAN REBUILD** - Use backups

**Steps**:
1. **Use isolated, clean machine**
2. **Create new Azure subscription if compromised**
3. **Build fresh infrastructure**
   ```bash
   # New resource group
   az group create --name foodxchange-clean-rg --location eastus
   
   # Run infrastructure script with new names
   ./recreate-infrastructure.sh
   ```
4. **Restore from oldest clean backup**
5. **Reset ALL passwords**
6. **Enable additional security**
   - MFA on all accounts
   - Azure AD authentication
   - Network isolation

---

## 📞 COMMUNICATION TEMPLATES

### Initial Notification
```
Subject: FoodXchange System Issue - Investigation Underway

We are currently experiencing [issue type] with the FoodXchange system.

Status: Investigating
Started: [time]
Impact: [description]
Updates: Every 30 minutes

We apologize for any inconvenience.
```

### Update Template
```
Subject: FoodXchange System Update - [timestamp]

Current Status: [Recovering/Restored/Testing]
Progress: [specific actions taken]
ETA: [estimated time]
Next Update: [time]

Thank you for your patience.
```

### Resolution Notice
```
Subject: FoodXchange System Restored

The FoodXchange system has been fully restored.

Issue Duration: [start] to [end]
Root Cause: [brief description]
Data Loss: None/Minimal [specify]
Prevention: [measures taken]

System is now fully operational.
```

---

## 🛠️ POST-RECOVERY CHECKLIST

### Immediate (First Hour)
- [ ] System fully operational
- [ ] All data recovered
- [ ] Users can login
- [ ] Basic functions work
- [ ] Monitoring enabled

### Short Term (First Day)
- [ ] Document incident fully
- [ ] Review what went wrong
- [ ] Check all backups worked
- [ ] Update recovery procedures
- [ ] Communicate with stakeholders

### Long Term (First Week)
- [ ] Root cause analysis
- [ ] Implement preventive measures
- [ ] Update documentation
- [ ] Review backup strategy
- [ ] Schedule recovery drill

---

## 🔧 RECOVERY TOOLS REFERENCE

### Essential Commands
```bash
# Test database connection
psql "postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require" -c "SELECT version();"

# Quick backup
./backup-db.sh

# Full recovery menu
./disaster-recovery.sh

# Rebuild infrastructure
./recreate-infrastructure.sh

# Check backup integrity
gunzip -t backups/database/backup_*.gz

# Monitor recovery progress
tail -f backups/logs/recovery-$(date +%Y%m%d).log
```

### Azure CLI Essentials
```bash
# Login to Azure
az login

# List all resources
az resource list --resource-group foodxchange-rg

# Server operations
az postgres server restart --resource-group foodxchange-rg --name fdx-postgres-server
az postgres server show --resource-group foodxchange-rg --name fdx-postgres-server
az postgres server list --resource-group foodxchange-rg

# Firewall management
az postgres server firewall-rule list --resource-group foodxchange-rg --server fdx-postgres-server
```

---

## 📱 EMERGENCY CONTACTS

### Internal
- **System Owner**: [Your Name] - [Phone]
- **Backup Admin**: [Backup Contact] - [Phone]
- **Azure Admin**: [Azure Contact] - [Phone]

### External Support
- **Azure Support**: 1-800-642-7676
- **GitHub Support**: support@github.com
- **PostgreSQL Community**: https://www.postgresql.org/support/

### Status Pages
- Azure Status: https://status.azure.com
- GitHub Status: https://www.githubstatus.com

---

## 🎯 RECOVERY PRIORITIES

1. **SAFETY FIRST** - Secure the system
2. **ASSESS** - Understand the problem
3. **COMMUNICATE** - Keep stakeholders informed
4. **RECOVER** - Follow the appropriate scenario
5. **VERIFY** - Test everything
6. **DOCUMENT** - Record what happened
7. **IMPROVE** - Update procedures

---

## 📝 INCIDENT LOG TEMPLATE

```
INCIDENT #: ________
Date: ______________
Time Started: ______
Time Resolved: _____

DESCRIPTION:
_____________________
_____________________

IMPACT:
_____________________

ACTIONS TAKEN:
1. _________________
2. _________________
3. _________________

ROOT CAUSE:
_____________________

LESSONS LEARNED:
_____________________

FOLLOW-UP REQUIRED:
_____________________
```

---

**Remember**: Stay calm. Follow the procedures. You have good backups. The system will recover.

**This playbook version**: 1.0 | August 2025