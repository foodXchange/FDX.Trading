"""
Email CRM Module for FoodXchange
Lean email tracking and automation
"""

from app.email_crm.service import email_crm
from app.email_crm.tracker import EmailTracker

__all__ = ['email_crm', 'EmailTracker']