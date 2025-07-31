"""
Search Service Package
Provides intelligent search functionality for the FoodXchange platform
"""

from .search_service import IntelligentSearchService
from .models import (
    SearchCategory,
    SearchFilterType,
    SearchFilter,
    SearchSuggestion,
    SearchResult
)
from .query_parser import QueryParser
from .suggestion_engine import SuggestionEngine
from .filters import FilterManager

__all__ = [
    'IntelligentSearchService',
    'SearchCategory',
    'SearchFilterType',
    'SearchFilter',
    'SearchSuggestion',
    'SearchResult',
    'QueryParser',
    'SuggestionEngine',
    'FilterManager'
]