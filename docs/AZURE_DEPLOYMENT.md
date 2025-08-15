# Azure Deployment Guide

## Prerequisites

- Azure subscription
- Azure CLI installed (`az login` completed)
- .NET 9 SDK installed
- GitHub repository configured

## Azure Resources Setup

### 1. Azure SQL Database

```bash
# Create resource group
az group create -n rg-foodxchange -l eastus

# Create SQL Server
az sql server create \
  -g rg-foodxchange \
  -n sql-foodxchange \
  -l eastus \
  --admin-user sqladmin \
  --admin-password <YourStrongPassword>

# Create database
az sql db create \
  -g rg-foodxchange \
  -s sql-foodxchange \
  -n FoodXchange \
  --service-objective S0

# Configure Azure AD admin (use your email)
az sql server ad-admin create \
  -g rg-foodxchange \
  -s sql-foodxchange \
  --display-name "Admin" \
  --object-id <your-azure-ad-object-id>
```

### 2. App Service with Managed Identity

```bash
# Create App Service Plan
az appservice plan create \
  -g rg-foodxchange \
  -n plan-foodxchange \
  --sku B1 \
  --is-linux false

# Create API App Service
az webapp create \
  -g rg-foodxchange \
  -p plan-foodxchange \
  -n app-foodxchange-api \
  --runtime "dotnet:9"

# Enable System Managed Identity
az webapp identity assign \
  -g rg-foodxchange \
  -n app-foodxchange-api

# Create Blazor App Service
az webapp create \
  -g rg-foodxchange \
  -p plan-foodxchange \
  -n app-foodxchange-web \
  --runtime "dotnet:9"
```

### 3. Configure Database Access

Connect to Azure SQL using Azure Data Studio or SSMS with Azure AD auth, then run:

```sql
-- In FoodXchange database (not master!)
CREATE USER [app-foodxchange-api] FROM EXTERNAL PROVIDER;
ALTER ROLE db_datareader ADD MEMBER [app-foodxchange-api];
ALTER ROLE db_datawriter ADD MEMBER [app-foodxchange-api];
-- If app runs migrations:
-- ALTER ROLE db_ddladmin ADD MEMBER [app-foodxchange-api];
```

### 4. Azure OpenAI (Optional)

```bash
# Create OpenAI resource
az cognitiveservices account create \
  -g rg-foodxchange \
  -n openai-foodxchange \
  --kind OpenAI \
  --sku S0 \
  -l eastus \
  --yes

# Deploy model
az cognitiveservices account deployment create \
  -g rg-foodxchange \
  -n openai-foodxchange \
  --deployment-name gpt-4o-mini \
  --model-name gpt-4o-mini \
  --model-version "2024-07-18" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "Standard"
```

## Configuration

### API App Service Settings

```bash
# Connection string for Managed Identity
az webapp config connection-string set \
  -g rg-foodxchange \
  -n app-foodxchange-api \
  --connection-string-type SQLAzure \
  --settings Sql="Server=tcp:sql-foodxchange.database.windows.net,1433;Database=FoodXchange;Encrypt=True;TrustServerCertificate=False;Authentication=Active Directory Managed Identity"

# Azure OpenAI settings
az webapp config appsettings set \
  -g rg-foodxchange \
  -n app-foodxchange-api \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://openai-foodxchange.openai.azure.com/" \
    AZURE_OPENAI_KEY="<get-from-portal>" \
    AZURE_OPENAI_DEPLOYMENT="gpt-4o-mini"

# Application Insights
az monitor app-insights component create \
  -g rg-foodxchange \
  -a appinsights-foodxchange \
  -l eastus

# Get connection string
APPINSIGHTS_CONNECTION=$(az monitor app-insights component show \
  -g rg-foodxchange \
  -a appinsights-foodxchange \
  --query connectionString -o tsv)

az webapp config appsettings set \
  -g rg-foodxchange \
  -n app-foodxchange-api \
  --settings APPLICATIONINSIGHTS_CONNECTION_STRING="$APPINSIGHTS_CONNECTION"
```

### Blazor App Settings

```bash
az webapp config appsettings set \
  -g rg-foodxchange \
  -n app-foodxchange-web \
  --settings \
    ApiBaseUrl="https://app-foodxchange-api.azurewebsites.net/" \
    APPLICATIONINSIGHTS_CONNECTION_STRING="$APPINSIGHTS_CONNECTION"
```

## Deployment

### Using GitHub Actions

The repository includes `.github/workflows/ci.yml` for CI/CD. Add these secrets to your GitHub repository:

- `AZURE_CREDENTIALS` - Service principal JSON
- `ACR_ENDPOINT` - If using containers
- `ACR_USERNAME` - If using containers
- `ACR_PASSWORD` - If using containers

### Manual Deployment

```bash
# API
cd src/FoodXchange.Api
dotnet publish -c Release -o ./publish
cd publish
zip -r ../../api.zip .
az webapp deploy \
  -g rg-foodxchange \
  -n app-foodxchange-api \
  --src-path ../../api.zip

# Blazor App
cd src/FoodXchange.App
dotnet publish -c Release -o ./publish
cd publish
zip -r ../../app.zip .
az webapp deploy \
  -g rg-foodxchange \
  -n app-foodxchange-web \
  --src-path ../../app.zip
```

## Verification

1. **Health Check**: `https://app-foodxchange-api.azurewebsites.net/health`
2. **DB Verify**: `https://app-foodxchange-api.azurewebsites.net/db/verify`
3. **AI Status**: `https://app-foodxchange-api.azurewebsites.net/ai/status`
4. **Admin Diagnostics**: `https://app-foodxchange-web.azurewebsites.net/admin/diagnostics`

## Database Migrations

### Option 1: From Local Machine

```bash
# Using Azure AD auth from your machine
cd src/FoodXchange.Api
dotnet ef migrations add InitialCreate \
  -p ../FoodXchange.Infrastructure \
  -s . \
  -c AppDbContext

dotnet ef database update \
  -p ../FoodXchange.Infrastructure \
  -s . \
  -c AppDbContext
```

### Option 2: In Pipeline

Add to GitHub Actions:

```yaml
- name: Run Migrations
  run: |
    dotnet tool install --global dotnet-ef
    dotnet ef database update \
      -p src/FoodXchange.Infrastructure \
      -s src/FoodXchange.Api \
      -c AppDbContext \
      --connection "${{ secrets.SQL_CONNECTION }}"
```

## Security Checklist

- [ ] Managed Identity enabled
- [ ] No secrets in code
- [ ] Azure AD admin configured for SQL
- [ ] Network restrictions configured
- [ ] HTTPS only enforced
- [ ] Diagnostic logs enabled
- [ ] Backup configured for SQL
- [ ] `/db/verify` and `/ai/status` protected with auth

## Monitoring

- Application Insights dashboard
- SQL Database metrics
- App Service logs
- Health check alerts

## Cost Optimization

- Use B1 tier for dev/test
- Scale to S1/P1V2 for production
- Consider Azure SQL Serverless for variable workloads
- Use Application Gateway for multiple apps
- Enable auto-scaling based on metrics