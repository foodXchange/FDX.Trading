# Azure Services Setup Guide for FoodXchange

## 🔴 HIGH PRIORITY: Configure Missing Azure Services

The system health check identified 5 missing Azure services. Follow this guide to configure them:

### 1. Azure OpenAI Service
**Purpose**: AI-powered features, natural language processing, content generation

**Setup Steps**:
1. Go to Azure Portal → Create Resource → AI + Machine Learning → Azure OpenAI
2. Create a new resource with:
   - Resource name: `foodxchange-openai`
   - Region: Choose closest to your users
   - Pricing tier: Standard S0 (or higher for production)
3. Deploy a model:
   - Go to Azure OpenAI Studio
   - Deploy GPT-3.5 Turbo or GPT-4
   - Note the deployment name
4. Get credentials:
   - Copy the endpoint URL
   - Generate an API key
5. Update `.env` file:
   ```
   AZURE_OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_ENDPOINT=https://foodxchange-openai.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
   ```

### 2. Azure Computer Vision
**Purpose**: Image analysis, OCR, product image processing

**Setup Steps**:
1. Go to Azure Portal → Create Resource → AI + Machine Learning → Computer Vision
2. Create resource with:
   - Resource name: `foodxchange-vision`
   - Region: Same as OpenAI
   - Pricing tier: Standard S1
3. Get credentials:
   - Copy the endpoint URL
   - Copy the API key
4. Update `.env` file:
   ```
   AZURE_VISION_ENDPOINT=https://foodxchange-vision.cognitiveservices.azure.com/
   AZURE_VISION_KEY=your-vision-key
   ```

### 3. Azure Cognitive Search
**Purpose**: Intelligent search functionality, product indexing

**Setup Steps**:
1. Go to Azure Portal → Create Resource → Web → Azure Cognitive Search
2. Create resource with:
   - Service name: `foodxchange-search`
   - Region: Same as other services
   - Pricing tier: Basic (or higher for production)
3. Create an index:
   - Go to Search Explorer
   - Create index named "products"
4. Get credentials:
   - Copy the service URL
   - Generate an admin key
5. Update `.env` file:
   ```
   AZURE_SEARCH_ENDPOINT=https://foodxchange-search.search.windows.net
   AZURE_SEARCH_KEY=your-search-key
   AZURE_SEARCH_INDEX=products
   ```

### 4. Azure Storage Account
**Purpose**: File storage, product images, document storage

**Setup Steps**:
1. Go to Azure Portal → Create Resource → Storage → Storage account
2. Create account with:
   - Storage account name: `foodxchangestorage`
   - Region: Same as other services
   - Performance: Standard
   - Redundancy: LRS
3. Create a container:
   - Go to Containers
   - Create container named "product-images"
4. Get connection string:
   - Go to Access keys
   - Copy connection string
5. Update `.env` file:
   ```
   AZURE_STORAGE_CONNECTION_STRING=your-connection-string
   AZURE_STORAGE_CONTAINER=product-images
   ```

### 5. Azure Communication Services
**Purpose**: Email notifications, SMS, chat functionality

**Setup Steps**:
1. Go to Azure Portal → Create Resource → Communication → Communication Services
2. Create resource with:
   - Resource name: `foodxchange-communication`
   - Region: Same as other services
   - Data location: Choose appropriate region
3. Set up email domain:
   - Go to Email → Add domain
   - Verify your domain
4. Get connection string:
   - Go to Keys
   - Copy connection string
5. Update `.env` file:
   ```
   AZURE_EMAIL_CONNECTION_STRING=your-connection-string
   ```

## 🚀 Quick Setup Commands

After configuring Azure services, run these commands:

```bash
# Test Azure configuration
python test_azure_config.py

# Start the server
python start_server_fixed.py

# Run health check
python scripts/system_health_monitor.py
```

## 📊 Expected Results

After configuration, the system health check should show:
- ✅ Azure OpenAI: Configured
- ✅ Azure Computer Vision: Configured  
- ✅ Azure Cognitive Search: Configured
- ✅ Azure Storage: Configured
- ✅ Azure Communication Services: Configured

## 🔧 Troubleshooting

If services are still showing as missing:
1. Check that `.env` file is in the `foodxchange/` directory
2. Verify API keys and endpoints are correct
3. Ensure services are in the same Azure region
4. Check Azure service status in Azure Portal

## 💰 Cost Optimization

For development/testing:
- Use Basic/Standard tiers where possible
- Set up spending limits in Azure
- Monitor usage in Azure Cost Management
- Consider using Azure Free tier for initial testing
