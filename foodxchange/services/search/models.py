"""
Search Models and Data Classes
Defines the data structures used by the search service
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


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