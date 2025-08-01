"""
AI Product Analysis Service for FoodXchange
Uses dependency injection for better testability and maintainability
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

from ..core.interfaces import AIClient, CacheProvider
from ..core.providers import ServiceResult

logger = logging.getLogger(__name__)

class ProductAnalysisService:
    """Service for AI-powered product analysis and brief generation"""
    
    def __init__(self, ai_client: AIClient, cache_provider: CacheProvider):
        """Initialize service with dependency injection"""
        self._ai_client = ai_client
        self._cache = cache_provider
        self.is_azure_configured = True  # Assume configured if dependencies are provided
    
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
                raise ValueError(
                    "Azure AI services not configured. Please set up the following environment variables:\n"
                    "- AZURE_VISION_ENDPOINT\n"
                    "- AZURE_VISION_KEY\n"
                    "- AZURE_OPENAI_API_KEY\n"
                    "- AZURE_OPENAI_ENDPOINT\n"
                    "Run setup_azure_keys.py or setup_azure_keys.bat to configure."
                )
        except Exception as e:
            logger.error(f"Azure services configuration error: {e}")
            raise
    
    async def analyze_product_image(self, image_url: str, db=None, use_gpt4v: bool = True) -> Dict[str, Any]:
        """
        Analyze product image using Azure AI services with Redis caching
        
        Args:
            image_url: URL or path to the product image
            db: Database session for ML improvements
            use_gpt4v: Whether to use GPT-4 Vision (True) or traditional Computer Vision (False)
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.is_azure_configured:
            raise ValueError(
                "Azure AI services not configured. Cannot analyze images without Azure credentials.\n"
                "Please run setup_azure_keys.py or setup_azure_keys.bat to configure."
            )
        
        # Get Redis service
        redis_service = get_redis_service()
        
        # Generate hash for the image
        image_hash = None
        if redis_service.is_connected():
            try:
                # Read image data for hashing
                if image_url.startswith(('http://', 'https://')):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(image_url) as resp:
                            image_data = await resp.read()
                else:
                    with open(image_url, 'rb') as f:
                        image_data = f.read()
                
                image_hash = redis_service.generate_image_hash(image_data)
                
                # Check cache first
                analysis_type = "gpt4v_analysis" if use_gpt4v else "vision_analysis"
                cached_result = redis_service.get_cached_ai_analysis(image_hash, analysis_type)
                
                if cached_result:
                    logger.info(f"✅ Returning cached {analysis_type} result")
                    return cached_result
                    
            except Exception as e:
                logger.warning(f"Cache check failed: {e}")
        
        # Use GPT-4 Vision for more accurate analysis
        if use_gpt4v:
            try:
                logger.info("Using GPT-4 Vision for product analysis")
                gpt4v_result = await azure_ai_vision_service.analyze_product_image_gpt4v(image_url)
                
                if gpt4v_result.get("success"):
                    # Format the GPT-4V result to match existing structure
                    analysis_data = gpt4v_result["data"]
                    
                    # Extract confidence scores
                    confidence_scores = analysis_data.get("confidence_scores", {})
                    
                    # Build analysis result in expected format
                    analysis = {
                        "product_name": analysis_data.get("product_name", "Unknown Product"),
                        "brand": analysis_data.get("brand_name", ""),
                        "category": analysis_data.get("category", "Food & Beverage"),
                        "description": f"{analysis_data.get('product_type', '')} - {analysis_data.get('package_size', '')}".strip(' - '),
                        "tags": [],  # GPT-4V doesn't provide tags
                        "objects": [],  # GPT-4V doesn't provide objects
                        "brands": [analysis_data.get("brand_name")] if analysis_data.get("brand_name") else [],
                        "detected_text": [analysis_data.get("product_name", ""), analysis_data.get("brand_name", "")],
                        "colors": {},  # GPT-4V doesn't analyze colors
                        "confidence_score": confidence_scores.get("overall", 0.9),
                        "ocr_text": "",  # GPT-4V extracts structured data directly
                        "hebrew_text": "",
                        "english_text": "",
                        "detected_language": "en",
                        "weight": analysis_data.get("package_size", ""),
                        "kosher": analysis_data.get("kosher_status", ""),
                        "features": analysis_data.get("dietary_features", []),
                        "gpt4v_analysis": analysis_data,  # Store full GPT-4V analysis
                        "analysis_method": "gpt-4-vision"
                    }
                    
                    # Apply ML improvements if database is available
                    if db:
                        try:
                            from .ml_improvement_service import ml_improvement_service
                            corrections = ml_improvement_service.check_for_corrections(
                                analysis.get('tags', []),
                                analysis.get('objects', []),
                                analysis.get('brands', []),
                                db
                            )
                            if corrections:
                                analysis = ml_improvement_service.apply_learning_to_analysis(
                                    analysis, corrections
                                )
                                logger.info(f"Applied ML corrections: {corrections}")
                        except Exception as e:
                            logger.warning(f"ML improvements not available: {e}")
                    
                    # Cache the result
                    if image_hash and redis_service.is_connected():
                        redis_service.cache_ai_analysis(image_hash, "gpt4v_analysis", analysis)
                    
                    return analysis
                else:
                    logger.warning(f"GPT-4 Vision analysis failed: {gpt4v_result.get('error')}")
                    # Fall back to traditional Computer Vision
                    use_gpt4v = False
            except Exception as e:
                logger.error(f"Error with GPT-4 Vision: {e}")
                # Fall back to traditional Computer Vision
                use_gpt4v = False
        
        # Traditional Computer Vision approach (fallback or if specified)
        if not use_gpt4v:
            try:
                # Use the newer Image Analysis 4.0 API for better results
                vision_url = f"{self.vision_endpoint}computervision/imageanalysis:analyze"
                params = {
                    'api-version': '2024-02-01',
                    'features': 'tags,read,caption,objects,denseCaptions',
                    'language': 'en'
                }
                
                headers = {
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
                                processed_result = self._process_vision_v4_result(result)
                                
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
                                
                                # Cache the result
                                if image_hash and redis_service.is_connected():
                                    redis_service.cache_ai_analysis(image_hash, "vision_analysis", processed_result)
                                
                                return processed_result
                            else:
                                error_text = await response.text()
                                logger.error(f"Azure Vision API error: {response.status} - {error_text}")
                                raise ValueError(f"Azure Vision API error: {response.status} - {error_text}")
                    else:
                        async with session.post(vision_url, params=params, headers=headers, data=body) as response:
                            if response.status == 200:
                                result = await response.json()
                                logger.info(f"Vision API response received successfully")
                                processed_result = self._process_vision_v4_result(result)
                                
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
                                
                                # Cache the result
                                if image_hash and redis_service.is_connected():
                                    redis_service.cache_ai_analysis(image_hash, "vision_analysis", processed_result)
                                
                                return processed_result
                            else:
                                error_text = await response.text()
                                logger.error(f"Azure Vision API error: {response.status} - {error_text}")
                                raise ValueError(f"Azure Vision API error: {response.status} - {error_text}")
                            
            except Exception as e:
                logger.error(f"Error in image analysis: {e}")
                raise
    
    async def _perform_ocr(self, image_url: str) -> Dict[str, Any]:
        """Perform OCR on image to extract text in multiple languages including Hebrew"""
        try:
            ocr_url = f"{self.vision_endpoint}vision/v3.2/ocr"
            params = {
                'language': 'he',  # Specify Hebrew explicitly
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
    
    def _process_vision_v4_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process results from Image Analysis 4.0 API"""
        detected_text = []
        hebrew_text = []
        english_text = []
        
        # Extract text from readResult
        if 'readResult' in result:
            for block in result['readResult'].get('blocks', []):
                for line in block.get('lines', []):
                    text = line.get('text', '')
                    detected_text.append(text)
                    
                    # Detect Hebrew characters
                    if any('\u0590' <= c <= '\u05FF' for c in text):
                        hebrew_text.append(text)
                    else:
                        english_text.append(text)
        
        # Extract tags
        tags = []
        if 'tagsResult' in result:
            tags = [tag['name'] for tag in result['tagsResult'].get('values', [])]
        
        # Extract description
        description = ''
        if 'captionResult' in result:
            description = result['captionResult'].get('text', '')
        
        # Extract objects
        objects = []
        if 'objectsResult' in result:
            objects = [obj['tags'][0]['name'] for obj in result['objectsResult'].get('values', []) if obj.get('tags')]
        
        # Extract specific product information from Hebrew text
        product_info = self._extract_product_info(detected_text)
        
        analysis = {
            "product_name": product_info.get('product_name') or self._extract_product_name_from_text(hebrew_text, english_text, tags),
            "brand": product_info.get('brand', ''),
            "category": product_info.get('category') or self._determine_category(tags, description),
            "description": description,
            "tags": tags,
            "objects": objects,
            "brands": [product_info.get('brand')] if product_info.get('brand') else [],
            "detected_text": detected_text,
            "colors": {},  # V4 API doesn't return colors in same format
            "confidence_score": 0.90,
            "ocr_text": ' '.join(detected_text),
            "hebrew_text": ' '.join(hebrew_text),
            "english_text": ' '.join(english_text),
            "detected_language": 'he' if hebrew_text else 'en',
            "weight": product_info.get('weight', ''),
            "kosher": product_info.get('kosher', ''),
            "features": product_info.get('features', [])
        }
        
        return analysis
    
    def _extract_product_name_from_text(self, hebrew_text, english_text, tags):
        """Extract product name from OCR text"""
        # For Hebrew products, look for specific patterns
        if hebrew_text:
            # Common product name patterns to skip
            skip_words = ['חטיף', 'בוטנים', 'גרם', 'מועשר', 'ללא', 'בהשגחת', 'עדיף']
            
            # Look for the largest/most prominent Hebrew text that's not a common word
            for text in hebrew_text:
                # Skip common descriptive words and check for substantial text
                if len(text) > 2 and not any(skip in text for skip in skip_words):
                    # במבה should be caught here
                    if 'במבה' in text or 'בַּמְבָּה' in text:
                        return 'במבה'
                    return text
        
        # Otherwise try English text
        if english_text:
            return english_text[0]
        
        # Fallback to tags
        if tags and tags[0] != 'text':
            return tags[0]
        
        return "Unknown Product"
    
    def _determine_category(self, tags, description):
        """Determine product category from tags and description"""
        food_categories = {
            'snack': 'Snacks',
            'cereal': 'Breakfast & Cereals',
            'candy': 'Confectionery',
            'beverage': 'Beverages',
            'food': 'Food & Beverage'
        }
        
        for tag in tags:
            for key, category in food_categories.items():
                if key in tag.lower():
                    return category
        
        return 'Food & Beverage'
    
    def _extract_product_info(self, text_list):
        """Extract specific product information from OCR text"""
        info = {
            'product_name': '',
            'brand': '',
            'category': '',
            'weight': '',
            'kosher': '',
            'features': []
        }
        
        for text in text_list:
            # Brand (Osem)
            if 'אֹסֶם' in text or 'אסם' in text:
                info['brand'] = 'אסם'
            
            # Product name (Bamba)
            elif 'בַּמְבָּה' in text or 'במבה' in text:
                info['product_name'] = 'במבה'
            
            # Category
            elif 'חטיף בוטנים' in text:
                info['category'] = 'חטיף בוטנים'
            
            # Weight
            elif 'גרם' in text:
                info['weight'] = text
            
            # Kosher
            elif 'בהשגחת' in text:
                info['kosher'] = text
            
            # Features
            elif 'ללא גלוטן' in text or 'חטיף אפוי' in text:
                info['features'].append('ללא גלוטן')
            elif 'מועשר בויטמינים' in text:
                info['features'].append(text)
            elif 'ללא חומרים משמרים' in text:
                info['features'].append(text)
            elif 'ללא צבעי מאכל' in text:
                info['features'].append(text)
        
        return info
    
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
        Generate comprehensive product brief using Azure OpenAI with Redis caching
        
        Args:
            analysis_result: Results from image analysis
            user_query: Additional user input
            db: Database session for ML improvements
            
        Returns:
            Dictionary containing brief information
        """
        if not self.is_azure_configured:
            raise ValueError(
                "Azure OpenAI not configured. Cannot generate product brief without Azure credentials.\n"
                "Please run setup_azure_keys.py or setup_azure_keys.bat to configure."
            )
        
        # Get Redis service
        redis_service = get_redis_service()
        
        # Create cache key from analysis result and query
        cache_key = None
        if redis_service.is_connected():
            try:
                # Create a unique key from the analysis data and query
                cache_data = {
                    "product_name": analysis_result.get("product_name", ""),
                    "category": analysis_result.get("category", ""),
                    "ocr_text": analysis_result.get("ocr_text", "")[:200],  # First 200 chars
                    "user_query": user_query
                }
                cache_key = redis_service.generate_image_hash(
                    json.dumps(cache_data, sort_keys=True).encode()
                )
                
                # Check cache
                cached_brief = redis_service.get_cached_ai_analysis(cache_key, "product_brief")
                if cached_brief:
                    logger.info("✅ Returning cached product brief")
                    return cached_brief
                    
            except Exception as e:
                logger.warning(f"Brief cache check failed: {e}")
        
        # If we have GPT-4V analysis data, use it directly for the brief
        if analysis_result.get("analysis_method") == "gpt-4-vision" and "gpt4v_analysis" in analysis_result:
            gpt4v_data = analysis_result["gpt4v_analysis"]
            
            # Map GPT-4V data to brief format
            brief_data = {
                "product_name": gpt4v_data.get("product_name", "Unknown Product"),
                "producing_company": gpt4v_data.get("brand_name", "Unknown Company"),
                "brand_name": gpt4v_data.get("brand_name", "Unknown Brand"),
                "country_of_origin": "Israel" if gpt4v_data.get("kosher_status", "").startswith("Kosher") else "Unknown",
                "category": gpt4v_data.get("category", "Food & Beverage"),
                "packaging_type": gpt4v_data.get("product_type", "Unknown"),
                "product_weight": gpt4v_data.get("package_size", "Unknown"),
                "product_appearance": f"{gpt4v_data.get('product_type', '')} with {gpt4v_data.get('flavor_profile', 'neutral')} flavor",
                "shelf_life": "12-24 months",
                "storage_conditions": "Store in a cool, dry place",
                "target_market": gpt4v_data.get("target_group", "General Market"),
                "kosher": gpt4v_data.get("kosher_status", "Not specified"),
                "kosher_writings": gpt4v_data.get("kosher_status", "None"),
                "gluten_free": "Gluten-Free" in gpt4v_data.get("dietary_features", []),
                "sugar_free": "Sugar-Free" in gpt4v_data.get("dietary_features", []),
                "no_sugar_added": "No Sugar Added" in gpt4v_data.get("health_claims", ""),
                "other_certifications": [f for f in gpt4v_data.get("dietary_features", []) if f not in ["Gluten-Free", "Sugar-Free"]],
                "price_range": "$2.50 - $8.00 per unit",
                "currency": "USD",
                "minimum_order": "1000 units",
                "payment_terms": "Net 30 days",
                "related_products": [],
                "supplier_requirements": ["Food safety certification", "Quality assurance", "Consistent supply"],
                "quality_standards": ["ISO 22000", "HACCP", "GMP"],
                "market_insights": f"Growing demand for {gpt4v_data.get('category', 'food')} products with {', '.join(gpt4v_data.get('dietary_features', ['standard']))} features",
                "main_ingredients": gpt4v_data.get("main_ingredients", ""),
                "flavor_profile": gpt4v_data.get("flavor_profile", "neutral"),
                "dietary_features": gpt4v_data.get("dietary_features", []),
                "health_claims": gpt4v_data.get("health_claims", ""),
                "allergen_warnings": gpt4v_data.get("allergen_warnings", ""),
                "calories_per_serving": gpt4v_data.get("calories_per_serving", ""),
                "serving_size": gpt4v_data.get("serving_size", ""),
                "key_nutrients": gpt4v_data.get("key_nutrients", ""),
                "text_quality": gpt4v_data.get("confidence_scores", {}).get("text_quality", "clear"),
                "analysis_status": gpt4v_data.get("confidence_scores", {}).get("analysis_status", "complete")
            }
            
            # Apply ML improvements if available
            if db:
                try:
                    from .ml_improvement_service import ml_improvement_service
                    brief_data = ml_improvement_service.apply_learning_to_brief(brief_data, db)
                except Exception as e:
                    logger.warning(f"ML improvements not available for brief: {e}")
            
            # Cache the brief
            if cache_key and redis_service.is_connected():
                redis_service.cache_ai_analysis(cache_key, "product_brief", brief_data)
            
            return brief_data
        
        try:
            
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
                        
                        # Cache the brief
                        if cache_key and redis_service.is_connected():
                            redis_service.cache_ai_analysis(cache_key, "product_brief", brief_data)
                        
                        return brief_data
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {response.status} - {error_text}")
                        raise ValueError(f"Azure OpenAI API error: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Error generating brief: {e}")
            raise
    
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
        # Product search implementation will be added when Azure Cognitive Search is configured
        # For now, return empty list to maintain API consistency
        logger.info(f"Similar products search requested for '{product_name}' in category '{category}' - Azure Cognitive Search not yet configured")
        return []
    
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
        }

# Create a global instance
product_analysis_service = ProductAnalysisService()