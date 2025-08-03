# Database connection module
# This file handles all database connections

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

def get_db_connection():
    """
    Create and return a database connection
    Uses DATABASE_URL from .env file
    """
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        
        # Create connection with RealDictCursor for dict-like results
        connection = psycopg2.connect(
            database_url,
            cursor_factory=RealDictCursor  # Returns rows as dictionaries
        )
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def get_suppliers():
    """
    Fetch all suppliers from the database
    Returns list of supplier dictionaries
    """
    try:
        # Get database connection
        conn = get_db_connection()
        if not conn:
            return []
        
        # Create cursor
        cursor = conn.cursor()
        
        # SQL query to get ALL columns from suppliers table
        query = """
        SELECT 
            id,
            supplier_name,
            company_name,
            company_email,
            company_website,
            supplier_type,
            address,
            country,
            products,
            created_at
        FROM suppliers
        ORDER BY supplier_name
        LIMIT 1000
        """
        
        # Execute query
        cursor.execute(query)
        
        # Fetch all results
        suppliers = cursor.fetchall()
        
        # Close connections
        cursor.close()
        conn.close()
        
        return suppliers
        
    except Exception as e:
        print(f"Error fetching suppliers: {e}")
        return []