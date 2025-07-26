#!/usr/bin/env python3
"""
Export Data from Azure PostgreSQL for Supabase Import
This script exports data in a format compatible with Supabase.
"""

import os
import sys
from sqlalchemy import create_engine, text
import json
from datetime import datetime

# Azure connection details
AZURE_DATABASE_URL = "postgresql://pgadmin:Ud30078123@foodxchangepgfr.postgres.database.azure.com:5432/foodxchange_db?sslmode=require"

def connect_to_azure():
    """Connect to Azure PostgreSQL"""
    try:
        engine = create_engine(AZURE_DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to Azure PostgreSQL: {version[:50]}...")
            return engine
    except Exception as e:
        print(f"❌ Failed to connect to Azure: {str(e)}")
        return None

def get_table_data(engine, table_name):
    """Get all data from a table"""
    try:
        with engine.connect() as conn:
            # Get column information
            result = conn.execute(text(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """))
            columns = [row[0] for row in result]
            
            # Get data
            result = conn.execute(text(f"SELECT * FROM {table_name}"))
            rows = result.fetchall()
            
            return columns, rows
    except Exception as e:
        print(f"❌ Error getting data from {table_name}: {str(e)}")
        return None, None

def format_value_for_sql(value, data_type):
    """Format a value for SQL INSERT statement"""
    if value is None:
        return "NULL"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    elif isinstance(value, datetime):
        return f"'{value.isoformat()}'"
    elif isinstance(value, (dict, list)):
        # Handle JSON data
        return f"'{json.dumps(value)}'"
    else:
        # String values - escape single quotes
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"

def generate_insert_statements(table_name, columns, rows):
    """Generate INSERT statements for a table"""
    if not rows:
        return []
    
    statements = []
    
    # Generate INSERT statements in batches
    batch_size = 100
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        
        # Start INSERT statement
        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES\n"
        
        # Add values
        value_rows = []
        for row in batch:
            values = [format_value_for_sql(val, 'text') for val in row]
            value_rows.append(f"({', '.join(values)})")
        
        insert_sql += ",\n".join(value_rows) + ";"
        statements.append(insert_sql)
    
    return statements

def export_all_data():
    """Export all data from Azure PostgreSQL"""
    print("🚀 Exporting data from Azure PostgreSQL...")
    print("=" * 50)
    
    # Connect to Azure
    engine = connect_to_azure()
    if not engine:
        return False
    
    # List of tables to export (in order to handle foreign keys)
    tables = [
        'users',
        'companies', 
        'suppliers',
        'rfqs',
        'quotes',
        'orders',
        'products'
    ]
    
    all_statements = []
    
    # Add header comment
    all_statements.append("-- FoodXchange Data Export for Supabase")
    all_statements.append(f"-- Generated on: {datetime.now().isoformat()}")
    all_statements.append("-- This file contains INSERT statements for all tables")
    all_statements.append("")
    
    # Export each table
    for table_name in tables:
        print(f"📤 Exporting {table_name}...")
        
        columns, rows = get_table_data(engine, table_name)
        if columns and rows:
            print(f"   Found {len(rows)} rows")
            
            # Add table comment
            all_statements.append(f"-- Table: {table_name}")
            all_statements.append(f"-- Rows: {len(rows)}")
            
            # Generate INSERT statements
            insert_statements = generate_insert_statements(table_name, columns, rows)
            all_statements.extend(insert_statements)
            all_statements.append("")
        else:
            print(f"   ⚠️ No data found or error occurred")
    
    # Write to file
    try:
        with open('foodxchange_data_supabase.sql', 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_statements))
        
        print(f"✅ Data exported successfully to foodxchange_data_supabase.sql")
        print(f"📊 Total statements generated: {len([s for s in all_statements if s.startswith('INSERT')])}")
        return True
        
    except Exception as e:
        print(f"❌ Error writing file: {str(e)}")
        return False

def create_sample_data():
    """Create sample data if no existing data"""
    print("📝 Creating sample data for testing...")
    
    sample_data = """
-- Sample Data for FoodXchange
-- This creates test data if your database is empty

-- Sample Users
INSERT INTO users (name, email, hashed_password, company, role, is_active, is_admin) VALUES
('Admin User', 'admin@foodxchange.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', 'FoodXchange Inc', 'admin', true, true),
('John Buyer', 'john@buyer.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', 'Buyer Corp', 'buyer', true, false),
('Sarah Supplier', 'sarah@supplier.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', 'Supplier Co', 'supplier', true, false);

-- Sample Companies
INSERT INTO companies (name, legal_name, registration_number, company_type, email, phone, country, is_active) VALUES
('FoodXchange Inc', 'FoodXchange Incorporated', 'FX001', 'buyer', 'info@foodxchange.com', '+1-555-0123', 'USA', true),
('Buyer Corp', 'Buyer Corporation', 'BC001', 'buyer', 'info@buyercorp.com', '+1-555-0124', 'USA', true),
('Supplier Co', 'Supplier Company', 'SC001', 'supplier', 'info@supplierco.com', '+1-555-0125', 'Canada', true);

-- Sample Suppliers
INSERT INTO suppliers (name, email, phone, address, country, products, status, rating) VALUES
('Fresh Foods Ltd', 'info@freshfoods.com', '+1-555-0201', '123 Fresh Street, Toronto', 'Canada', 'Fresh vegetables, fruits', 'active', 4.5),
('Quality Meats Inc', 'sales@qualitymeats.com', '+1-555-0202', '456 Meat Avenue, Chicago', 'USA', 'Beef, pork, chicken', 'active', 4.2),
('Organic Dairy Co', 'contact@organicdairy.com', '+1-555-0203', '789 Dairy Road, Wisconsin', 'USA', 'Milk, cheese, yogurt', 'active', 4.8);

-- Sample RFQs
INSERT INTO rfqs (title, description, company_id, status, deadline, budget) VALUES
('Fresh Vegetables Supply', 'Need fresh vegetables for restaurant chain', (SELECT id FROM companies WHERE name = 'Buyer Corp' LIMIT 1), 'active', '2024-02-15', 5000.00),
('Meat Supply Contract', 'Looking for quality meat supplier for 6 months', (SELECT id FROM companies WHERE name = 'FoodXchange Inc' LIMIT 1), 'draft', '2024-03-01', 15000.00);

-- Sample Quotes
INSERT INTO quotes (rfq_id, supplier_id, amount, currency, valid_until, status) VALUES
((SELECT id FROM rfqs WHERE title = 'Fresh Vegetables Supply' LIMIT 1), (SELECT id FROM suppliers WHERE name = 'Fresh Foods Ltd' LIMIT 1), 4800.00, 'USD', '2024-02-10', 'pending'),
((SELECT id FROM rfqs WHERE title = 'Meat Supply Contract' LIMIT 1), (SELECT id FROM suppliers WHERE name = 'Quality Meats Inc' LIMIT 1), 14500.00, 'USD', '2024-02-25', 'pending');

-- Sample Products
INSERT INTO products (name, description, category, unit, price, currency, supplier_id, is_active) VALUES
('Organic Tomatoes', 'Fresh organic tomatoes', 'Vegetables', 'kg', 3.50, 'USD', (SELECT id FROM suppliers WHERE name = 'Fresh Foods Ltd' LIMIT 1), true),
('Premium Beef', 'High-quality beef cuts', 'Meat', 'kg', 12.00, 'USD', (SELECT id FROM suppliers WHERE name = 'Quality Meats Inc' LIMIT 1), true),
('Organic Milk', 'Fresh organic whole milk', 'Dairy', 'liter', 2.50, 'USD', (SELECT id FROM suppliers WHERE name = 'Organic Dairy Co' LIMIT 1), true);
"""
    
    try:
        with open('sample_data_supabase.sql', 'w', encoding='utf-8') as f:
            f.write(sample_data)
        print("✅ Sample data created in sample_data_supabase.sql")
        return True
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 FoodXchange Data Export for Supabase")
    print("=" * 50)
    
    # Try to export existing data
    if export_all_data():
        print("\n✅ Data export completed successfully!")
        print("📁 File: foodxchange_data_supabase.sql")
    else:
        print("\n⚠️ Could not export existing data. Creating sample data instead...")
        create_sample_data()
        print("📁 File: sample_data_supabase.sql")
    
    print("\n📋 Next steps:")
    print("1. Go to Supabase Dashboard → SQL Editor")
    print("2. Copy and paste the content of the .sql file")
    print("3. Click 'Run' to import the data")
    print("4. Check Table Editor to verify the data was imported")

if __name__ == "__main__":
    main() 