"""
Setup projects table in PostgreSQL
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def create_projects_table():
    """Create projects and project_suppliers tables"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # Create projects table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                project_name VARCHAR(255) NOT NULL,
                description TEXT,
                user_email VARCHAR(255) DEFAULT 'udi@fdx.trading',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create project_suppliers table (many-to-many relationship)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS project_suppliers (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                supplier_id INTEGER,
                supplier_name VARCHAR(255),
                supplier_country VARCHAR(100),
                supplier_email VARCHAR(255),
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_project_suppliers_project 
            ON project_suppliers(project_id)
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_projects_user 
            ON projects(user_email)
        """)
        
        conn.commit()
        print("Projects tables created successfully")
        
        # Check structure
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'projects'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("\nProjects table structure:")
        for col in columns:
            print(f"  {col[0]}: {col[1]}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_projects_table()