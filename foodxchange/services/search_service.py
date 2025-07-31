"""
Intelligent Search Service for FoodXchange Platform
Provides advanced search functionality with AI-powered suggestions, natural language processing,
and comprehensive filtering capabilities for food industry professionals.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc, asc
from sqlalchemy.sql import text

from foodxchange.database import get_db
from foodxchange.models.user import User
from foodxchange.models.supplier import Supplier
from foodxchange.models.buyer import Buyer
from foodxchange.models.project import Project
from foodxchange.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class SearchCategory(Enum):
    """Search result categories"""
    PROJECTS = "projects"
    SUPPLIERS = "suppliers"
    BUYERS = "buyers"
    PRODUCTS = "products"
    CERTIFICATIONS = "certifications"
    LOCATIONS = "locations"


class SearchFilterType(Enum):
    """Search filter types"""
    LOCATION = "location"
    CERTIFICATION = "certification"
    PRODUCT_CATEGORY = "product_category"
    COMPANY_SIZE = "company_size"
    BUSINESS_TYPE = "business_type"
    DATE_RANGE = "date_range"
    PRICE_RANGE = "price_range"
    RATING = "rating"


@dataclass
class SearchFilter:
    """Search filter configuration"""
    type: SearchFilterType
    value: Any
    operator: str = "eq"  # eq, gt, lt, gte, lte, in, like
    label: Optional[str] = None


@dataclass
class SearchSuggestion:
    """Search suggestion item"""
    text: str
    category: SearchCategory
    relevance_score: float
    metadata: Dict[str, Any]
    type: str = "suggestion"  # suggestion, recent, trending


@dataclass
class SearchResult:
    """Search result item"""
    id: str
    title: str
    description: str
    category: SearchCategory
    relevance_score: float
    metadata: Dict[str, Any]
    url: str
    thumbnail: Optional[str] = None
    badges: List[str] = None


class IntelligentSearchService:
    """
    Intelligent search service with AI-powered features
    """
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.search_history = {}
        self.trending_searches = {}
        self.saved_searches = {}
        
        # Industry-specific terminology
        self.food_industry_terms = {
            "organic": ["organic", "bio", "ecological", "natural"],
            "kosher": ["kosher", "kashrut", "hechsher", "certified kosher"],
            "halal": ["halal", "halal certified", "islamic", "permissible"],
            "gluten_free": ["gluten-free", "gluten free", "celiac", "wheat-free"],
            "vegan": ["vegan", "plant-based", "dairy-free", "animal-free"],
            "non_gmo": ["non-gmo", "non gmo", "gmo-free", "genetically modified"],
            "fair_trade": ["fair trade", "fairtrade", "ethical sourcing"],
            "sustainable": ["sustainable", "eco-friendly", "environmentally friendly"],
            "local": ["local", "locally sourced", "farm-to-table", "regional"],
            "artisanal": ["artisanal", "handcrafted", "small-batch", "traditional"]
        }
        
        # Location patterns for natural language processing
        self.location_patterns = [
            r"in\s+([A-Za-z\s,]+)",
            r"from\s+([A-Za-z\s,]+)",
            r"based\s+in\s+([A-Za-z\s,]+)",
            r"located\s+in\s+([A-Za-z\s,]+)"
        ]
        
        # Certification patterns
        self.certification_patterns = [
            r"(kosher|halal|organic|gluten-free|vegan|non-gmo|fair trade)",
            r"(\w+)\s+certified",
            r"certified\s+(\w+)"
        ]

    async def search(self, query: str, filters: List[SearchFilter] = None, 
                    categories: List[SearchCategory] = None, limit: int = 20) -> Dict[str, Any]:
        """
        Perform intelligent search across all categories with comprehensive error handling
        """
        try:
            # Validate input parameters
            if not query or not query.strip():
                raise ValueError("Search query cannot be empty")
            
            if limit < 1 or limit > 100:
                limit = 20  # Default to safe limit
            
            # Parse natural language query
            try:
                parsed_query = await self._parse_natural_language_query(query)
            except Exception as e:
                logger.error(f"Error parsing natural language query: {e}")
                # Fallback to basic parsing
                parsed_query = {
                    "original_query": query,
                    "keywords": [word.strip() for word in query.split() if len(word.strip()) > 2],
                    "intent": "general"
                }
            
            # Apply filters
            if filters is None:
                filters = []
            
            # Determine search categories
            if categories is None:
                categories = list(SearchCategory)
            
            # Perform search across categories with error handling
            results = {}
            total_results = 0
            errors = []
            
            for category in categories:
                try:
                    category_results = await self._search_category(
                        category, parsed_query, filters, limit
                    )
                    results[category.value] = category_results
                    total_results += len(category_results)
                except Exception as e:
                    error_msg = f"Error searching category {category}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    results[category.value] = []
                    continue
            
            # Update search analytics (non-blocking)
            try:
                await self._update_search_analytics(query, total_results)
            except Exception as e:
                logger.warning(f"Failed to update search analytics: {e}")
            
            return {
                "query": query,
                "parsed_query": parsed_query,
                "results": results,
                "total_results": total_results,
                "filters_applied": [f.__dict__ for f in filters],
                "categories_searched": [c.value for c in categories],
                "search_id": self._generate_search_id(),
                "timestamp": datetime.now().isoformat(),
                "errors": errors if errors else None
            }
            
        except ValueError as e:
            logger.error(f"Search validation error: {e}")
            return {
                "error": "Search validation failed",
                "message": str(e),
                "results": {},
                "total_results": 0
            }
        except Exception as e:
            logger.error(f"Unexpected search error: {e}")
            return {
                "error": "Search service temporarily unavailable",
                "message": "Please try again later",
                "results": {},
                "total_results": 0
            }

    async def get_search_suggestions(self, partial_query: str, user_id: Optional[str] = None) -> List[SearchSuggestion]:
        """
        Get intelligent search suggestions based on partial query
        """
        try:
            suggestions = []
            
            # Get AI-powered suggestions
            ai_suggestions = await self._get_ai_suggestions(partial_query)
            suggestions.extend(ai_suggestions)
            
            # Get recent searches
            if user_id:
                recent_searches = await self._get_recent_searches(user_id, partial_query)
                suggestions.extend(recent_searches)
            
            # Get trending searches
            trending_searches = await self._get_trending_searches(partial_query)
            suggestions.extend(trending_searches)
            
            # Get database suggestions
            db_suggestions = await self._get_database_suggestions(partial_query)
            suggestions.extend(db_suggestions)
            
            # Sort by relevance and remove duplicates
            unique_suggestions = self._deduplicate_suggestions(suggestions)
            sorted_suggestions = sorted(unique_suggestions, key=lambda x: x.relevance_score, reverse=True)
            
            return sorted_suggestions[:10]  # Return top 10 suggestions
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            return []

    async def get_advanced_filters(self, query: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get available filters based on current search context
        """
        try:
            filters = {}
            
            # Location filters
            filters["locations"] = await self._get_location_filters()
            
            # Certification filters
            filters["certifications"] = await self._get_certification_filters()
            
            # Product category filters
            filters["product_categories"] = await self._get_product_category_filters()
            
            # Company size filters
            filters["company_sizes"] = [
                {"value": "startup", "label": "Startup (1-10 employees)", "count": 0},
                {"value": "small", "label": "Small (11-50 employees)", "count": 0},
                {"value": "medium", "label": "Medium (51-200 employees)", "count": 0},
                {"value": "large", "label": "Large (200+ employees)", "count": 0}
            ]
            
            # Business type filters
            filters["business_types"] = [
                {"value": "supplier", "label": "Supplier", "count": 0},
                {"value": "buyer", "label": "Buyer", "count": 0},
                {"value": "distributor", "label": "Distributor", "count": 0},
                {"value": "manufacturer", "label": "Manufacturer", "count": 0},
                {"value": "retailer", "label": "Retailer", "count": 0}
            ]
            
            # Update counts if query is provided
            if query:
                await self._update_filter_counts(filters, query)
            
            return filters
            
        except Exception as e:
            logger.error(f"Error getting advanced filters: {e}")
            return {}

    async def save_search(self, user_id: str, query: str, filters: List[SearchFilter] = None) -> bool:
        """
        Save search for user's search history
        """
        try:
            if user_id not in self.saved_searches:
                self.saved_searches[user_id] = []
            
            search_data = {
                "query": query,
                "filters": [f.__dict__ for f in filters] if filters else [],
                "timestamp": datetime.now().isoformat(),
                "search_id": self._generate_search_id()
            }
            
            self.saved_searches[user_id].append(search_data)
            
            # Keep only last 50 searches
            if len(self.saved_searches[user_id]) > 50:
                self.saved_searches[user_id] = self.saved_searches[user_id][-50:]
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving search: {e}")
            return False

    async def get_search_analytics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get search analytics and insights
        """
        try:
            analytics = {
                "total_searches": len(self.search_history),
                "trending_searches": await self._get_top_trending_searches(),
                "popular_categories": await self._get_popular_categories(),
                "search_success_rate": await self._calculate_success_rate(),
                "user_searches": []
            }
            
            if user_id and user_id in self.saved_searches:
                analytics["user_searches"] = self.saved_searches[user_id][-10:]
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting search analytics: {e}")
            return {}

    async def _parse_natural_language_query(self, query: str) -> Dict[str, Any]:
        """
        Parse natural language query to extract filters and intent
        """
        try:
            parsed = {
                "original_query": query,
                "keywords": [],
                "location": None,
                "certifications": [],
                "product_categories": [],
                "intent": "general"
            }
            
            # Extract location
            for pattern in self.location_patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    parsed["location"] = match.group(1).strip()
                    break
            
            # Extract certifications
            for pattern in self.certification_patterns:
                matches = re.findall(pattern, query, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        parsed["certifications"].extend([m.lower() for m in match if m])
                    else:
                        parsed["certifications"].append(match.lower())
            
            # Extract keywords (remove location and certification terms)
            keywords = query.lower()
            if parsed["location"]:
                keywords = keywords.replace(parsed["location"].lower(), "")
            for cert in parsed["certifications"]:
                keywords = keywords.replace(cert, "")
            
            # Clean up keywords
            keywords = re.sub(r'\s+', ' ', keywords).strip()
            parsed["keywords"] = [k.strip() for k in keywords.split() if len(k.strip()) > 2]
            
            # Determine search intent
            if any(term in query.lower() for term in ["supplier", "vendor", "source"]):
                parsed["intent"] = "find_supplier"
            elif any(term in query.lower() for term in ["buyer", "customer", "market"]):
                parsed["intent"] = "find_buyer"
            elif any(term in query.lower() for term in ["project", "analysis", "research"]):
                parsed["intent"] = "find_project"
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing natural language query: {e}")
            return {"original_query": query, "keywords": [], "intent": "general"}

    async def _search_category(self, category: SearchCategory, parsed_query: Dict[str, Any], 
                             filters: List[SearchFilter], limit: int) -> List[SearchResult]:
        """
        Search within a specific category
        """
        try:
            db = next(get_db())
            
            if category == SearchCategory.SUPPLIERS:
                return await self._search_suppliers(db, parsed_query, filters, limit)
            elif category == SearchCategory.BUYERS:
                return await self._search_buyers(db, parsed_query, filters, limit)
            elif category == SearchCategory.PROJECTS:
                return await self._search_projects(db, parsed_query, filters, limit)
            elif category == SearchCategory.PRODUCTS:
                return await self._search_products(db, parsed_query, filters, limit)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error searching category {category}: {e}")
            return []

    async def _search_suppliers(self, db: Session, parsed_query: Dict[str, Any], 
                              filters: List[SearchFilter], limit: int) -> List[SearchResult]:
        """
        Search suppliers with advanced filtering
        """
        try:
            query = db.query(Supplier)
            
            # Apply keyword search
            if parsed_query["keywords"]:
                keyword_conditions = []
                for keyword in parsed_query["keywords"]:
                    keyword_conditions.append(
                        or_(
                            Supplier.name.ilike(f"%{keyword}%"),
                            Supplier.description.ilike(f"%{keyword}%"),
                            Supplier.industry.ilike(f"%{keyword}%"),
                            Supplier.specializations.ilike(f"%{keyword}%")
                        )
                    )
                query = query.filter(or_(*keyword_conditions))
            
            # Apply location filter
            if parsed_query["location"]:
                query = query.filter(
                    or_(
                        Supplier.country.ilike(f"%{parsed_query['location']}%"),
                        Supplier.city.ilike(f"%{parsed_query['location']}%"),
                        Supplier.region.ilike(f"%{parsed_query['location']}%")
                    )
                )
            
            # Apply certification filters
            if parsed_query["certifications"]:
                cert_conditions = []
                for cert in parsed_query["certifications"]:
                    cert_conditions.append(Supplier.certifications.ilike(f"%{cert}%"))
                query = query.filter(or_(*cert_conditions))
            
            # Apply additional filters
            for filter_obj in filters:
                if filter_obj.type == SearchFilterType.LOCATION:
                    query = query.filter(
                        or_(
                            Supplier.country.ilike(f"%{filter_obj.value}%"),
                            Supplier.city.ilike(f"%{filter_obj.value}%")
                        )
                    )
                elif filter_obj.type == SearchFilterType.CERTIFICATION:
                    query = query.filter(Supplier.certifications.ilike(f"%{filter_obj.value}%"))
                elif filter_obj.type == SearchFilterType.COMPANY_SIZE:
                    query = query.filter(Supplier.company_size == filter_obj.value)
            
            # Order by relevance and limit results
            suppliers = query.limit(limit).all()
            
            # Convert to SearchResult objects
            results = []
            for supplier in suppliers:
                relevance_score = self._calculate_relevance_score(supplier, parsed_query)
                result = SearchResult(
                    id=str(supplier.id),
                    title=supplier.name,
                    description=supplier.description or "",
                    category=SearchCategory.SUPPLIERS,
                    relevance_score=relevance_score,
                    metadata={
                        "industry": supplier.industry,
                        "location": f"{supplier.city}, {supplier.country}",
                        "certifications": supplier.certifications,
                        "company_size": supplier.company_size,
                        "rating": getattr(supplier, 'rating', 0)
                    },
                    url=f"/suppliers/{supplier.id}",
                    badges=self._extract_badges(supplier)
                )
                results.append(result)
            
            # Sort by relevance score
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            return results
            
        except Exception as e:
            logger.error(f"Error searching suppliers: {e}")
            return []

    async def _search_buyers(self, db: Session, parsed_query: Dict[str, Any], 
                           filters: List[SearchFilter], limit: int) -> List[SearchResult]:
        """
        Search buyers with advanced filtering
        """
        try:
            query = db.query(Buyer)
            
            # Apply keyword search
            if parsed_query["keywords"]:
                keyword_conditions = []
                for keyword in parsed_query["keywords"]:
                    keyword_conditions.append(
                        or_(
                            Buyer.name.ilike(f"%{keyword}%"),
                            Buyer.description.ilike(f"%{keyword}%"),
                            Buyer.industry.ilike(f"%{keyword}%"),
                            Buyer.requirements.ilike(f"%{keyword}%")
                        )
                    )
                query = query.filter(or_(*keyword_conditions))
            
            # Apply location filter
            if parsed_query["location"]:
                query = query.filter(
                    or_(
                        Buyer.country.ilike(f"%{parsed_query['location']}%"),
                        Buyer.city.ilike(f"%{parsed_query['location']}%")
                    )
                )
            
            # Apply additional filters
            for filter_obj in filters:
                if filter_obj.type == SearchFilterType.LOCATION:
                    query = query.filter(
                        or_(
                            Buyer.country.ilike(f"%{filter_obj.value}%"),
                            Buyer.city.ilike(f"%{filter_obj.value}%")
                        )
                    )
                elif filter_obj.type == SearchFilterType.COMPANY_SIZE:
                    query = query.filter(Buyer.company_size == filter_obj.value)
            
            # Order by relevance and limit results
            buyers = query.limit(limit).all()
            
            # Convert to SearchResult objects
            results = []
            for buyer in buyers:
                relevance_score = self._calculate_relevance_score(buyer, parsed_query)
                result = SearchResult(
                    id=str(buyer.id),
                    title=buyer.name,
                    description=buyer.description or "",
                    category=SearchCategory.BUYERS,
                    relevance_score=relevance_score,
                    metadata={
                        "industry": buyer.industry,
                        "location": f"{buyer.city}, {buyer.country}",
                        "requirements": buyer.requirements,
                        "company_size": buyer.company_size
                    },
                    url=f"/buyers/{buyer.id}",
                    badges=self._extract_badges(buyer)
                )
                results.append(result)
            
            # Sort by relevance score
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            return results
            
        except Exception as e:
            logger.error(f"Error searching buyers: {e}")
            return []

    async def _search_projects(self, db: Session, parsed_query: Dict[str, Any], 
                             filters: List[SearchFilter], limit: int) -> List[SearchResult]:
        """
        Search projects with advanced filtering
        """
        try:
            query = db.query(Project)
            
            # Apply keyword search
            if parsed_query["keywords"]:
                keyword_conditions = []
                for keyword in parsed_query["keywords"]:
                    keyword_conditions.append(
                        or_(
                            Project.name.ilike(f"%{keyword}%"),
                            Project.description.ilike(f"%{keyword}%"),
                            Project.search_type.ilike(f"%{keyword}%")
                        )
                    )
                query = query.filter(or_(*keyword_conditions))
            
            # Apply additional filters
            for filter_obj in filters:
                if filter_obj.type == SearchFilterType.DATE_RANGE:
                    if filter_obj.value.get("start_date"):
                        query = query.filter(Project.created_at >= filter_obj.value["start_date"])
                    if filter_obj.value.get("end_date"):
                        query = query.filter(Project.created_at <= filter_obj.value["end_date"])
            
            # Order by creation date and limit results
            projects = query.order_by(desc(Project.created_at)).limit(limit).all()
            
            # Convert to SearchResult objects
            results = []
            for project in projects:
                relevance_score = self._calculate_relevance_score(project, parsed_query)
                result = SearchResult(
                    id=str(project.id),
                    title=project.name,
                    description=project.description or "",
                    category=SearchCategory.PROJECTS,
                    relevance_score=relevance_score,
                    metadata={
                        "search_type": project.search_type,
                        "created_at": project.created_at.isoformat(),
                        "status": project.status,
                        "user_id": project.user_id
                    },
                    url=f"/projects/{project.id}",
                    badges=[project.search_type] if project.search_type else []
                )
                results.append(result)
            
            # Sort by relevance score
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            return results
            
        except Exception as e:
            logger.error(f"Error searching projects: {e}")
            return []

    async def _search_products(self, db: Session, parsed_query: Dict[str, Any], 
                             filters: List[SearchFilter], limit: int) -> List[SearchResult]:
        """
        Search products (placeholder - would integrate with product database)
        """
        # This would integrate with a product database or external API
        # For now, return empty results
        return []

    async def _get_ai_suggestions(self, partial_query: str) -> List[SearchSuggestion]:
        """
        Get AI-powered search suggestions with predictive capabilities
        """
        try:
            suggestions = []
            
            # Try OpenAI integration first for advanced AI suggestions
            if self.openai_service.client:
                try:
                    prompt = f"""
                    Generate intelligent search suggestions for a food industry platform based on the partial query: "{partial_query}"
                    
                    Consider:
                    - Food industry terminology (organic, halal, kosher, gluten-free, etc.)
                    - Product categories (vegetables, fruits, meat, dairy, etc.)
                    - Business types (suppliers, buyers, distributors, etc.)
                    - Certifications and standards
                    - Geographic locations
                    - Seasonal trends
                    - Market demands
                    - Predictive patterns based on user behavior
                    
                    Return 8-12 relevant suggestions in JSON format with enhanced metadata:
                    {{
                        "suggestions": [
                            {{
                                "text": "suggestion text",
                                "category": "suppliers|buyers|products|projects|certifications",
                                "relevance": 0.9,
                                "metadata": {{
                                    "confidence": 0.95,
                                    "trending": true,
                                    "seasonal": false,
                                    "market_demand": "high",
                                    "predicted_clicks": 0.8
                                }}
                            }}
                        ],
                        "predictive_insights": {{
                            "trending_topics": ["organic", "sustainable"],
                            "seasonal_factors": ["summer_vegetables"],
                            "market_opportunities": ["plant_based"],
                            "user_intent": "find_suppliers"
                        }}
                    }}
                    """
                    
                    response = self.openai_service.client.chat.completions.create(
                        model=self.openai_service.deployment_name,
                        messages=[
                            {"role": "system", "content": "You are an expert food industry search assistant with predictive analytics capabilities."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.2,
                        max_tokens=400,
                        response_format={"type": "json_object"}
                    )
                    
                    suggestions_data = json.loads(response.choices[0].message.content)
                    
                    for item in suggestions_data.get("suggestions", []):
                        suggestion = SearchSuggestion(
                            text=item.get("text", ""),
                            category=SearchCategory(item.get("category", "suppliers")),
                            relevance_score=item.get("relevance", 0.5),
                            metadata=item.get("metadata", {}),
                            type="ai_suggestion"
                        )
                        suggestions.append(suggestion)
                    
                    # Store predictive insights for future use
                    if "predictive_insights" in suggestions_data:
                        await self._store_predictive_insights(suggestions_data["predictive_insights"])
                    
                    logger.info(f"Generated {len(suggestions)} AI-powered suggestions")
                    return suggestions
                    
                except Exception as e:
                    logger.warning(f"OpenAI suggestions failed, falling back to basic suggestions: {e}")
            
            # Fallback to enhanced basic suggestions
            suggestions = await self._get_enhanced_basic_suggestions(partial_query)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting AI suggestions: {e}")
            return []

    async def _get_recent_searches(self, user_id: str, partial_query: str) -> List[SearchSuggestion]:
        """
        Get user's recent searches
        """
        try:
            if user_id not in self.saved_searches:
                return []
            
            recent = []
            for search in self.saved_searches[user_id][-5:]:  # Last 5 searches
                if partial_query.lower() in search["query"].lower():
                    recent.append(SearchSuggestion(
                        text=search["query"],
                        category=SearchCategory.PROJECTS,
                        relevance_score=0.6,
                        metadata={"type": "recent_search", "timestamp": search["timestamp"]}
                    ))
            
            return recent
            
        except Exception as e:
            logger.error(f"Error getting recent searches: {e}")
            return []

    async def _get_trending_searches(self, partial_query: str) -> List[SearchSuggestion]:
        """
        Get trending searches
        """
        try:
            trending = []
            
            # Simulate trending searches (in production, this would be based on actual analytics)
            trending_terms = [
                "organic honey",
                "kosher meat",
                "gluten-free pasta",
                "sustainable seafood",
                "fair trade chocolate",
                "local produce",
                "artisanal bread",
                "vegan cheese"
            ]
            
            for term in trending_terms:
                if partial_query.lower() in term.lower():
                    trending.append(SearchSuggestion(
                        text=term,
                        category=SearchCategory.SUPPLIERS,
                        relevance_score=0.5,
                        metadata={"type": "trending"}
                    ))
            
            return trending
            
        except Exception as e:
            logger.error(f"Error getting trending searches: {e}")
            return []

    async def _get_enhanced_basic_suggestions(self, partial_query: str) -> List[SearchSuggestion]:
        """
        Enhanced basic suggestions with predictive patterns
        """
        try:
            suggestions = []
            
            # Generate suggestions based on food industry terminology
            for category, terms in self.food_industry_terms.items():
                for term in terms:
                    if partial_query.lower() in term.lower():
                        suggestions.append(SearchSuggestion(
                            text=f"{partial_query} {category}",
                            category=SearchCategory.SUPPLIERS,
                            relevance_score=0.8,
                            metadata={
                                "type": "industry_term", 
                                "category": category,
                                "confidence": 0.85,
                                "trending": True
                            }
                        ))
            
            # Enhanced common food industry search patterns with predictive elements
            enhanced_patterns = [
                {"text": "organic suppliers", "category": "suppliers", "trending": True, "seasonal": False},
                {"text": "kosher certified", "category": "certifications", "trending": True, "seasonal": False},
                {"text": "gluten-free products", "category": "products", "trending": True, "seasonal": False},
                {"text": "local farmers", "category": "suppliers", "trending": True, "seasonal": True},
                {"text": "sustainable sourcing", "category": "suppliers", "trending": True, "seasonal": False},
                {"text": "fair trade coffee", "category": "products", "trending": True, "seasonal": False},
                {"text": "artisanal cheese", "category": "products", "trending": True, "seasonal": False},
                {"text": "fresh produce", "category": "products", "trending": True, "seasonal": True},
                {"text": "plant-based alternatives", "category": "products", "trending": True, "seasonal": False},
                {"text": "regenerative agriculture", "category": "suppliers", "trending": True, "seasonal": False}
            ]
            
            for pattern in enhanced_patterns:
                if partial_query.lower() in pattern["text"].lower():
                    suggestions.append(SearchSuggestion(
                        text=pattern["text"],
                        category=SearchCategory(pattern["category"]),
                        relevance_score=0.7,
                        metadata={
                            "type": "enhanced_pattern",
                            "trending": pattern["trending"],
                            "seasonal": pattern["seasonal"],
                            "predicted_clicks": 0.75
                        }
                    ))
            
            # Add seasonal suggestions based on current date
            seasonal_suggestions = await self._get_seasonal_suggestions(partial_query)
            suggestions.extend(seasonal_suggestions)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting enhanced basic suggestions: {e}")
            return []
    
    async def _get_seasonal_suggestions(self, partial_query: str) -> List[SearchSuggestion]:
        """
        Get seasonal suggestions based on current date
        """
        try:
            suggestions = []
            current_month = datetime.now().month
            
            seasonal_patterns = {
                "spring": [3, 4, 5],
                "summer": [6, 7, 8],
                "fall": [9, 10, 11],
                "winter": [12, 1, 2]
            }
            
            current_season = None
            for season, months in seasonal_patterns.items():
                if current_month in months:
                    current_season = season
                    break
            
            if current_season:
                seasonal_terms = {
                    "spring": ["spring vegetables", "fresh herbs", "asparagus", "strawberries"],
                    "summer": ["summer fruits", "tomatoes", "corn", "berries"],
                    "fall": ["pumpkins", "apples", "squash", "root vegetables"],
                    "winter": ["winter squash", "citrus fruits", "root vegetables", "winter greens"]
                }
                
                for term in seasonal_terms.get(current_season, []):
                    if partial_query.lower() in term.lower():
                        suggestions.append(SearchSuggestion(
                            text=term,
                            category=SearchCategory.PRODUCTS,
                            relevance_score=0.6,
                            metadata={
                                "type": "seasonal",
                                "season": current_season,
                                "trending": True,
                                "seasonal": True
                            }
                        ))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting seasonal suggestions: {e}")
            return []
    
    async def _store_predictive_insights(self, insights: Dict[str, Any]):
        """
        Store predictive insights for future use
        """
        try:
            # In a production environment, this would store insights in a database
            # For now, we'll log them for demonstration
            logger.info(f"Storing predictive insights: {insights}")
            
            # Store trending topics
            if "trending_topics" in insights:
                for topic in insights["trending_topics"]:
                    if topic not in self.trending_searches:
                        self.trending_searches[topic] = {"count": 1, "first_seen": datetime.now()}
                    else:
                        self.trending_searches[topic]["count"] += 1
            
            # Store seasonal factors
            if "seasonal_factors" in insights:
                logger.info(f"Seasonal factors detected: {insights['seasonal_factors']}")
            
            # Store market opportunities
            if "market_opportunities" in insights:
                logger.info(f"Market opportunities identified: {insights['market_opportunities']}")
            
        except Exception as e:
            logger.error(f"Error storing predictive insights: {e}")

    async def _get_database_suggestions(self, partial_query: str) -> List[SearchSuggestion]:
        """
        Get suggestions from database entities
        """
        try:
            suggestions = []
            db = next(get_db())
            
            # Get supplier suggestions
            suppliers = db.query(Supplier.name).filter(
                Supplier.name.ilike(f"%{partial_query}%")
            ).limit(5).all()
            
            for supplier in suppliers:
                suggestions.append(SearchSuggestion(
                    text=supplier.name,
                    category=SearchCategory.SUPPLIERS,
                    relevance_score=0.9,
                    metadata={"type": "database_entity", "entity_type": "supplier"}
                ))
            
            # Get buyer suggestions
            buyers = db.query(Buyer.name).filter(
                Buyer.name.ilike(f"%{partial_query}%")
            ).limit(5).all()
            
            for buyer in buyers:
                suggestions.append(SearchSuggestion(
                    text=buyer.name,
                    category=SearchCategory.BUYERS,
                    relevance_score=0.9,
                    metadata={"type": "database_entity", "entity_type": "buyer"}
                ))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting database suggestions: {e}")
            return []

    def _deduplicate_suggestions(self, suggestions: List[SearchSuggestion]) -> List[SearchSuggestion]:
        """
        Remove duplicate suggestions
        """
        seen = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            if suggestion.text not in seen:
                seen.add(suggestion.text)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions

    def _calculate_relevance_score(self, entity: Any, parsed_query: Dict[str, Any]) -> float:
        """
        Calculate relevance score for search results
        """
        try:
            score = 0.0
            
            # Base score
            score += 0.1
            
            # Keyword matching
            if parsed_query["keywords"]:
                for keyword in parsed_query["keywords"]:
                    if hasattr(entity, 'name') and keyword.lower() in entity.name.lower():
                        score += 0.3
                    if hasattr(entity, 'description') and entity.description and keyword.lower() in entity.description.lower():
                        score += 0.2
                    if hasattr(entity, 'industry') and keyword.lower() in entity.industry.lower():
                        score += 0.2
            
            # Location matching
            if parsed_query["location"]:
                if hasattr(entity, 'country') and parsed_query["location"].lower() in entity.country.lower():
                    score += 0.3
                if hasattr(entity, 'city') and parsed_query["location"].lower() in entity.city.lower():
                    score += 0.4
            
            # Certification matching
            if parsed_query["certifications"] and hasattr(entity, 'certifications'):
                for cert in parsed_query["certifications"]:
                    if cert.lower() in entity.certifications.lower():
                        score += 0.3
            
            # Recency boost for projects
            if hasattr(entity, 'created_at'):
                days_old = (datetime.now() - entity.created_at).days
                if days_old < 7:
                    score += 0.2
                elif days_old < 30:
                    score += 0.1
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Error calculating relevance score: {e}")
            return 0.1

    def _extract_badges(self, entity: Any) -> List[str]:
        """
        Extract badges for search results
        """
        badges = []
        
        try:
            # Certification badges
            if hasattr(entity, 'certifications') and entity.certifications:
                certs = entity.certifications.lower()
                if 'kosher' in certs:
                    badges.append('Kosher')
                if 'halal' in certs:
                    badges.append('Halal')
                if 'organic' in certs:
                    badges.append('Organic')
                if 'gluten-free' in certs:
                    badges.append('Gluten-Free')
            
            # Company size badges
            if hasattr(entity, 'company_size'):
                if entity.company_size == 'large':
                    badges.append('Enterprise')
                elif entity.company_size == 'medium':
                    badges.append('Mid-Size')
                elif entity.company_size == 'small':
                    badges.append('Small Business')
            
            # Verification badges
            if hasattr(entity, 'verified') and entity.verified:
                badges.append('Verified')
            
        except Exception as e:
            logger.error(f"Error extracting badges: {e}")
        
        return badges

    async def _get_location_filters(self) -> List[Dict[str, Any]]:
        """
        Get available location filters
        """
        try:
            db = next(get_db())
            
            # Get unique countries
            countries = db.query(Supplier.country).distinct().filter(
                Supplier.country.isnot(None)
            ).limit(20).all()
            
            return [{"value": country[0], "label": country[0], "count": 0} for country in countries]
            
        except Exception as e:
            logger.error(f"Error getting location filters: {e}")
            return []

    async def _get_certification_filters(self) -> List[Dict[str, Any]]:
        """
        Get available certification filters
        """
        certifications = [
            {"value": "kosher", "label": "Kosher Certified", "count": 0},
            {"value": "halal", "label": "Halal Certified", "count": 0},
            {"value": "organic", "label": "Organic Certified", "count": 0},
            {"value": "gluten-free", "label": "Gluten-Free", "count": 0},
            {"value": "vegan", "label": "Vegan", "count": 0},
            {"value": "non-gmo", "label": "Non-GMO", "count": 0},
            {"value": "fair-trade", "label": "Fair Trade", "count": 0}
        ]
        
        return certifications

    async def _get_product_category_filters(self) -> List[Dict[str, Any]]:
        """
        Get available product category filters
        """
        categories = [
            {"value": "dairy", "label": "Dairy Products", "count": 0},
            {"value": "meat", "label": "Meat & Poultry", "count": 0},
            {"value": "seafood", "label": "Seafood", "count": 0},
            {"value": "produce", "label": "Fresh Produce", "count": 0},
            {"value": "grains", "label": "Grains & Cereals", "count": 0},
            {"value": "beverages", "label": "Beverages", "count": 0},
            {"value": "snacks", "label": "Snacks & Confectionery", "count": 0},
            {"value": "condiments", "label": "Condiments & Sauces", "count": 0},
            {"value": "bakery", "label": "Bakery Products", "count": 0},
            {"value": "frozen", "label": "Frozen Foods", "count": 0}
        ]
        
        return categories

    async def _update_filter_counts(self, filters: Dict[str, List[Dict[str, Any]]], query: str):
        """
        Update filter counts based on current search
        """
        # This would calculate actual counts based on the search query
        # For now, we'll leave counts at 0
        pass

    async def _update_search_analytics(self, query: str, result_count: int):
        """
        Update search analytics
        """
        try:
            search_id = self._generate_search_id()
            self.search_history[search_id] = {
                "query": query,
                "result_count": result_count,
                "timestamp": datetime.now().isoformat()
            }
            
            # Update trending searches
            if query not in self.trending_searches:
                self.trending_searches[query] = 0
            self.trending_searches[query] += 1
            
        except Exception as e:
            logger.error(f"Error updating search analytics: {e}")

    async def _get_top_trending_searches(self) -> List[Dict[str, Any]]:
        """
        Get top trending searches
        """
        try:
            sorted_trending = sorted(
                self.trending_searches.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            return [
                {"query": query, "count": count} 
                for query, count in sorted_trending[:10]
            ]
            
        except Exception as e:
            logger.error(f"Error getting trending searches: {e}")
            return []

    async def _get_popular_categories(self) -> List[Dict[str, Any]]:
        """
        Get popular search categories
        """
        # This would be calculated from actual search data
        return [
            {"category": "suppliers", "count": 150},
            {"category": "buyers", "count": 89},
            {"category": "projects", "count": 67},
            {"category": "products", "count": 45}
        ]

    async def _calculate_success_rate(self) -> float:
        """
        Calculate search success rate
        """
        # This would be calculated from actual search data
        return 0.85

    def _generate_search_id(self) -> str:
        """
        Generate unique search ID
        """
        import uuid
        return str(uuid.uuid4())


# Global search service instance
search_service = IntelligentSearchService() 