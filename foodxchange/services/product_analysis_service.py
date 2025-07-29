"""
AI Product Analysis Service for FoodXchange
Uses Azure Computer Vision and OpenAI for product analysis and brief generation
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

# Azure imports
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

# Local imports
from .config import settings

logger = logging.getLogger(__name__)

class ProductAnalysisService:
    """Service for AI-powered product analysis and brief generation"""
    
    def __init__(self):
        """Initialize Azure AI services"""
        self.vision_client = None
        self.openai_client = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Azure Computer Vision and OpenAI clients"""
        try:
            # Initialize Computer Vision
            if settings.azure_vision_endpoint and settings.azure_vision_key:
                self.vision_client = ComputerVisionClient(
                    endpoint=settings.azure_vision_endpoint,
                    credential=AzureKeyCredential(settings.azure_vision_key)
                )
                logger.info("Azure Computer Vision client initialized")
            
            # Initialize OpenAI
            if settings.azure_openai_api_key and settings.azure_openai_endpoint:
                self.openai_client = AzureOpenAI(
                    api_key=settings.azure_openai_api_key,
                    azure_endpoint=settings.azure_openai_endpoint,
                    api_version="2024-02-15-preview"
                )
                logger.info("Azure OpenAI client initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize Azure AI services: {e}")
    
    async def analyze_product_image(self, image_url: str) -> Dict[str, Any]:
        """
        Analyze product image using Azure Computer Vision
        
        Args:
            image_url: URL or path to the product image
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.vision_client:
            logger.warning("Azure Computer Vision not configured")
            return {"error": "Computer Vision service not available"}
        
        try:
            # Analyze image
            features = [
                VisualFeatureTypes.tags,
                VisualFeatureTypes.objects,
                VisualFeatureTypes.description,
                VisualFeatureTypes.faces,
                VisualFeatureTypes.categories,
                VisualFeatureTypes.color,
                VisualFeatureTypes.image_type
            ]
            
            analysis = self.vision_client.analyze_image(image_url, features)
            
            # Extract relevant information
            result = {
                "product_name": self._extract_product_name(analysis),
                "category": self._extract_category(analysis),
                "description": analysis.description.captions[0].text if analysis.description.captions else "",
                "tags": [tag.name for tag in analysis.tags],
                "objects": [obj.object_property for obj in analysis.objects],
                "colors": {
                    "dominant_colors": analysis.color.dominant_colors,
                    "accent_color": analysis.color.accent_color,
                    "is_bw_img": analysis.color.is_bw_img
                },
                "confidence_score": analysis.description.captions[0].confidence if analysis.description.captions else 0.0
            }
            
            logger.info(f"Image analysis completed for {image_url}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing image {image_url}: {e}")
            return {"error": str(e)}
    
    async def generate_product_brief(self, analysis_result: Dict[str, Any], user_query: str = "") -> Dict[str, Any]:
        """
        Generate comprehensive product brief using Azure OpenAI
        
        Args:
            analysis_result: Results from image analysis
            user_query: Additional user input or requirements
            
        Returns:
            Dictionary containing product brief
        """
        if not self.openai_client:
            logger.warning("Azure OpenAI not configured")
            return {"error": "OpenAI service not available"}
        
        try:
            # Prepare prompt for product brief generation
            prompt = self._create_brief_prompt(analysis_result, user_query)
            
            # Generate brief using OpenAI
            response = self.openai_client.chat.completions.create(
                model=settings.azure_openai_deployment_name,
                messages=[
                    {"role": "system", "content": "You are a food product expert and sourcing specialist. Create detailed, professional product briefs for B2B food sourcing."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            brief_text = response.choices[0].message.content
            
            # Parse and structure the brief
            brief = self._parse_brief_response(brief_text, analysis_result)
            
            logger.info("Product brief generated successfully")
            return brief
            
        except Exception as e:
            logger.error(f"Error generating product brief: {e}")
            return {"error": str(e)}
    
    async def search_similar_products(self, product_name: str, category: str) -> List[Dict[str, Any]]:
        """
        Search for similar products in the database
        
        Args:
            product_name: Name of the product to search for
            category: Product category
            
        Returns:
            List of similar products
        """
        try:
            # This would integrate with your existing product database
            # For now, return mock data
            similar_products = [
                {
                    "id": 1,
                    "name": f"Similar {product_name}",
                    "supplier": "Fresh Foods Co",
                    "category": category,
                    "price": 5.99,
                    "rating": 4.5,
                    "availability": "In Stock"
                }
            ]
            
            return similar_products
            
        except Exception as e:
            logger.error(f"Error searching similar products: {e}")
            return []
    
    def _extract_product_name(self, analysis) -> str:
        """Extract product name from analysis results"""
        if analysis.description.captions:
            caption = analysis.description.captions[0].text
            # Simple extraction - in production, use more sophisticated NLP
            words = caption.split()
            if len(words) >= 2:
                return " ".join(words[:3])  # First 3 words as product name
        return "Unknown Product"
    
    def _extract_category(self, analysis) -> str:
        """Extract product category from analysis results"""
        # Look for food-related tags
        food_tags = [tag.name for tag in analysis.tags if tag.name.lower() in [
            'food', 'fruit', 'vegetable', 'meat', 'seafood', 'dairy', 'grain', 'spice'
        ]]
        
        if food_tags:
            return food_tags[0].title()
        
        # Check categories
        if analysis.categories:
            for category in analysis.categories:
                if 'food' in category.name.lower() or 'product' in category.name.lower():
                    return category.name
        
        return "Food Product"
    
    def _create_brief_prompt(self, analysis_result: Dict[str, Any], user_query: str) -> str:
        """Create prompt for product brief generation"""
        product_name = analysis_result.get("product_name", "Unknown Product")
        category = analysis_result.get("category", "Food Product")
        description = analysis_result.get("description", "")
        tags = analysis_result.get("tags", [])
        
        prompt = f"""
        Create a comprehensive product brief for: {product_name}
        
        Product Details:
        - Category: {category}
        - Description: {description}
        - Tags: {', '.join(tags)}
        - User Query: {user_query}
        
        Please provide:
        1. Product Name and Description
        2. Product Specifications (ingredients, certifications, quality standards)
        3. Packaging Options (common sizes: 100g, 250g, 500g, 1kg, etc.)
        4. Target Market and Applications
        5. Quality Standards and Certifications
        6. Estimated Price Range (per kg/unit)
        7. Supplier Requirements
        8. Market Trends and Insights
        
        Format the response as a structured JSON with these sections.
        """
        
        return prompt
    
    def _parse_brief_response(self, brief_text: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse OpenAI response into structured brief"""
        try:
            # Try to extract JSON from response
            if "```json" in brief_text:
                json_start = brief_text.find("```json") + 7
                json_end = brief_text.find("```", json_start)
                json_str = brief_text[json_start:json_end].strip()
                brief_data = json.loads(json_str)
            else:
                # Fallback to structured text parsing
                brief_data = {
                    "product_name": analysis_result.get("product_name", "Unknown Product"),
                    "category": analysis_result.get("category", "Food Product"),
                    "description": brief_text,
                    "specifications": {},
                    "packaging_options": ["100g", "250g", "500g", "1kg"],
                    "target_market": "B2B Food Industry",
                    "quality_standards": ["ISO 22000", "HACCP"],
                    "estimated_price_range": {"min": 5.0, "max": 15.0, "currency": "USD"},
                    "supplier_requirements": ["Food safety certification", "Quality assurance"],
                    "market_insights": "Growing demand for quality food products"
                }
            
            return brief_data
            
        except Exception as e:
            logger.error(f"Error parsing brief response: {e}")
            return {
                "product_name": analysis_result.get("product_name", "Unknown Product"),
                "description": brief_text,
                "error": "Failed to parse structured data"
            }
    
    async def analyze_text_search(self, search_text: str) -> Dict[str, Any]:
        """
        Analyze text-based product search
        
        Args:
            search_text: Product name or description to search
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.openai_client:
            logger.warning("Azure OpenAI not configured")
            return {"error": "OpenAI service not available"}
        
        try:
            prompt = f"""
            Analyze this product search query: "{search_text}"
            
            Please provide:
            1. Product name and category
            2. Key specifications
            3. Common packaging options
            4. Quality requirements
            5. Market insights
            
            Format as JSON.
            """
            
            response = self.openai_client.chat.completions.create(
                model=settings.azure_openai_deployment_name,
                messages=[
                    {"role": "system", "content": "You are a food product expert. Analyze product search queries and provide detailed insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse the response
            try:
                if "```json" in analysis_text:
                    json_start = analysis_text.find("```json") + 7
                    json_end = analysis_text.find("```", json_start)
                    json_str = analysis_text[json_start:json_end].strip()
                    result = json.loads(json_str)
                else:
                    result = {
                        "product_name": search_text,
                        "category": "Food Product",
                        "description": analysis_text,
                        "specifications": {},
                        "packaging_options": ["100g", "250g", "500g", "1kg"]
                    }
                
                return result
                
            except Exception as e:
                logger.error(f"Error parsing text analysis: {e}")
                return {
                    "product_name": search_text,
                    "description": analysis_text,
                    "error": "Failed to parse structured data"
                }
                
        except Exception as e:
            logger.error(f"Error analyzing text search: {e}")
            return {"error": str(e)}

# Global instance
product_analysis_service = ProductAnalysisService()