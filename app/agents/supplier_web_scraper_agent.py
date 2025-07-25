"""
Supplier Web Scraper Agent - Automatically visits supplier websites and extracts product catalogs
Handles multiple languages and translates everything to English
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urlparse, urljoin
import aiohttp
from bs4 import BeautifulSoup
import re

from sqlalchemy.orm import Session
from app.database import get_db
from app.models.supplier import Supplier
from app.models.product import Product
from app.config import get_settings

# Azure services for translation and AI
# Azure services for translation and AI
# from azure.ai.translation.text import TextTranslationClient
# from azure.core.credentials import AzureKeyCredential
# from azure.ai.formrecognizer import DocumentAnalysisClient

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class ScrapedProduct:
    """Product extracted from supplier website"""
    original_name: str
    english_name: str
    description: Optional[str]
    category: Optional[str]
    price: Optional[float]
    currency: Optional[str]
    unit: Optional[str]
    image_url: Optional[str]
    source_url: str
    detected_language: str
    confidence_score: float


class SupplierWebScraperAgent:
    """
    Intelligent agent that scrapes supplier websites and extracts product catalogs
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
        # Azure Translation setup (disabled for now)
        self.translator = None
        # self.translator = TextTranslationClient(
        #     endpoint=settings.AZURE_TRANSLATOR_ENDPOINT,
        #     credential=AzureKeyCredential(settings.AZURE_TRANSLATOR_KEY)
        # )
        
        # Common product patterns in multiple languages
        self.product_patterns = {
            'price': [
                r'[\$€£¥₹]\s*(\d+(?:\.\d{2})?)',  # Currency symbols
                r'(\d+(?:\.\d{2})?)\s*(?:USD|EUR|GBP|INR)',  # Currency codes
                r'precio:\s*(\d+(?:\.\d{2})?)',  # Spanish
                r'prix:\s*(\d+(?:\.\d{2})?)',  # French
                r'prezzo:\s*(\d+(?:\.\d{2})?)',  # Italian
                r'价格[:：]\s*(\d+(?:\.\d{2})?)',  # Chinese
                r'मूल्य:\s*(\d+(?:\.\d{2})?)',  # Hindi
            ],
            'unit': [
                r'per\s+(\w+)', r'por\s+(\w+)', r'par\s+(\w+)',
                r'/(\w+)', r'(\d+\s*kg)', r'(\d+\s*lb)', r'(\d+\s*oz)',
                r'(\d+\s*liters?)', r'(\d+\s*gallons?)'
            ]
        }
        
    async def scrape_supplier_website(self, supplier_id: int) -> Dict[str, Any]:
        """
        Main method to scrape a supplier's website
        """
        supplier = self.db.query(Supplier).get(supplier_id)
        if not supplier or not supplier.website:
            return {"error": "Supplier not found or no website"}
        
        logger.info(f"Starting web scrape for supplier: {supplier.name} ({supplier.website})")
        
        try:
            # Step 1: Detect website structure and find product pages
            site_map = await self._analyze_site_structure(supplier.website)
            
            # Step 2: Extract products from identified pages
            all_products = []
            for product_url in site_map['product_urls'][:50]:  # Limit to 50 pages initially
                products = await self._extract_products_from_page(product_url)
                all_products.extend(products)
                
                # Be respectful - add delay between requests
                await asyncio.sleep(7)  # 7 seconds delay as required
            
            # Step 3: Deduplicate and enrich products
            unique_products = self._deduplicate_products(all_products)
            
            # Step 4: Save to database
            saved_count = await self._save_products_to_db(supplier_id, unique_products)
            
            return {
                "supplier_id": supplier_id,
                "supplier_name": supplier.name,
                "website": supplier.website,
                "pages_scraped": len(site_map['product_urls']),
                "products_found": len(all_products),
                "unique_products": len(unique_products),
                "products_saved": saved_count,
                "languages_detected": list(set(p.detected_language for p in unique_products)),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping supplier {supplier_id}: {str(e)}")
            return {"error": str(e), "supplier_id": supplier_id}
    
    async def _analyze_site_structure(self, website: str) -> Dict[str, Any]:
        """
        Analyze website to find product catalog pages
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(website, timeout=30) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for common product catalog patterns
                    product_urls = []
                    base_url = f"{urlparse(website).scheme}://{urlparse(website).netloc}"
                    
                    # Find links that likely contain products
                    product_keywords = [
                        'product', 'catalog', 'shop', 'store', 'item',
                        'productos', 'produits', 'prodotti', '产品', 'उत्पाद',
                        'menu', 'offerings', 'goods', 'merchandise'
                    ]
                    
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        full_url = urljoin(base_url, href)
                        
                        # Check if URL might be a product page
                        if any(keyword in href.lower() for keyword in product_keywords):
                            product_urls.append(full_url)
                    
                    # Also look for structured data (JSON-LD)
                    json_ld_scripts = soup.find_all('script', type='application/ld+json')
                    structured_products = self._extract_structured_data(json_ld_scripts)
                    
                    return {
                        'base_url': base_url,
                        'product_urls': list(set(product_urls))[:100],  # Unique URLs, limit 100
                        'structured_products': structured_products,
                        'detected_language': await self._detect_page_language(html)
                    }
                    
            except Exception as e:
                logger.error(f"Error analyzing site structure: {str(e)}")
                return {'product_urls': [], 'error': str(e)}
    
    async def _extract_products_from_page(self, url: str) -> List[ScrapedProduct]:
        """
        Extract products from a specific page
        """
        products = []
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=30) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Detect page language
                    page_language = await self._detect_page_language(html)
                    
                    # Strategy 1: Look for common product containers
                    product_containers = self._find_product_containers(soup)
                    
                    for container in product_containers:
                        product = await self._extract_product_from_container(
                            container, url, page_language
                        )
                        if product:
                            products.append(product)
                    
                    # Strategy 2: If no containers found, try table extraction
                    if not products:
                        products.extend(await self._extract_products_from_tables(soup, url, page_language))
                    
                    # Strategy 3: Use AI to extract products if still none found
                    if not products and len(html) < 50000:  # Limit size for AI processing
                        products.extend(await self._ai_extract_products(html, url, page_language))
                    
            except Exception as e:
                logger.error(f"Error extracting products from {url}: {str(e)}")
        
        return products
    
    def _find_product_containers(self, soup: BeautifulSoup) -> List[BeautifulSoup]:
        """
        Find HTML elements that likely contain products
        """
        containers = []
        
        # Common class/id patterns for products
        product_selectors = [
            {'class': re.compile(r'product|item|card|listing|article')},
            {'id': re.compile(r'product|item')},
            {'itemtype': re.compile(r'Product|Offer')},  # Schema.org
            {'data-product': True},  # Data attributes
        ]
        
        for selector in product_selectors:
            containers.extend(soup.find_all(['div', 'article', 'li', 'section'], selector))
        
        # Deduplicate containers (avoid nested selections)
        unique_containers = []
        for container in containers:
            if not any(container in parent.descendants for parent in unique_containers):
                unique_containers.append(container)
        
        return unique_containers[:50]  # Limit to 50 products per page
    
    async def _extract_product_from_container(self, container: BeautifulSoup, 
                                            source_url: str, detected_language: str) -> Optional[ScrapedProduct]:
        """
        Extract product information from an HTML container
        """
        try:
            # Extract text content
            text_content = container.get_text(strip=True, separator=' ')
            
            # Find product name (usually in heading or strong tags)
            name_element = (
                container.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']) or
                container.find('strong') or
                container.find('span', class_=re.compile(r'name|title|product'))
            )
            
            if not name_element:
                return None
            
            original_name = name_element.get_text(strip=True)
            if not original_name or len(original_name) < 2:
                return None
            
            # Translate to English if needed
            english_name = await self._translate_to_english(original_name, detected_language)
            
            # Extract price
            price, currency = self._extract_price(text_content)
            
            # Extract unit
            unit = self._extract_unit(text_content)
            
            # Extract description
            desc_element = container.find(['p', 'div'], class_=re.compile(r'desc|summary|details'))
            description = desc_element.get_text(strip=True) if desc_element else None
            if description and detected_language != 'en':
                description = await self._translate_to_english(description, detected_language)
            
            # Extract image
            img_element = container.find('img')
            image_url = None
            if img_element and img_element.get('src'):
                image_url = urljoin(source_url, img_element['src'])
            
            # Categorize product using AI
            category = await self._categorize_product(english_name, description)
            
            return ScrapedProduct(
                original_name=original_name,
                english_name=english_name,
                description=description,
                category=category,
                price=price,
                currency=currency,
                unit=unit,
                image_url=image_url,
                source_url=source_url,
                detected_language=detected_language,
                confidence_score=0.8  # Base confidence, can be adjusted
            )
            
        except Exception as e:
            logger.error(f"Error extracting product from container: {str(e)}")
            return None
    
    async def _extract_products_from_tables(self, soup: BeautifulSoup, 
                                          source_url: str, detected_language: str) -> List[ScrapedProduct]:
        """
        Extract products from HTML tables (common in B2B sites)
        """
        products = []
        
        for table in soup.find_all('table'):
            # Look for header row
            headers = []
            header_row = table.find('tr')
            if header_row:
                headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
            
            # Map headers to fields
            name_idx = next((i for i, h in enumerate(headers) if any(
                keyword in h for keyword in ['product', 'name', 'item', 'description']
            )), None)
            
            price_idx = next((i for i, h in enumerate(headers) if any(
                keyword in h for keyword in ['price', 'cost', 'rate']
            )), None)
            
            if name_idx is not None:
                # Extract products from rows
                for row in table.find_all('tr')[1:]:  # Skip header
                    cells = row.find_all(['td'])
                    if len(cells) > name_idx:
                        original_name = cells[name_idx].get_text(strip=True)
                        if original_name:
                            english_name = await self._translate_to_english(original_name, detected_language)
                            
                            price = None
                            if price_idx and len(cells) > price_idx:
                                price_text = cells[price_idx].get_text(strip=True)
                                price, currency = self._extract_price(price_text)
                            
                            products.append(ScrapedProduct(
                                original_name=original_name,
                                english_name=english_name,
                                description=None,
                                category=await self._categorize_product(english_name, None),
                                price=price,
                                currency=currency,
                                unit=None,
                                image_url=None,
                                source_url=source_url,
                                detected_language=detected_language,
                                confidence_score=0.7
                            ))
        
        return products
    
    async def _ai_extract_products(self, html: str, source_url: str, detected_language: str) -> List[ScrapedProduct]:
        """
        Use Azure OpenAI to extract products when standard parsing fails
        """
        try:
            # Clean HTML for AI processing
            soup = BeautifulSoup(html, 'html.parser')
            text_content = soup.get_text(separator='\n', strip=True)[:5000]  # Limit size
            
            prompt = f"""
            Extract product information from this webpage text. The page is in {detected_language}.
            
            Text:
            {text_content}
            
            For each product found, provide:
            1. Product name (original language)
            2. English translation
            3. Description (if available)
            4. Price (with currency)
            5. Unit (kg, lb, piece, etc.)
            
            Return as JSON array.
            """
            
            # Call Azure OpenAI
            from app.services.ai_service import ai_service
            response = await ai_service.analyze_supplier_email({
                'subject': 'Product Extraction',
                'body': prompt
            })
            
            products = []
            extracted_data = response.get('extracted_data', {}).get('products', [])
            
            for item in extracted_data:
                products.append(ScrapedProduct(
                    original_name=item.get('name', ''),
                    english_name=item.get('english_name', item.get('name', '')),
                    description=item.get('description'),
                    category=await self._categorize_product(item.get('english_name', ''), item.get('description')),
                    price=item.get('price'),
                    currency=item.get('currency'),
                    unit=item.get('unit'),
                    image_url=None,
                    source_url=source_url,
                    detected_language=detected_language,
                    confidence_score=0.9  # High confidence from AI
                ))
            
            return products
            
        except Exception as e:
            logger.error(f"AI extraction failed: {str(e)}")
            return []
    
    async def _translate_to_english(self, text: str, source_language: str) -> str:
        """
        Translate text to English (placeholder - returns original for now)
        """
        if not text or source_language == 'en':
            return text
            
        # For now, just return the original text
        # In production, use Azure Translator or Google Translate API
        return text
    
    async def _detect_page_language(self, html: str) -> str:
        """
        Detect the language of a webpage
        """
        # Check HTML lang attribute
        soup = BeautifulSoup(html, 'html.parser')
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            return html_tag['lang'][:2]  # Return first 2 chars (e.g., 'en' from 'en-US')
        
        # Simple language detection based on common words
        text_sample = soup.get_text(strip=True)[:1000].lower()
        
        # Language indicators
        if any(word in text_sample for word in ['the', 'and', 'for', 'with']):
            return 'en'
        elif any(word in text_sample for word in ['le', 'la', 'de', 'et']):
            return 'fr'
        elif any(word in text_sample for word in ['el', 'la', 'de', 'y']):
            return 'es'
        elif any(word in text_sample for word in ['il', 'la', 'di', 'e']):
            return 'it'
        elif any(word in text_sample for word in ['der', 'die', 'das', 'und']):
            return 'de'
        
        return 'en'  # Default to English
    
    def _extract_price(self, text: str) -> tuple[Optional[float], Optional[str]]:
        """
        Extract price and currency from text
        """
        for pattern in self.product_patterns['price']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    price = float(match.group(1).replace(',', ''))
                    
                    # Detect currency
                    currency = 'USD'  # Default
                    if '$' in text:
                        currency = 'USD'
                    elif '€' in text:
                        currency = 'EUR'
                    elif '£' in text:
                        currency = 'GBP'
                    elif '¥' in text:
                        currency = 'JPY'
                    elif '₹' in text:
                        currency = 'INR'
                    
                    return price, currency
                except:
                    continue
        
        return None, None
    
    def _extract_unit(self, text: str) -> Optional[str]:
        """
        Extract unit of measurement from text
        """
        # Common units in food industry
        units = ['kg', 'lb', 'oz', 'g', 'liter', 'l', 'gallon', 'piece', 'box', 'case', 'pallet']
        
        text_lower = text.lower()
        for unit in units:
            if f'/{unit}' in text_lower or f'per {unit}' in text_lower or f' {unit}' in text_lower:
                return unit
        
        return None
    
    async def _categorize_product(self, name: str, description: Optional[str]) -> Optional[str]:
        """
        Categorize product using AI or keyword matching
        """
        # Simple keyword-based categorization
        categories = {
            'dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream'],
            'meat': ['beef', 'pork', 'chicken', 'lamb', 'meat'],
            'seafood': ['fish', 'salmon', 'shrimp', 'tuna', 'seafood'],
            'produce': ['tomato', 'lettuce', 'onion', 'potato', 'vegetable', 'fruit'],
            'grains': ['rice', 'wheat', 'flour', 'bread', 'pasta'],
            'oils': ['oil', 'olive oil', 'cooking oil', 'vegetable oil'],
            'spices': ['spice', 'pepper', 'salt', 'seasoning', 'herb']
        }
        
        name_lower = name.lower()
        desc_lower = (description or '').lower()
        
        for category, keywords in categories.items():
            if any(keyword in name_lower or keyword in desc_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def _deduplicate_products(self, products: List[ScrapedProduct]) -> List[ScrapedProduct]:
        """
        Remove duplicate products based on name similarity
        """
        unique_products = []
        seen_names = set()
        
        for product in products:
            # Simple deduplication by exact name
            name_key = product.english_name.lower().strip()
            if name_key not in seen_names:
                seen_names.add(name_key)
                unique_products.append(product)
        
        return unique_products
    
    async def _save_products_to_db(self, supplier_id: int, products: List[ScrapedProduct]) -> int:
        """
        Save scraped products to database
        """
        saved_count = 0
        
        for product in products:
            try:
                # Check if product already exists
                existing = self.db.query(Product).filter(
                    Product.supplier_id == supplier_id,
                    Product.name == product.english_name
                ).first()
                
                if existing:
                    # Update existing product
                    existing.original_name = product.original_name
                    existing.description = product.description or existing.description
                    existing.category = product.category or existing.category
                    existing.price = product.price or existing.price
                    existing.currency = product.currency or existing.currency
                    existing.unit = product.unit or existing.unit
                    existing.image_url = product.image_url or existing.image_url
                    existing.last_updated = datetime.utcnow()
                else:
                    # Create new product
                    new_product = Product(
                        supplier_id=supplier_id,
                        name=product.english_name,
                        original_name=product.original_name,
                        description=product.description,
                        category=product.category,
                        price=product.price,
                        currency=product.currency,
                        unit=product.unit,
                        image_url=product.image_url,
                        source_url=product.source_url,
                        language=product.detected_language,
                        confidence_score=product.confidence_score,
                        created_at=datetime.utcnow()
                    )
                    self.db.add(new_product)
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving product {product.english_name}: {str(e)}")
                continue
        
        self.db.commit()
        return saved_count
    
    def _extract_structured_data(self, json_ld_scripts: List) -> List[Dict[str, Any]]:
        """
        Extract product data from JSON-LD structured data
        """
        products = []
        
        for script in json_ld_scripts:
            try:
                import json
                data = json.loads(script.string)
                
                # Handle different schema types
                if isinstance(data, dict):
                    if data.get('@type') == 'Product':
                        products.append(self._parse_product_schema(data))
                    elif data.get('@type') == 'ItemList':
                        for item in data.get('itemListElement', []):
                            if item.get('@type') == 'Product':
                                products.append(self._parse_product_schema(item))
                
            except Exception as e:
                logger.error(f"Error parsing structured data: {str(e)}")
        
        return products
    
    def _parse_product_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse schema.org Product data
        """
        return {
            'name': data.get('name'),
            'description': data.get('description'),
            'price': data.get('offers', {}).get('price'),
            'currency': data.get('offers', {}).get('priceCurrency'),
            'image': data.get('image'),
            'category': data.get('category'),
            'brand': data.get('brand', {}).get('name')
        }


class WebScrapingService:
    """
    Service to manage web scraping operations
    """
    
    def __init__(self):
        self.is_running = False
        self.scraping_interval = 86400  # Daily scraping
        
    async def start(self):
        """
        Start the web scraping service
        """
        self.is_running = True
        logger.info("Starting web scraping service")
        
        while self.is_running:
            try:
                await self._scrape_all_suppliers()
                await asyncio.sleep(self.scraping_interval)
            except Exception as e:
                logger.error(f"Web scraping service error: {str(e)}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def _scrape_all_suppliers(self):
        """
        Scrape all active suppliers' websites
        """
        db = next(get_db())
        agent = SupplierWebScraperAgent(db)
        
        # Get suppliers with websites
        suppliers = db.query(Supplier).filter(
            Supplier.website.isnot(None),
            Supplier.is_active == True
        ).all()
        
        logger.info(f"Starting web scrape for {len(suppliers)} suppliers")
        
        for supplier in suppliers:
            try:
                result = await agent.scrape_supplier_website(supplier.id)
                logger.info(f"Scraped {supplier.name}: {result.get('products_saved', 0)} products saved")
                
                # Update supplier last_scraped timestamp
                supplier.last_scraped = datetime.utcnow()
                db.commit()
                
                # Be respectful - wait between suppliers
                await asyncio.sleep(60)  # 1 minute between suppliers
                
            except Exception as e:
                logger.error(f"Error scraping supplier {supplier.id}: {str(e)}")
        
        db.close()
    
    async def scrape_single_supplier(self, supplier_id: int) -> Dict[str, Any]:
        """
        Scrape a single supplier on demand
        """
        db = next(get_db())
        agent = SupplierWebScraperAgent(db)
        
        result = await agent.scrape_supplier_website(supplier_id)
        db.close()
        
        return result
    
    async def stop(self):
        """
        Stop the web scraping service
        """
        self.is_running = False
        logger.info("Stopping web scraping service")


# Global service instance
web_scraping_service = WebScrapingService()