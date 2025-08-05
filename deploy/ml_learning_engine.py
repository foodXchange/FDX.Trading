#!/usr/bin/env python3
"""
Machine Learning Engine for FDX.trading
Learns user patterns and suggests process improvements
Lean implementation focused on practical business value
"""

import json
import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

class FDXLearningEngine:
    def __init__(self):
        self.user_email = 'udi@fdx.trading'
    
    def get_db_connection(self):
        return psycopg2.connect(os.getenv('DATABASE_URL'), cursor_factory=RealDictCursor)
    
    def track_interaction(self, action_type, context_data=None, success_indicator=None, 
                         time_spent=None, session_id=None):
        """
        Track user interactions for learning
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_interactions 
                (user_email, action_type, context_data, success_indicator, time_spent, session_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                self.user_email, action_type, json.dumps(context_data) if context_data else None,
                success_indicator, time_spent, session_id
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error tracking interaction: {e}")
    
    def analyze_patterns(self):
        """
        Analyze user interactions to identify patterns and generate suggestions
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Analyze search patterns
        search_patterns = self._analyze_search_patterns(cursor)
        
        # Analyze email patterns
        email_patterns = self._analyze_email_patterns(cursor)
        
        # Analyze project patterns
        project_patterns = self._analyze_project_patterns(cursor)
        
        # Generate suggestions based on patterns
        suggestions = []
        suggestions.extend(self._generate_search_suggestions(search_patterns))
        suggestions.extend(self._generate_email_suggestions(email_patterns))
        suggestions.extend(self._generate_project_suggestions(project_patterns))
        
        # Store suggestions in database
        self._store_suggestions(suggestions, cursor)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return suggestions
    
    def _analyze_search_patterns(self, cursor):
        """Analyze supplier search patterns"""
        cursor.execute("""
            SELECT context_data, success_indicator, COUNT(*) as frequency
            FROM user_interactions 
            WHERE action_type = 'supplier_search' 
            AND interaction_timestamp > NOW() - INTERVAL '30 days'
            GROUP BY context_data, success_indicator
            ORDER BY frequency DESC
        """)
        
        search_data = cursor.fetchall()
        patterns = {
            'successful_queries': [],
            'failed_queries': [],
            'popular_countries': Counter(),
            'popular_products': Counter()
        }
        
        for row in search_data:
            context = row['context_data'] if row['context_data'] else {}
            if row['success_indicator']:
                patterns['successful_queries'].append(context)
            else:
                patterns['failed_queries'].append(context)
            
            # Extract country and product patterns
            if 'country' in context:
                patterns['popular_countries'][context['country']] += row['frequency']
            if 'product' in context:
                patterns['popular_products'][context['product']] += row['frequency']
        
        return patterns
    
    def _analyze_email_patterns(self, cursor):
        """Analyze email communication patterns"""
        cursor.execute("""
            SELECT context_data, success_indicator, COUNT(*) as frequency
            FROM user_interactions 
            WHERE action_type IN ('email_sent', 'email_received', 'email_analyzed')
            AND interaction_timestamp > NOW() - INTERVAL '30 days'
            GROUP BY context_data, success_indicator
        """)
        
        email_data = cursor.fetchall()
        patterns = {
            'response_rates': {},
            'successful_templates': [],
            'best_contact_times': Counter(),
            'high_converting_subjects': []
        }
        
        # Analyze patterns from email data
        for row in email_data:
            context = row['context_data'] if row['context_data'] else {}
            if 'email_type' in context and row['success_indicator']:
                patterns['successful_templates'].append(context['email_type'])
        
        return patterns
    
    def _analyze_project_patterns(self, cursor):
        """Analyze project workflow patterns"""
        cursor.execute("""
            SELECT context_data, time_spent, COUNT(*) as frequency
            FROM user_interactions 
            WHERE action_type IN ('project_created', 'suppliers_added', 'bulk_email_sent')
            AND interaction_timestamp > NOW() - INTERVAL '30 days'
            GROUP BY context_data, time_spent
        """)
        
        project_data = cursor.fetchall()
        patterns = {
            'efficient_workflows': [],
            'time_consuming_tasks': [],
            'optimal_project_sizes': []
        }
        
        return patterns
    
    def _generate_search_suggestions(self, patterns):
        """Generate smart search suggestions"""
        suggestions = []
        
        # Suggest popular search combinations
        if patterns['popular_countries']:
            top_country = patterns['popular_countries'].most_common(1)[0]
            suggestions.append({
                'type': 'search_optimization',
                'title': f'Focus on {top_country[0]} suppliers',
                'description': f'You\'ve had good success finding suppliers in {top_country[0]}. Consider expanding your search there.',
                'action_data': {'suggested_country': top_country[0]},
                'priority_score': 75
            })
        
        # Suggest search refinement
        if len(patterns['failed_queries']) > 3:
            suggestions.append({
                'type': 'search_improvement',
                'title': 'Refine your search terms',
                'description': 'Try using more specific product categories or include certifications in your search.',
                'action_data': {'tip': 'use_specific_terms'},
                'priority_score': 60
            })
        
        return suggestions
    
    def _generate_email_suggestions(self, patterns):
        """Generate email optimization suggestions"""
        suggestions = []
        
        # Suggest best email templates
        if patterns['successful_templates']:
            best_template = Counter(patterns['successful_templates']).most_common(1)[0]
            suggestions.append({
                'type': 'email_optimization',
                'title': f'Use {best_template[0]} email template more',
                'description': f'Your {best_template[0]} emails get the best responses. Consider using this template as default.',
                'action_data': {'suggested_template': best_template[0]},
                'priority_score': 80
            })
        
        # Suggest email timing optimization
        suggestions.append({
            'type': 'email_timing',
            'title': 'Optimal email sending time',
            'description': 'Send emails Tuesday-Thursday, 10 AM local time for best response rates.',
            'action_data': {'tip': 'optimal_timing'},
            'priority_score': 65
        })
        
        return suggestions
    
    def _generate_project_suggestions(self, patterns):
        """Generate project workflow suggestions"""
        suggestions = []
        
        # Suggest project organization
        suggestions.append({
            'type': 'workflow_optimization',
            'title': 'Organize suppliers by product category',
            'description': 'Group suppliers by product type in separate projects for better tracking.',
            'action_data': {'tip': 'categorize_projects'},
            'priority_score': 70
        })
        
        # Suggest bulk email optimization
        suggestions.append({
            'type': 'bulk_email_optimization',
            'title': 'Optimal bulk email batch size',
            'description': 'Send emails in batches of 10-15 suppliers for better deliverability and tracking.',
            'action_data': {'suggested_batch_size': 12},
            'priority_score': 60
        })
        
        return suggestions
    
    def _store_suggestions(self, suggestions, cursor):
        """Store generated suggestions in database"""
        for suggestion in suggestions:
            cursor.execute("""
                INSERT INTO ai_suggestions 
                (suggestion_type, title, description, action_data, priority_score, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                suggestion['type'],
                suggestion['title'],
                suggestion['description'],
                json.dumps(suggestion['action_data']),
                suggestion['priority_score'],
                datetime.now() + timedelta(days=7)  # Suggestions expire in 7 days
            ))
    
    def get_active_suggestions(self, limit=5):
        """Get current active suggestions for user"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, suggestion_type, title, description, action_data, priority_score,
                   shown_count, clicked_count
            FROM ai_suggestions 
            WHERE is_active = true 
            AND (expires_at IS NULL OR expires_at > NOW())
            ORDER BY priority_score DESC, created_at DESC
            LIMIT %s
        """, (limit,))
        
        suggestions = cursor.fetchall()
        
        # Mark as shown
        if suggestions:
            suggestion_ids = [s['id'] for s in suggestions]
            cursor.execute("""
                UPDATE ai_suggestions 
                SET shown_count = shown_count + 1 
                WHERE id = ANY(%s)
            """, (suggestion_ids,))
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return suggestions
    
    def dismiss_suggestion(self, suggestion_id):
        """Dismiss a suggestion (user feedback)"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE ai_suggestions 
            SET dismissed_count = dismissed_count + 1, is_active = false
            WHERE id = %s
        """, (suggestion_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def click_suggestion(self, suggestion_id):
        """Track suggestion click (user engagement)"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE ai_suggestions 
            SET clicked_count = clicked_count + 1
            WHERE id = %s
        """, (suggestion_id,))
        
        conn.commit()
        cursor.close()
        conn.close()

# Usage example and testing
def test_learning_engine():
    """Test the ML learning engine"""
    engine = FDXLearningEngine()
    
    # Simulate some interactions
    engine.track_interaction('supplier_search', {
        'query': 'sunflower oil',
        'country': 'Italy',
        'results_count': 25
    }, success_indicator=True, time_spent=120)
    
    engine.track_interaction('email_sent', {
        'email_type': 'inquiry',
        'recipient_count': 1
    }, success_indicator=True)
    
    # Analyze patterns and generate suggestions
    suggestions = engine.analyze_patterns()
    
    print("Generated suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion['title']}")
        print(f"   {suggestion['description']}")
        print(f"   Priority: {suggestion['priority_score']}")
        print()

if __name__ == "__main__":
    test_learning_engine()