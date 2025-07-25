"""
AI Service for Azure OpenAI Integration
Handles email parsing, classification, and supplier matching
"""
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import asyncio
import aiohttp

from app.config import get_settings

try:
    from app.agents.email_monitor_agent import EmailIntent
except ImportError:
    # Define EmailIntent locally if import fails
    class EmailIntent(Enum):
        QUOTE_RESPONSE = "quote_response"
        PRICE_UPDATE = "price_update"
        PRODUCT_UPDATE = "product_update"
        CERTIFICATION_UPDATE = "certification_update"
        CONTACT_UPDATE = "contact_update"
        GENERAL_INQUIRY = "general_inquiry"
        UNKNOWN = "unknown"

settings = get_settings()
logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered operations using Azure OpenAI"""
    
    def __init__(self):
        self.api_key = settings.azure_openai_api_key
        self.endpoint = settings.azure_openai_endpoint
        self.deployment_name = settings.azure_openai_deployment_name
        self.api_version = "2023-05-15"
        self.is_configured = bool(self.api_key and self.endpoint and self.deployment_name)
        
    async def analyze_supplier_email(self, email_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze supplier email using Azure OpenAI
        Returns intent, extracted data, and confidence score
        """
        if not self.is_configured:
            logger.warning("Azure OpenAI not configured, returning default analysis")
            return self._get_default_analysis()
            
        try:
            prompt = self._create_email_analysis_prompt(email_content)
            
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"
            
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1000,
                "response_format": {"type": "json_object"}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._parse_ai_response(result)
                    else:
                        error_text = await response.text()
                        logger.error(f"Azure OpenAI API error: {response.status} - {error_text}")
                        return self._get_default_analysis()
                        
        except Exception as e:
            logger.error(f"AI analysis error: {str(e)}")
            return self._get_default_analysis()
            
    def _get_system_prompt(self) -> str:
        """Get system prompt for email analysis"""
        return """You are an AI assistant specialized in analyzing supplier emails for a B2B food sourcing platform.
        
Your task is to analyze emails and extract structured information in JSON format with the following schema:
{
    "intent": "quote_response|price_update|product_update|certification_update|contact_update|general_inquiry|unknown",
    "confidence": 0.0-1.0,
    "supplier_info": {
        "company_name": "string or null",
        "contact_name": "string or null",
        "phone": "string or null",
        "website": "string or null"
    },
    "extracted_data": {
        "products": [
            {
                "name": "string",
                "price": "number or null",
                "unit": "string or null",
                "quantity_available": "number or null",
                "moq": "number or null"
            }
        ],
        "certifications": ["string"],
        "delivery_terms": "string or null",
        "payment_terms": "string or null",
        "validity_date": "string or null"
    },
    "action_required": "none|quote_response|follow_up|urgent",
    "summary": "brief summary of the email content"
}

Analyze the email carefully and provide accurate extraction. If information is not available, use null."""
        
    def _create_email_analysis_prompt(self, email_content: Dict[str, Any]) -> str:
        """Create prompt for email analysis"""
        return f"""Analyze this supplier email and extract structured information:

Subject: {email_content.get('subject', 'No subject')}
From: {email_content.get('sender', 'Unknown')}
Date: {email_content.get('date', 'Unknown')}

Body:
{email_content.get('body', '')[:2000]}  # Limit to 2000 chars

Please analyze and return the structured JSON response."""
        
    def _parse_ai_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Azure OpenAI response"""
        try:
            content = response['choices'][0]['message']['content']
            parsed = json.loads(content)
            
            # Map string intent to enum
            intent_str = parsed.get('intent', 'unknown')
            intent_map = {
                'quote_response': EmailIntent.QUOTE_RESPONSE,
                'price_update': EmailIntent.PRICE_UPDATE,
                'product_update': EmailIntent.PRODUCT_UPDATE,
                'certification_update': EmailIntent.CERTIFICATION_UPDATE,
                'contact_update': EmailIntent.CONTACT_UPDATE,
                'general_inquiry': EmailIntent.GENERAL_INQUIRY,
                'unknown': EmailIntent.UNKNOWN
            }
            
            return {
                'intent': intent_map.get(intent_str, EmailIntent.UNKNOWN),
                'confidence': parsed.get('confidence', 0.5),
                'supplier_info': parsed.get('supplier_info', {}),
                'extracted_data': parsed.get('extracted_data', {}),
                'action_required': parsed.get('action_required', 'none'),
                'summary': parsed.get('summary', '')
            }
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return self._get_default_analysis()
            
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Return default analysis when AI fails"""
        return {
            'intent': EmailIntent.UNKNOWN,
            'confidence': 0.0,
            'supplier_info': {},
            'extracted_data': {},
            'action_required': 'none',
            'summary': 'Unable to analyze email'
        }
        
    async def match_supplier(self, email_address: str, company_info: Dict[str, Any]) -> Tuple[Optional[int], float]:
        """
        Match email to existing supplier using AI
        Returns (supplier_id, confidence_score)
        """
        # This would use AI to match based on email domain, company name, etc.
        # For POC, we'll use simple matching logic
        
        # In production, this would:
        # 1. Query database for potential matches
        # 2. Use AI to score matches based on multiple factors
        # 3. Return best match with confidence score
        
        return None, 0.0
        
    async def generate_email_response(self, intent: EmailIntent, extracted_data: Dict[str, Any]) -> str:
        """Generate appropriate email response based on intent"""
        try:
            prompt = f"""Generate a professional email response for a {intent.value} email.
            
Extracted data: {json.dumps(extracted_data, indent=2)}

Generate a brief, professional response acknowledging receipt and indicating next steps.
Keep it under 150 words."""
            
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"
            
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional B2B communication assistant for a food sourcing platform."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 200
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        return self._get_default_response(intent)
                        
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._get_default_response(intent)
            
    def _get_default_response(self, intent: EmailIntent) -> str:
        """Get default response based on intent"""
        responses = {
            EmailIntent.QUOTE_RESPONSE: "Thank you for your quote. We have received it and will review it shortly.",
            EmailIntent.PRICE_UPDATE: "Thank you for the pricing update. Our system has been updated accordingly.",
            EmailIntent.PRODUCT_UPDATE: "We have received your product update and will update our records.",
            EmailIntent.CERTIFICATION_UPDATE: "Thank you for providing the certification update.",
            EmailIntent.CONTACT_UPDATE: "Your contact information has been updated in our system.",
            EmailIntent.GENERAL_INQUIRY: "Thank you for your message. We will review and respond shortly.",
            EmailIntent.UNKNOWN: "Thank you for your email. We have received it and will process it accordingly."
        }
        
        return responses.get(intent, responses[EmailIntent.UNKNOWN])
        
    async def extract_product_catalog(self, attachment_content: str) -> List[Dict[str, Any]]:
        """Extract product catalog from attachment using AI"""
        # This would process PDFs, Excel files, etc. using AI
        # For POC, returning empty list
        return []
        
    async def analyze_quote_competitiveness(self, quote_data: Dict[str, Any], market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze quote competitiveness using AI"""
        try:
            prompt = f"""Analyze this quote against market data:
            
Quote: {json.dumps(quote_data, indent=2)}
Market Data: {json.dumps(market_data[:5], indent=2)}  # Limit to 5 for context

Provide analysis including:
1. Price competitiveness (percentage vs market average)
2. Delivery terms comparison
3. Quality indicators
4. Recommendations

Return as JSON with structure:
{{
    "price_vs_market": "percentage",
    "competitiveness_score": 0-100,
    "strengths": ["string"],
    "weaknesses": ["string"],
    "recommendation": "accept|negotiate|reject",
    "negotiation_points": ["string"]
}}"""
            
            # Call Azure OpenAI (similar to above)
            # For POC, return mock data
            return {
                "price_vs_market": "-5%",
                "competitiveness_score": 75,
                "strengths": ["Competitive pricing", "Good delivery terms"],
                "weaknesses": ["Higher MOQ than average"],
                "recommendation": "negotiate",
                "negotiation_points": ["Try to reduce MOQ", "Ask for volume discounts"]
            }
            
        except Exception as e:
            logger.error(f"Quote analysis error: {str(e)}")
            return {}


# Singleton instance
ai_service = AIService()


# Enhanced email analysis for the agent
async def analyze_email_with_ai(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze email using AI service"""
    return await ai_service.analyze_supplier_email(email_data)


# Supplier matching with AI
async def match_supplier_with_ai(email: str, company_info: Dict[str, Any]) -> Tuple[Optional[int], float]:
    """Match supplier using AI service"""
    return await ai_service.match_supplier(email, company_info)