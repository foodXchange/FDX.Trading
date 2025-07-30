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
import aiohttp
import base64
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ProductAnalysisService:
    """Service for AI-powered product analysis and brief generation"""
    
    def __init__(self):
        """Initialize service"""
        self.is_azure_configured = False
        self.vision_endpoint = None
        self.vision_key = None
        self.openai_endpoint = None
        self.openai_key = None
        self.openai_deployment = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Azure AI services if configured"""
        try:
            # Check if Azure settings are available
            from ..config import settings
            logger.info(f"Azure OpenAI Endpoint from config: {settings.azure_openai_endpoint}")
            logger.info(f"Azure OpenAI Deployment: {settings.azure_openai_deployment_name}")
            
            if (settings.azure_vision_endpoint and settings.azure_vision_key and 
                settings.azure_openai_api_key and settings.azure_openai_endpoint):
                self.is_azure_configured = True
                self.vision_endpoint = settings.azure_vision_endpoint
                self.vision_key = settings.azure_vision_key
                self.openai_endpoint = settings.azure_openai_endpoint
                self.openai_key = settings.azure_openai_api_key
                self.openai_deployment = settings.azure_openai_deployment_name or "gpt-4"
                logger.info("Azure AI services configured successfully")
                logger.info(f"Using OpenAI endpoint: {self.openai_endpoint}")
            else:
                logger.info("Azure AI services not configured - using demo mode")
        except Exception as e:
            logger.warning(f"Azure services not available: {e}")
    
    async def analyze_product_image(self, image_url: str, db=None) -> Dict[str, Any]:
        """
        Analyze product image using Azure Computer Vision with OCR
        
        Args:
            image_url: URL or path to the product image
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.is_azure_configured:
            logger.warning("Azure AI services not configured - using demo mode")
            return self._generate_demo_analysis(image_url)
        
        try:
            # First, perform OCR to read text (including Hebrew)
            ocr_text = await self._perform_ocr(image_url)
            
            # Prepare the request to Azure Computer Vision
            vision_url = f"{self.vision_endpoint}vision/v3.2/analyze"
            params = {
                'visualFeatures': 'Categories,Description,Tags,Objects,Color,Brands',
                'details': 'Landmarks',
                'language': 'en',
                'model-version': 'latest'
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Ocp-Apim-Subscription-Key': self.vision_key
            }
            
            # Check if image_url is a local file or remote URL
            if image_url.startswith(('http://', 'https://')):
                # Remote URL
                body = {'url': image_url}
                headers['Content-Type'] = 'application/json'
            else:
                # Local file - send as binary
                with open(image_url, 'rb') as image_file:
                    image_data = image_file.read()
                body = image_data
                headers['Content-Type'] = 'application/octet-stream'
            
            async with aiohttp.ClientSession() as session:
                if headers['Content-Type'] == 'application/json':
                    async with session.post(vision_url, params=params, headers=headers, json=body) as response:
                        if response.status == 200:
                            result = await response.json()
                            logger.info(f"Vision API response received successfully")
                            processed_result = self._process_vision_result(result, ocr_text)
                            
                            # Apply ML improvements if database is available
                            if db:
                                try:
                                    from .ml_improvement_service import ml_improvement_service
                                    corrections = ml_improvement_service.check_for_corrections(
                                        processed_result.get('tags', []),
                                        processed_result.get('objects', []),
                                        processed_result.get('brands', []),
                                        db
                                    )
                                    if corrections:
                                        processed_result = ml_improvement_service.apply_learning_to_analysis(
                                            processed_result, corrections
                                        )
                                        logger.info(f"Applied ML corrections: {corrections}")
                                except Exception as e:
                                    logger.warning(f"ML improvements not available: {e}")
                            
                            return processed_result
                        else:
                            error_text = await response.text()
                            logger.error(f"Azure Vision API error: {response.status} - {error_text}")
                            logger.warning("Falling back to demo mode due to API error")
                            return self._generate_demo_analysis(image_url)
                else:
                    async with session.post(vision_url, params=params, headers=headers, data=body) as response:
                        if response.status == 200:
                            result = await response.json()
                            logger.info(f"Vision API response received successfully")
                            processed_result = self._process_vision_result(result, ocr_text)
                            
                            # Apply ML improvements if database is available
                            if db:
                                try:
                                    from .ml_improvement_service import ml_improvement_service
                                    corrections = ml_improvement_service.check_for_corrections(
                                        processed_result.get('tags', []),
                                        processed_result.get('objects', []),
                                        processed_result.get('brands', []),
                                        db
                                    )
                                    if corrections:
                                        processed_result = ml_improvement_service.apply_learning_to_analysis(
                                            processed_result, corrections
                                        )
                                        logger.info(f"Applied ML corrections: {corrections}")
                                except Exception as e:
                                    logger.warning(f"ML improvements not available: {e}")
                            
                            return processed_result
                        else:
                            error_text = await response.text()
                            logger.error(f"Azure Vision API error: {response.status} - {error_text}")
                            logger.warning("Falling back to demo mode due to API error")
                            return self._generate_demo_analysis(image_url)
                            
        except Exception as e:
            logger.error(f"Error in image analysis: {e}")
            logger.warning("Falling back to demo mode due to error")
            return self._generate_demo_analysis(image_url)
    
    def _generate_demo_analysis(self, image_url: str) -> Dict[str, Any]:
        """Generate demo analysis when Azure services are not available"""
        logger.info("Generating demo analysis")
        
        # Extract filename or URL for demo data
        if image_url.startswith(('http://', 'https://')):
            demo_name = "Online Product"
        else:
            import os
            demo_name = os.path.basename(image_url).split('.')[0] or "Uploaded Product"
        
        return {
            "product_name": f"{demo_name}",
            "brand_name": "Sample Brand",
            "producing_company": "Sample Company",
            "country_of_origin": "United States",
            "category": "Food & Beverage",
            "packaging_type": "Stand-up bag",
            "product_weight": "250g",
            "product_appearance": "Pale white colored, extruded corn salty snack",
            "target_market": "Adults",
            "kosher_details": "Kosher certified",
            "gluten_free": "Yes",
            "sugar_free": "No",
            "no_sugar_added": "Yes",
            "shelf_life": "12 months",
            "storage_conditions": "Store in a cool, dry place",
            "tags": ["food", "snack", "corn", "salty"],
            "objects": ["package", "bag"],
            "brands": ["Sample Brand"],
            "colors": ["white", "pale"],
            "confidence": 0.85,
            "is_demo": True
        }
    
    async def _perform_ocr(self, image_url: str) -> Dict[str, Any]:
        """Perform OCR on image to extract text in multiple languages including Hebrew"""
        try:
            ocr_url = f"{self.vision_endpoint}vision/v3.2/ocr"
            params = {
                'language': 'unk',  # Auto-detect language (supports Hebrew)
                'detectOrientation': 'true'
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Ocp-Apim-Subscription-Key': self.vision_key
            }
            
            # Prepare request body
            if image_url.startswith(('http://', 'https://')):
                body = {'url': image_url}
                headers['Content-Type'] = 'application/json'
            else:
                with open(image_url, 'rb') as image_file:
                    image_data = image_file.read()
                body = image_data
                headers['Content-Type'] = 'application/octet-stream'
            
            async with aiohttp.ClientSession() as session:
                if headers['Content-Type'] == 'application/json':
                    async with session.post(ocr_url, params=params, headers=headers, json=body) as response:
                        if response.status == 200:
                            ocr_result = await response.json()
                            return self._extract_ocr_text(ocr_result)
                else:
                    async with session.post(ocr_url, params=params, headers=headers, data=body) as response:
                        if response.status == 200:
                            ocr_result = await response.json()
                            return self._extract_ocr_text(ocr_result)
            
            return {"text": "", "hebrew_text": "", "english_text": ""}
            
        except Exception as e:
            logger.error(f"Error performing OCR: {e}")
            return {"text": "", "hebrew_text": "", "english_text": ""}
    
    def _extract_ocr_text(self, ocr_result: Dict) -> Dict[str, Any]:
        """Extract text from OCR result"""
        all_text = []
        hebrew_text = []
        english_text = []
        
        for region in ocr_result.get('regions', []):
            for line in region.get('lines', []):
                line_text = ' '.join([word['text'] for word in line.get('words', [])])
                all_text.append(line_text)
                
                # Detect if text contains Hebrew characters
                if any('\u0590' <= char <= '\u05FF' for char in line_text):
                    hebrew_text.append(line_text)
                else:
                    english_text.append(line_text)
        
        return {
            "text": ' '.join(all_text),
            "hebrew_text": ' '.join(hebrew_text),
            "english_text": ' '.join(english_text),
            "detected_language": ocr_result.get('language', 'unknown')
        }
    
    def _process_vision_result(self, result: Dict, ocr_data: Dict = None) -> Dict[str, Any]:
        """Process vision API result into structured analysis"""
        # Extract text if available
        detected_text = []
        if result.get('brands'):
            detected_text.extend([brand['name'] for brand in result['brands']])
        
        # Add OCR text
        ocr_text_data = {}
        if ocr_data:
            ocr_text_data = {
                "ocr_text": ocr_data.get("text", ""),
                "hebrew_text": ocr_data.get("hebrew_text", ""),
                "english_text": ocr_data.get("english_text", ""),
                "detected_language": ocr_data.get("detected_language", "")
            }
            if ocr_data.get("text"):
                detected_text.append(ocr_data["text"])
        
        analysis = {
            "product_name": self._extract_product_name(result, ocr_data),
            "category": self._extract_category(result),
            "description": result.get('description', {}).get('captions', [{}])[0].get('text', ''),
            "tags": [tag['name'] for tag in result.get('tags', [])],
            "objects": [obj['object'] for obj in result.get('objects', [])],
            "brands": [brand['name'] for brand in result.get('brands', [])],
            "detected_text": detected_text,
            "colors": {
                "dominant_colors": result.get('color', {}).get('dominantColors', []),
                "accent_color": result.get('color', {}).get('accentColor', ''),
                "is_bw_img": result.get('color', {}).get('isBwImg', False)
            },
            "confidence_score": 0.90,  # Default confidence
            "demo_mode": False
        }
        
        # Add OCR data to analysis
        analysis.update(ocr_text_data)
        
        return analysis
    
    def _extract_product_name(self, vision_result: Dict, ocr_data: Dict = None) -> str:
        """Extract product name from vision analysis and OCR"""
        # Try to get from OCR text first (especially Hebrew)
        if ocr_data and ocr_data.get('hebrew_text'):
            # Look for product name patterns in Hebrew text
            hebrew_lines = ocr_data['hebrew_text'].split(' ')
            if hebrew_lines:
                # Return the first significant Hebrew text as product name
                return hebrew_lines[0] if len(hebrew_lines[0]) > 2 else ocr_data['hebrew_text'][:50]
        
        # Try to get from brands detected
        if vision_result.get('brands'):
            brand_names = [brand['name'] for brand in vision_result['brands']]
            if brand_names:
                return brand_names[0]
        
        # Try to get from objects detected
        if vision_result.get('objects'):
            # Filter for food-related objects
            food_objects = []
            for obj in vision_result['objects']:
                obj_name = obj.get('object', '').lower()
                if any(term in obj_name for term in ['food', 'drink', 'bottle', 'package', 'box', 'can', 'jar']):
                    food_objects.append(obj['object'])
            if food_objects:
                return food_objects[0].title()
        
        # Try to get from description
        if vision_result.get('description', {}).get('captions'):
            caption = vision_result['description']['captions'][0]['text']
            # Look for food-related terms in caption
            words = caption.split()
            for i, word in enumerate(words):
                if word.lower() in ['of', 'with', 'containing'] and i > 0:
                    return ' '.join(words[:i]).title()
            # Otherwise use first few words
            return ' '.join(words[:3]).title()
        
        # Try to get from tags
        tags = [tag['name'] for tag in vision_result.get('tags', [])]
        food_tags = [tag for tag in tags if not tag.lower() in ['indoor', 'outdoor', 'table', 'sitting']]
        if food_tags:
            return food_tags[0].title()
        
        return "Food Product"
    
    def _extract_category(self, vision_result: Dict) -> str:
        """Extract category from vision analysis"""
        # Check categories
        categories = vision_result.get('categories', [])
        for category in categories:
            name = category.get('name', '')
            if 'food' in name.lower() or 'beverage' in name.lower():
                return name
        
        # Check tags for food-related terms
        tags = [tag['name'] for tag in vision_result.get('tags', [])]
        food_tags = ['food', 'beverage', 'drink', 'snack', 'organic', 'natural']
        for tag in tags:
            if any(food_term in tag.lower() for food_term in food_tags):
                return "Food & Beverage"
        
        return "Product"
    
    async def generate_product_brief(self, analysis_result: Dict[str, Any], user_query: str = "", db=None) -> Dict[str, Any]:
        """
        Generate comprehensive product brief using Azure OpenAI
        
        Args:
            analysis_result: Results from image analysis
            user_query: Additional user input
            db: Database session for ML improvements
            
        Returns:
            Dictionary containing brief information
        """
        if not self.is_azure_configured:
            logger.warning("Azure OpenAI not configured - using demo brief")
            return self._generate_demo_brief(analysis_result, user_query)
        
        try:
            # Check if this is a demo analysis
            if analysis_result.get("is_demo", False):
                logger.info("Using demo brief for demo analysis")
                return self._generate_demo_brief(analysis_result, user_query)
            
            # Create the prompt for OpenAI
            prompt = self._create_brief_prompt(analysis_result, user_query)
            
            # Call Azure OpenAI
            openai_url = f"{self.openai_endpoint}openai/deployments/{self.openai_deployment}/chat/completions?api-version=2023-05-15"
            
            headers = {
                'Content-Type': 'application/json',
                'api-key': self.openai_key
            }
            
            data = {
                "messages": [
                    {"role": "system", "content": "You are a professional food product analyst. Provide detailed, accurate analysis in the requested format."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.3
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(openai_url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        logger.info("OpenAI brief generation successful")
                        
                        # Parse the response
                        brief_data = self._parse_brief_response(content, analysis_result)
                        
                        # Apply ML improvements if available
                        if db:
                            try:
                                from .ml_improvement_service import ml_improvement_service
                                brief_data = ml_improvement_service.apply_learning_to_brief(brief_data, db)
                            except Exception as e:
                                logger.warning(f"ML improvements not available for brief: {e}")
                        
                        return brief_data
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {response.status} - {error_text}")
                        logger.warning("Falling back to demo brief due to API error")
                        return self._generate_demo_brief(analysis_result, user_query)
                        
        except Exception as e:
            logger.error(f"Error generating brief: {e}")
            logger.warning("Falling back to demo brief due to error")
            return self._generate_demo_brief(analysis_result, user_query)
    
    def _create_brief_prompt(self, analysis_result: Dict, user_query: str) -> str:
        """Create a prompt for product brief generation"""
        product_name = analysis_result.get("product_name", "Unknown Product")
        category = analysis_result.get("category", "Food & Beverage")
        description = analysis_result.get("description", "")
        tags = analysis_result.get("tags", [])
        brands = analysis_result.get("brands", [])
        objects = analysis_result.get("objects", [])
        ocr_text = analysis_result.get("ocr_text", "")
        hebrew_text = analysis_result.get("hebrew_text", "")
        english_text = analysis_result.get("english_text", "")
        
        prompt = f"""
        You are a food industry expert. Analyze this product based on the computer vision analysis and OCR text.
        
        IMPORTANT TEXT DETECTED ON PACKAGE:
        - Hebrew Text: {hebrew_text if hebrew_text else 'None'}
        - English Text: {english_text if english_text else 'None'}
        - All OCR Text: {ocr_text[:500] if ocr_text else 'None'}
        
        VISUAL ANALYSIS:
        - Product Name/Description: {product_name}
        - Category: {category}
        - Visual Description: {description}
        - Detected Tags: {', '.join(tags)}
        - Detected Brands: {', '.join(brands) if brands else 'None detected'}
        - Detected Objects: {', '.join(objects[:5]) if objects else 'None'}
        - Additional Requirements: {user_query if user_query else 'Standard B2B sourcing requirements'}
        
        If Hebrew text is detected, this is likely an Israeli product. Use the Hebrew text to identify the actual product name and company.
        Be specific and realistic based on the text and visual features detected.
        
        Please provide a structured brief including:
        
        1. PRODUCT DETAILS:
        - product_name: Exact product name
        - producing_company: Manufacturing company name
        - brand_name: Brand name if different from company
        - country_of_origin: Country where the brand/company is based
        - category: Product category
        
        2. PRODUCT CHARACTERISTICS:
        - packaging_type: Type of packaging (pillow bag, stand up bag, DOYpack, glass jar, can, bottle, etc.)
        - product_weight: Weight with unit (e.g., "250g", "500ml", "1kg")
        - product_appearance: Detailed appearance description (e.g., "pale white colored, extruded corn salty snack")
        - shelf_life: Product shelf life
        - storage_conditions: Storage requirements
        
        3. TARGET MARKET & CERTIFICATIONS:
        - target_market: Target audience (kids, adults, food supplement, etc.)
        - kosher: Kosher certification details if applicable
        - kosher_writings: Specific kosher symbols/writings if present
        - gluten_free: Gluten-free status
        - sugar_free: Sugar-free status
        - no_sugar_added: No sugar added status
        - other_certifications: Any other relevant certifications
        
        4. PRICING & SUPPLY:
        - price_range: Estimated price range
        - currency: Currency
        - minimum_order: Minimum order quantity
        - payment_terms: Payment terms
        
        5. RELATED PRODUCTS:
        - related_products: Array of related products from same family with:
          * name: Product name
          * unit_weight: Weight with unit (gr., ml., kg.)
          * appearance: Product appearance
          * packaging_type: Packaging type
        
        6. SOURCING RECOMMENDATIONS:
        - supplier_requirements: Array of supplier requirements
        - quality_standards: Array of quality standards
        - market_insights: Market analysis
        
        Format the response as a JSON object with these exact keys:
        {{
            "product_name": "string",
            "producing_company": "string", 
            "brand_name": "string",
            "country_of_origin": "string",
            "category": "string",
            "packaging_type": "string",
            "product_weight": "string",
            "product_appearance": "string",
            "shelf_life": "string",
            "storage_conditions": "string",
            "target_market": "string",
            "kosher": "string",
            "kosher_writings": "string",
            "gluten_free": "boolean",
            "sugar_free": "boolean", 
            "no_sugar_added": "boolean",
            "other_certifications": ["array of strings"],
            "price_range": "string",
            "currency": "string",
            "minimum_order": "string",
            "payment_terms": "string",
            "related_products": [
                {{
                    "name": "string",
                    "unit_weight": "string", 
                    "appearance": "string",
                    "packaging_type": "string"
                }}
            ],
            "supplier_requirements": ["array of strings"],
            "quality_standards": ["array of strings"],
            "market_insights": "string"
        }}
        """
        
        return prompt
    
    def _parse_brief_response(self, content: str, analysis_result: Dict) -> Dict:
        """Parse OpenAI response into structured brief"""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                brief_data = json.loads(json_match.group())
            else:
                # Fallback to structured parsing
                brief_data = self._fallback_parse(content)
            
            return {
                "product_name": brief_data.get("product_name", analysis_result.get("product_name", "Unknown Product")),
                "producing_company": brief_data.get("producing_company", "Unknown Company"),
                "brand_name": brief_data.get("brand_name", "Unknown Brand"),
                "country_of_origin": brief_data.get("country_of_origin", "Unknown"),
                "category": brief_data.get("category", analysis_result.get("category", "Food & Beverage")),
                "packaging_type": brief_data.get("packaging_type", "Unknown"),
                "product_weight": brief_data.get("product_weight", "Unknown"),
                "product_appearance": brief_data.get("product_appearance", "Unknown"),
                "shelf_life": brief_data.get("shelf_life", "Unknown"),
                "storage_conditions": brief_data.get("storage_conditions", "Unknown"),
                "target_market": brief_data.get("target_market", "General Market"),
                "kosher": brief_data.get("kosher", "Not specified"),
                "kosher_writings": brief_data.get("kosher_writings", "None"),
                "gluten_free": brief_data.get("gluten_free", False),
                "sugar_free": brief_data.get("sugar_free", False),
                "no_sugar_added": brief_data.get("no_sugar_added", False),
                "other_certifications": brief_data.get("other_certifications", []),
                "price_range": brief_data.get("price_range", "$2.50 - $8.00 per unit"),
                "currency": brief_data.get("currency", "USD"),
                "minimum_order": brief_data.get("minimum_order", "1000 units"),
                "payment_terms": brief_data.get("payment_terms", "Net 30 days"),
                "related_products": brief_data.get("related_products", []),
                "supplier_requirements": brief_data.get("supplier_requirements", []),
                "quality_standards": brief_data.get("quality_standards", []),
                "market_insights": brief_data.get("market_insights", "No specific insights available"),
                "demo_mode": False
            }
            
        except Exception as e:
            logger.error(f"Error parsing brief response: {e}")
            # Return fallback brief
            return {
                "product_name": analysis_result.get("product_name", "Unknown Product"),
                "producing_company": "Unknown Company",
                "brand_name": "Unknown Brand",
                "country_of_origin": "Unknown",
                "category": analysis_result.get("category", "Food & Beverage"),
                "packaging_type": "Unknown",
                "product_weight": "Unknown",
                "product_appearance": "Unknown",
                "shelf_life": "12-24 months",
                "storage_conditions": "Store in a cool, dry place",
                "target_market": "General Market",
                "kosher": "Not specified",
                "kosher_writings": "None",
                "gluten_free": False,
                "sugar_free": False,
                "no_sugar_added": False,
                "other_certifications": [],
                "price_range": "$2.50 - $8.00 per unit",
                "currency": "USD",
                "minimum_order": "1000 units",
                "payment_terms": "Net 30 days",
                "related_products": [],
                "supplier_requirements": ["Food safety certification", "Quality assurance"],
                "quality_standards": ["ISO 22000", "HACCP"],
                "market_insights": "Growing demand for quality products",
                "demo_mode": False
            }
    
    def _generate_demo_brief(self, analysis_result: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """Generate demo brief when Azure OpenAI is not available"""
        return {
            "product_name": analysis_result.get("product_name", "Demo Product"),
            "producing_company": "Demo Company",
            "brand_name": "Demo Brand",
            "country_of_origin": "Demo Country",
            "category": analysis_result.get("category", "Food & Beverage"),
            "packaging_type": "Stand-up Pouch",
            "product_weight": "250g",
            "product_appearance": analysis_result.get("description", "Demo product appearance"),
            "shelf_life": "12 months",
            "storage_conditions": "Store in a cool, dry place",
            "target_market": "General consumers",
            "kosher": "Not specified",
            "kosher_writings": "None",
            "gluten_free": False,
            "sugar_free": False,
            "no_sugar_added": False,
            "other_certifications": ["Demo Certification"],
            "price_range": "$5.00 - $10.00 per unit",
            "currency": "USD",
            "minimum_order": "100 units",
            "payment_terms": "Net 30 days",
            "related_products": [
                {
                    "name": "Similar Demo Product",
                    "unit_weight": "250g",
                    "appearance": "Similar appearance",
                    "packaging_type": "Pouch"
                }
            ],
            "supplier_requirements": ["Quality certification", "Regular supply"],
            "quality_standards": ["ISO 9001", "HACCP"],
            "market_insights": "Demo market insights - Azure OpenAI not configured",
            "demo_mode": True
        }
    
    def _fallback_parse(self, content: str) -> Dict:
        """Fallback parsing for non-JSON responses"""
        return {
            "product_name": "Unknown Product",
            "producing_company": "Unknown Company",
            "brand_name": "Unknown Brand",
            "country_of_origin": "Unknown",
            "category": "Food & Beverage",
            "packaging_type": "Unknown",
            "product_weight": "Unknown",
            "product_appearance": "Unknown",
            "shelf_life": "12-24 months",
            "storage_conditions": "Store in a cool, dry place",
            "target_market": "General Market",
            "kosher": "Not specified",
            "kosher_writings": "None",
            "gluten_free": False,
            "sugar_free": False,
            "no_sugar_added": False,
            "other_certifications": [],
            "price_range": "$2.50 - $8.00 per unit",
            "currency": "USD",
            "minimum_order": "1000 units",
            "payment_terms": "Net 30 days",
            "related_products": [],
            "supplier_requirements": ["Food safety certification", "Quality assurance"],
            "quality_standards": ["ISO 22000", "HACCP"],
            "market_insights": "Growing demand for quality products"
        }
    
    async def search_similar_products(self, product_name: str, category: str) -> List[Dict[str, Any]]:
        """
        Search for similar products in the database
        
        Args:
            product_name: Name of the product to search for
            category: Product category
            
        Returns:
            List of similar products
        """
        # Demo mode - return mock similar products
        return [
            {
                "id": 1,
                "name": f"Similar {product_name}",
                "category": category,
                "supplier": "Demo Supplier 1",
                "price": "$3.50",
                "rating": 4.5,
                "availability": "In Stock"
            },
            {
                "id": 2,
                "name": f"Alternative {product_name}",
                "category": category,
                "supplier": "Demo Supplier 2",
                "price": "$4.20",
                "rating": 4.2,
                "availability": "In Stock"
            }
        ]
    
    async def analyze_text_search(self, search_text: str) -> Dict[str, Any]:
        """
        Analyze text search query
        
        Args:
            search_text: Text to analyze
            
        Returns:
            Analysis results
        """
        return {
            "query": search_text,
            "suggested_category": "Food & Beverage",
            "related_terms": ["organic", "natural", "healthy"],
            "demo_mode": True
        }

# Create a global instance
product_analysis_service = ProductAnalysisService()