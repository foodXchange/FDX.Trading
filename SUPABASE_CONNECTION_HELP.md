# Supabase Connection Options

Since we can't reset the password via CLI, here are your options:

## Option 1: Use Supabase Management API (Requires Login)

Try this simplified direct link:
https://app.supabase.com/project/hlugyivdpcwzihvhgjji/settings/database

If that doesn't work, try:
1. Go to https://app.supabase.com
2. Login with your account
3. Your project should appear
4. Click Settings → Database

## Option 2: Use a Local Database Instead (Temporary)

For now, you can use a local PostgreSQL database:

1. **Install PostgreSQL locally**:
   - Download from: https://www.postgresql.org/download/windows/
   - Use default settings
   - Set password as: `localpass123`

2. **Update .env**:
   ```env
   DATABASE_URL=postgresql://postgres:localpass123@localhost:5432/foodxchange
   ```

3. **Create database**:
   ```bash
   psql -U postgres -c "CREATE DATABASE foodxchange;"
   ```

## Option 3: Create a New Supabase Project

If you can't access the old project:

1. Go to https://supabase.com
2. Create new project
3. Set a password you'll remember
4. Update the connection string

## Option 4: Use Supabase Client Library

Instead of direct database connection, use Supabase client:

```python
from supabase import create_client

# These we already have:
url = "https://hlugyivdpcwzihvhgjji.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhsdWd5aXZkcGN3emlodmhnamppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM1MDkxMTIsImV4cCI6MjA2OTA4NTExMn0._UEtBBPKcR9CIWzKaeUp_uvhxN3S9-4PTgB2BUtZLPY"

supabase = create_client(url, key)
```

## Most Common Issue:

The Supabase dashboard URL structure changed. Try these variations:
- https://app.supabase.com/project/hlugyivdpcwzihvhgjji
- https://supabase.com/dashboard/project/hlugyivdpcwzihvhgjji
- https://app.supabase.io/project/hlugyivdpcwzihvhgjji

One of these should work!