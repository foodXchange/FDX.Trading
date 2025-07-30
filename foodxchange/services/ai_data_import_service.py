"""
AI-Powered Data Import Service using Azure OpenAI
Provides intelligent field mapping, data cleaning, and validation
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import asyncio
import aiohttp
from io import StringIO, BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class AIDataImportService:
    """Service for AI-powered data import with intelligent field mapping"""
    
    # Define schema for different entity types
    SCHEMAS = {
        'suppliers': {
            'fields': {
                'name': 'Company name',
                'email': 'Primary contact email',
                'phone': 'Phone number',
                'country': 'Country of operation',
                'address': 'Full address',
                'products': 'Product categories offered',
                'certifications': 'Quality certifications (ISO, HACCP, etc.)',
                'contact_name': 'Primary contact person',
                'website': 'Company website',
                'established_year': 'Year established',
                'annual_revenue': 'Annual revenue',
                'employee_count': 'Number of employees',
                'payment_terms': 'Standard payment terms',
                'minimum_order': 'Minimum order quantity',
                'lead_time': 'Average lead time',
                'export_countries': 'Countries exported to'
            },
            'required': ['name', 'email', 'country']
        },
        'buyers': {
            'fields': {
                'company_name': 'Company name',
                'contact_name': 'Contact person name',
                'email': 'Contact email',
                'phone': 'Phone number',
                'industry': 'Industry sector',
                'volume_requirements': 'Annual purchase volume',
                'product_interests': 'Product categories interested in',
                'country': 'Country',
                'preferred_suppliers': 'Preferred supplier regions',
                'budget_range': 'Budget range',
                'purchase_frequency': 'Purchase frequency'
            },
            'required': ['company_name', 'email', 'contact_name']
        },
        'products': {
            'fields': {
                'product_name': 'Product name',
                'brand_name': 'Brand name',
                'category': 'Product category',
                'subcategory': 'Product subcategory',
                'description': 'Product description',
                'ingredients': 'Ingredients list',
                'kosher_status': 'Kosher certification status',
                'halal_status': 'Halal certification status',
                'organic': 'Organic certification',
                'origin_country': 'Country of origin',
                'shelf_life': 'Shelf life',
                'packaging': 'Packaging type',
                'unit_size': 'Unit size/weight',
                'price_range': 'Price range',
                'minimum_order': 'Minimum order quantity',
                'certifications': 'Other certifications'
            },
            'required': ['product_name', 'category']
        }
    }
    
    def __init__(self):
        """Initialize AI Data Import service"""
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-35-turbo")
        self.api_version = "2024-02-01"
        
        # Debug logging
        logger.debug(f"Loading Azure OpenAI config - Endpoint: {self.endpoint[:20]}... Key: {'***' if self.api_key else 'Not set'}")
        
        if not self.endpoint or not self.api_key:
            logger.warning("Azure OpenAI credentials not configured")
        else:
            logger.info("AI Data Import service initialized with Azure OpenAI")
    
    async def analyze_import_file(
        self,
        file_data: bytes,
        file_name: str,
        entity_type: str
    ) -> Dict[str, Any]:
        """
        Analyze uploaded file and suggest field mappings
        
        Args:
            file_data: Raw file data
            file_name: Original filename
            entity_type: Type of data (suppliers, buyers, products)
            
        Returns:
            Analysis results with field mappings
        """
        try:
            # Extract sample data
            sample_data = await self._extract_sample_data(file_data, file_name)
            if not sample_data:
                return {
                    "success": False,
                    "error": "Could not extract data from file"
                }
            
            # Get schema for entity type
            schema = self.SCHEMAS.get(entity_type, self.SCHEMAS['suppliers'])
            
            # Create analysis prompt
            analysis_prompt = self._create_analysis_prompt(
                sample_data,
                schema,
                entity_type
            )
            
            # Call Azure OpenAI
            mapping_result = await self._call_openai_api(analysis_prompt)
            
            # Process and structure the results
            processed_result = self._process_mapping_result(
                mapping_result,
                sample_data['headers'],
                schema
            )
            
            return {
                "success": True,
                "data": processed_result,
                "sample_data": sample_data,
                "entity_type": entity_type
            }
            
        except Exception as e:
            logger.error(f"Error analyzing import file: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _extract_sample_data(
        self,
        file_data: bytes,
        file_name: str,
        sample_rows: int = 5
    ) -> Optional[Dict[str, Any]]:
        """Extract headers and sample rows from file"""
        try:
            # Determine file type
            file_ext = file_name.lower().split('.')[-1]
            
            if file_ext == 'csv':
                # Handle CSV
                text_data = file_data.decode('utf-8', errors='ignore')
                df = pd.read_csv(StringIO(text_data))
            elif file_ext in ['xlsx', 'xls']:
                # Handle Excel
                df = pd.read_excel(BytesIO(file_data))
            else:
                return None
            
            # Get headers and sample data
            headers = df.columns.tolist()
            sample_rows = df.head(sample_rows).replace(np.nan, '').to_dict('records')
            
            # Get data statistics
            stats = {
                "total_rows": len(df),
                "total_columns": len(headers),
                "empty_cells": df.isnull().sum().to_dict(),
                "data_types": df.dtypes.astype(str).to_dict()
            }
            
            return {
                "headers": headers,
                "sample_rows": sample_rows,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error extracting sample data: {e}")
            return None
    
    def _create_analysis_prompt(
        self,
        sample_data: Dict[str, Any],
        schema: Dict[str, Any],
        entity_type: str
    ) -> str:
        """Create the prompt for AI analysis"""
        prompt = f"""You are an expert data analyst specializing in food industry data import. 
Analyze this data file for importing {entity_type} into a food sourcing platform.

Input file headers: {json.dumps(sample_data['headers'])}

Sample data rows:
{json.dumps(sample_data['sample_rows'], indent=2)}

Our existing {entity_type} schema:
{json.dumps(schema['fields'], indent=2)}

Required fields: {schema['required']}

Please analyze and provide:
1. Field mappings from input headers to our schema fields
2. Confidence level for each mapping (0-100)
3. Unmapped input fields that might be useful
4. Data quality issues found
5. Suggested data cleaning operations
6. Potential duplicate detection strategy

Return your analysis in this exact JSON format:
{{
    "confirmed_mappings": [
        {{
            "source_field": "input header",
            "target_field": "our schema field",
            "confidence": 95,
            "sample_values": ["value1", "value2"],
            "data_type": "string",
            "cleaning_needed": "none"
        }}
    ],
    "uncertain_mappings": [
        {{
            "source_field": "input header",
            "suggested_targets": ["field1", "field2"],
            "confidence": 70,
            "reasoning": "why uncertain"
        }}
    ],
    "unmapped_fields": [
        {{
            "field": "input header",
            "sample_values": ["val1", "val2"],
            "suggestion": "could be useful for X"
        }}
    ],
    "new_field_suggestions": [
        {{
            "name": "suggested_field_name",
            "source_fields": ["field1", "field2"],
            "type": "string",
            "reasoning": "why this would be useful"
        }}
    ],
    "data_quality_issues": [
        {{
            "field": "field name",
            "issue": "issue description",
            "severity": "high/medium/low",
            "affected_rows": 10,
            "suggestion": "how to fix"
        }}
    ],
    "cleaning_operations": [
        {{
            "field": "field name",
            "operation": "standardize_country_names",
            "description": "Convert USA/US/United States to United States"
        }}
    ],
    "duplicate_strategy": {{
        "key_fields": ["field1", "field2"],
        "similarity_check_fields": ["field3", "field4"],
        "method": "description of deduplication approach"
    }}
}}"""
        
        return prompt
    
    async def _call_openai_api(self, prompt: str) -> Dict[str, Any]:
        """Call Azure OpenAI API"""
        if not self.endpoint or not self.api_key:
            raise ValueError("Azure OpenAI not configured")
        
        url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert data analyst. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result['choices'][0]['message']['content']
                    return json.loads(content)
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error: {response.status} - {error_text}")
    
    def _process_mapping_result(
        self,
        ai_result: Dict[str, Any],
        original_headers: List[str],
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process and enhance AI mapping results"""
        # Ensure all required fields have mappings
        required_fields = schema.get('required', [])
        mapped_required = set()
        
        for mapping in ai_result.get('confirmed_mappings', []):
            if mapping['target_field'] in required_fields:
                mapped_required.add(mapping['target_field'])
        
        # Flag missing required fields
        missing_required = set(required_fields) - mapped_required
        
        # Add validation rules based on field types
        for mapping in ai_result.get('confirmed_mappings', []):
            field_name = mapping['target_field']
            if 'email' in field_name.lower():
                mapping['validation'] = 'email'
            elif 'phone' in field_name.lower():
                mapping['validation'] = 'phone'
            elif 'date' in field_name.lower() or 'year' in field_name.lower():
                mapping['validation'] = 'date'
            elif 'price' in field_name.lower() or 'revenue' in field_name.lower():
                mapping['validation'] = 'currency'
        
        # Enhance result
        ai_result['missing_required_fields'] = list(missing_required)
        ai_result['total_fields'] = len(original_headers)
        ai_result['mapped_fields'] = len(ai_result.get('confirmed_mappings', []))
        ai_result['mapping_coverage'] = round(
            ai_result['mapped_fields'] / ai_result['total_fields'] * 100, 1
        )
        
        return ai_result
    
    async def apply_mappings_and_clean(
        self,
        file_data: bytes,
        file_name: str,
        mappings: Dict[str, Any],
        user_confirmations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply field mappings and clean data"""
        try:
            # Read full file
            file_ext = file_name.lower().split('.')[-1]
            if file_ext == 'csv':
                df = pd.read_csv(BytesIO(file_data))
            else:
                df = pd.read_excel(BytesIO(file_data))
            
            # Apply confirmed mappings
            mapped_df = pd.DataFrame()
            
            for mapping in mappings['confirmed_mappings']:
                source = mapping['source_field']
                target = mapping['target_field']
                
                if source in df.columns:
                    mapped_df[target] = df[source]
                    
                    # Apply cleaning operations
                    if mapping.get('cleaning_needed') != 'none':
                        mapped_df[target] = await self._clean_column(
                            mapped_df[target],
                            mapping.get('cleaning_needed', ''),
                            mapping.get('validation', '')
                        )
            
            # Apply user-confirmed uncertain mappings
            for source, target in user_confirmations.items():
                if source in df.columns and target:
                    mapped_df[target] = df[source]
            
            # Validate data
            validation_results = self._validate_data(mapped_df, mappings)
            
            # Detect duplicates
            duplicate_info = self._detect_duplicates(
                mapped_df,
                mappings.get('duplicate_strategy', {})
            )
            
            return {
                "success": True,
                "cleaned_data": mapped_df.to_dict('records'),
                "row_count": len(mapped_df),
                "validation_results": validation_results,
                "duplicate_info": duplicate_info
            }
            
        except Exception as e:
            logger.error(f"Error applying mappings: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _clean_column(
        self,
        series: pd.Series,
        cleaning_type: str,
        validation_type: str
    ) -> pd.Series:
        """Clean a data column based on type"""
        if validation_type == 'email':
            # Clean and validate emails
            series = series.str.lower().str.strip()
            series = series.str.replace(r'\s+', '', regex=True)
            
        elif validation_type == 'phone':
            # Clean phone numbers
            series = series.astype(str).str.replace(r'[^\d+\-\(\)\s]', '', regex=True)
            series = series.str.strip()
            
        elif cleaning_type == 'standardize_country':
            # Standardize country names
            country_mapping = {
                'usa': 'United States',
                'us': 'United States',
                'u.s.': 'United States',
                'u.s.a.': 'United States',
                'uk': 'United Kingdom',
                'u.k.': 'United Kingdom'
            }
            series = series.str.lower().replace(country_mapping).str.title()
            
        elif cleaning_type == 'trim_whitespace':
            series = series.str.strip()
            
        return series
    
    def _validate_data(
        self,
        df: pd.DataFrame,
        mappings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate cleaned data"""
        issues = []
        
        # Check required fields
        for field in mappings.get('missing_required_fields', []):
            if field not in df.columns or df[field].isnull().all():
                issues.append({
                    "field": field,
                    "issue": "Required field is missing",
                    "severity": "high"
                })
        
        # Validate emails
        email_fields = [col for col in df.columns if 'email' in col.lower()]
        for field in email_fields:
            if field in df.columns:
                invalid_emails = df[~df[field].str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$', na=False)][field]
                if len(invalid_emails) > 0:
                    issues.append({
                        "field": field,
                        "issue": f"Invalid email format",
                        "severity": "medium",
                        "affected_rows": len(invalid_emails),
                        "examples": invalid_emails.head(3).tolist()
                    })
        
        return {
            "total_issues": len(issues),
            "issues": issues,
            "data_quality_score": max(0, 100 - (len(issues) * 10))
        }
    
    def _detect_duplicates(
        self,
        df: pd.DataFrame,
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect potential duplicates in data"""
        duplicates = []
        
        # Use key fields for exact matching
        key_fields = strategy.get('key_fields', [])
        if key_fields:
            # Find exact duplicates
            exact_dupes = df[df.duplicated(subset=key_fields, keep=False)]
            if len(exact_dupes) > 0:
                duplicates.append({
                    "type": "exact",
                    "count": len(exact_dupes),
                    "key_fields": key_fields,
                    "examples": exact_dupes.head(10).to_dict('records')
                })
        
        return {
            "has_duplicates": len(duplicates) > 0,
            "duplicate_count": sum(d['count'] for d in duplicates),
            "duplicates": duplicates
        }
    
    async def process_import_with_ai(
        self,
        file_data: bytes,
        file_name: str,
        entity_type: str,
        user_mappings: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Complete import process with AI assistance
        
        Args:
            file_data: Raw file data
            file_name: Original filename
            entity_type: Type of data being imported
            user_mappings: User-confirmed mappings (optional)
            
        Returns:
            Import results
        """
        try:
            # Step 1: Analyze file
            if not user_mappings:
                analysis = await self.analyze_import_file(
                    file_data,
                    file_name,
                    entity_type
                )
                
                if not analysis['success']:
                    return analysis
                
                return {
                    "success": True,
                    "step": "mapping_required",
                    "analysis": analysis['data'],
                    "sample_data": analysis['sample_data']
                }
            
            # Step 2: Apply mappings and clean data
            cleaned_result = await self.apply_mappings_and_clean(
                file_data,
                file_name,
                user_mappings['analysis'],
                user_mappings.get('user_confirmations', {})
            )
            
            if not cleaned_result['success']:
                return cleaned_result
            
            return {
                "success": True,
                "step": "import_ready",
                "data": cleaned_result
            }
            
        except Exception as e:
            logger.error(f"Error in AI import process: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
ai_data_import_service = AIDataImportService()