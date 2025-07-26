"""
Start FoodXchange with a fresh database
"""
import os
import sys

# Delete existing database if it exists
db_path = "foodxchange.db"
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    except Exception as e:
        print(f"Could not remove database (it may be in use): {e}")
        print("Creating new database with timestamp...")
        import time
        db_path = f"foodxchange_{int(time.time())}.db"
        os.environ["DATABASE_URL"] = f"sqlite:///./{db_path}"

# Run the startup script
print("Starting FoodXchange application...")
os.system(f"{sys.executable} azure_startup.py")