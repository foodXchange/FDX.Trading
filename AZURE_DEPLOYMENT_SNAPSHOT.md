# Azure Deployment Snapshot - Working Configuration
**Date**: August 1, 2025  
**Status**: WORKING ✅  
**URL**: https://www.fdx.trading/

## Critical Working Configuration

### 1. Docker Container Settings
```
Container Image: foodxchangeacr2025deploy.azurecr.io/foodxchange:8e3c88b4e8b4b9763711f850cf917d22e786c09e
Port: 9000
User: appuser (non-root)
```

### 2. Azure Web App Settings
```
Resource Group: foodxchange-deploy
Web App Name: foodxchange-deploy-app
App Service Plan: foodxchange-deploy-plan (B1)
Location: West Europe
```

### 3. Essential Environment Variables
```
WEBSITES_PORT=9000
ENVIRONMENT=production
DEBUG=False
DOMAIN=fdx.trading
BASE_URL=https://www.fdx.trading
```

### 4. Container Registry Settings
```
Registry: foodxchangeacr2025deploy.azurecr.io
Username: foodxchangeacr2025deploy
Password: [Stored in GitHub Secrets as AZURE_REGISTRY_PASSWORD]
```

### 5. Custom Domain Configuration
```
Primary: www.fdx.trading (SSL Enabled)
Secondary: fdx.trading
SSL State: SNI Enabled
```

## Working Dockerfile Configuration

```dockerfile
# Production Dockerfile for FoodXchange
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security first
RUN useradd -m -u 1000 appuser

# Copy Python dependencies from builder to appuser's home
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser foodxchange/ ./foodxchange/
COPY --chown=appuser:appuser requirements.txt ./

# Create necessary directories with correct ownership
RUN mkdir -p logs uploads temp static/errors projects && \
    chown -R appuser:appuser /app

# Add local pip packages to PATH for appuser
ENV PATH=/home/appuser/.local/bin:$PATH

# Switch to non-root user
USER appuser

# Use port 9000 (non-privileged port that works with non-root user)
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:9000/health || exit 1

# Production server with Gunicorn on port 9000 for Azure
CMD ["gunicorn", "--bind", "0.0.0.0:9000", "--workers", "4", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "foodxchange.main:app", "-k", "uvicorn.workers.UvicornWorker"]
```

## Key Dependencies (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.35.0
gunicorn==21.2.0
aiofiles==23.2.1  # CRITICAL - was missing and caused failures
pydantic-settings==2.0.3
```

## Recovery Commands

### 1. Check Current Status
```bash
# Check if site is responding
curl -I https://www.fdx.trading/

# Check Azure Web App status
az webapp show --name foodxchange-deploy-app --resource-group foodxchange-deploy --query state -o tsv

# Check current container image
az webapp show --name foodxchange-deploy-app --resource-group foodxchange-deploy --query "siteConfig.linuxFxVersion" -o tsv
```

### 2. Emergency Recovery
```bash
# Set to last known working configuration
az webapp config container set \
  --name foodxchange-deploy-app \
  --resource-group foodxchange-deploy \
  --docker-custom-image-name foodxchangeacr2025deploy.azurecr.io/foodxchange:8e3c88b4e8b4b9763711f850cf917d22e786c09e

# Set correct port
az webapp config appsettings set \
  --name foodxchange-deploy-app \
  --resource-group foodxchange-deploy \
  --settings WEBSITES_PORT=9000

# Restart the app
az webapp restart --name foodxchange-deploy-app --resource-group foodxchange-deploy
```

### 3. View Logs
```bash
# Download logs
az webapp log download \
  --name foodxchange-deploy-app \
  --resource-group foodxchange-deploy \
  --log-file logs.zip

# Stream live logs (may timeout)
az webapp log tail \
  --name foodxchange-deploy-app \
  --resource-group foodxchange-deploy
```

## Common Issues and Solutions

### Issue 1: Permission Denied
**Error**: `/usr/local/bin/python3.11: can't open file '/root/.local/bin/gunicorn': [Errno 13] Permission denied`
**Solution**: Ensure Python packages are installed to `/home/appuser/.local` not `/root/.local`

### Issue 2: Port Binding Failed
**Error**: Container exits with code 2
**Solution**: Use port 9000 (non-privileged) instead of 80, ensure WEBSITES_PORT=9000

### Issue 3: Container Not Starting
**Error**: 503 Service Unavailable
**Solution**: Check for missing dependencies (especially aiofiles), verify Dockerfile permissions

### Issue 4: Timeout Issues
**Error**: Site doesn't respond
**Solution**: Ensure health check path exists (/health), check firewall rules, verify custom domain SSL

## Git Commit Reference
Working deployment commit: 8e3c88b4e8b4b9763711f850cf917d22e786c09e

## GitHub Actions Workflow
The deployment is automated via `.github/workflows/deploy-to-azure.yml`
Key settings:
- WEBSITES_PORT must be 9000
- Container registry credentials must be set correctly
- All app settings must be applied after deployment

## Monitoring
- Container should start within 2-3 minutes
- Health checks should pass after container starts
- Site should respond with 200 OK on GET requests
- Security headers should be present in responses

## Contact for Issues
Repository: https://github.com/foodXchange/FDX.Trading
Azure Resource Group: foodxchange-deploy
Azure Subscription: 88931ed0-52df-42fb-a09c-e024c9586f8a