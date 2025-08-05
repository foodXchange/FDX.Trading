# FoodXchange Complete Backup & Recovery Documentation

> **Version**: 1.0  
> **Last Updated**: August 2025  
> **System**: Azure PostgreSQL + GitHub + Local Backups  

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Setup Instructions](#setup-instructions)
4. [Backup Strategies](#backup-strategies)
5. [Recovery Procedures](#recovery-procedures)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Cost Analysis](#cost-analysis)
8. [Security Considerations](#security-considerations)
9. [Troubleshooting](#troubleshooting)
10. [Appendix](#appendix)

---

## Overview

The FoodXchange backup system provides comprehensive data protection through a multi-layered approach combining Azure's built-in features, automated local backups, and version control through GitHub.

### Key Features
- **Zero Data Loss**: Point-in-time recovery up to 14 days
- **Automated Backups**: Daily at 2 AM, Weekly on Sundays
- **Geographic Redundancy**: Azure geo-redundant storage
- **Quick Recovery**: 15 minutes to 4 hours depending on scenario
- **Cost Effective**: ~$5-15/month total cost

### What's Protected
- PostgreSQL database (18,000+ suppliers, all transactions)
- Application source code and configurations
- Infrastructure settings and firewall rules
- Environment variables and secrets (securely)

---

## Architecture

### Backup Layers

```
┌─────────────────────────────────────────────────────────┐
│                   BACKUP ARCHITECTURE                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Layer 1: Azure Automated Backups                       │
│  ├─ Continuous (every 5 minutes transaction logs)      │
│  ├─ Daily full backups (automatic)                     │
│  ├─ 14-day retention                                   │
│  └─ Geo-redundant storage                              │
│                                                         │
│  Layer 2: Local Database Dumps                          │
│  ├─ Daily compressed backups (2 AM)                    │
│  ├─ Weekly full exports (Sundays 3 AM)                 │
│  ├─ 10 backup rotation                                 │
│  └─ Optional Azure Blob upload                         │
│                                                         │
│  Layer 3: Code Version Control                          │
│  ├─ Git commits (daily)                                │
│  ├─ GitHub remote repository                           │
│  ├─ Weekly tagged releases                             │
│  └─ Infrastructure as code                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
PostgreSQL Database
    ├── Azure Automated Backup (Continuous)
    │   └── Point-in-Time Recovery
    │
    ├── Local pg_dump (Daily)
    │   ├── Compressed Storage
    │   └── Azure Blob (Optional)
    │
    └── Application Code
        ├── Git Repository
        └── GitHub Remote
```

---

## Setup Instructions

### Prerequisites

1. **Software Requirements**:
   - Git Bash (Windows) or Bash (Linux/Mac)
   - PostgreSQL client tools (`pg_dump`, `psql`)
   - Azure CLI (optional but recommended)
   - Git

2. **Access Requirements**:
   - Azure PostgreSQL connection credentials
   - GitHub account and repository
   - Azure subscription (for infrastructure management)

### Initial Setup

#### Step 1: Clone/Download Scripts
```bash
# If starting fresh
git clone https://github.com/yourusername/foodxchange.git
cd foodxchange

# If scripts are already in place
cd /path/to/foodxchange
```

#### Step 2: Configure Environment
```bash
# Copy template and edit with your values
cp .env.template .env
nano .env  # or use your preferred editor

# Required values:
# DATABASE_URL=postgresql://fdxadmin:PASSWORD@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require
```

#### Step 3: Make Scripts Executable
```bash
# Linux/Mac
chmod +x *.sh

# Windows - scripts should work with Git Bash
```

#### Step 4: Set Up Automation

**Windows:**
```batch
# Run as Administrator
backup-setup.bat
```

**Linux/Mac:**
```bash
# Edit crontab
crontab -e

# Add these lines:
0 2 * * * /path/to/foodxchange/daily-backup.sh >> /var/log/foodxchange-backup.log 2>&1
0 3 * * 0 /path/to/foodxchange/weekly-backup.sh >> /var/log/foodxchange-backup.log 2>&1
```

#### Step 5: Initialize Git Repository
```bash
git init
git remote add origin https://github.com/yourusername/foodxchange.git
git add .
git commit -m "Initial backup setup"
git push -u origin main
```

#### Step 6: Test the System
```bash
# Run test script
./test-backup-recovery.sh

# Manually test backup
./backup-db.sh
```

---

## Backup Strategies

### Daily Backup (Automated at 2 AM)

**What happens:**
1. Creates compressed PostgreSQL dump
2. Rotates old backups (keeps last 10)
3. Commits code changes to Git
4. Pushes to GitHub
5. Verifies Azure backup status
6. Logs all operations

**Script:** `daily-backup.sh`

**Manual execution:**
```bash
./daily-backup.sh
```

### Weekly Backup (Sundays at 3 AM)

**What happens:**
1. Runs full daily backup
2. Creates Git release tag
3. Exports infrastructure configuration
4. Creates schema-only backup
5. Generates recovery documentation
6. Cleans old files

**Script:** `weekly-backup.sh`

**Manual execution:**
```bash
./weekly-backup.sh
```

### On-Demand Backup

**Windows:**
```batch
run-backup-now.bat
```

**Linux/Mac:**
```bash
# Full backup
./daily-backup.sh

# Database only
./backup-db.sh
```

---

## Recovery Procedures

### Scenario 1: Recent Data Corruption (Last 14 Days)

**Use Azure Point-in-Time Recovery:**

```bash
# Interactive recovery
./disaster-recovery.sh
# Select option 1

# Or manually:
az postgres server restore \
  --resource-group foodxchange-rg \
  --name fdx-postgres-server-restored \
  --restore-point-in-time "2025-08-04T10:00:00Z" \
  --source-server fdx-postgres-server
```

**Time to recover:** 15-30 minutes

### Scenario 2: Database Corruption (Older than 14 Days)

**Use Local Backup:**

```bash
# Interactive recovery
./disaster-recovery.sh
# Select option 2

# Or manually:
# Find backup
ls -la ./backups/database/

# Restore
gunzip -c ./backups/database/backup_20250801_020000.sql.gz | \
  psql "postgresql://fdxadmin:PASSWORD@server.postgres.database.azure.com:5432/foodxchange?sslmode=require"
```

**Time to recover:** 30-60 minutes

### Scenario 3: Complete Infrastructure Loss

**Full System Rebuild:**

```bash
# Interactive recovery
./disaster-recovery.sh
# Select option 3

# Or step by step:
# 1. Recreate infrastructure
./recreate-infrastructure.sh

# 2. Restore latest database
gunzip -c ./backups/database/backup_LATEST.sql.gz | \
  psql "postgresql://fdxadmin:PASSWORD@NEW-server.postgres.database.azure.com:5432/foodxchange?sslmode=require"

# 3. Deploy application
git clone https://github.com/yourusername/foodxchange.git
cd foodxchange
# Deploy using your standard process
```

**Time to recover:** 2-4 hours

### Scenario 4: Code Recovery

```bash
# Restore to specific date
git checkout weekly-2025-08-04

# Or restore to last known good commit
git log --oneline
git checkout <commit-hash>
```

**Time to recover:** 5-10 minutes

---

## Monitoring & Maintenance

### Daily Monitoring

**Automated checks:**
- Backup completion status (check logs)
- Email notifications (if configured)
- Azure portal alerts

**Log locations:**
```
./backups/logs/daily-backup-YYYYMMDD.log
./backups/logs/weekly-backup-YYYYMMDD.log
```

### Monthly Tasks

1. **Run Health Check:**
```bash
./test-backup-recovery.sh
```

2. **Verify Backup Integrity:**
```bash
# Test restore to temporary database
pg_restore --list ./backups/database/backup_latest.sql.gz
```

3. **Check Storage Usage:**
```bash
# Local storage
du -sh ./backups/*

# Azure storage
az storage blob list --container-name backups --query "[].{name:name, size:properties.contentLength}"
```

4. **Clean Old Logs:**
```bash
# Remove logs older than 30 days
find ./backups/logs -name "*.log" -mtime +30 -delete
```

### Quarterly Tasks

1. **Full Disaster Recovery Drill:**
   - Create test environment
   - Perform complete restore
   - Verify application functionality
   - Document any issues

2. **Review and Update:**
   - Update scripts if needed
   - Review Azure costs
   - Update documentation
   - Rotate credentials

3. **Capacity Planning:**
   - Check backup growth rate
   - Plan storage expansion
   - Review retention policies

---

## Cost Analysis

### Monthly Costs Breakdown

| Service | Usage | Cost |
|---------|-------|------|
| Azure PostgreSQL Backup | Included | $0 |
| Azure Blob Storage | 100GB backups | ~$2 |
| GitHub | Private repo | $0 |
| Azure Storage transactions | ~10,000/month | ~$1 |
| **Total** | | **~$3-5/month** |

### Cost Optimization Tips

1. **Adjust Retention:**
   - Reduce local backups from 10 to 7
   - Archive monthly backups to cold storage

2. **Compress More:**
   - Use maximum compression for archives
   - Delete test/temporary files

3. **Monitor Usage:**
   ```bash
   # Check Azure costs
   az consumption usage list --start-date 2025-08-01 --end-date 2025-08-31
   ```

---

## Security Considerations

### Best Practices

1. **Credential Management:**
   - Never commit passwords to Git
   - Use Azure Key Vault for production
   - Rotate passwords quarterly
   - Use strong, unique passwords

2. **Access Control:**
   - Limit PostgreSQL firewall rules
   - Use SSL for all connections
   - Enable Azure AD authentication
   - Audit access logs

3. **Encryption:**
   - Database: SSL/TLS in transit
   - Backups: Encrypted at rest (Azure)
   - Local: Consider GPG encryption

4. **Secure Script Handling:**
```bash
# Secure permissions
chmod 700 *.sh
chmod 600 .env

# Encrypt sensitive backups
gpg --symmetric --cipher-algo AES256 backup.sql
```

### Security Checklist

- [ ] SSL enabled for database connections
- [ ] Firewall rules restricted to necessary IPs
- [ ] Passwords stored securely (not in scripts)
- [ ] Git repository is private
- [ ] Backup files have restricted permissions
- [ ] Regular security updates applied
- [ ] Access logs reviewed monthly

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Backup Fails with Connection Error

**Symptoms:**
```
psql: error: could not connect to server
```

**Solutions:**
```bash
# Check connection
psql "postgresql://fdxadmin:PASSWORD@server.postgres.database.azure.com:5432/foodxchange?sslmode=require"

# Verify firewall
az postgres server firewall-rule list --resource-group foodxchange-rg --server fdx-postgres-server

# Add your IP
MY_IP=$(curl -s https://api.ipify.org)
az postgres server firewall-rule create \
  --resource-group foodxchange-rg \
  --server fdx-postgres-server \
  --name MyIP \
  --start-ip-address $MY_IP \
  --end-ip-address $MY_IP
```

#### 2. Git Push Fails

**Symptoms:**
```
error: failed to push some refs
```

**Solutions:**
```bash
# Check remote
git remote -v

# Pull first
git pull origin main

# Force push (careful!)
git push -f origin main

# Check authentication
git config --global user.email
git config --global user.name
```

#### 3. Disk Space Issues

**Symptoms:**
```
No space left on device
```

**Solutions:**
```bash
# Check space
df -h

# Clean old backups
ls -la ./backups/database/ | head -20  # Check old files
rm ./backups/database/backup_OLD*.sql.gz  # Remove old

# Compress uncompressed files
gzip ./backups/database/*.sql
```

#### 4. Azure CLI Not Working

**Symptoms:**
```
az: command not found
```

**Solutions:**
```bash
# Install Azure CLI
# Windows: Download from https://aka.ms/installazurecliwindows
# Mac: brew install azure-cli
# Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Set subscription
az account set --subscription "Your Subscription Name"
```

#### 5. Restore Fails

**Symptoms:**
```
ERROR: database "foodxchange" already exists
```

**Solutions:**
```bash
# Drop and recreate
psql "connection-string" -c "DROP DATABASE IF EXISTS foodxchange;"
psql "connection-string" -c "CREATE DATABASE foodxchange;"

# Or restore to different database
psql "connection-string" -c "CREATE DATABASE foodxchange_restore;"
# Then restore to foodxchange_restore
```

---

## Appendix

### A. Script Reference

| Script | Purpose | Schedule |
|--------|---------|----------|
| `backup-db.sh` | Database backup only | Manual/Daily |
| `daily-backup.sh` | Complete daily routine | 2:00 AM |
| `weekly-backup.sh` | Deep backup with extras | Sundays 3:00 AM |
| `disaster-recovery.sh` | Interactive recovery | As needed |
| `test-backup-recovery.sh` | System health check | Monthly |
| `recreate-infrastructure.sh` | Rebuild Azure resources | Emergency |

### B. Important Paths

```
/FoodXchange/
├── backups/
│   ├── database/          # PostgreSQL dumps
│   ├── infrastructure/    # Azure configs
│   └── logs/             # Operation logs
├── docs/
│   └── backup-recovery/  # Documentation
├── *.sh                  # Backup scripts
└── .env                  # Configuration
```

### C. Connection Strings

**PostgreSQL:**
```
postgresql://fdxadmin:PASSWORD@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require
```

**Azure Resource Group:**
```
foodxchange-rg
```

### D. Useful Commands

```bash
# Check backup size
du -sh backups/*

# Find large files
find . -type f -size +100M

# Check last backup
ls -la backups/database/ | tail -5

# View backup log
tail -f backups/logs/daily-backup-$(date +%Y%m%d).log

# Test database connection
pg_isready -h fdx-postgres-server.postgres.database.azure.com -p 5432

# Count records
psql "connection-string" -c "SELECT COUNT(*) FROM suppliers;"
```

### E. Emergency Contacts

- Azure Support: 1-800-642-7676
- GitHub Status: https://www.githubstatus.com
- PostgreSQL Docs: https://www.postgresql.org/docs/

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Aug 2025 | Initial documentation | System |

---

*This document is part of the FoodXchange Backup & Recovery System. Keep it updated and accessible.*