#!/usr/bin/env python3
"""Database Health Check Script for FoodXchange"""

import psycopg2
from psycopg2 import sql
import json
from datetime import datetime
import sys
import os

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'foodxchange'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password')
    )

def check_connection():
    """Test database connection"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return True, "Connection successful"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def get_database_size():
    """Get database size"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT pg_size_pretty(pg_database_size(current_database())) as size
        """)
        size = cur.fetchone()[0]
        cur.close()
        conn.close()
        return size
    except Exception as e:
        return f"Error: {str(e)}"

def get_table_stats():
    """Get table statistics"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                n_live_tup as row_count
            FROM pg_stat_user_tables 
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """)
        tables = cur.fetchall()
        cur.close()
        conn.close()
        return tables
    except Exception as e:
        return f"Error: {str(e)}"

def get_connection_count():
    """Get active connection count"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT count(*) 
            FROM pg_stat_activity 
            WHERE datname = current_database()
        """)
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count
    except Exception as e:
        return f"Error: {str(e)}"

def get_slow_queries():
    """Get slow running queries"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                pid,
                now() - pg_stat_activity.query_start AS duration,
                query,
                state
            FROM pg_stat_activity
            WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
            AND state != 'idle'
            ORDER BY duration DESC
        """)
        queries = cur.fetchall()
        cur.close()
        conn.close()
        return queries
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Run health check"""
    print("=" * 60)
    print("FoodXchange Database Health Check")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check connection
    connected, msg = check_connection()
    print(f"\n1. Connection Status: {'✓' if connected else '✗'} {msg}")
    
    if not connected:
        print("\nCannot proceed with other checks. Please fix connection issues.")
        sys.exit(1)
    
    # Database size
    print(f"\n2. Database Size: {get_database_size()}")
    
    # Connection count
    print(f"\n3. Active Connections: {get_connection_count()}")
    
    # Table statistics
    print("\n4. Table Statistics:")
    tables = get_table_stats()
    if isinstance(tables, str):
        print(f"   {tables}")
    else:
        print(f"   {'Schema':<10} {'Table':<30} {'Size':<15} {'Rows':<10}")
        print("   " + "-" * 65)
        for schema, table, size, rows in tables:
            print(f"   {schema:<10} {table:<30} {size:<15} {rows:<10}")
    
    # Slow queries
    print("\n5. Slow Queries (> 5 minutes):")
    queries = get_slow_queries()
    if isinstance(queries, str):
        print(f"   {queries}")
    elif not queries:
        print("   No slow queries found ✓")
    else:
        for pid, duration, query, state in queries:
            print(f"   PID: {pid}, Duration: {duration}, State: {state}")
            print(f"   Query: {query[:100]}...")
    
    print("\n" + "=" * 60)
    print("Health check complete!")

if __name__ == "__main__":
    main()