#!/usr/bin/env python3
"""
Setup Machine Learning Database Tables for FDX.trading
Creates tables needed for pattern learning and AI suggestions
"""

import psycopg2
import os
import json
from dotenv import load_dotenv

load_dotenv()

def create_ml_tables():
    """Create all ML-related database tables"""
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    
    # User interactions table for tracking behavior patterns
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_interactions (
            id SERIAL PRIMARY KEY,
            user_email VARCHAR(255) NOT NULL,
            action_type VARCHAR(100) NOT NULL,
            context_data JSONB,
            success_indicator BOOLEAN,
            time_spent INTEGER,
            session_id VARCHAR(255),
            interaction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # AI suggestions table for storing generated recommendations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_suggestions (
            id SERIAL PRIMARY KEY,
            suggestion_type VARCHAR(100) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            action_data JSONB,
            priority_score INTEGER DEFAULT 50,
            is_active BOOLEAN DEFAULT true,
            shown_count INTEGER DEFAULT 0,
            clicked_count INTEGER DEFAULT 0,
            dismissed_count INTEGER DEFAULT 0,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for better performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_interactions_user_email 
        ON user_interactions(user_email)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_interactions_action_type 
        ON user_interactions(action_type)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_interactions_timestamp 
        ON user_interactions(interaction_timestamp)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ai_suggestions_active 
        ON ai_suggestions(is_active, priority_score DESC)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ai_suggestions_type 
        ON ai_suggestions(suggestion_type)
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("ML database tables created successfully:")
    print("  - user_interactions (for tracking user behavior)")
    print("  - ai_suggestions (for storing AI recommendations)")
    print("  - Created performance indexes")

def add_sample_interactions():
    """Add some sample interaction data for testing"""
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    
    sample_interactions = [
        ('supplier_search', {'query': 'sunflower oil', 'country': 'Italy', 'results_count': 15}, True, 90),
        ('supplier_search', {'query': 'organic spices', 'country': 'India', 'results_count': 22}, True, 120),
        ('email_sent', {'email_type': 'inquiry', 'recipient_count': 1}, True, 30),
        ('email_sent', {'email_type': 'follow_up', 'recipient_count': 3}, True, 45),
        ('project_created', {'project_name': 'Mediterranean Oils', 'initial_suppliers': 8}, True, 180),
        ('bulk_email_sent', {'recipient_count': 12, 'template_type': 'inquiry'}, True, 300),
        ('email_analyzed', {'response_count': 5, 'positive_responses': 3}, True, 60)
    ]
    
    user_email = 'udi@fdx.trading'
    
    for action_type, context_data, success, time_spent in sample_interactions:
        cursor.execute("""
            INSERT INTO user_interactions 
            (user_email, action_type, context_data, success_indicator, time_spent)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_email, action_type, json.dumps(context_data), success, time_spent))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Added sample interaction data for ML learning")

if __name__ == "__main__":
    try:
        create_ml_tables()
        add_sample_interactions()
        print("\nML database setup completed successfully!")
        print("Ready for pattern analysis and AI suggestions.")
        
    except Exception as e:
        print(f"Error setting up ML tables: {e}")