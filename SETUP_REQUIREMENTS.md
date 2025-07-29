# FoodXchange AI Product Sourcing - Setup Requirements

## 1. Database Setup (PostgreSQL)

### Option A: Supabase Cloud (Recommended - Free Tier Available)
1. Go to https://supabase.com and create a free account
2. Create a new project (takes ~2 minutes)
3. Once created, go to Settings > Database
4. Copy the connection string and add to `.env`:
```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT].supabase.co:5432/postgres
```

### Option B: Local PostgreSQL
1. Install PostgreSQL: https://www.postgresql.org/download/
2. Create database:
```bash
createdb foodxchange
```
3. Update `.env`:
```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@localhost:5432/foodxchange
```

## 2. Azure AI Services Keys

### Required Services:

#### A. Computer Vision (for image analysis)
1. Go to Azure Portal: https://portal.azure.com
2. Use existing: `foodxchange-vision` in `foodxchange-ai-rg`
3. Go to "Keys and Endpoint"
4. Copy Key 1 and add to `.env`:
```env
AZURE_COMPUTER_VISION_KEY=your-key-here
AZURE_COMPUTER_VISION_ENDPOINT=https://eastus.api.cognitive.microsoft.com/
```

#### B. OpenAI (for product descriptions)
1. In Azure Portal, find one of:
   - `foodxchange-openai` (Sweden Central)
   - `foodxchangeopenai` (France Central)
2. Go to "Keys and Endpoint"
3. Copy and add to `.env`:
```env
AZURE_OPENAI_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

#### C. Storage Account (for images)
1. Use: `foodxchangeproducts` in `foodxchange-ai-rg`
2. Go to "Access keys"
3. Copy connection string and add to `.env`:
```env
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=foodxchangeproducts;AccountKey=your-key;EndpointSuffix=core.windows.net
```

## 3. Complete .env File Template

Create/update your `.env` file with all required values:

```env
# Database (Choose one option from above)
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/[DATABASE]

# Authentication
SECRET_KEY=your-secret-key-min-32-chars-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Azure AI Services
AZURE_COMPUTER_VISION_ENDPOINT=https://eastus.api.cognitive.microsoft.com/
AZURE_COMPUTER_VISION_KEY=get-from-azure-portal

AZURE_OPENAI_ENDPOINT=get-from-azure-portal
AZURE_OPENAI_KEY=get-from-azure-portal
AZURE_OPENAI_DEPLOYMENT=gpt-4

AZURE_STORAGE_CONNECTION_STRING=get-from-azure-portal

# Optional
SENTRY_DSN=
ENVIRONMENT=development
```

## 4. Quick Start Commands

Once you have all the keys:

```bash
# 1. Install dependencies
pip install -r foodxchange/requirements.txt

# 2. Create database tables
python -c "from foodxchange.database import engine, Base; Base.metadata.create_all(bind=engine)"

# 3. Run the application
python start.py
```

## 5. Test the Setup

1. Open browser: http://localhost:8001
2. Go to: http://localhost:8001/product-analysis
3. Try uploading a product image or searching for "Organic dried cranberries"

## 6. Troubleshooting

### Database Connection Issues
- Check DATABASE_URL format
- Ensure PostgreSQL is running
- Verify password is correct

### Azure AI Issues
- Verify keys are copied correctly (no extra spaces)
- Check service is not suspended in Azure Portal
- Ensure correct endpoint URLs

### Port Issues
- If port 8001 is busy, edit `start.py` to use different port

## Need Help?

1. Database setup issues: Check PostgreSQL logs
2. Azure issues: Check Azure Portal > Activity Log
3. Application errors: Check console output

## Estimated Time
- Database setup: 5 minutes
- Getting Azure keys: 10 minutes
- Total setup: 15 minutes