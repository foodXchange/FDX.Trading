# FoodXchange Deployment Guide

## Overview

This guide covers deploying the FoodXchange application to various environments, from local development to production on Azure App Service.

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Azure CLI (for Azure deployment)
- Git

## Local Development

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/foodxchange.git
cd foodxchange

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Set up environment variables
cp .env.example .env
# Edit .env with your database configuration

# Run database setup
python setup_database.py
```

### 3. Start Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access the application at: http://localhost:8000

## Azure App Service Deployment

### Method 1: Automated Deployment Scripts

#### Windows Deployment
```bash
deploy.bat
```

#### PowerShell Deployment
```powershell
.\azure-deploy.ps1
```

### Method 2: Manual Deployment

#### 1. Prepare Application

```bash
# Create deployment package
python make_deploy_zip.py
```

This creates `app.zip` with all necessary files.

#### 2. Azure CLI Setup

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "your-subscription-id"

# Create resource group (if needed)
az group create --name foodxchange-rg --location "East US"

# Create App Service plan
az appservice plan create --name foodxchange-plan --resource-group foodxchange-rg --sku B1 --is-linux

# Create web app
az webapp create --name foodxchange-app --resource-group foodxchange-rg --plan foodxchange-plan --runtime "PYTHON|3.9"
```

#### 3. Configure Environment Variables

```bash
# Set environment variables
az webapp config appsettings set --name foodxchange-app --resource-group foodxchange-rg --settings \
  DATABASE_URL="postgresql://user:password@server.postgres.database.azure.com/database" \
  SECRET_KEY="your-secret-key" \
  SMTP_HOST="smtp.gmail.com" \
  SMTP_PORT="587" \
  SMTP_USER="your-email@gmail.com" \
  SMTP_PASSWORD="your-app-password"
```

#### 4. Deploy Application

```bash
# Deploy using Azure CLI
az webapp deployment source config-zip --resource-group foodxchange-rg --name foodxchange-app --src app.zip

# Or deploy using Git
az webapp deployment source config --name foodxchange-app --resource-group foodxchange-rg --repo-url https://github.com/yourusername/foodxchange.git --branch main --manual-integration
```

### Method 3: GitHub Actions (CI/CD)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Create deployment package
      run: python make_deploy_zip.py
    
    - name: Deploy to Azure
      uses: azure/webapps-deploy@v2
      with:
        app-name: 'foodxchange-app'
        package: ./app.zip
```

## Production Configuration

### 1. Environment Variables

Set these in Azure App Service Configuration:

```env
# Database
DATABASE_URL=postgresql://user:password@server.postgres.database.azure.com/database

# Security
SECRET_KEY=your-production-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@foodxchange.com
EMAILS_FROM_NAME=FoodXchange

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=your-azure-connection-string
AZURE_CONTAINER_NAME=foodxchange-files
```

### 2. Database Configuration

#### Azure Database for PostgreSQL

```bash
# Create PostgreSQL server
az postgres flexible-server create \
  --name foodxchange-db \
  --resource-group foodxchange-rg \
  --location "East US" \
  --admin-user foodxchange_admin \
  --admin-password "your-secure-password" \
  --sku-name Standard_B1ms \
  --version 13

# Create database
az postgres flexible-server db create \
  --server-name foodxchange-db \
  --resource-group foodxchange-rg \
  --database-name foodxchange_db
```

### 3. SSL Configuration

```bash
# Configure SSL
az webapp config set --name foodxchange-app --resource-group foodxchange-rg --min-tls-version 1.2

# Configure custom domain (if needed)
az webapp config hostname add --webapp-name foodxchange-app --resource-group foodxchange-rg --hostname your-domain.com
```

### 4. Monitoring and Logging

```bash
# Enable application logging
az webapp log config --name foodxchange-app --resource-group foodxchange-rg --application-logging filesystem --level information

# Enable detailed error messages
az webapp config set --name foodxchange-app --resource-group foodxchange-rg --detailed-error-logging true
```

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Build and Run

```bash
# Build image
docker build -t foodxchange .

# Run container
docker run -p 8000:8000 --env-file .env foodxchange
```

### 3. Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/foodxchange_db
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=foodxchange_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

## Performance Optimization

### 1. Gunicorn Configuration

For production, use Gunicorn with multiple workers:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 2. Static File Serving

Configure Azure CDN or use a reverse proxy for static files:

```bash
# Configure static file serving
az webapp config set --name foodxchange-app --resource-group foodxchange-rg --static-sites-enabled true
```

### 3. Caching

Implement Redis caching for frequently accessed data:

```python
# In your application
import redis

redis_client = redis.Redis(host='your-redis-host', port=6379, db=0)
```

## Security Considerations

### 1. Environment Variables

- Never commit sensitive data to version control
- Use Azure Key Vault for production secrets
- Rotate secrets regularly

### 2. Database Security

- Use connection pooling
- Enable SSL for database connections
- Implement proper access controls

### 3. Application Security

- Enable HTTPS only
- Implement rate limiting
- Use secure headers
- Regular security updates

## Monitoring and Maintenance

### 1. Health Checks

The application includes a health check endpoint:

```bash
curl https://your-app.azurewebsites.net/health
```

### 2. Logging

Configure application logging to monitor performance and errors:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### 3. Backup Strategy

- Regular database backups
- Application state backups
- Disaster recovery plan

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'uvicorn'**
   - Ensure uvicorn is in requirements.txt
   - Check virtual environment activation

2. **Database Connection Issues**
   - Verify DATABASE_URL format
   - Check firewall settings
   - Ensure database server is running

3. **Static Files Not Loading**
   - Check static file directory configuration
   - Verify file permissions
   - Use CDN for production

### Debug Mode

Enable debug mode for development:

```bash
export DEBUG=True
uvicorn app.main:app --reload --log-level debug
```

## Support

For deployment issues:
- Check Azure App Service logs
- Review application logs
- Contact support: deployment@foodxchange.com 