"""
Azure OpenAI Service Integration for FoodXchange
Handles email parsing, supplier matching, and intelligent features
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

try:
    from openai import AzureOpenAI
    OPENAI_AVAILABLE = True
except ImportError as e:
    OPENAI_AVAILABLE = False
    print(f"Warning: openai package not installed. Error: {e}")
    print("Run: pip install openai")

from foodxchange.config import get_settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for Azure OpenAI integration"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        
        logger.info(f"OpenAI Available: {OPENAI_AVAILABLE}")
        logger.info(f"API Key: {'***' + self.settings.azure_openai_api_key[-4:] if self.settings.azure_openai_api_key else 'Not set'}")
        logger.info(f"Endpoint: {self.settings.azure_openai_endpoint}")
        logger.info(f"Deployment: {self.settings.azure_openai_deployment_name}")
        
        if OPENAI_AVAILABLE and all([
            self.settings.azure_openai_api_key,
            self.settings.azure_openai_endpoint,
            self.settings.azure_openai_deployment_name
        ]):
            try:
                self.client = AzureOpenAI(
                    api_key=self.settings.azure_openai_api_key,
                    api_version="2024-02-01",
                    azure_endpoint=self.settings.azure_openai_endpoint
                )
                self.deployment_name = self.settings.azure_openai_deployment_name
                logger.info("Azure OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI: {e}")
                self.client = None
        else:
            logger.warning("Azure OpenAI not configured. Check environment variables.")
    
    async def parse_email_for_rfq(self, email_content: str) -> Dict[str, Any]:
        """
        Parse email content to extract RFQ information
        Returns structured data for creating an RFQ
        """
        if not self.client:
            return self._fallback_email_parser(email_content)
        
        system_prompt = """You are an expert at extracting RFQ (Request for Quote) information from emails.
        Extract the following information if present:
        - Product name(s) and descriptions
        - Quantities needed
        - Delivery dates/deadlines
        - Quality specifications
        - Pricing expectations
        - Contact information
        
        Return the data in JSON format with these fields:
        {
            "products": [{"name": "", "quantity": "", "unit": "", "specifications": ""}],
            "delivery_date": "",
            "budget_range": "",
            "additional_requirements": "",
            "urgency": "low|medium|high",
            "detected_type": "rfq|quote|order|inquiry"
        }
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this email:\n\n{email_content}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Successfully parsed email with OpenAI: {result.get('detected_type', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"OpenAI parsing failed: {e}")
            return self._fallback_email_parser(email_content)
    
    async def match_suppliers(self, product_requirements: Dict[str, Any], suppliers: List[Dict]) -> List[Dict]:
        """
        Use AI to match suppliers based on product requirements
        Returns ranked list of suppliers with match scores
        """
        if not self.client or not suppliers:
            return self._basic_supplier_matching(product_requirements, suppliers)
        
        system_prompt = """You are an expert at matching suppliers to product requirements.
        Analyze the requirements and rank suppliers based on:
        1. Product category match
        2. Quality certifications
        3. Delivery capabilities
        4. Price competitiveness
        5. Location/shipping distance
        
        Return JSON with supplier rankings and reasoning:
        {
            "matches": [
                {
                    "supplier_id": "",
                    "company_name": "",
                    "match_score": 0-100,
                    "reasons": [""],
                    "pros": [""],
                    "cons": [""]
                }
            ]
        }
        """
        
        try:
            # Prepare supplier data (limit to relevant fields)
            supplier_data = [
                {
                    "id": s.get("id"),
                    "name": s.get("company_name"),
                    "products": s.get("product_categories", []),
                    "certifications": s.get("certifications", []),
                    "location": s.get("location"),
                    "rating": s.get("rating", 0)
                }
                for s in suppliers[:20]  # Limit to 20 suppliers for API
            ]
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Requirements: {json.dumps(product_requirements)}\n\nSuppliers: {json.dumps(supplier_data)}"}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("matches", [])
            
        except Exception as e:
            logger.error(f"OpenAI supplier matching failed: {e}")
            return self._basic_supplier_matching(product_requirements, suppliers)
    
    async def generate_rfq_description(self, product_name: str, context: Optional[str] = None) -> str:
        """
        Generate a professional RFQ description based on product name
        """
        if not self.client:
            return f"Request for Quote: {product_name}"
        
        prompt = f"""Generate a professional RFQ description for: {product_name}
        {f'Context: {context}' if context else ''}
        
        Include:
        - Clear product specifications needed
        - Quality requirements
        - Delivery expectations
        - Request for pricing breakdown
        
        Keep it concise (2-3 paragraphs) and professional."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a procurement specialist writing RFQs."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI RFQ generation failed: {e}")
            return f"Request for Quote: {product_name}\n\nPlease provide your best pricing and terms for the above product."
    
    async def analyze_quote_competitiveness(self, quotes: List[Dict]) -> Dict[str, Any]:
        """
        Analyze multiple quotes to provide insights
        """
        if not self.client or not quotes:
            return self._basic_quote_analysis(quotes)
        
        system_prompt = """Analyze these quotes and provide:
        1. Price competitiveness ranking
        2. Best value recommendation (not just lowest price)
        3. Risk factors for each supplier
        4. Negotiation suggestions
        
        Return JSON format:
        {
            "best_value_quote_id": "",
            "lowest_price_quote_id": "",
            "analysis": {
                "quote_id": {
                    "rank": 1,
                    "price_score": 0-100,
                    "value_score": 0-100,
                    "risks": [""],
                    "negotiation_points": [""]
                }
            },
            "summary": ""
        }
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze these quotes: {json.dumps(quotes)}"}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"OpenAI quote analysis failed: {e}")
            return self._basic_quote_analysis(quotes)
    
    async def extract_insights_from_orders(self, order_history: List[Dict]) -> Dict[str, Any]:
        """
        Extract purchasing insights from order history
        """
        if not self.client or not order_history:
            return {"insights": [], "recommendations": []}
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "Analyze purchasing patterns and provide actionable insights."
                    },
                    {
                        "role": "user", 
                        "content": f"Analyze this order history and provide insights: {json.dumps(order_history[-50:])}"  # Last 50 orders
                    }
                ],
                temperature=0.3
            )
            
            insights_text = response.choices[0].message.content
            
            # Structure the insights
            return {
                "insights": self._extract_bullet_points(insights_text),
                "recommendations": self._extract_recommendations(insights_text),
                "summary": insights_text[:200] + "..."
            }
            
        except Exception as e:
            logger.error(f"OpenAI insights extraction failed: {e}")
            return {"insights": [], "recommendations": []}
    
    # Fallback methods when OpenAI is not available
    
    def _fallback_email_parser(self, email_content: str) -> Dict[str, Any]:
        """Basic email parsing without AI"""
        result = {
            "products": [],
            "delivery_date": "",
            "budget_range": "",
            "additional_requirements": "",
            "urgency": "medium",
            "detected_type": "unknown"
        }
        
        # Simple keyword detection
        email_lower = email_content.lower()
        
        # Detect type
        if any(word in email_lower for word in ["rfq", "request for quote", "quotation request"]):
            result["detected_type"] = "rfq"
        elif any(word in email_lower for word in ["quote", "quotation", "pricing"]):
            result["detected_type"] = "quote"
        elif any(word in email_lower for word in ["order", "purchase order", "po"]):
            result["detected_type"] = "order"
        
        # Extract quantities (basic regex)
        quantity_matches = re.findall(r'(\d+)\s*(kg|tons?|units?|boxes?|cases?)', email_lower)
        for qty, unit in quantity_matches:
            result["products"].append({
                "name": "Product",
                "quantity": qty,
                "unit": unit,
                "specifications": ""
            })
        
        # Detect urgency
        if any(word in email_lower for word in ["urgent", "asap", "immediately"]):
            result["urgency"] = "high"
        
        return result
    
    def _basic_supplier_matching(self, requirements: Dict, suppliers: List[Dict]) -> List[Dict]:
        """Basic supplier matching without AI"""
        matches = []
        
        for supplier in suppliers:
            score = 50  # Base score
            reasons = []
            
            # Simple scoring based on available data
            if supplier.get("rating", 0) > 4:
                score += 20
                reasons.append("High rating")
            
            if supplier.get("verified", False):
                score += 10
                reasons.append("Verified supplier")
            
            matches.append({
                "supplier_id": supplier.get("id"),
                "company_name": supplier.get("company_name"),
                "match_score": min(score, 100),
                "reasons": reasons,
                "pros": reasons,
                "cons": []
            })
        
        # Sort by score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches[:10]  # Top 10
    
    def _basic_quote_analysis(self, quotes: List[Dict]) -> Dict[str, Any]:
        """Basic quote analysis without AI"""
        if not quotes:
            return {"analysis": {}, "summary": "No quotes to analyze"}
        
        # Sort by price
        sorted_quotes = sorted(quotes, key=lambda x: x.get("total_price", float('inf')))
        
        analysis = {}
        for i, quote in enumerate(sorted_quotes):
            analysis[str(quote.get("id"))] = {
                "rank": i + 1,
                "price_score": 100 - (i * 20),  # Simple scoring
                "value_score": 80 - (i * 10),
                "risks": [],
                "negotiation_points": ["Consider volume discount", "Discuss payment terms"]
            }
        
        return {
            "best_value_quote_id": str(sorted_quotes[0].get("id")) if sorted_quotes else None,
            "lowest_price_quote_id": str(sorted_quotes[0].get("id")) if sorted_quotes else None,
            "analysis": analysis,
            "summary": f"Analyzed {len(quotes)} quotes. Price range: ${sorted_quotes[0].get('total_price', 0):,.2f} - ${sorted_quotes[-1].get('total_price', 0):,.2f}"
        }
    
    def _extract_bullet_points(self, text: str) -> List[str]:
        """Extract bullet points from text"""
        lines = text.split('\n')
        bullets = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                bullets.append(line.lstrip('-•* '))
        return bullets[:5]  # Max 5 points
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from text"""
        recommendations = []
        lines = text.split('\n')
        
        in_recommendations = False
        for line in lines:
            if 'recommend' in line.lower():
                in_recommendations = True
            elif in_recommendations and line.strip():
                if line.strip().startswith(('-', '•', '*', '1', '2', '3')):
                    recommendations.append(line.strip().lstrip('-•*123. '))
        
        return recommendations[:3]  # Max 3 recommendations


# Singleton instance
openai_service = OpenAIService()