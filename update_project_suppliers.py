"""
Add score column to project_suppliers table
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def update_project_suppliers_table():
    """Add score column to project_suppliers table"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # Add score column if it doesn't exist
        cur.execute("""
            ALTER TABLE project_suppliers 
            ADD COLUMN IF NOT EXISTS score INTEGER DEFAULT 0
        """)
        
        # Add products column to store product info
        cur.execute("""
            ALTER TABLE project_suppliers 
            ADD COLUMN IF NOT EXISTS products TEXT
        """)
        
        conn.commit()
        print("Updated project_suppliers table with score and products columns")
        
        # Check structure
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'project_suppliers'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("\nproject_suppliers table structure:")
        for col in columns:
            print(f"  {col[0]}: {col[1]}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_project_suppliers_table()