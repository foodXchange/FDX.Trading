#!/usr/bin/env python3
"""
Setup email response system tables for AI-powered supplier email analysis
"""

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def setup_email_response_tables():
    """Create tables for AI-powered email response system"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        # 1. Email responses table - stores raw emails and AI analysis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_responses (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id),
                supplier_id INTEGER,
                supplier_email VARCHAR(255) NOT NULL,
                supplier_name VARCHAR(255),
                subject VARCHAR(500),
                raw_content TEXT NOT NULL,
                ai_analysis JSONB,
                interest_level VARCHAR(50), -- 'interested', 'not_interested', 'need_info', 'unclear'
                priority_score INTEGER DEFAULT 0, -- 0-100 priority score
                processed_at TIMESTAMP DEFAULT NOW(),
                received_at TIMESTAMP DEFAULT NOW(),
                status VARCHAR(50) DEFAULT 'new', -- 'new', 'analyzed', 'responded', 'archived'
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # 2. Supplier analysis table - structured data extracted from emails
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS supplier_analysis (
                id SERIAL PRIMARY KEY,
                supplier_id INTEGER,
                project_id INTEGER REFERENCES projects(id),
                email_response_id INTEGER REFERENCES email_responses(id),
                pricing_info JSONB, -- pricing structure, MOQ, etc.
                capacity_info JSONB, -- production capacity, lead times
                certifications TEXT[], -- array of certifications
                product_details JSONB, -- specific product information
                contact_info JSONB, -- additional contact details
                quality_indicators JSONB, -- company size, experience, etc.
                ai_summary TEXT, -- human-readable summary
                confidence_score DECIMAL(3,2), -- AI confidence in analysis
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # 3. Supplier tasks table - automated task generation
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS supplier_tasks (
                id SERIAL PRIMARY KEY,
                supplier_id INTEGER,
                project_id INTEGER REFERENCES projects(id),
                email_response_id INTEGER REFERENCES email_responses(id),
                task_type VARCHAR(100) NOT NULL, -- 'follow_up', 'request_samples', 'negotiate', 'schedule_call'
                title VARCHAR(500) NOT NULL,
                description TEXT,
                priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
                status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'cancelled'
                due_date TIMESTAMP,
                assigned_to VARCHAR(255) DEFAULT 'udi@fdx.trading',
                ai_generated BOOLEAN DEFAULT true,
                metadata JSONB, -- additional task-specific data
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_email_responses_project_id 
            ON email_responses(project_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_email_responses_supplier_email 
            ON email_responses(supplier_email)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_email_responses_status 
            ON email_responses(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_supplier_analysis_project_id 
            ON supplier_analysis(project_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_supplier_tasks_project_id 
            ON supplier_tasks(project_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_supplier_tasks_status 
            ON supplier_tasks(status)
        """)
        
        conn.commit()
        print("Email response system tables created successfully!")
        
        # Show table structures
        tables = ['email_responses', 'supplier_analysis', 'supplier_tasks']
        for table in tables:
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = '{table}'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print(f"\n{table.upper()} table structure:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error creating email response tables: {e}")

if __name__ == "__main__":
    setup_email_response_tables()