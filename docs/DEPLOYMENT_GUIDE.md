# FoodXchange Deployment Guide

## Overview

This guide covers deployment scenarios for the FoodXchange platform, from local development to production Azure deployment.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Azure Cloud Deployment](#azure-cloud-deployment)
4. [Production Configuration](#production-configuration)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Troubleshooting](#troubleshooting)

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend assets)
- Docker Desktop
- Git
- Azure CLI (for cloud features)

### Step 1: Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd FoodXchange

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env file with local settings
nano .env
```

**Minimal Development Configuration:**
```bash
# Environment
ENVIRONMENT=development
DEBUG=true

# Database (Docker)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/foodxchange

# Redis (Docker)
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your-development-secret-key-min-32-chars
JWT_ALGORITHM=HS256

# Azure AI (Optional for development)
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
```

### Step 3: Start Services
```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Verify services
docker-compose ps

# Start development server
python start_clean.bat
# or
python -m uvicorn foodxchange.main:app --reload --port 9000
```

### Step 4: Verify Installation
```bash
# Health check
curl http://localhost:9000/health

# Test login
curl -X POST http://localhost:9000/auth/login \
  -d "email=admin@fdx.trading&password=FDX2030!"
```

## Docker Deployment

### Full Stack Deployment
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "9000:9000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/foodxchange
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./uploads:/app/uploads

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: foodxchange
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Build and Deploy
```bash
# Build application
docker build -t foodxchange:latest .

# Start full stack
docker-compose up -d

# View logs
docker-compose logs -f app

# Scale application
docker-compose up -d --scale app=3
```

### Docker Production Configuration
```dockerfile
# Dockerfile.prod
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 foodxchange && \
    chown -R foodxchange:foodxchange /app
USER foodxchange

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
  CMD curl -f http://localhost:9000/health || exit 1

# Start application
CMD ["uvicorn", "foodxchange.main:app", "--host", "0.0.0.0", "--port", "9000"]
```

## Azure Cloud Deployment

### Azure Resources Required

#### Core Infrastructure
- **Azure Container Registry** - Container image storage
- **Azure Container Instances** or **App Service** - Application hosting
- **Azure Database for PostgreSQL** - Managed database
- **Azure Cache for Redis** - Managed caching
- **Azure Storage Account** - File uploads and static assets

#### AI Services
- **Azure OpenAI Service** - GPT-4 Vision integration
- **Azure Computer Vision** - Image analysis
- **Azure Translator** - Multi-language support
- **Azure Document Intelligence** - Document processing

### Step 1: Azure Setup
```bash
# Login to Azure
az login

# Create resource group
az group create --name foodxchange-rg --location eastus

# Create container registry
az acr create --name foodxchangeacr --resource-group foodxchange-rg --sku Basic
```

### Step 2: Database Setup
```bash
# Create PostgreSQL server
az postgres flexible-server create \
  --name foodxchange-db \
  --resource-group foodxchange-rg \
  --location eastus \
  --admin-user foodxchange \
  --admin-password "SecurePassword123!" \
  --sku-name Standard_B1ms \
  --version 16

# Create database
az postgres flexible-server db create \
  --resource-group foodxchange-rg \
  --server-name foodxchange-db \
  --database-name foodxchange
```

### Step 3: Redis Setup
```bash
# Create Redis cache
az redis create \
  --name foodxchange-cache \
  --resource-group foodxchange-rg \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

### Step 4: AI Services Setup
```bash
# Create OpenAI service
az cognitiveservices account create \
  --name foodxchange-openai \
  --resource-group foodxchange-rg \
  --kind OpenAI \
  --sku S0 \
  --location eastus

# Create Computer Vision
az cognitiveservices account create \
  --name foodxchange-vision \
  --resource-group foodxchange-rg \
  --kind ComputerVision \
  --sku S1 \
  --location eastus

# Create Translator
az cognitiveservices account create \
  --name foodxchange-translator \
  --resource-group foodxchange-rg \
  --kind TextTranslation \
  --sku S1 \
  --location eastus
```

### Step 5: Application Deployment
```bash
# Build and push container
docker build -t foodxchange:latest .
docker tag foodxchange:latest foodxchangeacr.azurecr.io/foodxchange:latest

# Login to ACR
az acr login --name foodxchangeacr
docker push foodxchangeacr.azurecr.io/foodxchange:latest

# Deploy to Container Instances
az container create \
  --name foodxchange-app \
  --resource-group foodxchange-rg \
  --image foodxchangeacr.azurecr.io/foodxchange:latest \
  --registry-login-server foodxchangeacr.azurecr.io \
  --cpu 2 \
  --memory 4 \
  --ports 9000 \
  --dns-name-label foodxchange-app \
  --environment-variables \
    ENVIRONMENT=production \
    DATABASE_URL="postgresql://user:pass@server:5432/db" \
    REDIS_URL="redis://cache:6380/0?ssl=true" \
    AZURE_OPENAI_ENDPOINT="https://openai.openai.azure.com/"
```

### Step 6: Custom Domain & SSL
```bash
# Add custom domain (requires DNS configuration)
az container create \
  --name foodxchange-app \
  --resource-group foodxchange-rg \
  --image foodxchangeacr.azurecr.io/foodxchange:latest \
  --ports 443 \
  --environment-variables SSL_CERT_PATH=/certs/cert.pem

# Configure SSL certificate
# Use Azure Application Gateway or Azure Front Door for SSL termination
```

## Production Configuration

### Environment Variables
```bash
# Production Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Security
JWT_SECRET_KEY=super-secure-32-character-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Database
DATABASE_URL=postgresql://user:password@server:5432/db?sslmode=require
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://cache:6380/0?ssl=true&ssl_check_hostname=false
REDIS_POOL_SIZE=10

# Azure Services
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-secure-api-key
AZURE_COMPUTER_VISION_ENDPOINT=https://your-vision.cognitiveservices.azure.com/
AZURE_COMPUTER_VISION_KEY=your-vision-key

# File Upload
MAX_FILE_SIZE=50MB
UPLOAD_DIRECTORY=/app/uploads
ALLOWED_EXTENSIONS=jpg,png,pdf,docx,xlsx,csv

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REDIS_URL=redis://cache:6380/0?ssl=true

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
AZURE_INSIGHTS_INSTRUMENTATION_KEY=your-insights-key
```

### Security Configuration
```bash
# SSL/TLS
SSL_CERT_PATH=/certs/fullchain.pem
SSL_KEY_PATH=/certs/privkey.pem
SSL_REDIRECT=true

# CORS
ALLOWED_ORIGINS=https://foodxchange.com,https://app.foodxchange.com
CORS_ALLOW_CREDENTIALS=true

# Security Headers
SECURE_HEADERS_ENABLED=true
HSTS_MAX_AGE=31536000
CSP_POLICY="default-src 'self'; script-src 'self' 'unsafe-inline'"
```

### Performance Configuration
```bash
# Application
WORKERS=4
WORKER_CLASS=uvicorn.workers.UvicornWorker
WORKER_CONNECTIONS=1000
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=100

# Caching
CACHE_TTL=3600
STATIC_CACHE_TTL=86400
API_CACHE_ENABLED=true

# Database
DB_POOL_PRE_PING=true
DB_POOL_RECYCLE=3600
DB_ECHO=false
```

## Monitoring & Maintenance

### Health Monitoring
```bash
# Health check endpoint
curl https://yourapp.azurewebsites.net/health

# Database health
curl https://yourapp.azurewebsites.net/health/db

# Redis health
curl https://yourapp.azurewebsites.net/health/cache
```

### Log Monitoring
```bash
# View application logs
az container logs --name foodxchange-app --resource-group foodxchange-rg

# Stream logs
az container logs --name foodxchange-app --resource-group foodxchange-rg --follow

# Download logs
az container logs --name foodxchange-app --resource-group foodxchange-rg > app.log
```

### Performance Monitoring
```python
# Add to main.py for Azure Application Insights
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    connection_string="InstrumentationKey=your-key"
)
```

### Backup Strategy
```bash
# Database backup
az postgres flexible-server backup create \
  --resource-group foodxchange-rg \
  --server-name foodxchange-db

# File storage backup
az storage blob sync \
  --source /app/uploads \
  --destination https://storage.blob.core.windows.net/backups
```

### Updates and Scaling
```bash
# Update application
docker build -t foodxchange:v2 .
docker tag foodxchange:v2 foodxchangeacr.azurecr.io/foodxchange:v2
docker push foodxchangeacr.azurecr.io/foodxchange:v2

# Rolling update
az container create \
  --name foodxchange-app-v2 \
  --image foodxchangeacr.azurecr.io/foodxchange:v2 \
  --resource-group foodxchange-rg

# Scale horizontally
az container create \
  --name foodxchange-app-2 \
  --image foodxchangeacr.azurecr.io/foodxchange:latest \
  --resource-group foodxchange-rg
```

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Test database connectivity
psql -h server -U user -d database -c "SELECT 1"

# Check Azure PostgreSQL firewall
az postgres flexible-server firewall-rule list \
  --resource-group foodxchange-rg \
  --server-name foodxchange-db
```

#### Redis Connection Issues
```bash
# Test Redis connectivity
redis-cli -h cache -p 6380 -a password ping

# Check Azure Redis access keys
az redis list-keys \
  --name foodxchange-cache \
  --resource-group foodxchange-rg
```

#### SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in cert.pem -text -noout

# Verify certificate chain
openssl verify -CAfile chain.pem cert.pem
```

#### Performance Issues
```bash
# Check container resources
az container show \
  --name foodxchange-app \
  --resource-group foodxchange-rg \
  --query containers[0].resources

# Monitor CPU and memory
az monitor metrics list \
  --resource /subscriptions/sub/resourceGroups/rg/providers/Microsoft.ContainerInstance/containerGroups/app
```

### Debug Commands
```bash
# Container shell access
az container exec \
  --name foodxchange-app \
  --resource-group foodxchange-rg \
  --exec-command "/bin/bash"

# Environment variable check
az container show \
  --name foodxchange-app \
  --resource-group foodxchange-rg \
  --query containers[0].environmentVariables

# Port connectivity test
telnet yourapp.azurewebsites.net 443
```

### Recovery Procedures

#### Database Recovery
```bash
# Restore from backup
az postgres flexible-server restore \
  --source-server foodxchange-db \
  --name foodxchange-db-restored \
  --resource-group foodxchange-rg \
  --restore-time "2024-01-01T12:00:00Z"
```

#### Application Recovery
```bash
# Restart container
az container restart \
  --name foodxchange-app \
  --resource-group foodxchange-rg

# Rollback to previous version
az container create \
  --name foodxchange-app \
  --image foodxchangeacr.azurecr.io/foodxchange:previous \
  --resource-group foodxchange-rg
```

## Support

### Azure Support
- **Documentation**: https://docs.microsoft.com/azure
- **Support Portal**: https://portal.azure.com/#blade/Microsoft_Azure_Support
- **Community**: https://stackoverflow.com/questions/tagged/azure

### Application Support
- **Health Monitoring**: `/health` endpoint
- **Log Analysis**: Azure Application Insights
- **Performance Metrics**: Azure Monitor

---

*For production deployments, always test thoroughly in a staging environment first.*