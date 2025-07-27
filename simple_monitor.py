#!/usr/bin/env python3
"""
Simple FoodXchange System Monitor
Basic monitoring without complex dependencies
"""

import os
import sys
import time
import platform
import subprocess
from datetime import datetime

def get_system_info():
    """Get basic system information"""
    print("=" * 50)
    print("FOODXCHANGE SIMPLE SYSTEM MONITOR")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: {platform.platform()}")
    print(f"Python: {sys.version}")
    print()

def check_database():
    """Check database connection"""
    print("🗄️  DATABASE CHECK:")
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("   ❌ DATABASE_URL not found in environment")
        return False
    
    print(f"   📋 Database URL: {database_url[:50]}...")
    
    try:
        # Simple test - try to import and create engine
        from sqlalchemy import create_engine, text
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test, NOW() as timestamp"))
            row = result.fetchone()
            print(f"   ✅ Database: CONNECTED")
            print(f"   📅 Server Time: {row.timestamp}")
            return True
            
    except Exception as e:
        print(f"   ❌ Database: CONNECTION FAILED")
        print(f"   🔍 Error: {str(e)[:100]}...")
        return False

def check_azure_services():
    """Check Azure services"""
    print("\n☁️  AZURE SERVICES:")
    
    # Check OpenAI
    openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    openai_key = os.getenv('AZURE_OPENAI_API_KEY')
    
    if openai_endpoint and openai_key:
        print("   ✅ Azure OpenAI: CONFIGURED")
        print(f"   📍 Endpoint: {openai_endpoint}")
    else:
        print("   ⚠️  Azure OpenAI: NOT CONFIGURED")
    
    # Check Storage
    storage_conn = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if storage_conn:
        print("   ✅ Azure Storage: CONFIGURED")
    else:
        print("   ⚠️  Azure Storage: NOT CONFIGURED")
    
    # Check if using Azure PostgreSQL
    database_url = os.getenv('DATABASE_URL', '')
    if 'azure.com' in database_url:
        print("   ✅ Azure PostgreSQL: CONFIGURED")
    else:
        print("   ℹ️  Azure PostgreSQL: NOT USED")

def check_application():
    """Check if application is running"""
    print("\n🌐 APPLICATION:")
    
    try:
        import requests
        base_url = os.getenv('APP_BASE_URL', 'http://localhost:8000')
        
        # Test health endpoint
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ Health Endpoint: ONLINE ({response.status_code})")
            else:
                print(f"   ⚠️  Health Endpoint: RESPONDING ({response.status_code})")
        except:
            print(f"   ❌ Health Endpoint: OFFLINE")
        
        # Test API endpoint
        try:
            response = requests.get(f"{base_url}/api/v1/status", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ API Endpoint: ONLINE ({response.status_code})")
            else:
                print(f"   ⚠️  API Endpoint: RESPONDING ({response.status_code})")
        except:
            print(f"   ❌ API Endpoint: OFFLINE")
            
    except ImportError:
        print("   ℹ️  Requests library not available - skipping HTTP checks")
    except Exception as e:
        print(f"   ❌ Application Check Failed: {str(e)[:50]}...")

def check_system_resources():
    """Check system resources"""
    print("\n💻 SYSTEM RESOURCES:")
    
    try:
        import psutil
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"   🖥️  CPU Usage: {cpu_percent}%")
        
        # Memory
        memory = psutil.virtual_memory()
        print(f"   🧠 Memory Usage: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)")
        
        # Disk
        disk = psutil.disk_usage('/')
        print(f"   💾 Disk Usage: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)")
        
        # Network
        network = psutil.net_if_addrs()
        active_interfaces = len([iface for iface in network.keys() if network[iface]])
        print(f"   🌐 Network Interfaces: {active_interfaces} active")
        
    except ImportError:
        print("   ℹ️  psutil not available - skipping resource checks")
    except Exception as e:
        print(f"   ❌ Resource Check Failed: {str(e)[:50]}...")

def check_environment():
    """Check environment variables"""
    print("\n🔧 ENVIRONMENT:")
    
    important_vars = [
        'DATABASE_URL',
        'SECRET_KEY', 
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_API_KEY',
        'AZURE_STORAGE_CONNECTION_STRING',
        'SMTP_HOST',
        'SMTP_USER'
    ]
    
    for var in important_vars:
        value = os.getenv(var)
        if value:
            # Show first few characters for security
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ⚠️  {var}: NOT SET")

def main():
    """Main monitoring function"""
    try:
        get_system_info()
        
        # Run all checks
        db_ok = check_database()
        check_azure_services()
        check_application()
        check_system_resources()
        check_environment()
        
        # Summary
        print("\n" + "=" * 50)
        print("SUMMARY:")
        if db_ok:
            print("✅ System appears to be configured and running")
        else:
            print("⚠️  System has some configuration issues")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring interrupted by user")
    except Exception as e:
        print(f"\n❌ Monitoring failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 