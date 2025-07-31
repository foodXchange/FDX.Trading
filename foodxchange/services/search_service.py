"""
Search Service
This module has been refactored into a package structure.
Import from the search package instead.
"""

# Maintain backward compatibility
from .search import (
    IntelligentSearchService,
    SearchCategory,
    SearchFilterType,
    SearchFilter,
    SearchSuggestion,
    SearchResult,
    QueryParser,
    SuggestionEngine,
    FilterManager
)

# Export for backward compatibility

# Create default instance
search_service = IntelligentSearchService()
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