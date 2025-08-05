#!/usr/bin/env python3
"""
Setup email_log table for bulk email functionality
"""

import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def setup_email_log_table():
    """Create email_log table for tracking sent emails"""
    try:
        # Connect to database
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        # Create email_log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_log (
                id SERIAL PRIMARY KEY,
                supplier_id INTEGER,
                supplier_email VARCHAR(255) NOT NULL,
                supplier_name VARCHAR(255),
                project_id INTEGER,
                email_subject VARCHAR(500),
                email_content TEXT,
                sent_at TIMESTAMP DEFAULT NOW(),
                status VARCHAR(50) DEFAULT 'sent',
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create index for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_email_log_supplier_email 
            ON email_log(supplier_email)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_email_log_project_id 
            ON email_log(project_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_email_log_sent_at 
            ON email_log(sent_at)
        """)
        
        conn.commit()
        print("Email log table created successfully!")
        
        # Show table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'email_log'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("\nEmail log table structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error creating email log table: {e}")

if __name__ == "__main__":
    setup_email_log_table()