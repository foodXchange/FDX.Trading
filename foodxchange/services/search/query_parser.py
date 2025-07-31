"""
Query Parser Module
Handles natural language query parsing and analysis
"""

import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class QueryParser:
    """
    Parses and analyzes search queries
    """
    
    def __init__(self):
        # Industry-specific terminology
        self.food_industry_terms = {
            "organic": ["organic", "bio", "ecological", "natural"],
            "kosher": ["kosher", "kashrut", "hechsher", "certified kosher"],
            "halal": ["halal", "halal certified", "islamic", "permissible"],
            "gluten_free": ["gluten-free", "gluten free", "celiac", "wheat-free"],
            "vegan": ["vegan", "plant-based", "no animal", "cruelty-free"],
            "local": ["local", "locally sourced", "regional", "nearby"],
            "sustainable": ["sustainable", "eco-friendly", "green", "environmental"],
            "fair_trade": ["fair trade", "fairtrade", "ethical", "responsible"]
        }
        
        # Common search patterns
        self.patterns = {
            "location": re.compile(r'\b(in|from|near|around)\s+([A-Z][a-zA-Z\s]+)', re.IGNORECASE),
            "certification": re.compile(r'\b(certified|certification|cert)\s+(\w+)', re.IGNORECASE),
            "price": re.compile(r'\$?\d+(?:\.\d+)?(?:\s*-\s*\$?\d+(?:\.\d+)?)?'),
            "quantity": re.compile(r'\b(\d+)\s*(kg|lb|ton|unit|case|pallet)', re.IGNORECASE),
            "product": re.compile(r'\b(fresh|frozen|dried|canned|processed)\s+(\w+)', re.IGNORECASE),
            "date": re.compile(r'\b(today|tomorrow|this week|next week|this month)', re.IGNORECASE),
            "company_size": re.compile(r'\b(small|medium|large|enterprise)\s*(?:size|company)?', re.IGNORECASE)
        }
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Parse a natural language query into structured components
        """
        try:
            query_lower = query.lower()
            
            parsed = {
                "original_query": query,
                "normalized_query": self._normalize_query(query),
                "intent": self._detect_intent(query_lower),
                "entities": self._extract_entities(query),
                "filters": self._extract_filters(query),
                "keywords": self._extract_keywords(query),
                "industry_terms": self._extract_industry_terms(query_lower),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add query complexity score
            parsed["complexity_score"] = self._calculate_complexity(parsed)
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            return {
                "original_query": query,
                "normalized_query": query.lower().strip(),
                "intent": "general_search",
                "entities": {},
                "filters": [],
                "keywords": query.split(),
                "industry_terms": [],
                "complexity_score": 0
            }
    
    def _normalize_query(self, query: str) -> str:
        """Normalize the query for better matching"""
        # Remove extra spaces
        normalized = " ".join(query.split())
        
        # Expand common abbreviations
        abbreviations = {
            "qty": "quantity",
            "cert": "certification",
            "org": "organic",
            "min": "minimum",
            "max": "maximum"
        }
        
        for abbr, full in abbreviations.items():
            normalized = re.sub(rf'\b{abbr}\b', full, normalized, flags=re.IGNORECASE)
        
        return normalized.lower().strip()
    
    def _detect_intent(self, query: str) -> str:
        """Detect the user's search intent"""
        intents = {
            "find_supplier": ["supplier", "vendor", "provider", "source", "buy from"],
            "find_buyer": ["buyer", "customer", "client", "sell to", "market for"],
            "check_price": ["price", "cost", "rate", "quote", "pricing"],
            "verify_certification": ["certified", "certification", "verify", "authentic"],
            "track_order": ["order", "shipment", "delivery", "tracking", "status"],
            "compare": ["compare", "versus", "vs", "difference", "better"],
            "browse": ["browse", "explore", "show", "list", "all"]
        }
        
        for intent, keywords in intents.items():
            if any(keyword in query for keyword in keywords):
                return intent
        
        return "general_search"
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract named entities from the query"""
        entities = {
            "locations": [],
            "products": [],
            "companies": [],
            "certifications": [],
            "dates": [],
            "quantities": []
        }
        
        # Extract locations
        location_match = self.patterns["location"].findall(query)
        if location_match:
            entities["locations"] = [match[1].strip() for match in location_match]
        
        # Extract certifications
        cert_match = self.patterns["certification"].findall(query)
        if cert_match:
            entities["certifications"] = [match[1].strip() for match in cert_match]
        
        # Extract quantities
        qty_match = self.patterns["quantity"].findall(query)
        if qty_match:
            entities["quantities"] = [f"{match[0]} {match[1]}" for match in qty_match]
        
        # Extract product mentions
        product_match = self.patterns["product"].findall(query)
        if product_match:
            entities["products"] = [f"{match[0]} {match[1]}" for match in product_match]
        
        return entities
    
    def _extract_filters(self, query: str) -> List[Dict[str, Any]]:
        """Extract search filters from the query"""
        filters = []
        
        # Location filter
        if self.patterns["location"].search(query):
            location_match = self.patterns["location"].search(query)
            if location_match:
                filters.append({
                    "type": "location",
                    "value": location_match.group(2).strip(),
                    "operator": "near"
                })
        
        # Price filter
        price_match = self.patterns["price"].search(query)
        if price_match:
            price_str = price_match.group(0)
            if "-" in price_str:
                min_price, max_price = price_str.split("-")
                filters.append({
                    "type": "price_range",
                    "min": self._parse_price(min_price),
                    "max": self._parse_price(max_price)
                })
            else:
                filters.append({
                    "type": "price",
                    "value": self._parse_price(price_str),
                    "operator": "lte"
                })
        
        # Company size filter
        size_match = self.patterns["company_size"].search(query)
        if size_match:
            filters.append({
                "type": "company_size",
                "value": size_match.group(1).lower()
            })
        
        return filters
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from the query"""
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "about", "as", "is", "was", "are", "were",
            "been", "be", "have", "has", "had", "do", "does", "did", "will", "would",
            "should", "could", "may", "might", "must", "can", "i", "me", "we", "us"
        }
        
        words = query.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords
    
    def _extract_industry_terms(self, query: str) -> List[str]:
        """Extract food industry specific terms"""
        found_terms = []
        
        for term_key, term_variations in self.food_industry_terms.items():
            if any(variation in query for variation in term_variations):
                found_terms.append(term_key)
        
        return found_terms
    
    def _parse_price(self, price_str: str) -> float:
        """Parse price string to float"""
        try:
            # Remove currency symbols and spaces
            cleaned = re.sub(r'[$,\s]', '', price_str)
            return float(cleaned)
        except:
            return 0.0
    
    def _calculate_complexity(self, parsed: Dict[str, Any]) -> int:
        """Calculate query complexity score"""
        score = 0
        
        # Base score for number of words
        score += len(parsed["keywords"])
        
        # Add points for entities
        for entity_type, entities in parsed["entities"].items():
            score += len(entities) * 2
        
        # Add points for filters
        score += len(parsed["filters"]) * 3
        
        # Add points for industry terms
        score += len(parsed["industry_terms"]) * 2
        
        # Add points for specific intent
        if parsed["intent"] != "general_search":
            score += 5
        
        return min(score, 100)  # Cap at 100