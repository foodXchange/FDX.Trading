"""
Azure AI Vision Service with GPT-4 Vision Integration
Uses Azure OpenAI GPT-4 Vision for intelligent product analysis
"""

import os
import json
import logging
import base64
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import asyncio
import aiohttp
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)


class AzureAIVisionService:
    """Service for analyzing product images using Azure OpenAI GPT-4 Vision with multilingual support"""
    
    # Hebrew/multilingual specific constants
    HEBREW_KOSHER_TERMS = {
        "כשר": "kosher",
        "פרווה": "parve", 
        "חלבי": "dairy",
        "בשרי": "meat",
        'בד"ץ': "beit_din_certification",
        "רבנות": "rabbinate_supervision",
        "כשר לפסח": "kosher_for_passover"
    }
    
    DIETARY_CLAIMS_HEBREW = {
        "ללא גלוטן": "gluten_free",
        "אורגני": "organic", 
        "טבעוני": "vegan",
        "ללא סוכר מוסף": "no_added_sugar",
        "ללא חומרים משמרים": "no_preservatives",
        "טבעי": "natural"
    }
    
    def __init__(self):
        """Initialize Azure AI Vision service"""
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.deployment_name = os.getenv("AZURE_OPENAI_VISION_DEPLOYMENT", "gpt-4o")
        self.api_version = "2024-02-01"
        
        if not self.endpoint or not self.api_key:
            logger.warning("Azure OpenAI credentials not configured for GPT-4 Vision")
            self.client = None
        else:
            logger.info(f"Azure AI Vision service initialized with deployment: {self.deployment_name}")
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 string"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            raise
    
    def _create_product_analysis_prompt(self) -> Dict[str, Any]:
        """Create the structured prompt for multilingual product analysis"""
        system_prompt = """You are a multilingual food product analysis AI specializing in Israeli and international food packaging. You understand Hebrew, English, Arabic, and other languages commonly found on food products.

Your expertise includes:
1. Multilingual text extraction (Hebrew, English, Arabic, Russian, etc.)
2. Hebrew kosher certifications and dietary terms
3. Cultural food context and Israeli brand recognition
4. Right-to-left (RTL) text handling
5. Mixed-language packaging analysis

Extract ALL visible text in its original language, then provide English translations where appropriate. Pay special attention to Hebrew kosher certifications (כשר, פרווה, חלבי, בשרי) and dietary claims.

Be precise and culturally aware. Preserve original language for brand names and certifications."""

        form_fields_schema = {
            "product_name": "Main product name in original language AND English translation",
            "product_name_hebrew": "Product name in Hebrew if present",
            "brand_name": "Brand name in original script with transliteration",
            "brand_name_hebrew": "Brand name in Hebrew if present",
            "category": "Product category (Food & Beverage, Snacks, Beverages, etc.)",
            "package_size": "Size/weight (e.g., 25g, 500ml, 25 גרם)",
            "product_type": "Specific type (e.g., puffed snack, beverage)",
            "main_ingredients": "First 3-4 ingredients in original language with translations",
            "flavor_profile": "sweet/salty/spicy/neutral/sour/bitter/umami",
            "target_group": "kids/family/adults/general (only if obvious)",
            "kosher_status": "Specific kosher type: Kosher/Kosher Parve (כשר פרווה)/Kosher Dairy (כשר חלבי)/Kosher Meat (כשר בשרי)/Not Kosher/Unknown",
            "kosher_certification": "Certification body (OU, OK, Star-K, Badatz, Rabbinate, etc.)",
            "kosher_text_hebrew": "Original Hebrew kosher text if present",
            "dietary_features": ["Gluten-Free (ללא גלוטן)", "Organic (אורגני)", "Vegan (טבעוני)", "Non-GMO"],
            "health_claims": "Health benefits in original language with translations",
            "allergen_warnings": "Contains: list of allergens in original language",
            "hebrew_text_found": "All Hebrew text found on package",
            "arabic_text_found": "All Arabic text found on package",
            "english_text_found": "All English text found on package",
            "importer_info": "Israeli importer/distributor information if present",
            "country_of_origin": "Manufacturing country",
            "calories_per_serving": "Calorie count if visible",
            "serving_size": "Per package or per X grams",
            "key_nutrients": "Protein/fat/carbs if shown",
            "detected_languages": ["List of languages detected on package"],
            "confidence_scores": {
                "overall": "0-1 confidence score",
                "text_quality": "clear/partial/poor",
                "hebrew_recognition": "0-1 confidence for Hebrew text",
                "analysis_status": "complete/needs_review"
            }
        }

        hebrew_context = f"""Hebrew kosher terms to recognize:
{json.dumps(self.HEBREW_KOSHER_TERMS, ensure_ascii=False, indent=2)}

Hebrew dietary claims:
{json.dumps(self.DIETARY_CLAIMS_HEBREW, ensure_ascii=False, indent=2)}"""

        return {
            "system_prompt": system_prompt,
            "form_fields_schema": form_fields_schema,
            "hebrew_context": hebrew_context
        }
    
    async def analyze_product_image_gpt4v(
        self,
        image_path: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze product image using GPT-4 Vision
        
        Args:
            image_path: Path to the image file
            additional_context: Optional additional context from user
            
        Returns:
            Structured analysis result with confidence scores
        """
        if not self.endpoint or not self.api_key:
            raise ValueError("Azure OpenAI not configured for GPT-4 Vision")
        
        try:
            # Encode image
            base64_image = self._encode_image(image_path)
            
            # Create prompt
            prompt_config = self._create_product_analysis_prompt()
            
            # Build the messages
            messages = [
                {
                    "role": "system",
                    "content": prompt_config["system_prompt"]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Please analyze this product image and extract information for these fields:
                            
{json.dumps(prompt_config["form_fields_schema"], indent=2, ensure_ascii=False)}

{prompt_config.get('hebrew_context', '')}

{f'Additional context: {additional_context}' if additional_context else ''}

IMPORTANT: 
1. Extract ALL visible text in its ORIGINAL language (Hebrew, Arabic, English, etc.)
2. For Hebrew text, preserve the original Hebrew characters
3. Provide English translations in separate fields
4. Pay special attention to kosher certifications and Hebrew dietary terms
5. Check for Israeli importer/distributor information

Return ONLY valid JSON matching this exact structure. Include confidence_scores for each field."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            # Make API call
            url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"
            
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            data = {
                "messages": messages,
                "max_tokens": 1500,
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        
                        # Parse JSON response
                        try:
                            analysis_data = json.loads(content)
                        except json.JSONDecodeError:
                            logger.error("Failed to parse GPT-4V response as JSON")
                            analysis_data = self._parse_fallback_response(content)
                        
                        return {
                            "success": True,
                            "data": analysis_data,
                            "model": "gpt-4-vision",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"GPT-4 Vision API error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                            "details": error_text
                        }
                        
        except Exception as e:
            logger.error(f"Error in GPT-4 Vision analysis: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_multiple_images(
        self,
        image_paths: List[str],
        comparison_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze multiple product images
        
        Args:
            image_paths: List of image file paths
            comparison_mode: Whether to compare products
            
        Returns:
            Combined analysis results
        """
        if not image_paths:
            return {"success": False, "error": "No images provided"}
        
        # Analyze each image
        results = []
        for image_path in image_paths:
            result = await self.analyze_product_image_gpt4v(image_path)
            if result.get("success"):
                results.append(result["data"])
        
        if not results:
            return {"success": False, "error": "No successful analyses"}
        
        # If comparison mode, create comparison
        if comparison_mode and len(results) > 1:
            comparison = await self._compare_products(results)
            return {
                "success": True,
                "individual_results": results,
                "comparison": comparison,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _compare_products(self, products: List[Dict]) -> Dict[str, Any]:
        """Compare multiple products and generate insights"""
        # Create comparison prompt
        comparison_prompt = f"""Compare these {len(products)} products and provide:
1. Key differences
2. Common features
3. Price/value comparison
4. Target market analysis
5. Sourcing recommendations

Products:
{json.dumps(products, indent=2)}

Return as JSON with sections for differences, similarities, and recommendations."""
        
        try:
            url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"
            
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            data = {
                "messages": [
                    {"role": "system", "content": "You are a product comparison expert."},
                    {"role": "user", "content": comparison_prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.3
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        
                        try:
                            return json.loads(content)
                        except:
                            return {"comparison_text": content}
                    else:
                        logger.error(f"Comparison API error: {response.status}")
                        return {"error": "Comparison failed"}
                        
        except Exception as e:
            logger.error(f"Error in product comparison: {e}")
            return {"error": str(e)}
    
    def _parse_fallback_response(self, content: str) -> Dict[str, Any]:
        """Fallback parser for non-JSON responses"""
        # Try to extract key-value pairs from text
        result = {
            "product_name": "Unknown Product",
            "brand_name": "",
            "category": "Food & Beverage",
            "package_size": "",
            "product_type": "",
            "main_ingredients": "",
            "flavor_profile": "neutral",
            "target_group": "general",
            "kosher_status": "Unknown",
            "dietary_features": [],
            "health_claims": "",
            "allergen_warnings": "",
            "calories_per_serving": "",
            "serving_size": "",
            "key_nutrients": "",
            "confidence_scores": {
                "overall": 0.5,
                "text_quality": "poor",
                "analysis_status": "needs_review"
            }
        }
        
        # Simple extraction logic
        lines = content.split('\n')
        for line in lines:
            line_lower = line.lower()
            if 'product' in line_lower and 'name' in line_lower:
                parts = line.split(':')
                if len(parts) > 1:
                    result["product_name"] = parts[1].strip()
            elif 'brand' in line_lower:
                parts = line.split(':')
                if len(parts) > 1:
                    result["brand_name"] = parts[1].strip()
        
        return result
    
    async def extract_text_with_confidence(
        self,
        image_path: str
    ) -> Dict[str, Any]:
        """
        Extract text from image with confidence scores
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text with confidence scores
        """
        try:
            base64_image = self._encode_image(image_path)
            
            messages = [
                {
                    "role": "system",
                    "content": "Extract all visible text from this image. For each text element, provide the text content and a confidence score (0-1)."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text from this image. Return as JSON with 'text_elements' array containing objects with 'text' and 'confidence' fields."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"
            
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            data = {
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        
                        return {
                            "success": True,
                            "text_data": json.loads(content),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"API error: {response.status}"
                        }
                        
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
azure_ai_vision_service = AzureAIVisionService()