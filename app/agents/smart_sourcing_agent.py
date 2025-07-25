"""
Smart Sourcing Agent - Automatically matches buyers with ideal suppliers
Leverages Azure services for intelligent B2B matchmaking
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

from sqlalchemy.orm import Session
from app.database import get_db
from app.models.supplier import Supplier
from app.models.rfq import RFQ
from app.models.user import User
from app.config import get_settings
from app.services.ai_service import ai_service

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class BuyerIntent:
    """Analyzed buyer intent from their behavior"""
    products: List[str]
    quality_preferences: Dict[str, Any]
    budget_range: Dict[str, float]
    delivery_requirements: Dict[str, Any]
    certification_needs: List[str]
    preferred_regions: List[str]
    urgency_level: str  # low, medium, high, urgent
    confidence_score: float


@dataclass
class SupplierMatch:
    """Supplier matching result"""
    supplier_id: int
    match_score: float
    strengths: List[str]
    weaknesses: List[str]
    recommended_products: List[Dict[str, Any]]
    estimated_savings: float
    delivery_time: int  # days
    risk_score: float


class SmartSourcingAgent:
    """
    Intelligent agent that proactively matches buyers with suppliers
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.min_match_score = 0.7
        self.max_recommendations = 5
        self.learning_enabled = True
        
    async def analyze_buyer_intent(self, buyer_id: int) -> BuyerIntent:
        """
        Analyze buyer's behavior to understand their needs
        """
        # Get buyer's history
        recent_rfqs = self.db.query(RFQ).filter(
            RFQ.buyer_id == buyer_id,
            RFQ.created_at >= datetime.utcnow() - timedelta(days=90)
        ).all()
        
        # Analyze patterns using Azure OpenAI
        intent_prompt = f"""
        Analyze this buyer's RFQ history and extract their preferences:
        
        Recent RFQs:
        {json.dumps([{
            'product': rfq.product_name,
            'quantity': rfq.quantity,
            'budget': rfq.budget,
            'delivery_date': rfq.delivery_date.isoformat() if rfq.delivery_date else None,
            'requirements': rfq.requirements
        } for rfq in recent_rfqs], indent=2)}
        
        Extract:
        1. Product categories they frequently buy
        2. Quality preferences (premium, standard, budget)
        3. Typical budget ranges
        4. Delivery time patterns
        5. Certification requirements
        6. Preferred supplier regions
        7. Urgency patterns
        
        Return as structured JSON.
        """
        
        analysis = await ai_service.analyze_supplier_email({
            'subject': 'Buyer Intent Analysis',
            'body': intent_prompt
        })
        
        # Parse AI response into BuyerIntent
        return BuyerIntent(
            products=analysis.get('extracted_data', {}).get('products', []),
            quality_preferences=analysis.get('extracted_data', {}).get('quality', {}),
            budget_range=analysis.get('extracted_data', {}).get('budget_range', {}),
            delivery_requirements=analysis.get('extracted_data', {}).get('delivery', {}),
            certification_needs=analysis.get('extracted_data', {}).get('certifications', []),
            preferred_regions=analysis.get('extracted_data', {}).get('regions', []),
            urgency_level=analysis.get('extracted_data', {}).get('urgency', 'medium'),
            confidence_score=analysis.get('confidence', 0.8)
        )
        
    async def find_matching_suppliers(self, buyer_intent: BuyerIntent) -> List[SupplierMatch]:
        """
        Find suppliers that match buyer's needs using intelligent matching
        """
        # Query potential suppliers
        suppliers = self.db.query(Supplier).filter(
            Supplier.is_active == True,
            Supplier.is_verified == True
        ).all()
        
        matches = []
        
        for supplier in suppliers:
            # Calculate match score using multiple factors
            match_score = await self._calculate_match_score(supplier, buyer_intent)
            
            if match_score >= self.min_match_score:
                # Get detailed match analysis
                match_details = await self._analyze_match_details(supplier, buyer_intent)
                
                matches.append(SupplierMatch(
                    supplier_id=supplier.id,
                    match_score=match_score,
                    strengths=match_details['strengths'],
                    weaknesses=match_details['weaknesses'],
                    recommended_products=match_details['products'],
                    estimated_savings=match_details['savings'],
                    delivery_time=match_details['delivery_days'],
                    risk_score=match_details['risk']
                ))
        
        # Sort by match score and return top matches
        matches.sort(key=lambda x: x.match_score, reverse=True)
        return matches[:self.max_recommendations]
        
    async def _calculate_match_score(self, supplier: Supplier, intent: BuyerIntent) -> float:
        """
        Calculate how well a supplier matches buyer intent
        """
        score = 0.0
        weights = {
            'product_match': 0.3,
            'price_match': 0.25,
            'delivery_match': 0.2,
            'certification_match': 0.15,
            'region_match': 0.1
        }
        
        # Product match
        supplier_products = set(supplier.products.split(',')) if supplier.products else set()
        buyer_products = set(intent.products)
        product_overlap = len(supplier_products.intersection(buyer_products))
        if buyer_products:
            score += weights['product_match'] * (product_overlap / len(buyer_products))
        
        # Price competitiveness
        # In real implementation, would check actual pricing data
        score += weights['price_match'] * 0.8  # Placeholder
        
        # Delivery capability
        if supplier.delivery_days:
            if intent.urgency_level == 'urgent' and supplier.delivery_days <= 3:
                score += weights['delivery_match']
            elif intent.urgency_level == 'high' and supplier.delivery_days <= 7:
                score += weights['delivery_match'] * 0.8
            else:
                score += weights['delivery_match'] * 0.5
        
        # Certification match
        supplier_certs = set(supplier.certifications.split(',')) if supplier.certifications else set()
        required_certs = set(intent.certification_needs)
        if required_certs:
            cert_match = len(supplier_certs.intersection(required_certs)) / len(required_certs)
            score += weights['certification_match'] * cert_match
        
        # Region preference
        if supplier.location in intent.preferred_regions:
            score += weights['region_match']
        
        return min(score, 1.0)
        
    async def _analyze_match_details(self, supplier: Supplier, intent: BuyerIntent) -> Dict[str, Any]:
        """
        Get detailed analysis of why this supplier is a good match
        """
        # Use AI to provide detailed matching insights
        analysis_prompt = f"""
        Analyze why this supplier matches the buyer's needs:
        
        Supplier: {supplier.name}
        Products: {supplier.products}
        Certifications: {supplier.certifications}
        Location: {supplier.location}
        Rating: {supplier.rating}
        
        Buyer needs:
        Products: {intent.products}
        Certifications: {intent.certification_needs}
        Urgency: {intent.urgency_level}
        
        Provide:
        1. Key strengths of this match
        2. Potential weaknesses
        3. Recommended products to source
        4. Estimated cost savings percentage
        5. Risk assessment (0-1)
        """
        
        # In production, this would call Azure OpenAI
        # For now, return realistic mock data
        return {
            'strengths': [
                f"Specializes in {intent.products[0] if intent.products else 'your products'}",
                "Competitive pricing with volume discounts",
                "Excellent delivery track record"
            ],
            'weaknesses': [
                "Minimum order quantities may be high",
                "Limited weekend support"
            ],
            'products': [
                {
                    'name': intent.products[0] if intent.products else 'Premium Olive Oil',
                    'price_range': '$10-12/L',
                    'moq': '100L',
                    'lead_time': '3-5 days'
                }
            ],
            'savings': 15.5,
            'delivery_days': 4,
            'risk': 0.2
        }
        
    async def generate_recommendations(self, buyer_id: int) -> Dict[str, Any]:
        """
        Generate personalized supplier recommendations for a buyer
        """
        try:
            # Analyze buyer intent
            buyer_intent = await self.analyze_buyer_intent(buyer_id)
            
            # Find matching suppliers
            matches = await self.find_matching_suppliers(buyer_intent)
            
            # Format recommendations
            recommendations = {
                'buyer_id': buyer_id,
                'generated_at': datetime.utcnow().isoformat(),
                'intent_confidence': buyer_intent.confidence_score,
                'recommendations': []
            }
            
            for match in matches:
                supplier = self.db.query(Supplier).get(match.supplier_id)
                recommendations['recommendations'].append({
                    'supplier': {
                        'id': supplier.id,
                        'name': supplier.name,
                        'location': supplier.location,
                        'rating': supplier.rating
                    },
                    'match_score': match.match_score,
                    'strengths': match.strengths,
                    'weaknesses': match.weaknesses,
                    'recommended_products': match.recommended_products,
                    'estimated_savings': f"{match.estimated_savings}%",
                    'delivery_time': f"{match.delivery_time} days",
                    'risk_level': 'Low' if match.risk_score < 0.3 else 'Medium'
                })
            
            # Store recommendations for learning
            if self.learning_enabled:
                await self._store_recommendations(recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {
                'error': 'Failed to generate recommendations',
                'buyer_id': buyer_id
            }
            
    async def _store_recommendations(self, recommendations: Dict[str, Any]):
        """
        Store recommendations for learning and improvement
        """
        # In production, store in Azure Cosmos DB for analysis
        logger.info(f"Storing recommendations for buyer {recommendations['buyer_id']}")
        
    async def learn_from_feedback(self, recommendation_id: str, feedback: Dict[str, Any]):
        """
        Learn from buyer feedback to improve future recommendations
        """
        # Update ML models based on feedback
        # Track which recommendations led to successful orders
        pass
        
    async def proactive_sourcing_alerts(self) -> List[Dict[str, Any]]:
        """
        Generate proactive alerts for buyers about new opportunities
        """
        alerts = []
        
        # Check for price drops
        # Check for new suppliers
        # Check for seasonal opportunities
        # Check for bulk discount opportunities
        
        return alerts


class ProactiveSourcingService:
    """
    Service to run proactive sourcing for all buyers
    """
    
    def __init__(self):
        self.check_interval = 3600  # 1 hour
        self.is_running = False
        
    async def start(self):
        """
        Start proactive sourcing service
        """
        self.is_running = True
        
        while self.is_running:
            try:
                await self._run_sourcing_cycle()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Proactive sourcing error: {str(e)}")
                
    async def _run_sourcing_cycle(self):
        """
        Run one cycle of proactive sourcing
        """
        db = next(get_db())
        agent = SmartSourcingAgent(db)
        
        # Get active buyers
        active_buyers = db.query(User).filter(
            User.is_active == True,
            User.role == 'buyer'
        ).all()
        
        for buyer in active_buyers:
            try:
                # Generate recommendations
                recommendations = await agent.generate_recommendations(buyer.id)
                
                # Send notifications if good matches found
                if recommendations.get('recommendations'):
                    await self._notify_buyer(buyer, recommendations)
                    
            except Exception as e:
                logger.error(f"Error processing buyer {buyer.id}: {str(e)}")
                
        db.close()
        
    async def _notify_buyer(self, buyer: User, recommendations: Dict[str, Any]):
        """
        Notify buyer about new supplier matches
        """
        # Send email/push notification
        top_match = recommendations['recommendations'][0]
        
        message = f"""
        Hi {buyer.name},
        
        We found a great supplier match for you!
        
        {top_match['supplier']['name']} - {top_match['match_score']*100:.0f}% match
        Location: {top_match['supplier']['location']}
        Potential savings: {top_match['estimated_savings']}
        
        Key strengths:
        {chr(10).join('• ' + s for s in top_match['strengths'])}
        
        View full recommendations in your dashboard.
        """
        
        logger.info(f"Notifying buyer {buyer.id} about {len(recommendations['recommendations'])} matches")
        
    async def stop(self):
        """
        Stop the proactive sourcing service
        """
        self.is_running = False


# Global service instance
proactive_sourcing = ProactiveSourcingService()