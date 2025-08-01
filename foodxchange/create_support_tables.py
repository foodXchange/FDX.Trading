"""
Database Migration Script for Support System
Creates all necessary tables for the support system
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from foodxchange.database import DATABASE_URL, engine
from foodxchange.models.support import (
    SupportTicket, TicketStatusHistory, TicketResponse, ErrorLog,
    SupportAnalytics, UserFeedback, Base
)
from foodxchange.models.user import User

def create_support_tables():
    """Create all support system tables"""
    try:
        print("Creating support system tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Support system tables created successfully!")
        
        # Verify tables were created
        with engine.connect() as conn:
            # Check if tables exist
            tables_to_check = [
                'support_tickets',
                'ticket_status_history', 
                'ticket_responses',
                'error_logs',
                'support_analytics',
                'user_feedback'
            ]
            
            for table in tables_to_check:
                result = conn.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
                if result.fetchone():
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' not found")
        
        print("\n🎉 Support system database setup complete!")
        
    except Exception as e:
        print(f"❌ Error creating support tables: {e}")
        raise

def create_sample_data():
    """Create sample data for testing"""
    try:
        print("\nCreating sample data...")
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Create sample support ticket
        from foodxchange.services.support_service import support_service
        from foodxchange.models.support import TicketCategory, TicketPriority
        
        # Check if we have any users
        user_count = db.query(User).count()
        if user_count == 0:
            print("⚠️ No users found in database. Creating sample user...")
            # Create a sample user
            sample_user = User(
                name="Sample User",
                email="sample@foodxchange.com",
                hashed_password="hashed_password_here",
                company="Sample Company",
                role="buyer",
                is_active=True
            )
            db.add(sample_user)
            db.commit()
            db.refresh(sample_user)
            user_id = sample_user.id
        else:
            user_id = db.query(User).first().id
        
        # Create sample ticket
        sample_ticket = support_service.create_ticket(
            db=db,
            user_id=user_id,
            title="Sample Support Ticket",
            description="This is a sample support ticket for testing the support system.",
            category=TicketCategory.GENERAL_INQUIRY,
            priority=TicketPriority.MEDIUM,
            steps_to_reproduce="This is a sample ticket for testing purposes.",
            expected_behavior="System should work normally.",
            actual_behavior="Sample ticket created successfully."
        )
        
        # Create sample error log
        from foodxchange.models.support import ErrorSeverity
        
        sample_error = support_service.log_error(
            db=db,
            error_id="SAMPLE-ERR-001",
            error_type="SampleError",
            error_message="This is a sample error for testing purposes.",
            user_id=user_id,
            severity=ErrorSeverity.MEDIUM,
            category=TicketCategory.SYSTEM_ERROR,
            url_path="/sample/path",
            http_method="GET",
            status_code=500
        )
        
        # Create sample user feedback
        sample_feedback = support_service.create_user_feedback(
            db=db,
            feedback_type="feature_request",
            title="Sample Feature Request",
            description="This is a sample feature request for testing the support system.",
            user_id=user_id,
            category=TicketCategory.FEATURE_REQUEST,
            priority=TicketPriority.LOW
        )
        
        db.close()
        
        print("✅ Sample data created successfully!")
        print(f"   - Sample ticket: {sample_ticket.ticket_id}")
        print(f"   - Sample error: {sample_error.error_id}")
        print(f"   - Sample feedback: {sample_feedback.id}")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        raise

def main():
    """Main function to run the migration"""
    print("🚀 FoodXchange Support System Database Setup")
    print("=" * 50)
    
    try:
        # Create tables
        create_support_tables()
        
        # Create sample data
        create_sample_data()
        
        print("\n" + "=" * 50)
        print("🎉 Support system setup completed successfully!")
        print("\nNext steps:")
        print("1. Start your FastAPI application")
        print("2. Visit /support to access the support admin dashboard")
        print("3. Visit /api/support/center to access the user support center")
        print("4. Test the support system functionality")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 