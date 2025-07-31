"""
Filter Manager Module
Handles search filters and faceted search
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import Session

from .models import SearchFilter, SearchFilterType

logger = logging.getLogger(__name__)


class FilterManager:
    """
    Manages search filters and facets
    """
    
    def __init__(self):
        # Define available filters for each category
        self.category_filters = {
            "suppliers": [
                SearchFilterType.LOCATION,
                SearchFilterType.CERTIFICATION,
                SearchFilterType.COMPANY_SIZE,
                SearchFilterType.BUSINESS_TYPE,
                SearchFilterType.RATING
            ],
            "buyers": [
                SearchFilterType.LOCATION,
                SearchFilterType.COMPANY_SIZE,
                SearchFilterType.BUSINESS_TYPE
            ],
            "products": [
                SearchFilterType.PRODUCT_CATEGORY,
                SearchFilterType.CERTIFICATION,
                SearchFilterType.PRICE_RANGE,
                SearchFilterType.LOCATION
            ],
            "projects": [
                SearchFilterType.DATE_RANGE,
                SearchFilterType.PRICE_RANGE,
                SearchFilterType.LOCATION
            ]
        }
        
        # Define filter value mappings
        self.filter_values = {
            SearchFilterType.COMPANY_SIZE: ["small", "medium", "large", "enterprise"],
            SearchFilterType.BUSINESS_TYPE: ["manufacturer", "distributor", "retailer", "wholesaler"],
            SearchFilterType.CERTIFICATION: ["organic", "kosher", "halal", "gluten-free", "fair-trade"],
            SearchFilterType.PRODUCT_CATEGORY: [
                "fruits", "vegetables", "dairy", "meat", "seafood",
                "grains", "beverages", "snacks", "frozen", "bakery"
            ]
        }
    
    def get_available_filters(self, category: str) -> List[Dict[str, Any]]:
        """Get available filters for a category"""
        filters = []
        
        filter_types = self.category_filters.get(category, [])
        
        for filter_type in filter_types:
            filter_info = {
                "type": filter_type.value,
                "label": self._get_filter_label(filter_type),
                "options": self._get_filter_options(filter_type)
            }
            filters.append(filter_info)
        
        return filters
    
    def apply_filters(self, query, filters: List[SearchFilter], model_class):
        """Apply filters to a SQLAlchemy query"""
        for filter_item in filters:
            query = self._apply_single_filter(query, filter_item, model_class)
        
        return query
    
    def _apply_single_filter(self, query, filter_item: SearchFilter, model_class):
        """Apply a single filter to the query"""
        try:
            if filter_item.type == SearchFilterType.LOCATION:
                # Location-based filtering
                if hasattr(model_class, 'city') and hasattr(model_class, 'country'):
                    location_conditions = or_(
                        model_class.city.ilike(f"%{filter_item.value}%"),
                        model_class.country.ilike(f"%{filter_item.value}%")
                    )
                    query = query.filter(location_conditions)
            
            elif filter_item.type == SearchFilterType.CERTIFICATION:
                # Certification filtering
                if hasattr(model_class, 'certifications'):
                    query = query.filter(
                        model_class.certifications.contains(filter_item.value)
                    )
            
            elif filter_item.type == SearchFilterType.COMPANY_SIZE:
                # Company size filtering
                if hasattr(model_class, 'company_size'):
                    query = query.filter(
                        model_class.company_size == filter_item.value
                    )
            
            elif filter_item.type == SearchFilterType.PRICE_RANGE:
                # Price range filtering
                if hasattr(model_class, 'price'):
                    if isinstance(filter_item.value, dict):
                        if 'min' in filter_item.value:
                            query = query.filter(
                                model_class.price >= filter_item.value['min']
                            )
                        if 'max' in filter_item.value:
                            query = query.filter(
                                model_class.price <= filter_item.value['max']
                            )
            
            elif filter_item.type == SearchFilterType.DATE_RANGE:
                # Date range filtering
                if hasattr(model_class, 'created_at'):
                    if filter_item.value == "today":
                        start_date = datetime.now().replace(hour=0, minute=0, second=0)
                        query = query.filter(model_class.created_at >= start_date)
                    elif filter_item.value == "week":
                        start_date = datetime.now() - timedelta(days=7)
                        query = query.filter(model_class.created_at >= start_date)
                    elif filter_item.value == "month":
                        start_date = datetime.now() - timedelta(days=30)
                        query = query.filter(model_class.created_at >= start_date)
            
            elif filter_item.type == SearchFilterType.RATING:
                # Rating filtering
                if hasattr(model_class, 'rating'):
                    if filter_item.operator == "gte":
                        query = query.filter(model_class.rating >= filter_item.value)
                    else:
                        query = query.filter(model_class.rating == filter_item.value)
            
        except Exception as e:
            logger.error(f"Error applying filter {filter_item.type}: {e}")
        
        return query
    
    def _get_filter_label(self, filter_type: SearchFilterType) -> str:
        """Get human-readable label for filter type"""
        labels = {
            SearchFilterType.LOCATION: "Location",
            SearchFilterType.CERTIFICATION: "Certification",
            SearchFilterType.PRODUCT_CATEGORY: "Category",
            SearchFilterType.COMPANY_SIZE: "Company Size",
            SearchFilterType.BUSINESS_TYPE: "Business Type",
            SearchFilterType.DATE_RANGE: "Date Range",
            SearchFilterType.PRICE_RANGE: "Price Range",
            SearchFilterType.RATING: "Rating"
        }
        return labels.get(filter_type, filter_type.value.title())
    
    def _get_filter_options(self, filter_type: SearchFilterType) -> List[Dict[str, str]]:
        """Get available options for a filter type"""
        options = []
        
        if filter_type in self.filter_values:
            for value in self.filter_values[filter_type]:
                options.append({
                    "value": value,
                    "label": value.replace("-", " ").title()
                })
        elif filter_type == SearchFilterType.DATE_RANGE:
            options = [
                {"value": "today", "label": "Today"},
                {"value": "week", "label": "This Week"},
                {"value": "month", "label": "This Month"},
                {"value": "custom", "label": "Custom Range"}
            ]
        elif filter_type == SearchFilterType.RATING:
            options = [
                {"value": "5", "label": "5 Stars"},
                {"value": "4", "label": "4+ Stars"},
                {"value": "3", "label": "3+ Stars"}
            ]
        
        return options
    
    def parse_filter_string(self, filter_string: str) -> List[SearchFilter]:
        """Parse filter string from URL parameters"""
        filters = []
        
        try:
            # Expected format: "type:value,type:value"
            if not filter_string:
                return filters
            
            filter_parts = filter_string.split(',')
            
            for part in filter_parts:
                if ':' in part:
                    type_str, value = part.split(':', 1)
                    
                    # Try to match filter type
                    for filter_type in SearchFilterType:
                        if filter_type.value == type_str:
                            filters.append(SearchFilter(
                                type=filter_type,
                                value=value
                            ))
                            break
            
        except Exception as e:
            logger.error(f"Error parsing filter string: {e}")
        
        return filters
    
    def build_filter_string(self, filters: List[SearchFilter]) -> str:
        """Build URL-friendly filter string"""
        filter_parts = []
        
        for filter_item in filters:
            if isinstance(filter_item.value, dict):
                # Handle complex values like price ranges
                value_str = "-".join(str(v) for v in filter_item.value.values())
            else:
                value_str = str(filter_item.value)
            
            filter_parts.append(f"{filter_item.type.value}:{value_str}")
        
        return ",".join(filter_parts)
    
    def get_facet_counts(self, query, filter_type: SearchFilterType, model_class) -> Dict[str, int]:
        """Get facet counts for a filter type"""
        facets = {}
        
        try:
            if filter_type == SearchFilterType.CERTIFICATION:
                # Count certifications
                if hasattr(model_class, 'certifications'):
                    # This is simplified - in reality you'd need to handle JSON fields properly
                    for cert in self.filter_values[SearchFilterType.CERTIFICATION]:
                        count = query.filter(
                            model_class.certifications.contains(cert)
                        ).count()
                        if count > 0:
                            facets[cert] = count
            
            elif filter_type == SearchFilterType.COMPANY_SIZE:
                # Count by company size
                if hasattr(model_class, 'company_size'):
                    size_counts = query.with_entities(
                        model_class.company_size,
                        func.count(model_class.id)
                    ).group_by(model_class.company_size).all()
                    
                    for size, count in size_counts:
                        if size:
                            facets[size] = count
            
            elif filter_type == SearchFilterType.LOCATION:
                # Count by location (top 10 cities)
                if hasattr(model_class, 'city'):
                    city_counts = query.with_entities(
                        model_class.city,
                        func.count(model_class.id)
                    ).group_by(model_class.city).order_by(
                        func.count(model_class.id).desc()
                    ).limit(10).all()
                    
                    for city, count in city_counts:
                        if city:
                            facets[city] = count
            
        except Exception as e:
            logger.error(f"Error getting facet counts: {e}")
        
        return facets