"""
Seed script to create default admin user
Run this after database is initialized
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from app.models import Base, User
from app.auth import get_password_hash

def seed_admin():
    """Create default admin user"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == "admin@foodxchange.com").first()
        if admin:
            print("Admin user already exists")
            return
        
        # Create admin user
        admin = User(
            name="Admin User",
            email="admin@foodxchange.com",
            hashed_password=get_password_hash("admin123"),  # Change this password!
            company="FoodXchange",
            is_active=True,
            is_admin=True
        )
        
        db.add(admin)
        db.commit()
        print("✅ Admin user created successfully!")
        print("Email: admin@foodxchange.com")
        print("Password: admin123 (PLEASE CHANGE THIS!)")
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()