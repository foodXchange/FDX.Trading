#!/usr/bin/env python3
"""
FoodXchange Migration to Supabase
This script helps migrate your data from Azure PostgreSQL to Supabase.
"""

import os
import sys
import subprocess
from sqlalchemy import create_engine, text
import json

def export_from_azure():
    """Export data from Azure PostgreSQL"""
    print("📤 Exporting data from Azure PostgreSQL...")
    
    # Azure connection details
    azure_host = "foodxchangepgfr.postgres.database.azure.com"
    azure_user = "pgadmin"
    azure_password = "Ud30078123"
    azure_db = "foodxchange_db"
    
    # Export command
    export_cmd = f'pg_dump -h {azure_host} -U {azure_user} -d {azure_db} --no-password --data-only --column-inserts > foodxchange_data.sql'
    
    try:
        # Set password environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = azure_password
        
        # Run export
        result = subprocess.run(export_cmd, shell=True, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Data exported successfully to foodxchange_data.sql")
            return True
        else:
            print(f"❌ Export failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Export error: {str(e)}")
        return False

def create_supabase_schema():
    """Create the database schema for Supabase"""
    print("🏗️ Creating Supabase schema...")
    
    schema_sql = """
-- FoodXchange Database Schema for Supabase

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    company VARCHAR(200),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    legal_name VARCHAR(200),
    registration_number VARCHAR(100) UNIQUE,
    company_type VARCHAR(8) NOT NULL,
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(20),
    website VARCHAR(255),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) NOT NULL,
    company_size VARCHAR(10),
    year_established INTEGER,
    annual_revenue VARCHAR(50),
    description TEXT,
    industry VARCHAR(100),
    categories JSONB,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    verification_date TIMESTAMP WITH TIME ZONE,
    verification_documents JSONB,
    rating INTEGER,
    total_reviews INTEGER DEFAULT 0,
    payment_terms VARCHAR(100),
    credit_limit INTEGER,
    currency VARCHAR(3) DEFAULT 'USD',
    certifications JSONB,
    preferred_payment_methods JSONB,
    delivery_preferences JSONB,
    communication_preferences JSONB,
    external_id VARCHAR(100),
    integration_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Suppliers table
CREATE TABLE IF NOT EXISTS suppliers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(120),
    phone VARCHAR(20),
    address TEXT,
    country VARCHAR(100),
    products TEXT,
    certifications TEXT,
    status VARCHAR(50) DEFAULT 'active',
    rating FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RFQs table
CREATE TABLE IF NOT EXISTS rfqs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    company_id UUID REFERENCES companies(id),
    status VARCHAR(50) DEFAULT 'draft',
    deadline DATE,
    budget DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quotes table
CREATE TABLE IF NOT EXISTS quotes (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    rfq_id UUID REFERENCES rfqs(id),
    supplier_id UUID REFERENCES suppliers(id),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    valid_until DATE,
    status VARCHAR(50) DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    quote_id UUID REFERENCES quotes(id),
    company_id UUID REFERENCES companies(id),
    supplier_id UUID REFERENCES suppliers(id),
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) DEFAULT 'pending',
    order_date DATE DEFAULT CURRENT_DATE,
    expected_delivery DATE,
    actual_delivery DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    unit VARCHAR(50),
    price DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    supplier_id UUID REFERENCES suppliers(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
CREATE INDEX IF NOT EXISTS idx_suppliers_name ON suppliers(name);
CREATE INDEX IF NOT EXISTS idx_rfqs_company_id ON rfqs(company_id);
CREATE INDEX IF NOT EXISTS idx_quotes_rfq_id ON quotes(rfq_id);
CREATE INDEX IF NOT EXISTS idx_orders_company_id ON orders(company_id);
CREATE INDEX IF NOT EXISTS idx_products_supplier_id ON products(supplier_id);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE rfqs ENABLE ROW LEVEL SECURITY;
ALTER TABLE quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
"""
    
    try:
        with open('supabase_schema.sql', 'w') as f:
            f.write(schema_sql)
        print("✅ Schema created in supabase_schema.sql")
        return True
    except Exception as e:
        print(f"❌ Schema creation failed: {str(e)}")
        return False

def get_supabase_credentials():
    """Get Supabase credentials from user"""
    print("\n🔑 Supabase Credentials Setup")
    print("=" * 40)
    
    print("Please provide your Supabase credentials:")
    print("(You can find these in your Supabase project dashboard → Settings → API)")
    
    project_url = input("Project URL (e.g., https://your-project.supabase.co): ").strip()
    anon_key = input("Anon Key: ").strip()
    service_role_key = input("Service Role Key: ").strip()
    db_password = input("Database Password: ").strip()
    
    # Extract project ID from URL
    project_id = project_url.replace('https://', '').replace('.supabase.co', '')
    
    credentials = {
        'project_url': project_url,
        'project_id': project_id,
        'anon_key': anon_key,
        'service_role_key': service_role_key,
        'db_password': db_password
    }
    
    # Save credentials to file
    with open('supabase_credentials.json', 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print("✅ Credentials saved to supabase_credentials.json")
    return credentials

def create_env_file(credentials):
    """Create .env file with Supabase credentials"""
    print("📝 Creating .env file...")
    
    env_content = f"""# Supabase Configuration
DATABASE_URL=postgresql://postgres:{credentials['db_password']}@db.{credentials['project_id']}.supabase.co:5432/postgres
SUPABASE_URL={credentials['project_url']}
SUPABASE_ANON_KEY={credentials['anon_key']}
SUPABASE_SERVICE_ROLE_KEY={credentials['service_role_key']}

# Application Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# Email Configuration (optional)
EMAILS_ENABLED=false

# OpenAI Configuration (optional)
OPENAI_API_KEY=your-openai-api-key-here

# Storage Configuration (optional)
AZURE_STORAGE_ENABLED=false
"""
    
    try:
        with open('.env.supabase', 'w') as f:
            f.write(env_content)
        print("✅ .env.supabase file created")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {str(e)}")
        return False

def main():
    """Main migration function"""
    print("🚀 FoodXchange Migration to Supabase")
    print("=" * 50)
    
    # Step 1: Get Supabase credentials
    credentials = get_supabase_credentials()
    
    # Step 2: Create schema
    if not create_supabase_schema():
        return
    
    # Step 3: Export data from Azure
    if not export_from_azure():
        print("⚠️ Skipping data export - you can do this manually with pgAdmin")
    
    # Step 4: Create environment file
    if not create_env_file(credentials):
        return
    
    print("\n🎉 Migration setup complete!")
    print("\nNext steps:")
    print("1. Go to your Supabase dashboard → SQL Editor")
    print("2. Run the contents of 'supabase_schema.sql'")
    print("3. Import your data using 'foodxchange_data.sql' (if exported)")
    print("4. Copy .env.supabase to .env")
    print("5. Test your application: python start_local.py")
    print("\n📚 See supabase_migration_guide.md for detailed instructions")

if __name__ == "__main__":
    main() 