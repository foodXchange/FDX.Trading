"""
Suggestion Engine Module
Handles search suggestions, autocomplete, and related searches
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import Counter
import json

from .models import SearchSuggestion, SearchCategory

logger = logging.getLogger(__name__)


class SuggestionEngine:
    """
    Generates intelligent search suggestions
    """
    
    def __init__(self):
        self.search_history = {}
        self.trending_searches = Counter()
        self.popular_products = [
            "organic tomatoes", "fresh lettuce", "avocados", "strawberries",
            "potatoes", "onions", "carrots", "apples", "bananas", "oranges"
        ]
        self.popular_categories = [
            "fruits", "vegetables", "dairy", "meat", "seafood", "grains",
            "beverages", "snacks", "frozen foods", "bakery"
        ]
    
    async def get_suggestions(self, query: str, user_id: Optional[str] = None, limit: int = 10) -> List[SearchSuggestion]:
        """
        Get search suggestions based on partial query
        """
        try:
            suggestions = []
            query_lower = query.lower().strip()
            
            if not query_lower:
                # Return trending or recent searches if no query
                return await self._get_default_suggestions(user_id, limit)
            
            # Get autocomplete suggestions
            autocomplete = await self._get_autocomplete_suggestions(query_lower, limit)
            suggestions.extend(autocomplete)
            
            # Get category suggestions
            if len(query_lower) >= 2:
                category_suggestions = self._get_category_suggestions(query_lower)
                suggestions.extend(category_suggestions)
            
            # Get product suggestions
            if len(query_lower) >= 3:
                product_suggestions = self._get_product_suggestions(query_lower)
                suggestions.extend(product_suggestions)
            
            # Get user's recent searches
            if user_id:
                recent_suggestions = self._get_recent_search_suggestions(user_id, query_lower)
                suggestions.extend(recent_suggestions)
            
            # Deduplicate and sort by relevance
            suggestions = self._deduplicate_suggestions(suggestions)
            suggestions.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []
    
    async def _get_default_suggestions(self, user_id: Optional[str], limit: int) -> List[SearchSuggestion]:
        """Get default suggestions when no query is provided"""
        suggestions = []
        
        # Add trending searches
        for search_term, count in self.trending_searches.most_common(5):
            suggestions.append(SearchSuggestion(
                text=search_term,
                category=SearchCategory.PRODUCTS,
                relevance_score=0.9,
                metadata={"count": count},
                type="trending"
            ))
        
        # Add user's recent searches
        if user_id and user_id in self.search_history:
            recent_searches = self.search_history[user_id][-5:]
            for search in reversed(recent_searches):
                suggestions.append(SearchSuggestion(
                    text=search["query"],
                    category=SearchCategory.PRODUCTS,
                    relevance_score=0.8,
                    metadata={"timestamp": search["timestamp"]},
                    type="recent"
                ))
        
        # Add popular categories
        for category in self.popular_categories[:5]:
            suggestions.append(SearchSuggestion(
                text=f"Browse {category}",
                category=SearchCategory.PRODUCTS,
                relevance_score=0.7,
                metadata={"category": category},
                type="suggestion"
            ))
        
        return suggestions[:limit]
    
    async def _get_autocomplete_suggestions(self, query: str, limit: int) -> List[SearchSuggestion]:
        """Generate autocomplete suggestions"""
        suggestions = []
        
        # Common search prefixes
        prefixes = [
            "organic", "fresh", "local", "certified", "premium",
            "wholesale", "bulk", "sustainable", "imported", "domestic"
        ]
        
        # Generate suggestions with prefixes
        for prefix in prefixes:
            if prefix.startswith(query):
                suggestions.append(SearchSuggestion(
                    text=f"{prefix} products",
                    category=SearchCategory.PRODUCTS,
                    relevance_score=0.85,
                    metadata={"prefix": prefix},
                    type="suggestion"
                ))
            elif query in prefix:
                suggestions.append(SearchSuggestion(
                    text=prefix,
                    category=SearchCategory.PRODUCTS,
                    relevance_score=0.75,
                    metadata={"match_type": "contains"},
                    type="suggestion"
                ))
        
        # Product-based suggestions
        for product in self.popular_products:
            if product.startswith(query):
                suggestions.append(SearchSuggestion(
                    text=product,
                    category=SearchCategory.PRODUCTS,
                    relevance_score=0.9,
                    metadata={"product": product},
                    type="suggestion"
                ))
            elif query in product:
                suggestions.append(SearchSuggestion(
                    text=product,
                    category=SearchCategory.PRODUCTS,
                    relevance_score=0.7,
                    metadata={"product": product},
                    type="suggestion"
                ))
        
        return suggestions
    
    def _get_category_suggestions(self, query: str) -> List[SearchSuggestion]:
        """Get category-based suggestions"""
        suggestions = []
        
        for category in self.popular_categories:
            if category.startswith(query) or query in category:
                suggestions.append(SearchSuggestion(
                    text=f"All {category}",
                    category=SearchCategory.PRODUCTS,
                    relevance_score=0.8,
                    metadata={"category": category},
                    type="suggestion"
                ))
        
        return suggestions
    
    def _get_product_suggestions(self, query: str) -> List[SearchSuggestion]:
        """Get product-specific suggestions"""
        suggestions = []
        
        # Suggest related searches
        related_terms = {
            "tomato": ["tomatoes", "cherry tomatoes", "roma tomatoes", "tomato sauce"],
            "apple": ["apples", "green apples", "red apples", "apple juice"],
            "potato": ["potatoes", "sweet potatoes", "potato chips", "french fries"],
            "milk": ["whole milk", "skim milk", "almond milk", "oat milk"],
            "bread": ["whole wheat bread", "white bread", "sourdough", "baguette"]
        }
        
        for base_term, related in related_terms.items():
            if base_term in query or query in base_term:
                for term in related:
                    suggestions.append(SearchSuggestion(
                        text=term,
                        category=SearchCategory.PRODUCTS,
                        relevance_score=0.75,
                        metadata={"base_term": base_term},
                        type="suggestion"
                    ))
        
        return suggestions
    
    def _get_recent_search_suggestions(self, user_id: str, query: str) -> List[SearchSuggestion]:
        """Get suggestions from user's search history"""
        suggestions = []
        
        if user_id not in self.search_history:
            return suggestions
        
        for search in self.search_history[user_id]:
            if query in search["query"].lower():
                suggestions.append(SearchSuggestion(
                    text=search["query"],
                    category=SearchCategory.PRODUCTS,
                    relevance_score=0.85,
                    metadata={
                        "timestamp": search["timestamp"],
                        "result_count": search.get("result_count", 0)
                    },
                    type="recent"
                ))
        
        return suggestions
    
    def _deduplicate_suggestions(self, suggestions: List[SearchSuggestion]) -> List[SearchSuggestion]:
        """Remove duplicate suggestions"""
        seen = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            key = suggestion.text.lower().strip()
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions
    
    def record_search(self, user_id: str, query: str, result_count: int = 0):
        """Record a search for history and trending"""
        try:
            # Update user search history
            if user_id not in self.search_history:
                self.search_history[user_id] = []
            
            self.search_history[user_id].append({
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "result_count": result_count
            })
            
            # Keep only last 50 searches per user
            if len(self.search_history[user_id]) > 50:
                self.search_history[user_id] = self.search_history[user_id][-50:]
            
            # Update trending searches
            self.trending_searches[query.lower()] += 1
            
            # Clean old trending data periodically
            if len(self.trending_searches) > 1000:
                # Keep only top 500 trending searches
                self.trending_searches = Counter(
                    dict(self.trending_searches.most_common(500))
                )
            
        except Exception as e:
            logger.error(f"Error recording search: {e}")
    
    def get_trending_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get current trending searches"""
        trending = []
        
        for term, count in self.trending_searches.most_common(limit):
            trending.append({
                "term": term,
                "count": count,
                "trend": "up"  # Could implement trend detection
            })
        
        return trending
    
    def clear_user_history(self, user_id: str):
        """Clear a user's search history"""
        if user_id in self.search_history:
            del self.search_history[user_id]