"""
Intelligent Search Service
Main search service that coordinates all search functionality
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc

from foodxchange.database import get_db
from foodxchange.models.user import User
from foodxchange.models.supplier import Supplier
from foodxchange.models.buyer import Buyer
from foodxchange.models.project import Project
from foodxchange.services.openai_service import OpenAIService

from .models import SearchCategory, SearchResult, SearchSuggestion, SearchFilter
from .query_parser import QueryParser
from .suggestion_engine import SuggestionEngine
from .filters import FilterManager

logger = logging.getLogger(__name__)


class IntelligentSearchService:
    """
    Main search service coordinating all search functionality
    """
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.query_parser = QueryParser()
        self.suggestion_engine = SuggestionEngine()
        self.filter_manager = FilterManager()
        
        # Cache for search results
        self.search_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def search(
        self,
        query: str,
        filters: Optional[List[SearchFilter]] = None,
        categories: Optional[List[SearchCategory]] = None,
        user_id: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Perform intelligent search across all categories
        """
        try:
            # Parse the query
            parsed_query = self.query_parser.parse_query(query)
            
            # Check cache
            cache_key = self._generate_cache_key(query, filters, categories, page)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Initialize results
            results = {
                "query": query,
                "parsed_query": parsed_query,
                "results": [],
                "facets": {},
                "total": 0,
                "page": page,
                "per_page": per_page,
                "categories": {},
                "suggestions": [],
                "execution_time": 0
            }
            
            start_time = datetime.now()
            
            # Determine which categories to search
            search_categories = categories or self._determine_categories(parsed_query)
            
            # Execute searches in parallel
            search_tasks = []
            for category in search_categories:
                if category == SearchCategory.SUPPLIERS:
                    search_tasks.append(self._search_suppliers(parsed_query, filters, db))
                elif category == SearchCategory.BUYERS:
                    search_tasks.append(self._search_buyers(parsed_query, filters, db))
                elif category == SearchCategory.PROJECTS:
                    search_tasks.append(self._search_projects(parsed_query, filters, db))
                elif category == SearchCategory.PRODUCTS:
                    search_tasks.append(self._search_products(parsed_query, filters, db))
            
            # Wait for all searches to complete
            if search_tasks:
                category_results = await asyncio.gather(*search_tasks)
                
                # Combine results
                all_results = []
                for cat_results in category_results:
                    all_results.extend(cat_results)
                
                # Sort by relevance
                all_results.sort(key=lambda x: x.relevance_score, reverse=True)
                
                # Paginate
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                results["results"] = all_results[start_idx:end_idx]
                results["total"] = len(all_results)
            
            # Get facets for filtering
            if db and not filters:  # Only get facets if no filters applied
                results["facets"] = await self._get_search_facets(parsed_query, search_categories, db)
            
            # Get related suggestions
            results["suggestions"] = await self.suggestion_engine.get_suggestions(
                query, user_id, limit=5
            )
            
            # Record search for trending
            if user_id:
                self.suggestion_engine.record_search(user_id, query, results["total"])
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            results["execution_time"] = execution_time
            
            # Cache results
            self._cache_result(cache_key, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                "query": query,
                "results": [],
                "error": str(e),
                "total": 0
            }
    
    async def get_suggestions(self, query: str, user_id: Optional[str] = None) -> List[SearchSuggestion]:
        """Get search suggestions"""
        return await self.suggestion_engine.get_suggestions(query, user_id)
    
    async def _search_suppliers(
        self,
        parsed_query: Dict[str, Any],
        filters: Optional[List[SearchFilter]],
        db: Session
    ) -> List[SearchResult]:
        """Search suppliers"""
        results = []
        
        try:
            if not db:
                return results
            
            # Build base query
            query = db.query(Supplier)
            
            # Apply text search
            if parsed_query["keywords"]:
                search_conditions = []
                for keyword in parsed_query["keywords"]:
                    search_conditions.append(
                        or_(
                            Supplier.company_name.ilike(f"%{keyword}%"),
                            Supplier.description.ilike(f"%{keyword}%"),
                            Supplier.products.ilike(f"%{keyword}%")
                        )
                    )
                query = query.filter(or_(*search_conditions))
            
            # Apply filters
            if filters:
                query = self.filter_manager.apply_filters(query, filters, Supplier)
            
            # Execute query
            suppliers = query.limit(50).all()
            
            # Convert to search results
            for supplier in suppliers:
                results.append(SearchResult(
                    id=f"supplier_{supplier.id}",
                    title=supplier.company_name,
                    description=supplier.description or "",
                    category=SearchCategory.SUPPLIERS,
                    relevance_score=self._calculate_relevance_score(supplier, parsed_query),
                    metadata={
                        "location": f"{supplier.city}, {supplier.country}",
                        "products": supplier.products,
                        "certifications": supplier.certifications
                    },
                    url=f"/suppliers/{supplier.id}",
                    badges=self._extract_badges(supplier)
                ))
            
        except Exception as e:
            logger.error(f"Error searching suppliers: {e}")
        
        return results
    
    async def _search_buyers(
        self,
        parsed_query: Dict[str, Any],
        filters: Optional[List[SearchFilter]],
        db: Session
    ) -> List[SearchResult]:
        """Search buyers"""
        results = []
        
        try:
            if not db:
                return results
            
            # Build base query
            query = db.query(Buyer)
            
            # Apply text search
            if parsed_query["keywords"]:
                search_conditions = []
                for keyword in parsed_query["keywords"]:
                    search_conditions.append(
                        or_(
                            Buyer.company_name.ilike(f"%{keyword}%"),
                            Buyer.description.ilike(f"%{keyword}%")
                        )
                    )
                query = query.filter(or_(*search_conditions))
            
            # Apply filters
            if filters:
                query = self.filter_manager.apply_filters(query, filters, Buyer)
            
            # Execute query
            buyers = query.limit(50).all()
            
            # Convert to search results
            for buyer in buyers:
                results.append(SearchResult(
                    id=f"buyer_{buyer.id}",
                    title=buyer.company_name,
                    description=buyer.description or "",
                    category=SearchCategory.BUYERS,
                    relevance_score=self._calculate_relevance_score(buyer, parsed_query),
                    metadata={
                        "location": f"{buyer.city}, {buyer.country}",
                        "industry": buyer.industry
                    },
                    url=f"/buyers/{buyer.id}",
                    badges=self._extract_badges(buyer)
                ))
            
        except Exception as e:
            logger.error(f"Error searching buyers: {e}")
        
        return results
    
    async def _search_projects(
        self,
        parsed_query: Dict[str, Any],
        filters: Optional[List[SearchFilter]],
        db: Session
    ) -> List[SearchResult]:
        """Search projects"""
        results = []
        
        try:
            if not db:
                return results
            
            # Build base query
            query = db.query(Project)
            
            # Apply text search
            if parsed_query["keywords"]:
                search_conditions = []
                for keyword in parsed_query["keywords"]:
                    search_conditions.append(
                        or_(
                            Project.name.ilike(f"%{keyword}%"),
                            Project.description.ilike(f"%{keyword}%")
                        )
                    )
                query = query.filter(or_(*search_conditions))
            
            # Apply filters
            if filters:
                query = self.filter_manager.apply_filters(query, filters, Project)
            
            # Execute query
            projects = query.limit(50).all()
            
            # Convert to search results
            for project in projects:
                results.append(SearchResult(
                    id=f"project_{project.id}",
                    title=project.name,
                    description=project.description or "",
                    category=SearchCategory.PROJECTS,
                    relevance_score=self._calculate_relevance_score(project, parsed_query),
                    metadata={
                        "created_at": project.created_at.isoformat(),
                        "status": project.status
                    },
                    url=f"/projects/{project.id}",
                    badges=self._extract_badges(project)
                ))
            
        except Exception as e:
            logger.error(f"Error searching projects: {e}")
        
        return results
    
    async def _search_products(
        self,
        parsed_query: Dict[str, Any],
        filters: Optional[List[SearchFilter]],
        db: Session
    ) -> List[SearchResult]:
        """Search products (simplified for now)"""
        # Product search implementation will be added when Product model is available
        # For now, return empty results to maintain API consistency
        logger.info("Product search requested but Product model not yet implemented")
        return []
    
    async def _get_search_facets(
        self,
        parsed_query: Dict[str, Any],
        categories: List[SearchCategory],
        db: Session
    ) -> Dict[str, Any]:
        """Get facets for search results"""
        facets = {}
        
        try:
            # Get facets for each category
            if SearchCategory.SUPPLIERS in categories:
                facets["suppliers"] = {
                    "location": self.filter_manager.get_facet_counts(
                        db.query(Supplier), 
                        SearchFilterType.LOCATION, 
                        Supplier
                    ),
                    "certification": self.filter_manager.get_facet_counts(
                        db.query(Supplier), 
                        SearchFilterType.CERTIFICATION, 
                        Supplier
                    )
                }
            
            if SearchCategory.BUYERS in categories:
                facets["buyers"] = {
                    "location": self.filter_manager.get_facet_counts(
                        db.query(Buyer), 
                        SearchFilterType.LOCATION, 
                        Buyer
                    ),
                    "company_size": self.filter_manager.get_facet_counts(
                        db.query(Buyer), 
                        SearchFilterType.COMPANY_SIZE, 
                        Buyer
                    )
                }
            
        except Exception as e:
            logger.error(f"Error getting facets: {e}")
        
        return facets
    
    def _determine_categories(self, parsed_query: Dict[str, Any]) -> List[SearchCategory]:
        """Determine which categories to search based on query"""
        categories = []
        
        # Check intent
        intent = parsed_query.get("intent", "general_search")
        
        if intent == "find_supplier":
            categories = [SearchCategory.SUPPLIERS]
        elif intent == "find_buyer":
            categories = [SearchCategory.BUYERS]
        elif intent == "general_search":
            # Search all categories
            categories = [
                SearchCategory.SUPPLIERS,
                SearchCategory.BUYERS,
                SearchCategory.PROJECTS,
                SearchCategory.PRODUCTS
            ]
        
        return categories
    
    def _calculate_relevance_score(self, entity: Any, parsed_query: Dict[str, Any]) -> float:
        """Calculate relevance score for a search result"""
        score = 0.5  # Base score
        
        # Boost for exact matches
        keywords = parsed_query.get("keywords", [])
        
        # Check title match
        title = getattr(entity, "company_name", getattr(entity, "name", ""))
        for keyword in keywords:
            if keyword.lower() in title.lower():
                score += 0.2
        
        # Check description match
        description = getattr(entity, "description", "")
        for keyword in keywords:
            if keyword.lower() in description.lower():
                score += 0.1
        
        # Boost for location match
        locations = parsed_query.get("entities", {}).get("locations", [])
        entity_location = getattr(entity, "city", "") + " " + getattr(entity, "country", "")
        for location in locations:
            if location.lower() in entity_location.lower():
                score += 0.15
        
        # Boost for certification match
        if hasattr(entity, "certifications"):
            industry_terms = parsed_query.get("industry_terms", [])
            entity_certs = getattr(entity, "certifications", "")
            for term in industry_terms:
                if term in entity_certs.lower():
                    score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _extract_badges(self, entity: Any) -> List[str]:
        """Extract badges for display"""
        badges = []
        
        # Verified badge
        if hasattr(entity, "is_verified") and entity.is_verified:
            badges.append("verified")
        
        # Premium badge
        if hasattr(entity, "is_premium") and entity.is_premium:
            badges.append("premium")
        
        # Certification badges
        if hasattr(entity, "certifications"):
            certs = entity.certifications
            if "organic" in certs.lower():
                badges.append("organic")
            if "kosher" in certs.lower():
                badges.append("kosher")
            if "halal" in certs.lower():
                badges.append("halal")
        
        return badges
    
    def _generate_cache_key(
        self,
        query: str,
        filters: Optional[List[SearchFilter]],
        categories: Optional[List[SearchCategory]],
        page: int
    ) -> str:
        """Generate cache key for search results"""
        key_parts = [
            query.lower(),
            str(page)
        ]
        
        if filters:
            filter_str = self.filter_manager.build_filter_string(filters)
            key_parts.append(filter_str)
        
        if categories:
            cat_str = ",".join(c.value for c in categories)
            key_parts.append(cat_str)
        
        return "|".join(key_parts)
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached search result"""
        if cache_key in self.search_cache:
            cached = self.search_cache[cache_key]
            # Check if cache is still valid
            if (datetime.now() - cached["timestamp"]).total_seconds() < self.cache_ttl:
                return cached["data"]
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache search result"""
        self.search_cache[cache_key] = {
            "data": result,
            "timestamp": datetime.now()
        }
        
        # Clean old cache entries
        if len(self.search_cache) > 100:
            # Remove oldest entries
            sorted_keys = sorted(
                self.search_cache.keys(),
                key=lambda k: self.search_cache[k]["timestamp"]
            )
            for key in sorted_keys[:20]:
                del self.search_cache[key]