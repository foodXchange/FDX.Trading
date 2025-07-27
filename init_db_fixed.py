#!/usr/bin/env python
"""
Initialize FoodXchange database with tables and default data (Fixed Version)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from app.models import Base, User, Supplier, Product, Company, CompanyType
from app.auth import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with tables and seed data"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully!")
    
    db = SessionLocal()
    try:
        # Check if we already have data
        user_count = db.query(User).count()
        if user_count > 0:
            logger.info(f"Database already has {user_count} users. Skipping seed data.")
            return
        
        # Create companies first
        logger.info("Creating companies...")
        
        # FoodXchange company (for admin)
        foodxchange_company = Company(
            name="FoodXchange",
            legal_name="FoodXchange Inc.",
            email="admin@foodxchange.com",
            phone="+1-555-123-4567",
            website="https://foodxchange.com",
            address_line1="123 Food Street",
            city="Food City",
            country="United States",
            company_type=CompanyType.BOTH,
            is_verified=True,
            is_active=True
        )
        db.add(foodxchange_company)
        
        # Demo company
        demo_company = Company(
            name="Demo Company Ltd",
            legal_name="Demo Company Limited",
            email="demo@democompany.com",
            phone="+1-555-987-6543",
            website="https://democompany.com",
            address_line1="456 Demo Avenue",
            city="Demo City",
            country="United States",
            company_type=CompanyType.BUYER,
            is_verified=True,
            is_active=True
        )
        db.add(demo_company)
        
        # Commit companies to get their IDs
        db.commit()
        
        # Create admin user
        logger.info("Creating admin user...")
        admin = User(
            name="Admin User",
            email="admin@foodxchange.com",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_active=True,
            is_admin=True,
            company_id=foodxchange_company.id
        )
        db.add(admin)
        
        # Create demo user
        demo_user = User(
            name="Demo User",
            email="demo@foodxchange.com",
            hashed_password=get_password_hash("demo123"),
            role="buyer",
            is_active=True,
            is_admin=False,
            company_id=demo_company.id
        )
        db.add(demo_user)
        
        # Create demo suppliers
        suppliers_data = [
            {
                "name": "Mediterranean Delights",
                "email": "contact@meddelights.com",
                "phone": "+30-210-1234567",
                "address": "123 Olive Street, Athens, Greece",
                "country": "Greece",
                "specialties": ["Olive Oil", "Feta Cheese", "Olives"],
                "certifications": ["Organic", "ISO 22000"],
                "status": "active"
            },
            {
                "name": "Italian Fine Foods",
                "email": "info@italianfinefoods.it",
                "phone": "+39-02-12345678",
                "address": "456 Via Roma, Milan, Italy",
                "country": "Italy",
                "specialties": ["Pasta", "Tomatoes", "Cheese"],
                "certifications": ["DOP", "IGP"],
                "status": "active"
            },
            {
                "name": "Spanish Imports Co",
                "email": "sales@spanishimports.es",
                "phone": "+34-91-1234567",
                "address": "789 Calle Mayor, Madrid, Spain",
                "country": "Spain",
                "specialties": ["Jamón", "Manchego", "Olive Oil"],
                "certifications": ["PDO", "Organic"],
                "status": "pending"
            }
        ]
        
        for supplier_data in suppliers_data:
            supplier = Supplier(**supplier_data)
            db.add(supplier)
        
        # Commit all changes
        db.commit()
        logger.info("✅ Database initialized successfully!")
        logger.info("\n=== Default Users Created ===")
        logger.info("Admin: admin@foodxchange.com / admin123")
        logger.info("Demo: demo@foodxchange.com / demo123")
        logger.info("PLEASE CHANGE THESE PASSWORDS IN PRODUCTION!")
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database() 