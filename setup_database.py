#!/usr/bin/env python3
"""
Database Setup Script for FoodXchange

This script:
1. Creates the database if it doesn't exist
2. Runs Alembic migrations
3. Creates initial admin user
4. Seeds with sample data
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.database import engine, get_db
from app.models import User, Supplier, RFQ, Quote, Email
from app.config import get_settings
from sqlalchemy import text
import bcrypt
from datetime import datetime, timedelta
import random

def create_database():
    """Create the database if it doesn't exist"""
    settings = get_settings()
    
    # Extract database name from URL
    db_name = settings.database_url.split('/')[-1]
    base_url = '/'.join(settings.database_url.split('/')[:-1])
    
    # Connect to postgres database to create our database
    engine_postgres = engine_from_config(
        {"sqlalchemy.url": f"{base_url}/postgres"},
        prefix="sqlalchemy."
    )
    
    with engine_postgres.connect() as conn:
        # Check if database exists
        result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
        if not result.fetchone():
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"✅ Created database: {db_name}")
        else:
            print(f"✅ Database already exists: {db_name}")
    
    engine_postgres.dispose()

def run_migrations():
    """Run Alembic migrations"""
    try:
        import subprocess
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        if result.returncode == 0:
            print("✅ Migrations completed successfully")
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False
    return True

def create_admin_user():
    """Create initial admin user"""
    settings = get_settings()
    
    # Hash password
    password = "admin123"  # Change this in production
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    admin_user = User(
        email="admin@foodxchange.com",
        hashed_password=hashed_password,
        full_name="System Administrator",
        role="admin",
        department="IT",
        is_active=True
    )
    
    with next(get_db()) as db:
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.email == admin_user.email).first()
        if not existing_user:
            db.add(admin_user)
            db.commit()
            print("✅ Created admin user: admin@foodxchange.com / admin123")
        else:
            print("✅ Admin user already exists")

def seed_sample_data():
    """Seed database with sample data"""
    with next(get_db()) as db:
        # Create sample suppliers
        suppliers_data = [
            {
                "company_name": "Mediterranean Delights Ltd",
                "email": "info@meddelights.com",
                "phone": "+30 210 1234567",
                "website": "https://meddelights.com",
                "address": "123 Olive Street, Athens, Greece",
                "city": "Athens",
                "country": "Greece",
                "categories": ["Olive Oil", "Cheese", "Olives"],
                "status": "active",
                "rating": 4.5,
                "response_rate": 92,
                "average_response_time": 2.5,
                "is_verified": True
            },
            {
                "company_name": "Italian Fine Foods Co",
                "email": "sales@italianfinefoods.it",
                "phone": "+39 06 1234567",
                "website": "https://italianfinefoods.it",
                "address": "456 Pasta Avenue, Rome, Italy",
                "city": "Rome",
                "country": "Italy",
                "categories": ["Pasta", "Tomatoes", "Mozzarella"],
                "status": "active",
                "rating": 4.3,
                "response_rate": 87,
                "average_response_time": 3.2,
                "is_verified": True
            },
            {
                "company_name": "Spanish Imports Ltd",
                "email": "contact@spanishimports.es",
                "phone": "+34 91 1234567",
                "website": "https://spanishimports.es",
                "address": "789 Jamón Street, Madrid, Spain",
                "city": "Madrid",
                "country": "Spain",
                "categories": ["Jamón", "Manchego", "Saffron"],
                "status": "pending",
                "rating": 4.1,
                "response_rate": 78,
                "average_response_time": 4.1,
                "is_verified": False
            }
        ]
        
        for supplier_data in suppliers_data:
            existing = db.query(Supplier).filter(
                Supplier.company_name == supplier_data["company_name"]
            ).first()
            if not existing:
                supplier = Supplier(**supplier_data)
                db.add(supplier)
        
        # Create sample RFQs
        rfqs_data = [
            {
                "rfq_number": "RFQ-2024-001",
                "buyer_id": 1,  # Admin user
                "customer_name": "FoodXchange Demo",
                "product_name": "Extra Virgin Olive Oil",
                "category": "Olive Oil",
                "quantity": "1000",
                "unit_of_measure": "Liters",
                "specifications": "Cold-pressed, organic, acidity < 0.8%",
                "requirements": "ISO 22000 certified, sustainable packaging",
                "delivery_date": datetime.now() + timedelta(days=30),
                "delivery_location": "London, UK",
                "budget_min": 5000.00,
                "budget_max": 8000.00,
                "currency": "EUR",
                "status": "receiving_quotes",
                "sent_date": datetime.now() - timedelta(days=5)
            },
            {
                "rfq_number": "RFQ-2024-002",
                "buyer_id": 1,
                "customer_name": "FoodXchange Demo",
                "product_name": "Aged Parmesan Cheese",
                "category": "Cheese",
                "quantity": "500",
                "unit_of_measure": "kg",
                "specifications": "24-month aged, DOP certified",
                "requirements": "HACCP certified, vacuum packed",
                "delivery_date": datetime.now() + timedelta(days=45),
                "delivery_location": "Manchester, UK",
                "budget_min": 15000.00,
                "budget_max": 25000.00,
                "currency": "EUR",
                "status": "draft"
            }
        ]
        
        for rfq_data in rfqs_data:
            existing = db.query(RFQ).filter(
                RFQ.rfq_number == rfq_data["rfq_number"]
            ).first()
            if not existing:
                rfq = RFQ(**rfq_data)
                db.add(rfq)
        
        db.commit()
        print("✅ Seeded sample data (suppliers and RFQs)")

def main():
    """Main setup function"""
    print("🚀 Starting FoodXchange Database Setup...")
    
    # Step 1: Create database
    print("\n📦 Step 1: Creating database...")
    create_database()
    
    # Step 2: Run migrations
    print("\n🔄 Step 2: Running migrations...")
    if not run_migrations():
        print("❌ Setup failed at migration step")
        return
    
    # Step 3: Create admin user
    print("\n👤 Step 3: Creating admin user...")
    create_admin_user()
    
    # Step 4: Seed sample data
    print("\n🌱 Step 4: Seeding sample data...")
    seed_sample_data()
    
    print("\n🎉 Database setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update your .env file with the correct database credentials")
    print("2. Start your FastAPI application: uvicorn app.main:app --reload")
    print("3. Access the admin panel at: http://localhost:8000/admin")
    print("4. Login with: admin@foodxchange.com / admin123")

if __name__ == "__main__":
    main() 