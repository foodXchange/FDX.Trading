"""Simplified models for FoodXchange database"""
from .user import User
from .project import Project
from .quote import Quote
from .product import Product
from .document import Document
from .activity_log import ActivityLog

__all__ = [
    "User",
    "Project", 
    "Quote",
    "Product",
    "Document",
    "ActivityLog"
]