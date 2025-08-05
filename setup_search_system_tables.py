"""
Setup tables for AI Search System with History Tracking
======================================================
"""

import psycopg2
import os
from dotenv import load_dotenv
import sys

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def create_search_tables():
    """Create tables for search history and saved searches"""
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    try:
        # 1. Search History Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id SERIAL PRIMARY KEY,
                user_email VARCHAR(255),
                search_query TEXT NOT NULL,
                search_type VARCHAR(50) DEFAULT 'product',
                filters JSONB,
                result_count INTEGER,
                clicked_results JSONB,
                search_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id VARCHAR(100),
                ip_address VARCHAR(50),
                execution_time_ms INTEGER,
                -- Analytics fields
                relevance_feedback JSONB,
                converted_to_project BOOLEAN DEFAULT FALSE,
                project_id INTEGER REFERENCES projects(id)
            )
        """)
        
        # 2. Saved Searches Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS saved_searches (
                id SERIAL PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                search_name VARCHAR(255) NOT NULL,
                search_query TEXT NOT NULL,
                filters JSONB,
                alert_enabled BOOLEAN DEFAULT FALSE,
                alert_frequency VARCHAR(50), -- 'daily', 'weekly', 'monthly'
                last_alert_sent TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                tags TEXT[],
                notes TEXT
            )
        """)
        
        # 3. Search Results Cache
        cur.execute("""
            CREATE TABLE IF NOT EXISTS search_results_cache (
                id SERIAL PRIMARY KEY,
                search_hash VARCHAR(64) UNIQUE NOT NULL,
                search_query TEXT NOT NULL,
                filters JSONB,
                results JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                hit_count INTEGER DEFAULT 0
            )
        """)
        
        # 4. Popular Searches Analytics
        cur.execute("""
            CREATE TABLE IF NOT EXISTS popular_searches (
                id SERIAL PRIMARY KEY,
                search_term VARCHAR(255) NOT NULL,
                category VARCHAR(100),
                search_count INTEGER DEFAULT 1,
                last_searched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trending_score FLOAT DEFAULT 0,
                week_number INTEGER,
                year INTEGER,
                UNIQUE(search_term, week_number, year)
            )
        """)
        
        # 5. Search Suggestions
        cur.execute("""
            CREATE TABLE IF NOT EXISTS search_suggestions (
                id SERIAL PRIMARY KEY,
                original_term VARCHAR(255) NOT NULL,
                suggested_term VARCHAR(255) NOT NULL,
                suggestion_type VARCHAR(50), -- 'spelling', 'related', 'category'
                confidence_score FLOAT,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 6. User Search Preferences
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_search_preferences (
                id SERIAL PRIMARY KEY,
                user_email VARCHAR(255) UNIQUE NOT NULL,
                preferred_countries TEXT[],
                preferred_categories TEXT[],
                excluded_terms TEXT[],
                default_filters JSONB,
                results_per_page INTEGER DEFAULT 50,
                sort_preference VARCHAR(50) DEFAULT 'relevance',
                language_preference VARCHAR(10) DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        print("📇 Creating indexes...")
        
        # Search history indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_search_history_user ON search_history(user_email)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_search_history_timestamp ON search_history(timestamp DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_search_history_query ON search_history USING gin(to_tsvector('english', query))")
        
        # Saved searches indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_saved_searches_user ON saved_searches(user_email)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_saved_searches_active ON saved_searches(is_active)")
        
        # Cache indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cache_hash ON search_results_cache(search_hash)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON search_results_cache(expires_at)")
        
        # Popular searches indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_popular_term ON popular_searches(search_term)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_popular_trending ON popular_searches(trending_score DESC)")
        
        conn.commit()
        print("✅ All search system tables created successfully!")
        
        # Show table summary
        cur.execute("""
            SELECT table_name, 
                   pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_tables 
            WHERE tablename IN ('search_history', 'saved_searches', 'search_results_cache', 
                               'popular_searches', 'search_suggestions', 'user_search_preferences')
            ORDER BY tablename
        """)
        
        tables = cur.fetchall()
        print("\n📊 Search System Tables:")
        for table in tables:
            print(f"   - {table[0]}: {table[1]}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        conn.rollback()
        raise
        
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    print("🔍 Setting up AI Search System Tables\n")
    create_search_tables()
    print("\n✅ Setup complete! Search system ready for use.")