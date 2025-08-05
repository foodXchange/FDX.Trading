"""
AI-Powered Search System with History and Project Management
==========================================================
Features:
- AI-enhanced search across entire database
- Shows top 50 matches with scoring
- Checkbox selection for adding to projects
- Search history tracking
- Save searches for later use
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import hashlib
import json
import sys
from typing import List, Dict, Any, Optional

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

class AISearchSystem:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        
    def get_db_connection(self):
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
    
    def ai_search_suppliers(self, query: str, user_email: str = None, 
                           filters: Dict[str, Any] = None, limit: int = 50) -> Dict[str, Any]:
        """
        Advanced AI search with intelligent scoring and ranking
        Returns top 50 matches with detailed scoring breakdown
        """
        
        start_time = datetime.now()
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        # Parse search query intelligently
        search_terms = query.lower().split()
        primary_terms = [term for term in search_terms if len(term) > 3]
        
        # Build comprehensive scoring query
        query_sql = """
            WITH supplier_scores AS (
                SELECT 
                    s.*,
                    -- AI Relevance Scoring Components
                    (
                        -- 1. Direct product match (40 points max)
                        CASE 
                            WHEN LOWER(products) LIKE %s THEN 40
                            WHEN LOWER(products) LIKE %s THEN 30
                            ELSE 0
                        END +
                        
                        -- 2. Individual term matching (30 points max)
                        %s +
                        
                        -- 3. Supplier name relevance (15 points max)
                        CASE 
                            WHEN LOWER(supplier_name) LIKE %s THEN 15
                            WHEN LOWER(company_name) LIKE %s THEN 10
                            ELSE 0
                        END +
                        
                        -- 4. Certification bonuses (10 points max)
                        CASE 
                            WHEN LOWER(products) LIKE '%%organic%%' THEN 3
                            ELSE 0
                        END +
                        CASE 
                            WHEN LOWER(products) LIKE '%%kosher%%' THEN 3
                            ELSE 0
                        END +
                        CASE 
                            WHEN LOWER(products) LIKE '%%halal%%' THEN 3
                            ELSE 0
                        END +
                        CASE 
                            WHEN LOWER(products) LIKE '%%certified%%' THEN 1
                            ELSE 0
                        END +
                        
                        -- 5. Business quality indicators (15 points max)
                        CASE WHEN verified = true THEN 5 ELSE 0 END +
                        CASE WHEN rating >= 4.5 THEN 5
                             WHEN rating >= 4.0 THEN 3
                             WHEN rating >= 3.5 THEN 1
                             ELSE 0
                        END +
                        CASE WHEN company_website IS NOT NULL THEN 3 ELSE 0 END +
                        CASE WHEN contact_person IS NOT NULL THEN 2 ELSE 0 END
                        
                    ) as total_score,
                    
                    -- Detailed scoring breakdown
                    CASE WHEN LOWER(products) LIKE %s THEN 40
                         WHEN LOWER(products) LIKE %s THEN 30
                         ELSE 0 END as product_match_score,
                    
                    %s as term_match_score,
                    
                    CASE WHEN verified = true THEN 'Verified' ELSE 'Not Verified' END as verification_status,
                    
                    -- Extract matched terms
                    ARRAY(
                        SELECT DISTINCT term 
                        FROM unnest(ARRAY%s) as term 
                        WHERE LOWER(products) LIKE '%%' || LOWER(term) || '%%'
                    ) as matched_terms,
                    
                    -- Product preview with highlighting
                    SUBSTRING(products, 1, 300) as product_preview
                    
                FROM suppliers s
                WHERE 
                    products IS NOT NULL 
                    AND LENGTH(products) > 100
                    AND company_email IS NOT NULL 
                    AND company_email != ''
                    AND (%s)  -- Term matching condition
            )
            SELECT 
                *,
                -- Percentage score
                ROUND((total_score::numeric / 100) * 100, 1) as match_percentage
            FROM supplier_scores
            WHERE total_score > 0
        """
        
        # Build query parameters
        full_search = f"%{query.lower()}%"
        fuzzy_search = f"%{' '.join(primary_terms)}%"
        
        # Term scoring SQL
        term_scoring_sql = " + ".join([
            f"CASE WHEN LOWER(products) LIKE '%{term}%' THEN {min(10, 30//len(primary_terms))} ELSE 0 END"
            for term in primary_terms
        ]) if primary_terms else "0"
        
        # Term matching condition
        term_conditions = " OR ".join([
            f"LOWER(products) LIKE '%{term}%'"
            for term in search_terms
        ])
        
        # Apply filters
        filter_conditions = []
        if filters:
            if filters.get('countries'):
                filter_conditions.append(f"AND country IN ({','.join(['%s']*len(filters['countries']))})")
            if filters.get('verified_only'):
                filter_conditions.append("AND verified = true")
            if filters.get('min_rating'):
                filter_conditions.append("AND rating >= %s")
            if filters.get('certifications'):
                cert_conditions = []
                for cert in filters['certifications']:
                    cert_conditions.append(f"LOWER(products) LIKE '%{cert.lower()}%'")
                filter_conditions.append(f"AND ({' OR '.join(cert_conditions)})")
        
        # Add filters to query
        query_sql = query_sql.replace("WHERE total_score > 0", 
                                    f"WHERE total_score > 0 {' '.join(filter_conditions)}")
        
        # Order by score and limit
        query_sql += " ORDER BY total_score DESC, rating DESC NULLS LAST, verified DESC LIMIT %s"
        
        # Build final parameters
        params = [
            full_search, fuzzy_search,  # Product match
            term_scoring_sql,           # Term scoring
            full_search, full_search,   # Name match
            full_search, fuzzy_search,  # Score breakdown
            term_scoring_sql,           # Term score breakdown
            search_terms,               # Matched terms array
            term_conditions            # WHERE condition
        ]
        
        # Add filter parameters
        if filters:
            if filters.get('countries'):
                params.extend(filters['countries'])
            if filters.get('min_rating'):
                params.append(filters['min_rating'])
        
        params.append(limit)
        
        # Execute search
        cur.execute(query_sql, params)
        results = cur.fetchall()
        
        # Calculate execution time
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Save to search history
        if user_email:
            cur.execute("""
                INSERT INTO search_history 
                (user_email, search_query, search_type, filters, result_count, 
                 execution_time_ms, session_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                user_email,
                query,
                'ai_search',
                json.dumps(filters) if filters else None,
                len(results),
                execution_time,
                hashlib.md5(f"{user_email}{datetime.now().date()}".encode()).hexdigest()[:20]
            ))
            search_id = cur.fetchone()['id']
        else:
            search_id = None
        
        # Update popular searches
        self._update_popular_searches(query, len(results))
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Format results
        formatted_results = []
        for idx, result in enumerate(results, 1):
            formatted_results.append({
                'rank': idx,
                'supplier_id': result['id'],
                'supplier_name': result['supplier_name'],
                'company_name': result['company_name'],
                'country': result['country'],
                'email': result['company_email'],
                'website': result['company_website'],
                'contact_person': result['contact_person'],
                'phone': result['phone'],
                'verified': result['verified'],
                'rating': float(result['rating']) if result['rating'] else None,
                'total_score': result['total_score'],
                'match_percentage': float(result['match_percentage']),
                'product_match_score': result['product_match_score'],
                'matched_terms': result['matched_terms'],
                'verification_status': result['verification_status'],
                'product_preview': result['product_preview'],
                'scoring_breakdown': {
                    'product_match': result['product_match_score'],
                    'term_matches': result['term_match_score'],
                    'quality_indicators': result['total_score'] - result['product_match_score'] - result['term_match_score']
                }
            })
        
        return {
            'search_id': search_id,
            'query': query,
            'filters': filters,
            'total_results': len(results),
            'execution_time_ms': execution_time,
            'timestamp': datetime.now().isoformat(),
            'results': formatted_results
        }
    
    def add_suppliers_to_project(self, supplier_ids: List[int], project_id: int = None,
                                project_name: str = None, user_email: str = None) -> int:
        """Add selected suppliers to existing or new project"""
        
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        try:
            # Create new project if needed
            if not project_id and project_name:
                cur.execute("""
                    INSERT INTO projects (project_name, description, created_at, user_email)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (
                    project_name,
                    f"Created from AI search on {datetime.now().strftime('%Y-%m-%d')}",
                    datetime.now(),
                    user_email
                ))
                project_id = cur.fetchone()['id']
            
            # Add suppliers to project
            added_count = 0
            for supplier_id in supplier_ids:
                # Check if already in project
                cur.execute("""
                    SELECT id FROM project_suppliers 
                    WHERE project_id = %s AND supplier_id = %s
                """, (project_id, supplier_id))
                
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO project_suppliers (project_id, supplier_id, added_at, status)
                        VALUES (%s, %s, %s, %s)
                    """, (project_id, supplier_id, datetime.now(), 'new'))
                    added_count += 1
            
            conn.commit()
            
            return {
                'project_id': project_id,
                'suppliers_added': added_count,
                'total_suppliers': len(supplier_ids)
            }
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()
    
    def save_search(self, user_email: str, search_name: str, query: str, 
                   filters: Dict[str, Any] = None, alert_enabled: bool = False) -> int:
        """Save a search for future use"""
        
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO saved_searches 
            (user_email, search_name, search_query, filters, alert_enabled)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            user_email,
            search_name,
            query,
            json.dumps(filters) if filters else None,
            alert_enabled
        ))
        
        saved_id = cur.fetchone()['id']
        conn.commit()
        cur.close()
        conn.close()
        
        return saved_id
    
    def get_search_history(self, user_email: str, limit: int = 20) -> List[Dict]:
        """Get user's search history"""
        
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                id,
                search_query,
                filters,
                result_count,
                search_timestamp,
                execution_time_ms,
                converted_to_project,
                project_id
            FROM search_history
            WHERE user_email = %s
            ORDER BY search_timestamp DESC
            LIMIT %s
        """, (user_email, limit))
        
        history = cur.fetchall()
        cur.close()
        conn.close()
        
        return history
    
    def get_popular_searches(self, limit: int = 10) -> List[Dict]:
        """Get trending/popular searches"""
        
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                search_term,
                search_count,
                trending_score,
                last_searched
            FROM popular_searches
            WHERE last_searched > CURRENT_TIMESTAMP - INTERVAL '30 days'
            ORDER BY trending_score DESC, search_count DESC
            LIMIT %s
        """, (limit,))
        
        popular = cur.fetchall()
        cur.close()
        conn.close()
        
        return popular
    
    def _update_popular_searches(self, query: str, result_count: int):
        """Update popular searches analytics"""
        
        if result_count == 0:
            return
            
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        # Extract main terms
        terms = [term for term in query.lower().split() if len(term) > 3]
        week_num = datetime.now().isocalendar()[1]
        year = datetime.now().year
        
        for term in terms[:3]:  # Top 3 terms
            # Calculate trending score (combines recency and frequency)
            trending_score = result_count * 0.1 + 10  # Base score
            
            cur.execute("""
                INSERT INTO popular_searches (search_term, search_count, trending_score, 
                                            week_number, year, last_searched)
                VALUES (%s, 1, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (search_term, week_number, year) 
                DO UPDATE SET 
                    search_count = popular_searches.search_count + 1,
                    trending_score = popular_searches.trending_score + %s,
                    last_searched = CURRENT_TIMESTAMP
            """, (term, trending_score, week_num, year, trending_score * 0.5))
        
        conn.commit()
        cur.close()
        conn.close()


# Example usage function
def demo_search():
    """Demo function showing how to use the AI search system"""
    
    search = AISearchSystem()
    
    # Example: Search for chocolate wafer products
    print("🔍 AI Search Demo: Chocolate Wafer Manufacturers\n")
    
    results = search.ai_search_suppliers(
        query="chocolate wafer biscuits cream filling manufacturing",
        user_email="buyer@foodxchange.com",
        filters={
            'countries': ['Italy', 'Turkey', 'Poland', 'Germany'],
            'verified_only': True,
            'min_rating': 3.5
        },
        limit=50
    )
    
    print(f"✅ Found {results['total_results']} suppliers in {results['execution_time_ms']}ms\n")
    
    # Show top 10 results with checkboxes
    print("📊 Top 10 Results (Select for Project):\n")
    print("[ ] Rank | Score | Supplier Name | Country | Matched Terms")
    print("-" * 80)
    
    for result in results['results'][:10]:
        checkbox = "[ ]"
        print(f"{checkbox} #{result['rank']:2d} | {result['match_percentage']:5.1f}% | "
              f"{result['supplier_name'][:30]:30s} | {result['country']:12s} | "
              f"{', '.join(result['matched_terms'][:3])}")
    
    # Save search
    saved_id = search.save_search(
        user_email="buyer@foodxchange.com",
        search_name="Chocolate Wafer Suppliers Q1 2025",
        query="chocolate wafer biscuits cream filling manufacturing",
        filters={'countries': ['Italy', 'Turkey', 'Poland', 'Germany']},
        alert_enabled=True
    )
    
    print(f"\n💾 Search saved with ID: {saved_id}")
    
    # Add to project (example with first 5 suppliers)
    selected_suppliers = [r['supplier_id'] for r in results['results'][:5]]
    
    project_result = search.add_suppliers_to_project(
        supplier_ids=selected_suppliers,
        project_name="Chocolate Wafer Sourcing 2025",
        user_email="buyer@foodxchange.com"
    )
    
    print(f"\n📁 Added {project_result['suppliers_added']} suppliers to project ID: {project_result['project_id']}")


if __name__ == "__main__":
    demo_search()