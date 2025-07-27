# Azure Services Configuration Guide for FoodXchange

This guide explains how to configure Azure services for production deployment. These services are optional and the application will work without them.

## Available Azure Services

### 1. Azure OpenAI Service
Used for AI-powered features like intelligent sourcing and email analysis.

```env
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
```

### 2. Azure Blob Storage
Used for file uploads and document storage.

```env
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=youraccountname;AccountKey=yourkey;EndpointSuffix=core.windows.net
```

### 3. Azure Communication Services
Used for sending emails via Azure.

```env
AZURE_EMAIL_CONNECTION_STRING=endpoint=https://your-resource.communication.azure.com;accesskey=yourkey
```

### 4. Azure PostgreSQL (Alternative to Supabase)
If you prefer Azure PostgreSQL over Supabase:

```env
DATABASE_URL=postgresql://username:password@your-server.postgres.database.azure.com:5432/database?sslmode=require
```

## Setting Up Azure Services

### Prerequisites
- Azure account with active subscription
- Azure CLI installed (optional but recommended)

### Step 1: Create Resource Group
```bash
az group create --name foodxchange-rg --location westus
```

### Step 2: Create Azure OpenAI Service (Optional)
1. Go to Azure Portal > Create a resource > Azure OpenAI
2. Select your subscription and resource group
3. Choose a region that supports OpenAI
4. Create a deployment (e.g., gpt-35-turbo)
5. Copy the endpoint and key to your .env file

### Step 3: Create Storage Account (Optional)
```bash
az storage account create \
  --name foodxchangestorage \
  --resource-group foodxchange-rg \
  --location westus \
  --sku Standard_LRS
```

### Step 4: Create Communication Service (Optional)
1. Go to Azure Portal > Create a resource > Communication Services
2. Create the service in your resource group
3. Get the connection string from Keys section

### Step 5: Create Azure PostgreSQL (Optional)
```bash
az postgres flexible-server create \
  --resource-group foodxchange-rg \
  --name foodxchange-db \
  --location westus \
  --admin-user adminuser \
  --admin-password YourPassword123! \
  --sku-name Standard_B1ms \
  --version 14
```

## Security Best Practices

1. **Use Azure Key Vault**: Store secrets in Key Vault instead of environment variables for production
2. **Enable Managed Identity**: Use managed identities for Azure resources when possible
3. **Network Security**: Configure firewalls and network security groups
4. **Enable SSL/TLS**: Always use SSL for database connections
5. **Regular Backups**: Enable automatic backups for PostgreSQL

## Cost Optimization

1. **Start Small**: Use basic tiers initially
2. **Auto-scaling**: Configure auto-scaling for compute resources
3. **Monitor Usage**: Use Azure Cost Management
4. **Reserved Instances**: Consider reserved instances for long-term savings

## Monitoring and Logging

1. **Application Insights**: Already integrated via Sentry
2. **Azure Monitor**: Set up alerts for critical metrics
3. **Log Analytics**: Centralize logs from all services

## Current Configuration

The application is currently configured to use:
- **Database**: Supabase PostgreSQL (cloud-hosted)
- **File Storage**: Local filesystem (can be migrated to Azure Blob)
- **Email**: SMTP configuration (can be migrated to Azure Communication Services)
- **AI Services**: Optional Azure OpenAI integration

## Migration Checklist

- [ ] Decide which Azure services to use
- [ ] Create Azure resources
- [ ] Update .env file with Azure credentials
- [ ] Test services in development
- [ ] Deploy to Azure App Service or Container Instances
- [ ] Configure production environment variables
- [ ] Enable monitoring and alerts

## Support

For Azure-specific issues:
- Azure Documentation: https://docs.microsoft.com/azure
- Azure Support: https://azure.microsoft.com/support

For FoodXchange-specific issues:
- Check the `/docs` directory
- Review error logs in the application