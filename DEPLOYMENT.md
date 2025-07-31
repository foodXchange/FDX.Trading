# FoodXchange Deployment Guide

## Overview

This guide provides complete instructions for setting up a controlled deployment system for FoodXchange with manual production deployment control.

## Table of Contents

1. [Architecture](#architecture)
2. [Environment Setup](#environment-setup)
3. [GitHub Configuration](#github-configuration)
4. [Local Development](#local-development)
5. [Staging Deployment](#staging-deployment)
6. [Production Deployment](#production-deployment)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

## Architecture

### Deployment Flow
```
Local Development → GitHub (main) → Staging (auto) → Production (manual)
```

### Environments
- **Development**: Local machine, hot-reload enabled
- **Staging**: Testing environment, auto-deploys from staging branch
- **Production**: Live environment, requires manual approval

## Environment Setup

### 1. Initial Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/foodxchange.git
cd foodxchange

# Create environment files
fx setup env

# Update environment files with your values
notepad .env.development
notepad .env.staging
notepad .env.production
```

### 2. Environment Variables

#### Development (.env.development)
```env
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=postgresql://foodxchange:devpassword@localhost:5432/foodxchange_dev
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-change-in-production
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
```

#### Staging (.env.staging)
```env
ENVIRONMENT=staging
DEBUG=False
DATABASE_URL=postgresql://foodxchange:${DB_PASSWORD_STAGING}@db:5432/foodxchange_staging
REDIS_URL=redis://:${REDIS_PASSWORD_STAGING}@redis:6379/0
SECRET_KEY=${SECRET_KEY_STAGING}
# Azure keys same as production
```

#### Production (.env.production)
```env
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://foodxchange:${DB_PASSWORD_PROD}@db:5432/foodxchange_prod
REDIS_URL=redis://:${REDIS_PASSWORD_PROD}@redis:6379/0
SECRET_KEY=${SECRET_KEY_PROD}
# Use environment variables for all sensitive data
```

## GitHub Configuration

### 1. Create Branches

```bash
# Create staging branch
git checkout -b staging
git push origin staging

# Create production branch
git checkout -b production
git push origin production
```

### 2. Branch Protection Rules

#### Production Branch
1. Go to Settings → Branches
2. Add rule for `production`
3. Enable:
   - Require pull request reviews (2 approvers)
   - Require status checks to pass
   - Require branches to be up to date
   - Include administrators
   - Restrict who can push

#### Staging Branch
1. Add rule for `staging`
2. Enable:
   - Require pull request reviews (1 approver)
   - Require status checks to pass

### 3. GitHub Secrets

Navigate to Settings → Secrets and variables → Actions

#### Repository Secrets
```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
STAGING_SSH_KEY=(your staging server SSH private key)
STAGING_HOST=staging.foodxchange.com
STAGING_USER=deploy
PRODUCTION_SSH_KEY=(your production server SSH private key)
PRODUCTION_HOSTS=prod1.foodxchange.com,prod2.foodxchange.com
PRODUCTION_USER=deploy
SLACK_WEBHOOK=(optional Slack webhook URL)
```

#### Environment Secrets (staging)
```
DB_PASSWORD_STAGING=strong-password-here
REDIS_PASSWORD_STAGING=strong-password-here
SECRET_KEY_STAGING=random-secret-key-here
```

#### Environment Secrets (production)
```
DB_PASSWORD_PROD=very-strong-password-here
REDIS_PASSWORD_PROD=very-strong-password-here
SECRET_KEY_PROD=random-secret-key-here
```

### 4. Variables

Navigate to Settings → Variables → Actions

```
PRODUCTION_APPROVERS=username1,username2
```

## Local Development

### Starting Development Environment

```bash
# Start all services
fx start

# Or explicitly specify dev environment
fx start dev

# View logs
fx logs

# Access services
# - Web app: http://localhost:8003
# - pgAdmin: http://localhost:5050
# - Database: localhost:5432
# - Redis: localhost:6379
```

### Development Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and test
fx test

# Format and lint code
fx format
fx lint

# Commit changes
git add .
git commit -m "feat: add new feature"

# Push to GitHub
git push origin feature/new-feature

# Create PR to main branch
```

## Staging Deployment

### Automatic Deployment

1. Merge PR to main branch
2. Push main to staging:
   ```bash
   git checkout main
   git pull origin main
   git push origin main:staging
   ```
3. GitHub Actions automatically deploys to staging
4. Monitor deployment: https://github.com/YOUR_REPO/actions

### Manual Staging Deployment

```bash
# Deploy current branch to staging
fx deploy staging

# This will push to staging branch and trigger deployment
```

### Testing on Staging

```bash
# Check staging health
curl https://staging.foodxchange.com/health

# View staging logs (on staging server)
ssh deploy@staging.foodxchange.com
cd /opt/foodxchange
docker compose -f docker-compose.staging.yml logs -f
```

## Production Deployment

### Prerequisites

- [ ] All tests passing on staging
- [ ] Staging environment tested thoroughly
- [ ] Database migrations reviewed
- [ ] Team notified about deployment
- [ ] Rollback plan prepared

### Deployment Process

1. **Trigger Deployment**
   ```bash
   # Show deployment instructions
   fx deploy production
   ```

2. **Use GitHub Actions UI**
   - Go to: https://github.com/YOUR_REPO/actions/workflows/deploy-production.yml
   - Click "Run workflow"
   - Enter version (e.g., v1.0.0)
   - Type `DEPLOY` to confirm
   - Click "Run workflow"

3. **Manual Approval**
   - Wait for "Manual Approval Required" step
   - Review deployment details
   - Two approvers must approve
   - Click "Approve and deploy"

4. **Monitor Deployment**
   - Watch GitHub Actions logs
   - Check production health endpoints
   - Verify version deployed correctly

### Emergency Rollback

If something goes wrong:

```bash
# On production server
ssh deploy@prod1.foodxchange.com
cd /opt/foodxchange
sudo ./scripts/rollback.sh

# Or rollback to specific backup
sudo ./scripts/rollback.sh 20240115_143022
```

## Monitoring & Maintenance

### Health Checks

```bash
# Development
fx monitor health

# Staging
curl https://staging.foodxchange.com/health

# Production
curl https://foodxchange.com/health
```

### Logs

```bash
# View logs by environment
fx logs dev
fx logs staging

# Tail logs
fx monitor logs dev
```

### Database Management

```bash
# Backup database
fx db backup dev
fx db backup staging
fx db backup production

# Connect to database
fx db connect dev

# Run migrations
fx db migrate dev
```

### Cleaning Up

```bash
# Clean environment
fx clean dev

# Clean all Docker resources
fx clean dev all
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port
netstat -ano | findstr :8003

# Kill process
taskkill /PID <PID> /F
```

#### 2. Docker Issues
```bash
# Reset Docker
fx clean all
docker system prune -af
docker volume prune -f
```

#### 3. Database Connection Failed
```bash
# Check database container
docker ps
docker logs foodxchange_db_dev

# Restart database
docker restart foodxchange_db_dev
```

#### 4. Deployment Failed
- Check GitHub Actions logs
- Verify all secrets are set correctly
- Check server connectivity
- Review deployment script output

### Getting Help

1. Check logs: `fx logs`
2. Review GitHub Actions output
3. SSH to server and check Docker logs
4. Check `/opt/foodxchange/logs/deployment.log`

## Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Use strong passwords** - Minimum 32 characters for production
3. **Rotate secrets regularly** - Every 90 days
4. **Limit production access** - Only authorized personnel
5. **Enable 2FA** - On GitHub and server accounts
6. **Monitor logs** - Set up alerts for errors
7. **Regular backups** - Automated daily backups
8. **Test rollback process** - Practice emergency procedures

## Maintenance Schedule

### Daily
- Monitor health endpoints
- Check error logs
- Verify backups completed

### Weekly
- Review performance metrics
- Update dependencies (development)
- Test staging environment

### Monthly
- Security updates
- Rotate API keys
- Review access logs
- Test disaster recovery

### Quarterly
- Full security audit
- Performance optimization
- Documentation updates
- Team training

---

For more information, see:
- [Git Workflow](./docs/GIT_WORKFLOW.md)
- [API Documentation](./docs/API.md)
- [Contributing Guide](./CONTRIBUTING.md)