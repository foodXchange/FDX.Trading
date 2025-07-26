# 🚀 FoodXchange Startup Guide

## ✅ Current Status

### Azure Services (All Configured!)
- ✅ **PostgreSQL Database** - `foodxchange_db` on `foodxchangepgfr`
- ✅ **Blob Storage** - `foodxchangestorage` 
- ✅ **OpenAI Service** - `foodxchangeopenai`
- ✅ **App Service** - `foodxchange-app` with all env vars configured

### Local Issue
- ⚠️ PostgreSQL connection timing out from your local network
- ✅ App Service can connect (Azure services allowed)

## 🎯 Option 1: Run Locally with SQLite (Recommended for now)

```bash
# 1. Start the application
python azure_startup.py

# 2. Access at
http://localhost:8000

# 3. Features available:
# - All UI/UX features
# - Order management
# - Notification system  
# - File uploads (needs Azure Storage connection string in .env)
# - AI features (needs OpenAI credentials in .env)
```

## 🌐 Option 2: Deploy Directly to App Service

Since the App Service already has all environment variables configured:

```bash
# 1. Create deployment zip
# Add these files to a zip:
# - app/ folder
# - alembic/ folder  
# - requirements.txt
# - azure_startup.py
# - alembic.ini

# 2. Deploy via Azure CLI
az webapp deployment source config-zip \
  --resource-group foodxchange-rg \
  --name foodxchange-app \
  --src foodxchange.zip

# 3. Run migrations on App Service
az webapp ssh --resource-group foodxchange-rg --name foodxchange-app
# In SSH session:
python -m alembic upgrade head
```

## 🧪 Option 3: Test Services from Cloud Shell

```bash
# 1. Open Azure Cloud Shell
# https://shell.azure.com

# 2. Clone your repo or upload files

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
export DATABASE_URL="postgresql://foodxchangedbadmin:Ud30078123@foodxchangepgfr.postgres.database.azure.com:5432/foodxchange_db?sslmode=require"
alembic upgrade head

# 5. Create app user
psql $DATABASE_URL -f database/create_app_user.sql
```

## 📋 Testing Checklist

### 1. Test OpenAI Integration
```python
# Create a file: test_ai.py
import asyncio
from app.services.openai_service import openai_service

async def test():
    # Test email parsing
    email = "We need 500kg of olive oil by next month. Budget $5000."
    result = await openai_service.parse_email_for_rfq(email)
    print("Parsed:", result)
    
    # Test RFQ generation
    desc = await openai_service.generate_rfq_description("Premium Olive Oil")
    print("Generated:", desc)

asyncio.run(test())
```

### 2. Test Blob Storage
```python
# Create a file: test_storage.py
import asyncio
from io import BytesIO
from app.services.blob_storage_service import blob_storage_service

async def test():
    # Upload test file
    file = BytesIO(b"Test document content")
    result = await blob_storage_service.upload_file(
        file=file,
        filename="test.pdf",
        container_type="quotes",
        company_id=1
    )
    print("Uploaded:", result)

asyncio.run(test())
```

## 🔧 Local Development Setup

### 1. Update your `.env` file:
```env
# Use SQLite locally (automatic fallback)
DATABASE_URL=sqlite:///./foodxchange.db

# Azure Storage (get from Azure Portal)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=foodxchangestorage;AccountKey=...

# Azure OpenAI (get from Azure Portal)
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://foodxchangeopenai.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

### 2. Create local database:
```bash
# This happens automatically when you run:
python azure_startup.py
```

### 3. Create test user:
```python
# The app creates a default admin user:
# Email: admin@foodxchange.com
# Password: admin123
```

## 🎯 High-Value Features to Try

### 1. **Email Intelligence**
- Go to Email Intelligence page
- Paste an email with RFQ content
- Watch AI extract products, quantities, dates

### 2. **Smart File Storage**
- Upload quotes to any RFQ
- Files stored securely in Azure
- Automatic organization by company

### 3. **Order Management**
- Create orders from quotes
- Track status changes
- Get notifications

### 4. **Unified Dashboard**
- All metrics in one view
- Quick actions for common tasks
- Real-time updates

## 🚨 Troubleshooting

### PostgreSQL Connection from Local
```bash
# Option 1: Use mobile hotspot
# Option 2: Use VPN
# Option 3: Deploy to App Service
# Option 4: Use SQLite locally
```

### Missing Packages
```bash
pip install -r requirements.txt
pip install azure-storage-blob openai
```

### Environment Variables
- Check `.env` file exists
- Verify all Azure credentials are set
- Restart app after changes

## 📞 Next Steps

1. **Get the app running locally** with SQLite
2. **Test AI features** with OpenAI
3. **Upload test files** to Blob Storage
4. **Deploy to App Service** when ready

Everything is configured and ready to use! The PostgreSQL connection issue is only affecting your local machine - the App Service can connect fine.

Would you like to:
1. Start the app locally with SQLite?
2. Deploy directly to App Service?
3. Test specific features?