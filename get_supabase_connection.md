# 🔧 Getting Your Supabase Connection String

## Step 1: Go to Supabase Dashboard
1. Open: https://supabase.com/dashboard
2. Sign in to your account
3. Select your project: `hlugyivdpcwzivhvgjii`

## Step 2: Get Database Connection String
1. Click on **"Settings"** in the left sidebar
2. Click on **"Database"** 
3. Scroll down to **"Connection string"** section
4. Look for **"URI"** or **"Connection string"**

## Step 3: Copy the Connection String
You should see something like:
```
postgresql://postgres:[YOUR-PASSWORD]@[PROJECT-REF].supabase.co:5432/postgres
```

## Step 4: Update Your Startup Script
Replace the DATABASE_URL in `start_optimized.py` with your actual connection string.

## Alternative: Check Project Status
1. Go to **"Overview"** in your Supabase dashboard
2. Make sure your project is **"Active"** (not paused)
3. If paused, click **"Resume"** to activate it

## Common Issues:
- **Project paused**: Resume the project in dashboard
- **Wrong password**: Check the password in your credentials
- **Network issues**: Try from a different network

## Quick Test:
Once you have the correct connection string, test it with:
```bash
python test_supabase_connection.py
```

## Need Help?
If you can't find the connection string, please:
1. Take a screenshot of your Supabase Settings → Database page
2. Or share the exact error message you're getting 