#!/usr/bin/env python3
"""
Simple Tips Engine for FDX.trading
Basic pattern recognition and helpful suggestions
Lean and simple approach
"""

import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import os

load_dotenv()

class SimpleTipsEngine:
    def __init__(self):
        self.user_email = 'udi@fdx.trading'
    
    def get_db_connection(self):
        return psycopg2.connect(os.getenv('DATABASE_URL'), cursor_factory=RealDictCursor)
    
    def get_smart_tips(self):
        """
        Generate simple, practical tips based on current data
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        tips = []
        
        # Tip 1: Check project activity
        cursor.execute("SELECT COUNT(*) as count FROM projects WHERE user_email = %s", (self.user_email,))
        project_count = cursor.fetchone()['count']
        
        if project_count == 0:
            tips.append({
                'icon': 'bi-lightbulb',
                'title': 'Start Your First Project',
                'description': 'Create a project to organize your supplier searches and track communications.',
                'action': '/suppliers',
                'action_text': 'Start Searching',
                'priority': 'high'
            })
        elif project_count >= 3:
            tips.append({
                'icon': 'bi-check-circle',
                'title': 'Great Progress!',
                'description': f'You have {project_count} projects. Consider using bulk emails to contact multiple suppliers efficiently.',
                'action': '/email-composer',
                'action_text': 'Compose Email',
                'priority': 'medium'
            })
        
        # Tip 2: Check email activity
        cursor.execute("SELECT COUNT(*) as sent FROM email_log WHERE created_at > NOW() - INTERVAL '7 days'")
        recent_emails = cursor.fetchone()['sent']
        
        cursor.execute("SELECT COUNT(*) as analyzed FROM email_responses WHERE created_at > NOW() - INTERVAL '7 days'")
        recent_responses = cursor.fetchone()['analyzed']
        
        if recent_emails > 0 and recent_responses == 0:
            tips.append({
                'icon': 'bi-robot',
                'title': 'Analyze Email Responses',
                'description': 'Use AI to analyze supplier responses and generate follow-up tasks automatically.',
                'action': '/email-analyzer',
                'action_text': 'Analyze Emails',
                'priority': 'high'
            })
        
        # Tip 3: Check supplier database usage
        cursor.execute("SELECT COUNT(*) as searches FROM search_history WHERE created_at > NOW() - INTERVAL '30 days'")
        recent_searches = cursor.fetchone()['searches']
        
        if recent_searches < 5:
            tips.append({
                'icon': 'bi-search',
                'title': 'Explore More Suppliers',
                'description': 'Search our database of 18,000+ suppliers to find better deals and more options.',
                'action': '/suppliers',
                'action_text': 'Search Suppliers',
                'priority': 'medium'
            })
        
        # Add general helpful tips
        tips.extend(self._get_general_tips())
        
        cursor.close()
        conn.close()
        
        return tips[:6]  # Return max 6 tips
    
    def _get_general_tips(self):
        """Static helpful tips for process improvement"""
        return [
            {
                'icon': 'bi-clock',
                'title': 'Best Email Timing',
                'description': 'Send business emails Tuesday-Thursday, 10 AM-2 PM local time for better response rates.',
                'action': None,
                'action_text': None,
                'priority': 'low'
            },
            {
                'icon': 'bi-list-check',
                'title': 'Organize by Product Category',
                'description': 'Group suppliers by product type in separate projects for easier management.',
                'action': '/projects',
                'action_text': 'View Projects',
                'priority': 'low'
            },
            {
                'icon': 'bi-envelope-check',
                'title': 'Professional Email Templates',
                'description': 'Use our AI composer to create professional business inquiries that get responses.',
                'action': '/email-composer',
                'action_text': 'Compose Email',
                'priority': 'low'
            },
            {
                'icon': 'bi-graph-up',
                'title': 'Track Response Rates',
                'description': 'Keep notes on which suppliers respond quickly to build a preferred supplier list.',
                'action': None,
                'action_text': None,
                'priority': 'low'
            }
        ]

def test_tips_engine():
    """Test the simple tips engine"""
    engine = SimpleTipsEngine()
    tips = engine.get_smart_tips()
    
    print("Smart Tips Generated:")
    for tip in tips:
        print(f"• {tip['title']}")
        print(f"  {tip['description']}")
        if tip['action']:
            print(f"  Action: {tip['action_text']} -> {tip['action']}")
        print()

if __name__ == "__main__":
    test_tips_engine()