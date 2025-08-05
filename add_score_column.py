from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

try:
    # Check if score column exists
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'suppliers' AND column_name = 'score'
    """)
    
    score_exists = cursor.fetchone()
    print(f"Score column exists: {bool(score_exists)}")
    
    if not score_exists:
        print("Adding score column...")
        cursor.execute("ALTER TABLE suppliers ADD COLUMN score INTEGER DEFAULT 0")
        conn.commit()
        print("✅ Score column added successfully")
    else:
        print("Score column already exists")
        
    # Show current columns
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'suppliers' 
        ORDER BY ordinal_position
    """)
    columns = [row[0] for row in cursor.fetchall()]
    print(f"Current suppliers columns: {columns}")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()