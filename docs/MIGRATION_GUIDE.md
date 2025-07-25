# Database Migration Guide

## Overview

FoodXchange uses Alembic for database migrations. This guide covers:
- Setting up migrations locally
- Creating new migrations
- Deploying migrations to production
- Troubleshooting common issues

## Initial Setup

### 1. Install Dependencies
```bash
pip install alembic sqlalchemy psycopg2-binary
```

### 2. Environment Configuration
Set your database URL:
```bash
# For development (SQLite)
export DATABASE_URL=sqlite:///./foodxchange.db

# For production (Azure PostgreSQL)
export DATABASE_URL=postgresql://foodxchange_app:PASSWORD@foodxchangepgfr.postgres.database.azure.com:5432/foodxchange_db?sslmode=require
```

### 3. Initialize Migrations (Already Done)
```bash
alembic init migrations
```

## Working with Migrations

### Check Current Database State
```bash
python migrate.py current
```

### Create a New Migration
After modifying models:
```bash
python migrate.py create "Add new field to supplier model"
# or directly with alembic:
alembic revision --autogenerate -m "Add new field to supplier model"
```

### Apply Migrations
```bash
# Apply all pending migrations
python migrate.py upgrade

# Apply to specific revision
python migrate.py upgrade abc123

# Using alembic directly
alembic upgrade head
```

### Rollback Migrations
```bash
# Rollback one migration
python migrate.py downgrade

# Rollback to specific revision
python migrate.py downgrade abc123

# Using alembic directly
alembic downgrade -1
```

### View Migration History
```bash
python migrate.py history
# or
alembic history
```

## Production Deployment

### Method 1: Automatic with azure_startup_with_migrations.py
1. Update your App Service startup command:
   ```
   python azure_startup_with_migrations.py
   ```

2. This script will:
   - Run pending migrations
   - Initialize database if needed
   - Start the FastAPI application

### Method 2: Manual Migration
1. Connect to Azure App Service SSH:
   ```bash
   az webapp ssh --name your-app-name --resource-group foodxchange-rg
   ```

2. Run migrations:
   ```bash
   cd /home/site/wwwroot
   alembic upgrade head
   ```

### Method 3: GitHub Actions
The workflow automatically runs migrations after deployment:
```yaml
- name: Run migrations on Azure
  run: |
    az webapp ssh --name ${{ env.AZURE_WEBAPP_NAME }} \
      --command "cd /home/site/wwwroot && python migrate.py upgrade"
```

## Best Practices

### 1. Always Review Generated Migrations
```bash
# After creating a migration, review it:
cat migrations/versions/latest_migration.py
```

### 2. Test Migrations Locally First
```bash
# Use a test database
export DATABASE_URL=postgresql://test_user:pass@localhost/test_db
python migrate.py upgrade
```

### 3. Backup Before Production Migrations
```bash
# Backup Azure PostgreSQL
az postgres flexible-server backup create \
  --resource-group foodxchange-rg \
  --server-name foodxchangepgfr \
  --backup-name pre-migration-backup
```

### 4. Handle Migration Failures
If a migration fails:
1. Check the error message
2. Fix the issue in the migration script
3. If partially applied, manually clean up
4. Re-run the migration

## Common Issues and Solutions

### Issue: "Can't locate revision identifier"
**Solution**: Database is out of sync. Check current revision:
```bash
alembic current
alembic stamp head  # Mark as up-to-date
```

### Issue: "Target database is not up to date"
**Solution**: Run pending migrations:
```bash
alembic upgrade head
```

### Issue: "Multiple head revisions"
**Solution**: Merge branches:
```bash
alembic merge -m "Merge heads"
```

### Issue: Connection Timeout to Azure
**Solution**: 
1. Check firewall rules in Azure Portal
2. Verify connection string format
3. Ensure SSL is enabled with `?sslmode=require`

## Migration Workflow

### Development Cycle
1. Modify models in `app/models/`
2. Generate migration: `python migrate.py create "Description"`
3. Review generated migration
4. Test locally: `python migrate.py upgrade`
5. Commit migration files to Git

### Deployment Cycle
1. Push to main branch
2. GitHub Actions runs deployment
3. Migrations apply automatically
4. Verify in Azure Portal

## Emergency Procedures

### Rollback Failed Migration
```bash
# Connect to Azure
az webapp ssh --name your-app-name --resource-group foodxchange-rg

# Rollback
alembic downgrade -1

# Or restore from backup
az postgres flexible-server restore \
  --resource-group foodxchange-rg \
  --server-name foodxchangepgfr \
  --restore-time "2024-06-15T13:00:00Z"
```

### Reset Migration History (Development Only!)
```bash
# WARNING: This will delete all data!
alembic downgrade base
alembic upgrade head
```

## Monitoring

### Check Migration Status in Production
Add this endpoint to your app:
```python
@app.get("/api/migration-status")
async def migration_status():
    from alembic import command
    from alembic.config import Config
    
    alembic_cfg = Config("alembic.ini")
    # Return current revision
    return {"status": "check logs"}
```

### View Logs
```bash
az webapp log tail --name your-app-name --resource-group foodxchange-rg
```

## Further Reading

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Migration Patterns](https://docs.sqlalchemy.org/en/14/core/migration.html)
- [Azure PostgreSQL Best Practices](https://docs.microsoft.com/en-us/azure/postgresql/)