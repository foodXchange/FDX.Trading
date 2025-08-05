#!/usr/bin/env python3
"""
Simple Interaction Tracker for FDX.trading
Tracks user interactions for machine learning analysis
Lean implementation focused on data collection only
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv
import psycopg2

load_dotenv()

class InteractionTracker:
    def __init__(self):
        self.user_email = 'udi@fdx.trading'
    
    def get_db_connection(self):
        return psycopg2.connect(os.getenv('DATABASE_URL'))
    
    def track(self, action_type, context_data=None, success_indicator=None, time_spent=None):
        """
        Track a user interaction - lean and simple
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_interactions 
                (user_email, action_type, context_data, success_indicator, time_spent)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                self.user_email, 
                action_type, 
                json.dumps(context_data) if context_data else None,
                success_indicator, 
                time_spent
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            # Fail silently to not disrupt user experience
            pass
    
    def track_search(self, query, results_count=0, countries=None, success=True):
        """Track supplier search"""
        self.track('supplier_search', {
            'query': query,
            'results_count': results_count,
            'countries': countries or [],
            'timestamp': datetime.now().isoformat()
        }, success)
    
    def track_email_sent(self, recipient_count, email_type='inquiry', success=True):
        """Track email sending"""
        self.track('email_sent', {
            'recipient_count': recipient_count,
            'email_type': email_type,
            'timestamp': datetime.now().isoformat()
        }, success)
    
    def track_project_created(self, project_name, supplier_count=0, success=True):
        """Track project creation"""
        self.track('project_created', {
            'project_name': project_name,
            'supplier_count': supplier_count,
            'timestamp': datetime.now().isoformat()
        }, success)
    
    def track_page_visit(self, page_name, time_spent=None):
        """Track page visits"""
        self.track('page_visit', {
            'page': page_name,
            'timestamp': datetime.now().isoformat()
        }, True, time_spent)

# Global tracker instance
tracker = InteractionTracker()

# Test the tracker
if __name__ == "__main__":
    # Test tracking
    tracker.track_search("sunflower oil", 15, ["Italy", "Spain"], True)
    tracker.track_email_sent(3, "inquiry", True)
    tracker.track_project_created("Mediterranean Oils", 8, True)
    print("Interaction tracking test completed successfully")