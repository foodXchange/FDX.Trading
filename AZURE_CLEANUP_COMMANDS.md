# Azure Complete Cleanup and Fresh Deployment Commands

## Prerequisites
```bash
# Install required tools
winget install Microsoft.AzureCLI
winget install GitHub.cli
```

## 🔍 PHASE 1: AUDIT - List All Resources

### List All Azure Resources
```bash
# Login to Azure
az login

# Set subscription (if you have multiple)
az account list --output table
az account set --subscription "YOUR_SUBSCRIPTION_NAME"

# List ALL resources related to foodxchange/fdx
az resource list --query "[?contains(name, 'food') || contains(name, 'fdx')]" -o table

# List resource groups
az group list --query "[?contains(name, 'food') || contains(name, 'fdx')]" -o table

# List App Services
az webapp list --query "[?contains(name, 'food') || contains(name, 'fdx')]" -o table

# List PostgreSQL servers
az postgres server list --query "[?contains(name, 'food') || contains(name, 'fdx')]" -o table

# List Redis caches
az redis list --query "[?contains(name, 'food') || contains(name, 'fdx')]" -o table

# List Storage accounts
az storage account list --query "[?contains(name, 'food') || contains(name, 'fdx')]" -o table

# List Container registries
az acr list --query "[?contains(name, 'food') || contains(name, 'fdx')]" -o table

# List Container instances
az container list --query "[?contains(name, 'food') || contains(name, 'fdx')]" -o table

# List DNS zones
az network dns zone list --query "[?contains(name, 'fdx.trading')]" -o table

# List SSL certificates
az webapp config ssl list -o table

# List Key Vaults
az keyvault list --query "[?contains(name, 'food') || contains(name, 'fdx')]" -o table

# List Application Insights
az monitor app-insights component list --query "[?contains(name, 'food') || contains(name, 'fdx')]" -o table
```

### List GitHub Resources
```bash
# List branches
git branch -a

# List tags
git tag -l

# List GitHub Actions artifacts
gh run list --limit 50
gh api repos/:owner/:repo/actions/artifacts

# List releases
gh release list

# List secrets
gh secret list
```

## 🧹 PHASE 2: CLEANUP - Delete Old Resources

### Delete Azure Resources
```bash
# Delete specific resources (replace with actual names from audit)
# CAUTION: These commands will permanently delete resources!

# Delete App Service
az webapp delete --name "OLD_APP_NAME" --resource-group "RG_NAME"

# Delete PostgreSQL server
az postgres server delete --name "OLD_PG_SERVER" --resource-group "RG_NAME" --yes

# Delete Redis cache
az redis delete --name "OLD_REDIS_NAME" --resource-group "RG_NAME" --yes

# Delete Storage account
az storage account delete --name "OLD_STORAGE_NAME" --resource-group "RG_NAME" --yes

# Delete Container registry
az acr delete --name "OLD_ACR_NAME" --resource-group "RG_NAME" --yes

# Delete Container instances
az container delete --name "OLD_CONTAINER_NAME" --resource-group "RG_NAME" --yes

# Delete DNS zone (BE CAREFUL!)
az network dns zone delete --name "fdx.trading" --resource-group "RG_NAME" --yes

# Delete SSL certificates
az webapp config ssl delete --certificate-thumbprint "THUMBPRINT" --resource-group "RG_NAME"

# Delete Key Vault
az keyvault delete --name "OLD_KEYVAULT_NAME" --resource-group "RG_NAME"
az keyvault purge --name "OLD_KEYVAULT_NAME" # Permanently delete

# Delete entire resource group (deletes ALL resources in it)
az group delete --name "OLD_RG_NAME" --yes --no-wait
```

### Clean GitHub Repository
```bash
# Delete local branches
git branch | grep -v "main" | xargs -r git branch -D

# Delete remote branches
git push origin --delete OLD_BRANCH_NAME

# Delete all tags
git tag -l | xargs git tag -d
git push origin --delete $(git tag -l)

# Delete GitHub Actions runs
gh run list --limit 100 --json databaseId -q '.[].databaseId' | xargs -I {} gh run delete {}

# Delete artifacts
gh api repos/:owner/:repo/actions/artifacts --jq '.artifacts[].id' | xargs -I {} gh api -X DELETE repos/:owner/:repo/actions/artifacts/{}

# Clean git history (optional - creates fresh start)
git checkout --orphan newMain
git add -A
git commit -m "Initial commit - Fresh FoodXchange deployment"
git branch -D main
git branch -m main
git push -f origin main
```

## 🆕 PHASE 3: CREATE - Set Up Fresh Infrastructure

### Create New Azure Resources
```bash
# Set variables
$RG_NAME="foodxchange-prod-rg"
$LOCATION="eastus"
$APP_NAME="foodxchange-app"
$ACR_NAME="foodxchangeacr"
$PG_SERVER="foodxchange-pg-server"
$REDIS_NAME="foodxchange-redis"
$STORAGE_NAME="foodxchangestorage"
$KEYVAULT_NAME="foodxchange-kv"

# Create resource group
az group create --name $RG_NAME --location $LOCATION

# Create Container Registry
az acr create --name $ACR_NAME --resource-group $RG_NAME --sku Basic --admin-enabled true

# Create PostgreSQL server
az postgres server create `
  --name $PG_SERVER `
  --resource-group $RG_NAME `
  --location $LOCATION `
  --admin-user fdxadmin `
  --admin-password "YOUR_STRONG_PASSWORD" `
  --sku-name B_Gen5_1 `
  --version 11

# Create database
az postgres db create `
  --name foodxchange `
  --resource-group $RG_NAME `
  --server-name $PG_SERVER

# Configure firewall for PostgreSQL
az postgres server firewall-rule create `
  --name AllowAzureServices `
  --resource-group $RG_NAME `
  --server-name $PG_SERVER `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 0.0.0.0

# Create Redis Cache
az redis create `
  --name $REDIS_NAME `
  --resource-group $RG_NAME `
  --location $LOCATION `
  --sku Basic `
  --vm-size c0

# Create Storage Account
az storage account create `
  --name $STORAGE_NAME `
  --resource-group $RG_NAME `
  --location $LOCATION `
  --sku Standard_LRS

# Create container in storage
az storage container create `
  --name uploads `
  --account-name $STORAGE_NAME `
  --public-access blob

# Create Key Vault
az keyvault create `
  --name $KEYVAULT_NAME `
  --resource-group $RG_NAME `
  --location $LOCATION

# Create App Service Plan
az appservice plan create `
  --name foodxchange-plan `
  --resource-group $RG_NAME `
  --sku B1 `
  --is-linux

# Create Web App
az webapp create `
  --name $APP_NAME `
  --resource-group $RG_NAME `
  --plan foodxchange-plan `
  --deployment-container-image-name "$ACR_NAME.azurecr.io/foodxchange:latest"
```

### Configure Domain and SSL
```bash
# Create DNS Zone
az network dns zone create `
  --name fdx.trading `
  --resource-group $RG_NAME

# Get name servers
az network dns zone show `
  --name fdx.trading `
  --resource-group $RG_NAME `
  --query nameServers

# Add DNS records
az network dns record-set a add-record `
  --resource-group $RG_NAME `
  --zone-name fdx.trading `
  --record-set-name @ `
  --ipv4-address "YOUR_APP_IP"

az network dns record-set a add-record `
  --resource-group $RG_NAME `
  --zone-name fdx.trading `
  --record-set-name www `
  --ipv4-address "YOUR_APP_IP"

# Add custom domain to app
az webapp config hostname add `
  --webapp-name $APP_NAME `
  --resource-group $RG_NAME `
  --hostname www.fdx.trading

az webapp config hostname add `
  --webapp-name $APP_NAME `
  --resource-group $RG_NAME `
  --hostname fdx.trading

# Create managed SSL certificate
az webapp config ssl create `
  --name $APP_NAME `
  --resource-group $RG_NAME `
  --hostname www.fdx.trading

# Bind SSL certificate
az webapp config ssl bind `
  --name $APP_NAME `
  --resource-group $RG_NAME `
  --certificate-thumbprint "THUMBPRINT" `
  --ssl-type SNI
```

### Set Up Secrets in Key Vault
```bash
# Database connection string
az keyvault secret set `
  --vault-name $KEYVAULT_NAME `
  --name "DatabaseUrl" `
  --value "postgresql://fdxadmin@$PG_SERVER:PASSWORD@$PG_SERVER.postgres.database.azure.com:5432/foodxchange?sslmode=require"

# Redis connection string
$REDIS_KEY=$(az redis list-keys --name $REDIS_NAME --resource-group $RG_NAME --query primaryKey -o tsv)
az keyvault secret set `
  --vault-name $KEYVAULT_NAME `
  --name "RedisUrl" `
  --value "rediss://:$REDIS_KEY@$REDIS_NAME.redis.cache.windows.net:6380/0"

# Application secret key
az keyvault secret set `
  --vault-name $KEYVAULT_NAME `
  --name "SecretKey" `
  --value "$(openssl rand -hex 32)"

# Storage connection string
$STORAGE_KEY=$(az storage account keys list --account-name $STORAGE_NAME --query "[0].value" -o tsv)
az keyvault secret set `
  --vault-name $KEYVAULT_NAME `
  --name "StorageConnectionString" `
  --value "DefaultEndpointsProtocol=https;AccountName=$STORAGE_NAME;AccountKey=$STORAGE_KEY;EndpointSuffix=core.windows.net"
```

## 🚀 PHASE 4: DEPLOY - Fresh Deployment

### Configure GitHub Secrets
```bash
# Get ACR credentials
$ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
$ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# Set GitHub secrets
gh secret set AZURE_REGISTRY_URL --body "$ACR_NAME.azurecr.io"
gh secret set AZURE_REGISTRY_USERNAME --body $ACR_USERNAME
gh secret set AZURE_REGISTRY_PASSWORD --body $ACR_PASSWORD
gh secret set AZURE_WEBAPP_NAME --body $APP_NAME
gh secret set AZURE_RESOURCE_GROUP --body $RG_NAME

# Set environment secrets from Key Vault
gh secret set DATABASE_URL --body "$(az keyvault secret show --vault-name $KEYVAULT_NAME --name DatabaseUrl --query value -o tsv)"
gh secret set REDIS_URL --body "$(az keyvault secret show --vault-name $KEYVAULT_NAME --name RedisUrl --query value -o tsv)"
gh secret set SECRET_KEY --body "$(az keyvault secret show --vault-name $KEYVAULT_NAME --name SecretKey --query value -o tsv)"
gh secret set AZURE_STORAGE_CONNECTION_STRING --body "$(az keyvault secret show --vault-name $KEYVAULT_NAME --name StorageConnectionString --query value -o tsv)"

# Add your Azure AI services secrets
gh secret set AZURE_OPENAI_ENDPOINT --body "YOUR_ENDPOINT"
gh secret set AZURE_OPENAI_KEY --body "YOUR_KEY"
```

### Deploy Application
```bash
# Build and push Docker image
docker build -t foodxchange:latest -f Dockerfile.azure .
docker tag foodxchange:latest $ACR_NAME.azurecr.io/foodxchange:latest

# Login to ACR
az acr login --name $ACR_NAME

# Push image
docker push $ACR_NAME.azurecr.io/foodxchange:latest

# Deploy to Web App
az webapp config container set `
  --name $APP_NAME `
  --resource-group $RG_NAME `
  --docker-custom-image-name $ACR_NAME.azurecr.io/foodxchange:latest `
  --docker-registry-server-url https://$ACR_NAME.azurecr.io `
  --docker-registry-server-user $ACR_USERNAME `
  --docker-registry-server-password $ACR_PASSWORD

# Set environment variables
az webapp config appsettings set `
  --name $APP_NAME `
  --resource-group $RG_NAME `
  --settings `
    ENVIRONMENT=production `
    DATABASE_URL="@Microsoft.KeyVault(SecretUri=https://$KEYVAULT_NAME.vault.azure.net/secrets/DatabaseUrl/)" `
    REDIS_URL="@Microsoft.KeyVault(SecretUri=https://$KEYVAULT_NAME.vault.azure.net/secrets/RedisUrl/)" `
    SECRET_KEY="@Microsoft.KeyVault(SecretUri=https://$KEYVAULT_NAME.vault.azure.net/secrets/SecretKey/)"

# Restart app
az webapp restart --name $APP_NAME --resource-group $RG_NAME
```

## ✅ PHASE 5: VERIFY - Test Deployment

```bash
# Check app status
az webapp show --name $APP_NAME --resource-group $RG_NAME --query state

# View logs
az webapp log tail --name $APP_NAME --resource-group $RG_NAME

# Test endpoints
curl https://www.fdx.trading/health
curl https://www.fdx.trading/api/health

# Check SSL certificate
openssl s_client -connect www.fdx.trading:443 -servername www.fdx.trading

# Monitor metrics
az monitor metrics list `
  --resource $APP_NAME `
  --resource-group $RG_NAME `
  --metric "Http5xx" `
  --interval PT1M
```

## 🔄 Rollback Commands (if needed)

```bash
# Rollback to previous Docker image
az webapp config container set `
  --name $APP_NAME `
  --resource-group $RG_NAME `
  --docker-custom-image-name $ACR_NAME.azurecr.io/foodxchange:previous

# Restore database from backup
az postgres db restore `
  --name foodxchange-restored `
  --resource-group $RG_NAME `
  --server-name $PG_SERVER `
  --source-database foodxchange `
  --restore-point-in-time "2024-01-15T00:00:00Z"
```