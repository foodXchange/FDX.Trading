#!/usr/bin/env python3
"""
Setup Supabase connection for FoodXchange
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("""
=================================
Supabase Setup for FoodXchange
=================================

To connect to Supabase, you need to update your .env file with one of these options:

OPTION 1: Supabase Cloud (Recommended)
--------------------------------------
1. Go to your Supabase project dashboard
2. Settings > Database
3. Copy the connection string and update .env:

DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT].supabase.co:5432/postgres

OPTION 2: Local Supabase
------------------------
1. Start Docker Desktop
2. Run: supabase start
3. Get the connection info: supabase status
4. Update .env with local connection:

DATABASE_URL=postgresql://postgres:postgres@localhost:54322/postgres

Current DATABASE_URL in .env:
{}

""".format(os.getenv("DATABASE_URL", "Not set")))

# Check if it's a Supabase URL
db_url = os.getenv("DATABASE_URL", "")
if "supabase.co" in db_url:
    print("✓ Detected Supabase Cloud URL")
elif "localhost:54322" in db_url:
    print("✓ Detected Local Supabase URL")
elif "localhost:5432" in db_url:
    print("⚠ Detected standard PostgreSQL (not Supabase)")
    print("  Update to use Supabase cloud or local instance")
else:
    print("❌ No valid database URL detected")

print("\nOnce you've updated the DATABASE_URL, run:")
print("  python cleanup_database.py")
print("\nThis will remove all tables except AI-related ones.")