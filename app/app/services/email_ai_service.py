"""
Enhanced Email AI Service
Pattern-based email analysis for immediate functionality
"""
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json

logger = logging.getLogger(__name__)


class EmailIntent(Enum):
    QUOTE_RESPONSE = "quote_response"
    PRICE_UPDATE = "price_update"
    PRODUCT_UPDATE = "product_update"
    AVAILABILITY_UPDATE = "availability_update"
    DELIVERY_UPDATE = "delivery_update"
    CERTIFICATION_UPDATE = "certification_update"
    CONTACT_UPDATE = "contact_update"
    ORDER_CONFIRMATION = "order_confirmation"
    INVOICE = "invoice"
    GENERAL_INQUIRY = "general_inquiry"
    UNKNOWN = "unknown"


class EmailAIService:
    """
    AI service for analyzing supplier emails using pattern matching
    In production, this would integrate with Azure OpenAI
    """
    
    def __init__(self):
        # Intent detection patterns
        self.intent_patterns = {
            EmailIntent.QUOTE_RESPONSE: [
                r"quote|quotation|pricing|offer|proposal",
                r"in response to your (rfq|request)",
                r"pleased to (quote|offer|provide pricing)"
            ],
            EmailIntent.PRICE_UPDATE: [
                r"price (update|change|adjustment|increase|decrease)",
                r"new pricing",
                r"updated (prices|pricing|rates)"
            ],
            EmailIntent.PRODUCT_UPDATE: [
                r"new product|product update|product launch",
                r"now available|now offering",
                r"product catalog|product list"
            ],
            EmailIntent.AVAILABILITY_UPDATE: [
                r"(in|out of) stock",
                r"availability|available",
                r"inventory update",
                r"stock level"
            ],
            EmailIntent.DELIVERY_UPDATE: [
                r"delivery|shipping|shipment",
                r"dispatch|dispatched",
                r"tracking|eta|arrival"
            ],
            EmailIntent.ORDER_CONFIRMATION: [
                r"order confirm|order receipt|order acknowledge",
                r"order #|order number",
                r"confirmed your order"
            ],
            EmailIntent.INVOICE: [
                r"invoice|bill|payment due",
                r"invoice #|invoice number",
                r"amount due|total due"
            ]
        }
        
        # Data extraction patterns
        self.extraction_patterns = {
            "prices": [
                (r"(?:USD|EUR|GBP|€|\$|£)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)", "currency_first"),
                (r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|EUR|GBP|€|\$|£)", "currency_last"),
                (r"(\d+(?:\.\d{2})?)\s*per\s*(kg|lb|unit|case|pallet)", "unit_price")
            ],
            "quantities": [
                r"(\d+(?:,\d{3})*)\s*(kg|tons?|lbs?|units?|cases?|pallets?|containers?)",
                r"quantity:?\s*(\d+(?:,\d{3})*)",
                r"(\d+(?:,\d{3})*)\s*(?:pieces?|pcs)"
            ],
            "dates": [
                r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
                r"(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{2,4})",
                r"delivery (?:by|on|before)\s*([^,\n]+)"
            ],
            "products": [
                r"product:?\s*([^\n,]+)",
                r"item:?\s*([^\n,]+)",
                r"(?:olive oil|pasta|tomatoes?|cheese|wine|vinegar|rice|beans?)[^\n,]*"
            ],
            "order_numbers": [
                r"order\s*#?\s*([A-Z0-9-]+)",
                r"po\s*#?\s*([A-Z0-9-]+)",
                r"reference:?\s*([A-Z0-9-]+)"
            ]
        }
        
    async def analyze_email(self, email_content: str, subject: str, sender: str) -> Dict[str, Any]:
        """
        Analyze email content and extract relevant information
        """
        # Combine subject and content for analysis
        full_text = f"{subject}\n{email_content}".lower()
        
        # Detect intent
        intent, confidence = self._detect_intent(full_text)
        
        # Extract data based on intent
        extracted_data = await self._extract_data(email_content, intent)
        
        # Identify supplier
        supplier_info = self._extract_supplier_info(sender, email_content)
        
        # Generate insights
        insights = self._generate_insights(intent, extracted_data, supplier_info)
        
        return {
            "intent": intent.value,
            "confidence": confidence,
            "extracted_data": extracted_data,
            "supplier_info": supplier_info,
            "insights": insights,
            "requires_action": self._requires_action(intent),
            "suggested_actions": self._suggest_actions(intent, extracted_data)
        }
        
    def _detect_intent(self, text: str) -> Tuple[EmailIntent, float]:
        """
        Detect the intent of the email
        """
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 1
            intent_scores[intent] = score
            
        # Get the intent with highest score
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            if best_intent[1] > 0:
                # Calculate confidence based on pattern matches
                confidence = min(0.3 + (best_intent[1] * 0.2), 0.95)
                return best_intent[0], confidence
                
        return EmailIntent.UNKNOWN, 0.0
        
    async def _extract_data(self, content: str, intent: EmailIntent) -> Dict[str, Any]:
        """
        Extract relevant data based on email intent
        """
        extracted = {}
        
        # Extract prices
        prices = self._extract_prices(content)
        if prices:
            extracted["prices"] = prices
            
        # Extract quantities
        quantities = self._extract_quantities(content)
        if quantities:
            extracted["quantities"] = quantities
            
        # Extract dates
        dates = self._extract_dates(content)
        if dates:
            extracted["dates"] = dates
            
        # Extract products
        products = self._extract_products(content)
        if products:
            extracted["products"] = products
            
        # Extract order/reference numbers
        if intent in [EmailIntent.ORDER_CONFIRMATION, EmailIntent.INVOICE, EmailIntent.QUOTE_RESPONSE]:
            order_numbers = self._extract_order_numbers(content)
            if order_numbers:
                extracted["reference_numbers"] = order_numbers
                
        # Intent-specific extraction
        if intent == EmailIntent.DELIVERY_UPDATE:
            tracking = self._extract_tracking_info(content)
            if tracking:
                extracted["tracking"] = tracking
                
        return extracted
        
    def _extract_prices(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract price information from content
        """
        prices = []
        
        for pattern, pattern_type in self.extraction_patterns["prices"]:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                price_str = match.group(1).replace(",", "")
                try:
                    price = float(price_str)
                    price_info = {"amount": price, "raw": match.group(0)}
                    
                    # Extract unit if present
                    if pattern_type == "unit_price" and len(match.groups()) > 1:
                        price_info["unit"] = match.group(2)
                        
                    prices.append(price_info)
                except ValueError:
                    continue
                    
        return prices
        
    def _extract_quantities(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract quantity information
        """
        quantities = []
        
        for pattern in self.extraction_patterns["quantities"]:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                qty_str = match.group(1).replace(",", "")
                try:
                    quantity = float(qty_str)
                    qty_info = {"amount": quantity, "raw": match.group(0)}
                    
                    # Extract unit if present
                    if len(match.groups()) > 1:
                        qty_info["unit"] = match.group(2).lower()
                        
                    quantities.append(qty_info)
                except ValueError:
                    continue
                    
        return quantities
        
    def _extract_dates(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract date information
        """
        dates = []
        
        for pattern in self.extraction_patterns["dates"]:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                date_str = match.group(1) if len(match.groups()) >= 1 else match.group(0)
                dates.append({
                    "raw": date_str,
                    "context": match.group(0)
                })
                
        return dates
        
    def _extract_products(self, content: str) -> List[str]:
        """
        Extract product mentions
        """
        products = set()
        
        # Known product patterns
        product_patterns = [
            r"olive oil", r"pasta", r"tomatoes?", r"cheese", r"wine",
            r"vinegar", r"rice", r"beans?", r"flour", r"sugar",
            r"coffee", r"tea", r"spices?", r"herbs?", r"nuts?"
        ]
        
        for pattern in product_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Get some context around the product
                start = max(0, match.start() - 20)
                end = min(len(content), match.end() + 20)
                context = content[start:end].strip()
                
                # Clean up the product name
                product = match.group(0).strip().title()
                products.add(product)
                
        return list(products)
        
    def _extract_order_numbers(self, content: str) -> List[str]:
        """
        Extract order/reference numbers
        """
        numbers = []
        
        for pattern in self.extraction_patterns["order_numbers"]:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                number = match.group(1) if len(match.groups()) >= 1 else match.group(0)
                numbers.append(number.upper())
                
        return list(set(numbers))  # Remove duplicates
        
    def _extract_tracking_info(self, content: str) -> Dict[str, Any]:
        """
        Extract tracking/delivery information
        """
        tracking = {}
        
        # Tracking number patterns
        tracking_patterns = [
            r"tracking\s*(?:number|#)?:?\s*([A-Z0-9]+)",
            r"track your (?:order|shipment):\s*([A-Z0-9]+)"
        ]
        
        for pattern in tracking_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                tracking["number"] = match.group(1)
                break
                
        # Delivery status patterns
        status_patterns = [
            r"(shipped|dispatched|in transit|delivered|out for delivery)",
            r"status:\s*([^\n,]+)"
        ]
        
        for pattern in status_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                tracking["status"] = match.group(1).strip()
                break
                
        return tracking
        
    def _extract_supplier_info(self, sender: str, content: str) -> Dict[str, Any]:
        """
        Extract supplier information from email
        """
        supplier_info = {"email": sender}
        
        # Extract company name from email
        email_parts = sender.split("@")
        if len(email_parts) == 2:
            domain = email_parts[1].split(".")[0]
            supplier_info["company_hint"] = domain.title()
            
        # Look for company name in signature
        signature_patterns = [
            r"(?:regards|sincerely|best)[,\n]+([^\n]+)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\n\s*(?:sales|support|customer)",
            r"(?:from|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|LLC|Ltd|Co))?)"
        ]
        
        for pattern in signature_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                supplier_info["company_name"] = match.group(1).strip()
                break
                
        # Extract contact person
        contact_patterns = [
            r"(?:regards|sincerely|best)[,\n]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*\n",
        ]
        
        for pattern in contact_patterns:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                name = match.group(1).strip()
                if len(name.split()) <= 3:  # Likely a person's name
                    supplier_info["contact_name"] = name
                    break
                    
        return supplier_info
        
    def _generate_insights(self, intent: EmailIntent, extracted_data: Dict[str, Any], 
                          supplier_info: Dict[str, Any]) -> List[str]:
        """
        Generate actionable insights from the analysis
        """
        insights = []
        
        # Price-related insights
        if "prices" in extracted_data and extracted_data["prices"]:
            prices = extracted_data["prices"]
            if len(prices) > 1:
                insights.append(f"Multiple price points detected ({len(prices)} prices)")
            
            # Check for unit prices
            unit_prices = [p for p in prices if "unit" in p]
            if unit_prices:
                insights.append("Unit pricing available for comparison")
                
        # Quantity insights
        if "quantities" in extracted_data and extracted_data["quantities"]:
            quantities = extracted_data["quantities"]
            total_qty = sum(q["amount"] for q in quantities)
            if total_qty > 1000:
                insights.append("Large quantity available - potential for volume discount")
                
        # Delivery insights
        if "dates" in extracted_data and extracted_data["dates"]:
            insights.append(f"Delivery timeline mentioned ({len(extracted_data['dates'])} dates)")
            
        # Intent-specific insights
        if intent == EmailIntent.QUOTE_RESPONSE:
            insights.append("New quote received - compare with existing quotes")
        elif intent == EmailIntent.PRICE_UPDATE:
            insights.append("Price change notification - review impact on orders")
        elif intent == EmailIntent.AVAILABILITY_UPDATE:
            insights.append("Stock levels updated - check against pending orders")
            
        # Supplier insights
        if supplier_info.get("company_name"):
            insights.append(f"Supplier identified: {supplier_info['company_name']}")
            
        return insights
        
    def _requires_action(self, intent: EmailIntent) -> bool:
        """
        Determine if the email requires immediate action
        """
        action_required_intents = [
            EmailIntent.QUOTE_RESPONSE,
            EmailIntent.ORDER_CONFIRMATION,
            EmailIntent.INVOICE,
            EmailIntent.DELIVERY_UPDATE
        ]
        
        return intent in action_required_intents
        
    def _suggest_actions(self, intent: EmailIntent, extracted_data: Dict[str, Any]) -> List[str]:
        """
        Suggest actions based on email content
        """
        actions = []
        
        if intent == EmailIntent.QUOTE_RESPONSE:
            actions.append("Add quote to comparison matrix")
            actions.append("Review pricing against budget")
            if "dates" in extracted_data:
                actions.append("Check delivery timeline against requirements")
                
        elif intent == EmailIntent.PRICE_UPDATE:
            actions.append("Update supplier pricing in database")
            actions.append("Assess impact on active RFQs")
            
        elif intent == EmailIntent.PRODUCT_UPDATE:
            actions.append("Update product catalog")
            if "products" in extracted_data:
                actions.append(f"Review new products: {', '.join(extracted_data['products'][:3])}")
                
        elif intent == EmailIntent.ORDER_CONFIRMATION:
            actions.append("Update order status")
            if "reference_numbers" in extracted_data:
                actions.append(f"Track order: {extracted_data['reference_numbers'][0]}")
                
        elif intent == EmailIntent.INVOICE:
            actions.append("Process invoice for payment")
            actions.append("Verify against purchase order")
            
        elif intent == EmailIntent.DELIVERY_UPDATE:
            actions.append("Update delivery status")
            if "tracking" in extracted_data and "number" in extracted_data["tracking"]:
                actions.append(f"Track shipment: {extracted_data['tracking']['number']}")
                
        return actions
        
    async def batch_analyze(self, emails: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple emails in batch
        """
        results = []
        
        for email in emails:
            try:
                result = await self.analyze_email(
                    email.get("content", ""),
                    email.get("subject", ""),
                    email.get("sender", "")
                )
                result["email_id"] = email.get("id")
                results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing email {email.get('id')}: {str(e)}")
                results.append({
                    "email_id": email.get("id"),
                    "error": str(e),
                    "intent": EmailIntent.UNKNOWN.value,
                    "confidence": 0.0
                })
                
        return results


# Singleton instance
email_ai_service = EmailAIService()