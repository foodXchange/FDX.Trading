"""
Azure Translator Service for multilingual text processing
Handles translation of product information while preserving context
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
import aiohttp
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class AzureTranslatorService:
    """Service for translating text using Azure Translator"""
    
    def __init__(self):
        """Initialize Azure Translator service"""
        self.endpoint = os.getenv("AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com")
        self.api_key = os.getenv("AZURE_TRANSLATOR_KEY", "")
        self.region = os.getenv("AZURE_TRANSLATOR_REGION", "")
        self.api_version = "3.0"
        
        # Custom dictionary for food industry terms
        self.custom_dictionary = {
            "hebrew": {
                "במבה": "Bamba",
                "ביסלי": "Bisli", 
                "אסם": "Osem",
                "עלית": "Elite",
                "שטראוס": "Strauss",
                "תנובה": "Tnuva"
            }
        }
        
        if not self.api_key:
            logger.warning("Azure Translator credentials not configured")
        else:
            logger.info("Azure Translator service initialized")
    
    async def detect_language(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Detect the language of the given text
        
        Args:
            text: Text to analyze
            
        Returns:
            Language detection result with confidence score
        """
        if not self.api_key:
            return None
        
        try:
            url = f"{self.endpoint}/detect?api-version={self.api_version}"
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key,
                'Content-type': 'application/json'
            }
            
            if self.region:
                headers['Ocp-Apim-Subscription-Region'] = self.region
            
            body = [{'text': text}]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=body) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result and len(result) > 0:
                            detection = result[0]
                            return {
                                "language": detection.get("language"),
                                "score": detection.get("score", 0),
                                "is_hebrew": detection.get("language") == "he",
                                "is_arabic": detection.get("language") == "ar",
                                "is_rtl": detection.get("language") in ["he", "ar"]
                            }
                    else:
                        error_text = await response.text()
                        logger.error(f"Language detection failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
        
        return None
    
    async def translate_text(
        self,
        text: str,
        target_language: str = "en",
        source_language: Optional[str] = None,
        preserve_entities: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code (default: "en")
            source_language: Source language code (auto-detect if None)
            preserve_entities: Whether to preserve brand names and special terms
            
        Returns:
            Translation result with metadata
        """
        if not self.api_key:
            return None
        
        try:
            # Check if text needs translation
            if not text or text.strip() == "":
                return {"translatedText": "", "detectedLanguage": None}
            
            # Preserve entities if requested
            preserved_terms = []
            if preserve_entities:
                text, preserved_terms = self._preserve_entities(text, source_language)
            
            url = f"{self.endpoint}/translate?api-version={self.api_version}&to={target_language}"
            if source_language:
                url += f"&from={source_language}"
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key,
                'Content-type': 'application/json'
            }
            
            if self.region:
                headers['Ocp-Apim-Subscription-Region'] = self.region
            
            body = [{'text': text}]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=body) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result and len(result) > 0:
                            translation = result[0]
                            translated_text = translation['translations'][0]['text']
                            
                            # Restore preserved entities
                            if preserved_terms:
                                translated_text = self._restore_entities(translated_text, preserved_terms)
                            
                            return {
                                "translatedText": translated_text,
                                "detectedLanguage": translation.get('detectedLanguage', {}).get('language'),
                                "detectedLanguageScore": translation.get('detectedLanguage', {}).get('score'),
                                "targetLanguage": target_language
                            }
                    else:
                        error_text = await response.text()
                        logger.error(f"Translation failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Error translating text: {e}")
        
        return None
    
    async def translate_product_fields(
        self,
        product_data: Dict[str, Any],
        target_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Translate specific product fields while preserving structure
        
        Args:
            product_data: Product data dictionary
            target_language: Target language for translation
            
        Returns:
            Product data with translated fields
        """
        translated_data = product_data.copy()
        
        # Fields to translate
        translatable_fields = [
            "product_name", "brand_name", "main_ingredients",
            "health_claims", "allergen_warnings", "kosher_text_hebrew"
        ]
        
        # Translate each field
        for field in translatable_fields:
            if field in product_data and product_data[field]:
                # Detect if field contains Hebrew/Arabic
                detection = await self.detect_language(str(product_data[field]))
                
                if detection and detection.get("language") != target_language:
                    translation = await self.translate_text(
                        str(product_data[field]),
                        target_language=target_language,
                        source_language=detection.get("language"),
                        preserve_entities=True
                    )
                    
                    if translation:
                        # Store both original and translated
                        translated_data[f"{field}_translated"] = translation["translatedText"]
                        translated_data[f"{field}_original_language"] = detection.get("language")
        
        return translated_data
    
    async def batch_translate(
        self,
        texts: List[str],
        target_language: str = "en",
        source_language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Translate multiple texts in a single request
        
        Args:
            texts: List of texts to translate
            target_language: Target language
            source_language: Source language (auto-detect if None)
            
        Returns:
            List of translation results
        """
        if not self.api_key or not texts:
            return []
        
        try:
            url = f"{self.endpoint}/translate?api-version={self.api_version}&to={target_language}"
            if source_language:
                url += f"&from={source_language}"
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key,
                'Content-type': 'application/json'
            }
            
            if self.region:
                headers['Ocp-Apim-Subscription-Region'] = self.region
            
            # Prepare batch (Azure Translator supports up to 100 texts per request)
            batch_size = 100
            results = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                body = [{'text': text} for text in batch]
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=body) as response:
                        if response.status == 200:
                            batch_results = await response.json()
                            results.extend(batch_results)
                        else:
                            logger.error(f"Batch translation failed: {response.status}")
                            # Add empty results for failed batch
                            results.extend([{"error": "Translation failed"} for _ in batch])
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch translation: {e}")
            return []
    
    def _preserve_entities(self, text: str, language: Optional[str]) -> Tuple[str, List[Dict]]:
        """
        Preserve brand names and special terms from translation
        
        Args:
            text: Original text
            language: Source language
            
        Returns:
            Modified text and list of preserved terms
        """
        preserved = []
        modified_text = text
        
        # Preserve known brand names
        if language == "he" and "hebrew" in self.custom_dictionary:
            for hebrew_term, english_term in self.custom_dictionary["hebrew"].items():
                if hebrew_term in text:
                    placeholder = f"[[ENTITY_{len(preserved)}]]"
                    modified_text = modified_text.replace(hebrew_term, placeholder)
                    preserved.append({
                        "original": hebrew_term,
                        "translation": english_term,
                        "placeholder": placeholder
                    })
        
        return modified_text, preserved
    
    def _restore_entities(self, text: str, preserved_terms: List[Dict]) -> str:
        """
        Restore preserved entities in translated text
        
        Args:
            text: Translated text with placeholders
            preserved_terms: List of preserved terms
            
        Returns:
            Text with restored entities
        """
        restored_text = text
        
        for term in preserved_terms:
            # Replace placeholder with the appropriate translation
            restored_text = restored_text.replace(
                term["placeholder"],
                term["translation"]
            )
        
        return restored_text
    
    async def get_supported_languages(self) -> Dict[str, Any]:
        """
        Get list of supported languages
        
        Returns:
            Dictionary of supported languages
        """
        if not self.api_key:
            return {}
        
        try:
            url = f"{self.endpoint}/languages?api-version={self.api_version}"
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key
            }
            
            if self.region:
                headers['Ocp-Apim-Subscription-Region'] = self.region
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to get supported languages: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error getting supported languages: {e}")
        
        return {}


# Singleton instance
azure_translator_service = AzureTranslatorService()