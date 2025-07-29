# FoodXchange AI - Quick Start Guide

## What You Need (15 minutes total)

### 1. Database (5 min)
**Easiest: Supabase Free Tier**
- Sign up at https://supabase.com
- Create project
- Copy connection string from Settings > Database

### 2. Azure Keys (10 min)
Log into Azure Portal and get these 3 keys:

**Computer Vision:**
- Resource: `foodxchange-vision`
- Location: Keys and Endpoint
- Copy: KEY 1

**OpenAI:**
- Resource: `foodxchange-openai` 
- Location: Keys and Endpoint
- Copy: KEY 1 + Endpoint URL

**Storage:**
- Resource: `foodxchangeproducts`
- Location: Access keys
- Copy: Connection string

### 3. Create .env file
```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[PROJECT].supabase.co:5432/postgres
SECRET_KEY=any-random-32-character-string-here
AZURE_COMPUTER_VISION_KEY=your-vision-key
AZURE_OPENAI_KEY=your-openai-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_STORAGE_CONNECTION_STRING=your-storage-connection-string
```

### 4. Run
```bash
pip install -r foodxchange/requirements.txt
python start.py
```

### 5. Test
Open: http://localhost:8001/product-analysis

That's it! 🎉