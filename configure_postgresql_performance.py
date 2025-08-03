#!/usr/bin/env python3
"""
PostgreSQL Performance Configuration Script
Configures Query Performance Insights and monitoring settings for Azure Database for PostgreSQL
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create database connection"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not found in environment variables")
            return None
        
        connection = psycopg2.connect(database_url)
        return connection
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def configure_query_store():
    """Configure Query Store settings"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Enable Query Store capture mode
        print("🔧 Configuring Query Store capture mode...")
        cursor.execute("ALTER SYSTEM SET pg_qs.query_capture_mode = 'ALL';")
        
        # Enable Wait Sampling
        print("🔧 Configuring Wait Sampling...")
        cursor.execute("ALTER SYSTEM SET pgms_wait_sampling.query_capture_mode = 'ALL';")
        
        # Enable IO timing tracking
        print("🔧 Enabling IO timing tracking...")
        cursor.execute("ALTER SYSTEM SET track_io_timing = 'on';")
        
        # Reload configuration
        print("🔄 Reloading PostgreSQL configuration...")
        cursor.execute("SELECT pg_reload_conf();")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ PostgreSQL performance monitoring configured successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error configuring PostgreSQL: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def verify_configuration():
    """Verify the configuration settings"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        print("\n📊 Current Configuration Status:")
        print("=" * 50)
        
        # Check Query Store capture mode
        cursor.execute("SHOW pg_qs.query_capture_mode;")
        result = cursor.fetchone()
        print(f"Query Store Capture Mode: {result[0] if result else 'Not set'}")
        
        # Check Wait Sampling
        cursor.execute("SHOW pgms_wait_sampling.query_capture_mode;")
        result = cursor.fetchone()
        print(f"Wait Sampling Capture Mode: {result[0] if result else 'Not set'}")
        
        # Check IO timing
        cursor.execute("SHOW track_io_timing;")
        result = cursor.fetchone()
        print(f"IO Timing Tracking: {result[0] if result else 'Not set'}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying configuration: {e}")
        if conn:
            conn.close()
        return False

def main():
    """Main function to configure PostgreSQL performance monitoring"""
    print("🚀 PostgreSQL Performance Configuration Tool")
    print("=" * 50)
    
    # Check if we can connect to the database
    print("🔍 Testing database connection...")
    if not get_db_connection():
        print("❌ Cannot connect to database. Please check your DATABASE_URL.")
        return
    
    print("✅ Database connection successful!")
    
    # Configure performance settings
    if configure_query_store():
        print("\n🔍 Verifying configuration...")
        verify_configuration()
        
        print("\n📋 Next Steps:")
        print("1. Wait 5-10 minutes for Query Store to start collecting data")
        print("2. Access Query Performance Insights in Azure Portal")
        print("3. Monitor query performance and identify optimization opportunities")
        
        print("\n🔗 Useful Links:")
        print("- Query Store Guide: https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-query-store")
        print("- Performance Tuning: https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-query-performance-insight")
    else:
        print("❌ Failed to configure PostgreSQL performance monitoring")

if __name__ == "__main__":
    main() 