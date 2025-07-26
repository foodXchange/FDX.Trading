# 🚀 FoodXchange Migration to Supabase Guide

## Step 1: Create Supabase Account

1. **Go to**: https://supabase.com
2. **Click "Start your project"**
3. **Sign up** with your GitHub account
4. **Create new organization** (if prompted)
5. **Create new project**:
   - Name: `foodxchange`
   - Database Password: Choose a strong password (save it!)
   - Region: Choose closest to you (Europe for better performance)

## Step 2: Get Your Supabase Credentials

Once your project is created:

1. **Go to Settings** → **API**
2. **Copy these details**:
   - Project URL: `https://your-project-id.supabase.co`
   - Anon Key: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - Service Role Key: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## Step 3: Export Data from Azure PostgreSQL

### Option A: Using pgAdmin (Recommended)
1. **Open pgAdmin** and connect to your Azure database
2. **Right-click** on `foodxchange_db` → **Backup**
3. **Format**: Custom
4. **Filename**: `foodxchange_backup.backup`
5. **Click "Backup"**

### Option B: Using Command Line
```bash
# Install pg_dump if not already installed
# Then run:
pg_dump -h foodxchangepgfr.postgres.database.azure.com -U pgadmin -d foodxchange_db -f foodxchange_backup.sql
```

## Step 4: Import Data to Supabase

### Using Supabase Dashboard:
1. **Go to** Supabase Dashboard → **SQL Editor**
2. **Upload** your backup file or paste SQL
3. **Click "Run"**

### Using Command Line:
```bash
# Connect to Supabase and import
psql "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-ID].supabase.co:5432/postgres" -f foodxchange_backup.sql
```

## Step 5: Update Your Application

### Update Environment Variables:
```env
# Replace your Azure DATABASE_URL with:
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-ID].supabase.co:5432/postgres

# Add Supabase specific variables:
SUPABASE_URL=https://[YOUR-PROJECT-ID].supabase.co
SUPABASE_ANON_KEY=[YOUR-ANON-KEY]
SUPABASE_SERVICE_ROLE_KEY=[YOUR-SERVICE-ROLE-KEY]
```

## Step 6: Test Your Application

1. **Update** your `.env` file with Supabase credentials
2. **Run**: `python start_local.py`
3. **Test** all features work correctly

## Step 7: Explore Supabase Features

### Database Management:
- **Table Editor**: Visual table management
- **SQL Editor**: Run queries with syntax highlighting
- **API**: Auto-generated REST API
- **Real-time**: Live data subscriptions

### Authentication:
- **Built-in auth** with multiple providers
- **User management** dashboard
- **Row Level Security** (RLS)

### Storage:
- **File uploads** and management
- **CDN** for fast file delivery

## Benefits of Supabase:

✅ **Better Web Interface** - Much easier than pgAdmin
✅ **Real-time Features** - Live updates for your app
✅ **Built-in Auth** - User authentication ready
✅ **File Storage** - Upload and manage files
✅ **API Generation** - Auto-generated REST API
✅ **Better Documentation** - Clear guides and examples
✅ **Free Tier** - 500MB database, 50K monthly users

## Troubleshooting:

### Connection Issues:
- Check your Supabase credentials
- Verify the database password
- Ensure your IP is not blocked

### Import Issues:
- Check SQL syntax in your backup
- Verify all dependencies are imported
- Test with a small subset first

## Next Steps:

1. **Complete the migration**
2. **Test all features**
3. **Update your deployment scripts**
4. **Consider using Supabase Auth** for user management
5. **Explore real-time features** for live updates

## Cost Comparison:

| Service | Free Tier | Paid Plans |
|---------|-----------|------------|
| **Azure PostgreSQL** | None | ~$25-50/month |
| **Supabase** | 500MB, 50K users | $25/month for 8GB |

Supabase is much more cost-effective for development and small to medium applications! 