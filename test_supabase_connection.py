#!/usr/bin/env python3
"""
Test Supabase Connection
Tests the correct connection string for the user's Supabase database
"""

import psycopg2

# Try different connection string formats
connection_strings = [
    "postgresql://postgres:Ud30078123@db.hlugyivdpcwzivhvgjii.supabase.co:5432/postgres?sslmode=require",
    "postgresql://postgres:Ud30078123@hlugyivdpcwzivhvgjii.supabase.co:5432/postgres?sslmode=require",
    "postgresql://postgres:Ud30078123@aws-0-us-east-1.pooler.supabase.com:5432/postgres.hlugyivdpcwzivhvgjii?sslmode=require"
]

print("🔍 Testing Supabase connection strings...")
print("=" * 50)

for i, conn_str in enumerate(connection_strings, 1):
    print(f"\n🧪 Test {i}: {conn_str}")
    try:
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ SUCCESS! Connected to PostgreSQL: {version[0]}")
        conn.close()
        
        # Test if tables exist
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
        tables = cursor.fetchall()
        print(f"📋 Tables found: {len(tables)}")
        if tables:
            print(f"   Tables: {[t[0] for t in tables]}")
        conn.close()
        
        print(f"\n🎉 Use this connection string:")
        print(f"   {conn_str}")
        break
        
    except Exception as e:
        print(f"❌ Failed: {str(e)[:100]}...")

print("\n" + "=" * 50) 