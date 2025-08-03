"""
Setup search history table in PostgreSQL
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def create_search_history_table():
    """Create search history table if it doesn't exist"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # Create search history table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                query TEXT NOT NULL,
                filters JSONB,
                results_count INTEGER,
                search_time FLOAT,
                user_email VARCHAR(255) DEFAULT 'udi@fdx.trading',
                selected_suppliers JSONB,
                query_hash VARCHAR(32)
            )
        """)
        
        # Create indexes for better performance
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_search_history_timestamp 
            ON search_history(timestamp DESC)
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_search_history_user 
            ON search_history(user_email)
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_search_history_query 
            ON search_history(LOWER(query))
        """)
        
        conn.commit()
        print("Search history table created successfully")
        
        # Check if table was created
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'search_history'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("\nTable structure:")
        for col in columns:
            print(f"  {col[0]}: {col[1]}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        # Try to check if table already exists
        try:
            conn = psycopg2.connect(os.getenv('DATABASE_URL'))
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM search_history")
            count = cur.fetchone()[0]
            print(f"Search history table already exists with {count} records")
            cur.close()
            conn.close()
        except:
            pass

if __name__ == "__main__":
    create_search_history_table()