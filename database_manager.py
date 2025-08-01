"""
FoodXchange Database Manager
Consolidated database management utility
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv, set_key
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database management utility class"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///./foodxchange.db')
        self.engine = self._create_engine()
    
    def _create_engine(self):
        """Create database engine with appropriate settings"""
        if self.database_url.startswith('sqlite'):
            return create_engine(self.database_url, connect_args={"check_same_thread": False})
        else:
            return create_engine(self.database_url)
    
    def setup_postgresql(self):
        """Interactive PostgreSQL setup"""
        print("\n" + "=" * 60)
        print("PostgreSQL Configuration")
        print("=" * 60)
        
        if 'postgresql' in self.database_url:
            print(f"\n✅ Already using PostgreSQL: {self.database_url}")
            update = input("Update configuration? (y/n): ")
            if update.lower() != 'y':
                return
        
        # Get connection details
        print("\nEnter PostgreSQL connection details:")
        db_host = input("Host (e.g., localhost): ").strip()
        db_port = input("Port (default: 5432): ").strip() or "5432"
        db_name = input("Database (default: foodxchange): ").strip() or "foodxchange"
        db_user = input("Username: ").strip()
        db_password = input("Password: ").strip()
        
        # SSL for production
        use_ssl = input("Use SSL? (y/n): ").lower() == 'y'
        ssl_mode = "?sslmode=require" if use_ssl else ""
        
        # Construct URL
        new_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}{ssl_mode}"
        
        # Test connection
        print("\nTesting connection...")
        try:
            test_engine = create_engine(new_url)
            with test_engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.scalar()
                print(f"✅ Connected successfully!")
                print(f"   PostgreSQL {version}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return
        
        # Save configuration
        if input("\nSave to .env? (y/n): ").lower() == 'y':
            set_key('.env', 'DATABASE_URL', new_url)
            set_key('.env', 'DB_HOST', db_host)
            set_key('.env', 'DB_PORT', db_port)
            set_key('.env', 'DB_NAME', db_name)
            set_key('.env', 'DB_USER', db_user)
            set_key('.env', 'DB_PASSWORD', db_password)
            print("✅ Configuration saved!")
            self.database_url = new_url
            self.engine = self._create_engine()
    
    def list_tables(self):
        """List all tables in the database"""
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        
        print(f"\nTables in database ({len(tables)}):")
        for table in sorted(tables):
            print(f"  • {table}")
        
        return tables
    
    def create_tables(self):
        """Create all tables from models"""
        print("\nCreating database tables...")
        
        try:
            # Import Base and all models
            from foodxchange.database import Base
            from foodxchange.models import (
                User, Buyer, Supplier, 
                FileUpload, ImportRecord,
                SupportTicket
            )
            from foodxchange.models.project_enhanced import Project
            
            # Create all tables
            Base.metadata.create_all(self.engine)
            print("✅ All tables created successfully!")
            
            # List created tables
            self.list_tables()
            
        except Exception as e:
            logger.error(f"❌ Error creating tables: {e}")
            import traceback
            traceback.print_exc()
    
    def drop_tables(self, table_names=None):
        """Drop specified tables or all tables"""
        if table_names is None:
            # Drop all tables
            confirm = input("\n⚠️  Drop ALL tables? Type 'DELETE ALL': ")
            if confirm != 'DELETE ALL':
                print("Cancelled.")
                return
            
            from foodxchange.database import Base
            Base.metadata.drop_all(self.engine)
            print("✅ All tables dropped!")
        else:
            # Drop specific tables
            for table in table_names:
                try:
                    with self.engine.begin() as conn:
                        conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    print(f"✅ Dropped table: {table}")
                except Exception as e:
                    print(f"❌ Error dropping {table}: {e}")
    
    def migrate_to_enhanced_projects(self):
        """Migrate from old project model to enhanced model"""
        print("\n" + "=" * 60)
        print("Project Model Migration")
        print("=" * 60)
        
        # Check current tables
        tables = self.list_tables()
        
        if 'project' in tables:
            print("\n⚠️  Old 'project' table found!")
            if input("Drop old table and create enhanced tables? (y/n): ").lower() == 'y':
                self.drop_tables(['project'])
        
        # Create new tables
        self.create_tables()
        print("\n✅ Migration complete!")
    
    def run_interactive(self):
        """Run interactive database manager"""
        while True:
            print("\n" + "=" * 60)
            print("FoodXchange Database Manager")
            print("=" * 60)
            print(f"Current DB: {'PostgreSQL' if 'postgresql' in self.database_url else 'SQLite'}")
            
            print("\nOptions:")
            print("1. Setup PostgreSQL")
            print("2. List tables")
            print("3. Create all tables")
            print("4. Migrate to enhanced projects")
            print("5. Drop specific tables")
            print("6. Drop ALL tables")
            print("7. Exit")
            
            choice = input("\nSelect (1-7): ")
            
            if choice == '1':
                self.setup_postgresql()
            elif choice == '2':
                self.list_tables()
            elif choice == '3':
                self.create_tables()
            elif choice == '4':
                self.migrate_to_enhanced_projects()
            elif choice == '5':
                tables = self.list_tables()
                if tables:
                    table_list = input("\nTables to drop (comma-separated): ").strip()
                    if table_list:
                        self.drop_tables(table_list.split(','))
            elif choice == '6':
                self.drop_tables()
            elif choice == '7':
                print("\nGoodbye!")
                break
            else:
                print("Invalid option!")


def main():
    """Main entry point"""
    manager = DatabaseManager()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'setup':
            manager.setup_postgresql()
        elif command == 'list':
            manager.list_tables()
        elif command == 'create':
            manager.create_tables()
        elif command == 'migrate':
            manager.migrate_to_enhanced_projects()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: setup, list, create, migrate")
    else:
        # Run interactive mode
        manager.run_interactive()


if __name__ == "__main__":
    main()