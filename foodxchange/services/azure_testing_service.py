"""
Azure Testing Service with Real Services and Free Tier Limits
Handles actual Azure API calls with cost monitoring
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import json
from dataclasses import dataclass, asdict
import aiohttp
from azure.core.exceptions import AzureError
from azure.ai.formrecognizer import DocumentAnalysisClient
try:
    from azure.cognitiveservices.vision.computervision import ComputerVisionClient
except ImportError:
    ComputerVisionClient = None
    logger.warning("Azure Computer Vision SDK not available")
# from azure.ai.translation.text import TextTranslationClient  # Not available in current SDK
from azure.core.credentials import AzureKeyCredential
from msrest.authentication import CognitiveServicesCredentials
import pandas as pd
from io import BytesIO

logger = logging.getLogger(__name__)

@dataclass
class UsageMetrics:
    """Track Azure service usage"""
    service: str
    operation: str
    timestamp: datetime
    tokens_used: int = 0
    characters_processed: int = 0
    api_calls: int = 1
    estimated_cost: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    processing_time: float = 0.0

@dataclass
class ServiceLimits:
    """Free tier limits for Azure services"""
    openai_tokens_per_minute: int = 10000
    openai_requests_per_minute: int = 3
    document_pages_per_month: int = 500
    translator_characters_per_month: int = 2000000
    vision_transactions_per_month: int = 5000
    
class AzureTestingService:
    """Service for testing Azure capabilities with real APIs"""
    
    # Pricing estimates (as of 2024)
    PRICING = {
        'openai_gpt4': 0.03 / 1000,  # per token
        'document_intelligence': 1.50 / 1000,  # per page
        'translator': 10.00 / 1000000,  # per character
        'computer_vision': 1.00 / 1000,  # per transaction
    }
    
    def __init__(self):
        self.usage_history: List[UsageMetrics] = []
        self.limits = ServiceLimits()
        self._initialize_clients()
        self.usage_file = "azure_usage_history.json"
        self._load_usage_history()
        
    def _initialize_clients(self):
        """Initialize Azure service clients"""
        # Document Intelligence
        doc_endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
        doc_key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
        if doc_endpoint and doc_key:
            self.document_client = DocumentAnalysisClient(
                endpoint=doc_endpoint,
                credential=AzureKeyCredential(doc_key)
            )
        else:
            self.document_client = None
            
        # Computer Vision
        vision_endpoint = os.getenv('AZURE_VISION_ENDPOINT')
        vision_key = os.getenv('AZURE_VISION_KEY')
        if vision_endpoint and vision_key and ComputerVisionClient:
            self.vision_client = ComputerVisionClient(
                endpoint=vision_endpoint,
                credentials=CognitiveServicesCredentials(vision_key)
            )
        else:
            self.vision_client = None
            
        # Translator (using REST API directly)
        self.translator_key = os.getenv('AZURE_TRANSLATOR_KEY')
        self.translator_endpoint = os.getenv('AZURE_TRANSLATOR_ENDPOINT')
        self.translator_region = os.getenv('AZURE_TRANSLATOR_REGION', 'eastus')
        self.translator_client = bool(self.translator_key and self.translator_endpoint)
            
        # OpenAI configuration
        self.openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.openai_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.openai_deployment = os.getenv('AZURE_OPENAI_VISION_DEPLOYMENT', 'gpt-4o')
        
    def _load_usage_history(self):
        """Load usage history from file"""
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r') as f:
                    data = json.load(f)
                    self.usage_history = [
                        UsageMetrics(**{
                            **item,
                            'timestamp': datetime.fromisoformat(item['timestamp'])
                        })
                        for item in data
                    ]
            except Exception as e:
                logger.error(f"Error loading usage history: {e}")
                
    def _save_usage_history(self):
        """Save usage history to file"""
        try:
            data = [
                {**asdict(metric), 'timestamp': metric.timestamp.isoformat()}
                for metric in self.usage_history
            ]
            with open(self.usage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving usage history: {e}")
            
    def _track_usage(self, metric: UsageMetrics):
        """Track usage and save to history"""
        self.usage_history.append(metric)
        self._save_usage_history()
        
    def check_limits(self, service: str, operation: str) -> Tuple[bool, str]:
        """Check if we're within free tier limits"""
        now = datetime.now()
        
        if service == 'openai':
            # Check tokens per minute
            minute_ago = now - timedelta(minutes=1)
            recent_tokens = sum(
                m.tokens_used for m in self.usage_history
                if m.service == 'openai' and m.timestamp > minute_ago
            )
            if recent_tokens >= self.limits.openai_tokens_per_minute:
                return False, f"OpenAI token limit reached ({recent_tokens}/{self.limits.openai_tokens_per_minute} per minute)"
                
            # Check requests per minute
            recent_requests = sum(
                1 for m in self.usage_history
                if m.service == 'openai' and m.timestamp > minute_ago
            )
            if recent_requests >= self.limits.openai_requests_per_minute:
                return False, f"OpenAI request limit reached ({recent_requests}/{self.limits.openai_requests_per_minute} per minute)"
                
        elif service == 'document_intelligence':
            # Check monthly page limit
            month_start = now.replace(day=1, hour=0, minute=0, second=0)
            monthly_pages = sum(
                m.api_calls for m in self.usage_history
                if m.service == 'document_intelligence' and m.timestamp > month_start
            )
            if monthly_pages >= self.limits.document_pages_per_month:
                return False, f"Document Intelligence monthly limit reached ({monthly_pages}/{self.limits.document_pages_per_month} pages)"
                
        elif service == 'translator':
            # Check monthly character limit
            month_start = now.replace(day=1, hour=0, minute=0, second=0)
            monthly_chars = sum(
                m.characters_processed for m in self.usage_history
                if m.service == 'translator' and m.timestamp > month_start
            )
            if monthly_chars >= self.limits.translator_characters_per_month:
                return False, f"Translator monthly limit reached ({monthly_chars}/{self.limits.translator_characters_per_month} characters)"
                
        elif service == 'computer_vision':
            # Check monthly transaction limit
            month_start = now.replace(day=1, hour=0, minute=0, second=0)
            monthly_transactions = sum(
                m.api_calls for m in self.usage_history
                if m.service == 'computer_vision' and m.timestamp > month_start
            )
            if monthly_transactions >= self.limits.vision_transactions_per_month:
                return False, f"Computer Vision monthly limit reached ({monthly_transactions}/{self.limits.vision_transactions_per_month} transactions)"
                
        return True, "Within limits"
        
    async def test_product_image_analysis(self, image_path: str) -> Dict[str, Any]:
        """Test product image analysis with GPT-4 Vision"""
        start_time = datetime.now()
        
        # Check limits
        can_proceed, message = self.check_limits('openai', 'image_analysis')
        if not can_proceed:
            return {
                'success': False,
                'error': message,
                'limit_reached': True
            }
            
        try:
            # Read image
            with open(image_path, 'rb') as f:
                image_data = f.read()
                
            # Prepare API call
            headers = {
                'api-key': self.openai_key,
                'Content-Type': 'application/json'
            }
            
            # Create prompt for product analysis
            prompt = """Analyze this product image and extract:
1. Product name (in Hebrew if visible)
2. Brand
3. Weight/Volume
4. Ingredients (if visible)
5. Nutritional information
6. Certifications (Kosher, etc.)
7. Barcode if visible

Format as JSON."""
            
            # Prepare request
            import base64
            image_base64 = base64.b64encode(image_data).decode()
            
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.1
            }
            
            # Make API call
            async with aiohttp.ClientSession() as session:
                url = f"{self.openai_endpoint}/openai/deployments/{self.openai_deployment}/chat/completions?api-version=2024-02-15-preview"
                async with session.post(url, headers=headers, json=payload) as response:
                    result = await response.json()
                    
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if 'error' in result:
                raise Exception(result['error']['message'])
                
            # Extract response
            content = result['choices'][0]['message']['content']
            tokens_used = result['usage']['total_tokens']
            
            # Parse JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                product_info = json.loads(json_match.group())
            else:
                product_info = {'raw_response': content}
                
            # Track usage
            cost = tokens_used * self.PRICING['openai_gpt4']
            self._track_usage(UsageMetrics(
                service='openai',
                operation='image_analysis',
                timestamp=datetime.now(),
                tokens_used=tokens_used,
                estimated_cost=cost,
                success=True,
                processing_time=processing_time
            ))
            
            return {
                'success': True,
                'product_info': product_info,
                'tokens_used': tokens_used,
                'estimated_cost': cost,
                'processing_time': processing_time
            }
            
        except Exception as e:
            self._track_usage(UsageMetrics(
                service='openai',
                operation='image_analysis',
                timestamp=datetime.now(),
                success=False,
                error_message=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            ))
            return {
                'success': False,
                'error': str(e)
            }
            
    async def test_csv_translation(self, file_path: str, source_lang: str = 'he', target_lang: str = 'en') -> Dict[str, Any]:
        """Test CSV translation with Azure Translator"""
        start_time = datetime.now()
        
        if not self.translator_client:
            return {
                'success': False,
                'error': 'Translator service not configured'
            }
            
        try:
            # Read CSV
            df = pd.read_csv(file_path, encoding='utf-8')
            total_chars = 0
            translations = {}
            
            # Identify text columns
            text_columns = []
            for col in df.columns:
                if df[col].dtype == 'object':
                    sample = df[col].dropna().head(5)
                    if any(isinstance(val, str) and len(val) > 3 for val in sample):
                        text_columns.append(col)
                        
            # Check character limit
            for col in text_columns:
                col_chars = df[col].dropna().astype(str).str.len().sum()
                total_chars += col_chars
                
            can_proceed, message = self.check_limits('translator', 'csv_translation')
            if not can_proceed:
                return {
                    'success': False,
                    'error': message,
                    'limit_reached': True
                }
                
            # Translate columns
            for col in text_columns:
                translations[col] = []
                
                # Batch translate (max 100 items per request)
                texts = df[col].fillna('').astype(str).tolist()
                for i in range(0, len(texts), 100):
                    batch = texts[i:i+100]
                    
                    # Skip empty texts
                    batch_to_translate = [
                        {"text": text} for text in batch if text.strip()
                    ]
                    
                    if batch_to_translate:
                        # Use REST API directly
                        headers = {
                            'Ocp-Apim-Subscription-Key': self.translator_key,
                            'Ocp-Apim-Subscription-Region': self.translator_region,
                            'Content-type': 'application/json'
                        }
                        
                        endpoint = f"{self.translator_endpoint}/translate"
                        params = {
                            'api-version': '3.0',
                            'from': source_lang,
                            'to': target_lang
                        }
                        
                        async with aiohttp.ClientSession() as session:
                            async with session.post(endpoint, params=params, headers=headers, json=batch_to_translate) as resp:
                                response = await resp.json()
                        
                        # Map results back
                        translated_batch = []
                        translate_idx = 0
                        for text in batch:
                            if text.strip():
                                translated_batch.append(
                                    response[translate_idx]['translations'][0]['text']
                                )
                                translate_idx += 1
                            else:
                                translated_batch.append('')
                                
                        translations[col].extend(translated_batch)
                    else:
                        translations[col].extend([''] * len(batch))
                        
            processing_time = (datetime.now() - start_time).total_seconds()
            cost = total_chars * self.PRICING['translator']
            
            # Track usage
            self._track_usage(UsageMetrics(
                service='translator',
                operation='csv_translation',
                timestamp=datetime.now(),
                characters_processed=total_chars,
                estimated_cost=cost,
                success=True,
                processing_time=processing_time
            ))
            
            # Create translated dataframe
            df_translated = df.copy()
            for col, trans in translations.items():
                df_translated[f"{col}_translated"] = trans
                
            return {
                'success': True,
                'original_df': df,
                'translated_df': df_translated,
                'characters_processed': total_chars,
                'columns_translated': len(text_columns),
                'estimated_cost': cost,
                'processing_time': processing_time
            }
            
        except Exception as e:
            self._track_usage(UsageMetrics(
                service='translator',
                operation='csv_translation',
                timestamp=datetime.now(),
                success=False,
                error_message=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            ))
            return {
                'success': False,
                'error': str(e)
            }
            
    async def test_document_analysis(self, file_path: str) -> Dict[str, Any]:
        """Test document analysis with Azure Document Intelligence"""
        start_time = datetime.now()
        
        if not self.document_client:
            return {
                'success': False,
                'error': 'Document Intelligence service not configured'
            }
            
        # Check limits
        can_proceed, message = self.check_limits('document_intelligence', 'document_analysis')
        if not can_proceed:
            return {
                'success': False,
                'error': message,
                'limit_reached': True
            }
            
        try:
            with open(file_path, 'rb') as f:
                poller = self.document_client.begin_analyze_document(
                    "prebuilt-document", document=f
                )
                result = poller.result()
                
            # Extract information
            extracted_data = {
                'tables': [],
                'key_value_pairs': {},
                'text_content': []
            }
            
            # Extract tables
            for table in result.tables:
                table_data = []
                for cell in table.cells:
                    table_data.append({
                        'row': cell.row_index,
                        'column': cell.column_index,
                        'text': cell.content
                    })
                extracted_data['tables'].append(table_data)
                
            # Extract key-value pairs
            for kv_pair in result.key_value_pairs:
                if kv_pair.key and kv_pair.value:
                    extracted_data['key_value_pairs'][kv_pair.key.content] = kv_pair.value.content
                    
            # Extract text
            for page in result.pages:
                for line in page.lines:
                    extracted_data['text_content'].append(line.content)
                    
            processing_time = (datetime.now() - start_time).total_seconds()
            pages = len(result.pages)
            cost = pages * self.PRICING['document_intelligence']
            
            # Track usage
            self._track_usage(UsageMetrics(
                service='document_intelligence',
                operation='document_analysis',
                timestamp=datetime.now(),
                api_calls=pages,
                estimated_cost=cost,
                success=True,
                processing_time=processing_time
            ))
            
            return {
                'success': True,
                'extracted_data': extracted_data,
                'pages_processed': pages,
                'estimated_cost': cost,
                'processing_time': processing_time
            }
            
        except Exception as e:
            self._track_usage(UsageMetrics(
                service='document_intelligence',
                operation='document_analysis',
                timestamp=datetime.now(),
                success=False,
                error_message=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            ))
            return {
                'success': False,
                'error': str(e)
            }
            
    def get_usage_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get usage summary for the specified period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_usage = [m for m in self.usage_history if m.timestamp > cutoff_date]
        
        summary = {
            'period_days': days,
            'total_cost': sum(m.estimated_cost for m in recent_usage),
            'total_api_calls': len(recent_usage),
            'by_service': {},
            'by_operation': {},
            'success_rate': 0,
            'average_processing_time': 0
        }
        
        # Group by service
        for service in ['openai', 'document_intelligence', 'translator', 'computer_vision']:
            service_usage = [m for m in recent_usage if m.service == service]
            if service_usage:
                summary['by_service'][service] = {
                    'calls': len(service_usage),
                    'cost': sum(m.estimated_cost for m in service_usage),
                    'success_rate': sum(1 for m in service_usage if m.success) / len(service_usage),
                    'average_time': sum(m.processing_time for m in service_usage) / len(service_usage)
                }
                
        # Group by operation
        operations = set(m.operation for m in recent_usage)
        for operation in operations:
            op_usage = [m for m in recent_usage if m.operation == operation]
            summary['by_operation'][operation] = {
                'calls': len(op_usage),
                'cost': sum(m.estimated_cost for m in op_usage),
                'success_rate': sum(1 for m in op_usage if m.success) / len(op_usage)
            }
            
        # Overall metrics
        if recent_usage:
            summary['success_rate'] = sum(1 for m in recent_usage if m.success) / len(recent_usage)
            summary['average_processing_time'] = sum(m.processing_time for m in recent_usage) / len(recent_usage)
            
        return summary
        
    def get_current_limits_status(self) -> Dict[str, Any]:
        """Get current status of all service limits"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        month_start = now.replace(day=1, hour=0, minute=0, second=0)
        
        status = {
            'openai': {
                'tokens_used_per_minute': sum(
                    m.tokens_used for m in self.usage_history
                    if m.service == 'openai' and m.timestamp > minute_ago
                ),
                'tokens_limit_per_minute': self.limits.openai_tokens_per_minute,
                'requests_used_per_minute': sum(
                    1 for m in self.usage_history
                    if m.service == 'openai' and m.timestamp > minute_ago
                ),
                'requests_limit_per_minute': self.limits.openai_requests_per_minute
            },
            'document_intelligence': {
                'pages_used_this_month': sum(
                    m.api_calls for m in self.usage_history
                    if m.service == 'document_intelligence' and m.timestamp > month_start
                ),
                'pages_limit_per_month': self.limits.document_pages_per_month
            },
            'translator': {
                'characters_used_this_month': sum(
                    m.characters_processed for m in self.usage_history
                    if m.service == 'translator' and m.timestamp > month_start
                ),
                'characters_limit_per_month': self.limits.translator_characters_per_month
            },
            'computer_vision': {
                'transactions_used_this_month': sum(
                    m.api_calls for m in self.usage_history
                    if m.service == 'computer_vision' and m.timestamp > month_start
                ),
                'transactions_limit_per_month': self.limits.vision_transactions_per_month
            }
        }
        
        # Add percentage used
        for service in status:
            service_data = status[service]
            for metric in service_data:
                if metric.endswith('_limit_per_minute') or metric.endswith('_limit_per_month'):
                    used_metric = metric.replace('_limit', '_used')
                    if used_metric in service_data:
                        limit = service_data[metric]
                        used = service_data[used_metric]
                        service_data[f"{metric.split('_')[0]}_percentage"] = (used / limit * 100) if limit > 0 else 0
                        
        return status

# Create singleton instance
azure_testing_service = AzureTestingService()