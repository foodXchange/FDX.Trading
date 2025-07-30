"""
Azure Document Intelligence Service
Extracts structured data from documents using Azure AI Document Intelligence (formerly Form Recognizer)
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import asyncio
from io import BytesIO

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.formrecognizer import AnalyzeResult
from azure.core.exceptions import HttpResponseError

logger = logging.getLogger(__name__)


class DocumentIntelligenceService:
    """Service for extracting data from documents using Azure Document Intelligence"""
    
    def __init__(self):
        """Initialize Document Intelligence client"""
        self.endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", "")
        self.key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY", "")
        
        if not self.endpoint or not self.key:
            logger.warning("Document Intelligence credentials not configured")
            self.client = None
        else:
            try:
                self.client = DocumentAnalysisClient(
                    endpoint=self.endpoint,
                    credential=AzureKeyCredential(self.key)
                )
                logger.info("Document Intelligence client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Document Intelligence client: {e}")
                self.client = None
    
    async def analyze_document(
        self,
        file_content: bytes,
        model_id: str = "prebuilt-document",
        content_type: str = "application/pdf"
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze a document using the specified model
        
        Available models:
        - prebuilt-document: General document analysis
        - prebuilt-invoice: Invoice processing
        - prebuilt-receipt: Receipt processing
        - prebuilt-businessCard: Business card extraction
        - prebuilt-idDocument: ID document processing
        - prebuilt-layout: Document layout analysis
        - prebuilt-read: Text extraction (OCR)
        """
        if not self.client:
            logger.error("Document Intelligence client not initialized")
            return None
        
        try:
            # Start analysis
            poller = self.client.begin_analyze_document(
                model_id=model_id,
                document=BytesIO(file_content),
                content_type=content_type
            )
            
            # Wait for completion
            result: AnalyzeResult = await asyncio.to_thread(poller.result)
            
            # Extract data based on model type
            extracted_data = await self._extract_data_from_result(result, model_id)
            
            return {
                "success": True,
                "model_used": model_id,
                "pages": len(result.pages) if result.pages else 0,
                "data": extracted_data,
                "confidence": self._calculate_average_confidence(result),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except HttpResponseError as e:
            logger.error(f"HTTP error analyzing document: {e}")
            return {
                "success": False,
                "error": f"HTTP error: {e.message}",
                "error_code": e.error.code if e.error else None
            }
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _extract_data_from_result(
        self,
        result: AnalyzeResult,
        model_id: str
    ) -> Dict[str, Any]:
        """Extract structured data from analysis result based on model type"""
        extracted_data = {
            "text_content": "",
            "tables": [],
            "key_value_pairs": {},
            "entities": [],
            "styles": []
        }
        
        # Extract text content
        if result.content:
            extracted_data["text_content"] = result.content
        
        # Extract tables
        if result.tables:
            for table in result.tables:
                table_data = {
                    "row_count": table.row_count,
                    "column_count": table.column_count,
                    "cells": []
                }
                for cell in table.cells:
                    table_data["cells"].append({
                        "row": cell.row_index,
                        "column": cell.column_index,
                        "text": cell.content,
                        "row_span": cell.row_span if hasattr(cell, 'row_span') else 1,
                        "column_span": cell.column_span if hasattr(cell, 'column_span') else 1
                    })
                extracted_data["tables"].append(table_data)
        
        # Extract key-value pairs
        if result.key_value_pairs:
            for kv_pair in result.key_value_pairs:
                if kv_pair.key and kv_pair.value:
                    key = kv_pair.key.content
                    value = kv_pair.value.content if kv_pair.value else ""
                    confidence = kv_pair.confidence if hasattr(kv_pair, 'confidence') else None
                    extracted_data["key_value_pairs"][key] = {
                        "value": value,
                        "confidence": confidence
                    }
        
        # Extract entities (if available)
        if hasattr(result, 'entities') and result.entities:
            for entity in result.entities:
                extracted_data["entities"].append({
                    "category": entity.category,
                    "subcategory": entity.sub_category if hasattr(entity, 'sub_category') else None,
                    "content": entity.content,
                    "confidence": entity.confidence if hasattr(entity, 'confidence') else None
                })
        
        # Extract document type specific data
        if model_id == "prebuilt-invoice" and result.documents:
            extracted_data["invoice_data"] = self._extract_invoice_data(result.documents[0])
        elif model_id == "prebuilt-receipt" and result.documents:
            extracted_data["receipt_data"] = self._extract_receipt_data(result.documents[0])
        elif model_id == "prebuilt-businessCard" and result.documents:
            extracted_data["business_card_data"] = self._extract_business_card_data(result.documents[0])
        
        # Extract styles and formatting
        if result.styles:
            for style in result.styles:
                extracted_data["styles"].append({
                    "is_handwritten": style.is_handwritten if hasattr(style, 'is_handwritten') else False,
                    "confidence": style.confidence if hasattr(style, 'confidence') else None
                })
        
        return extracted_data
    
    def _extract_invoice_data(self, document) -> Dict[str, Any]:
        """Extract invoice specific fields"""
        invoice_data = {}
        
        fields = document.fields
        field_mapping = {
            "InvoiceId": "invoice_id",
            "InvoiceDate": "invoice_date",
            "DueDate": "due_date",
            "VendorName": "vendor_name",
            "VendorAddress": "vendor_address",
            "CustomerName": "customer_name",
            "CustomerAddress": "customer_address",
            "SubTotal": "subtotal",
            "TotalTax": "tax",
            "InvoiceTotal": "total",
            "Items": "line_items"
        }
        
        for field_name, output_name in field_mapping.items():
            if field_name in fields and fields[field_name]:
                field = fields[field_name]
                if field_name == "Items" and hasattr(field, 'value'):
                    # Process line items
                    items = []
                    for item in field.value:
                        item_data = {}
                        if hasattr(item, 'fields'):
                            for item_field, item_value in item.fields.items():
                                if item_value and hasattr(item_value, 'content'):
                                    item_data[item_field] = item_value.content
                        items.append(item_data)
                    invoice_data[output_name] = items
                else:
                    invoice_data[output_name] = field.content if hasattr(field, 'content') else str(field)
        
        return invoice_data
    
    def _extract_receipt_data(self, document) -> Dict[str, Any]:
        """Extract receipt specific fields"""
        receipt_data = {}
        
        fields = document.fields
        field_mapping = {
            "MerchantName": "merchant_name",
            "MerchantAddress": "merchant_address",
            "MerchantPhoneNumber": "merchant_phone",
            "TransactionDate": "transaction_date",
            "TransactionTime": "transaction_time",
            "Subtotal": "subtotal",
            "Tax": "tax",
            "Total": "total",
            "Items": "items"
        }
        
        for field_name, output_name in field_mapping.items():
            if field_name in fields and fields[field_name]:
                field = fields[field_name]
                if field_name == "Items" and hasattr(field, 'value'):
                    # Process receipt items
                    items = []
                    for item in field.value:
                        item_data = {}
                        if hasattr(item, 'fields'):
                            for item_field, item_value in item.fields.items():
                                if item_value and hasattr(item_value, 'content'):
                                    item_data[item_field] = item_value.content
                        items.append(item_data)
                    receipt_data[output_name] = items
                else:
                    receipt_data[output_name] = field.content if hasattr(field, 'content') else str(field)
        
        return receipt_data
    
    def _extract_business_card_data(self, document) -> Dict[str, Any]:
        """Extract business card specific fields"""
        business_card_data = {}
        
        fields = document.fields
        field_mapping = {
            "ContactNames": "contact_names",
            "JobTitles": "job_titles",
            "Departments": "departments",
            "Emails": "emails",
            "Websites": "websites",
            "Addresses": "addresses",
            "MobilePhones": "mobile_phones",
            "WorkPhones": "work_phones",
            "Faxes": "faxes",
            "CompanyNames": "company_names"
        }
        
        for field_name, output_name in field_mapping.items():
            if field_name in fields and fields[field_name]:
                field = fields[field_name]
                if hasattr(field, 'value') and isinstance(field.value, list):
                    # Extract list values
                    values = []
                    for item in field.value:
                        if hasattr(item, 'content'):
                            values.append(item.content)
                    business_card_data[output_name] = values
                else:
                    business_card_data[output_name] = field.content if hasattr(field, 'content') else str(field)
        
        return business_card_data
    
    def _calculate_average_confidence(self, result: AnalyzeResult) -> float:
        """Calculate average confidence score from result"""
        confidences = []
        
        # Collect confidence scores from various elements
        if result.key_value_pairs:
            for kv in result.key_value_pairs:
                if hasattr(kv, 'confidence') and kv.confidence:
                    confidences.append(kv.confidence)
        
        if hasattr(result, 'entities') and result.entities:
            for entity in result.entities:
                if hasattr(entity, 'confidence') and entity.confidence:
                    confidences.append(entity.confidence)
        
        if result.tables:
            for table in result.tables:
                if hasattr(table, 'confidence') and table.confidence:
                    confidences.append(table.confidence)
        
        # Return average confidence or 0 if no confidence scores
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    async def analyze_product_document(
        self,
        file_content: bytes,
        content_type: str = "application/pdf"
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze a product-related document (spec sheet, catalog, etc.)
        Uses general document model and extracts product-specific information
        """
        result = await self.analyze_document(
            file_content=file_content,
            model_id="prebuilt-document",
            content_type=content_type
        )
        
        if not result or not result.get("success"):
            return result
        
        # Extract product-specific information
        data = result.get("data", {})
        key_value_pairs = data.get("key_value_pairs", {})
        
        # Look for common product fields
        product_info = {
            "product_name": self._find_field_value(key_value_pairs, ["product", "name", "item", "description"]),
            "brand": self._find_field_value(key_value_pairs, ["brand", "manufacturer", "company"]),
            "sku": self._find_field_value(key_value_pairs, ["sku", "item number", "product code", "code"]),
            "price": self._find_field_value(key_value_pairs, ["price", "cost", "msrp", "retail"]),
            "weight": self._find_field_value(key_value_pairs, ["weight", "net weight", "gross weight"]),
            "dimensions": self._find_field_value(key_value_pairs, ["dimensions", "size", "measurements"]),
            "ingredients": self._find_field_value(key_value_pairs, ["ingredients", "composition", "materials"]),
            "nutrition": self._find_field_value(key_value_pairs, ["nutrition", "nutritional", "nutrients"]),
            "certifications": self._find_field_value(key_value_pairs, ["certification", "certified", "kosher", "halal", "organic"]),
            "shelf_life": self._find_field_value(key_value_pairs, ["shelf life", "expiry", "best before", "expiration"]),
            "storage": self._find_field_value(key_value_pairs, ["storage", "store", "temperature", "conditions"])
        }
        
        # Add extracted product info to result
        result["product_info"] = product_info
        
        return result
    
    def _find_field_value(
        self,
        key_value_pairs: Dict[str, Any],
        search_terms: List[str]
    ) -> Optional[str]:
        """Find a field value by searching for various key terms"""
        for key, value_data in key_value_pairs.items():
            key_lower = key.lower()
            for term in search_terms:
                if term.lower() in key_lower:
                    return value_data.get("value") if isinstance(value_data, dict) else value_data
        return None
    
    async def extract_text_with_layout(
        self,
        file_content: bytes,
        content_type: str = "application/pdf"
    ) -> Optional[Dict[str, Any]]:
        """
        Extract text while preserving layout information
        Useful for maintaining document structure
        """
        return await self.analyze_document(
            file_content=file_content,
            model_id="prebuilt-layout",
            content_type=content_type
        )
    
    async def extract_text_only(
        self,
        file_content: bytes,
        content_type: str = "application/pdf"
    ) -> Optional[str]:
        """
        Extract only text content from document (OCR)
        Returns plain text without structure
        """
        result = await self.analyze_document(
            file_content=file_content,
            model_id="prebuilt-read",
            content_type=content_type
        )
        
        if result and result.get("success"):
            return result.get("data", {}).get("text_content", "")
        return None


# Singleton instance
document_intelligence_service = DocumentIntelligenceService()