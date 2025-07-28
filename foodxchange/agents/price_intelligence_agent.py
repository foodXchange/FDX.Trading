"""
Price Intelligence Agent - Real-time market price monitoring and alerts
Helps buyers save money and sellers price competitively
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.quote import Quote
from app.models.rfq import RFQ
from app.models.product import Product
from app.models.user import User
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class PriceMovement(Enum):
    STABLE = "stable"
    RISING = "rising"
    FALLING = "falling"
    VOLATILE = "volatile"


@dataclass
class PriceInsight:
    """Market price intelligence for a product"""
    product_name: str
    current_price: float
    average_price: float
    min_price: float
    max_price: float
    price_trend: PriceMovement
    change_percentage: float
    forecast_7_days: float
    best_supplier_id: Optional[int]
    savings_opportunity: float
    confidence_score: float


@dataclass
class PriceAlert:
    """Alert for significant price changes"""
    alert_type: str  # price_drop, price_rise, new_low, bulk_discount
    product_name: str
    price_change: float
    percentage_change: float
    supplier_id: Optional[int]
    action_required: str
    expires_at: datetime
    priority: str  # low, medium, high, urgent


class PriceIntelligenceAgent:
    """
    Monitors market prices and provides actionable insights
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.price_change_threshold = 0.05  # 5% triggers alert
        self.lookback_days = 30
        self.forecast_days = 7
        
    async def analyze_product_prices(self, product_name: str) -> PriceInsight:
        """
        Analyze price trends for a specific product
        """
        # Get recent quotes for this product
        recent_quotes = self.db.query(Quote).join(RFQ).filter(
            RFQ.product_name.ilike(f"%{product_name}%"),
            Quote.created_at >= datetime.utcnow() - timedelta(days=self.lookback_days),
            Quote.status == 'active'
        ).all()
        
        if not recent_quotes:
            return None
            
        # Calculate price statistics
        prices = [q.unit_price for q in recent_quotes]
        current_price = prices[-1] if prices else 0
        average_price = statistics.mean(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        # Determine price trend
        price_trend = self._calculate_price_trend(prices)
        
        # Calculate change percentage
        if len(prices) > 1:
            change_percentage = ((current_price - prices[0]) / prices[0]) * 100
        else:
            change_percentage = 0
            
        # Simple forecast (in production, use Azure ML)
        forecast_7_days = self._forecast_price(prices)
        
        # Find best current supplier
        best_quote = min(recent_quotes, key=lambda q: q.unit_price)
        best_supplier_id = best_quote.supplier_id
        
        # Calculate savings opportunity
        user_avg_price = self._get_user_average_price(product_name)
        savings_opportunity = max(0, (user_avg_price - min_price) / user_avg_price * 100) if user_avg_price else 0
        
        return PriceInsight(
            product_name=product_name,
            current_price=current_price,
            average_price=average_price,
            min_price=min_price,
            max_price=max_price,
            price_trend=price_trend,
            change_percentage=change_percentage,
            forecast_7_days=forecast_7_days,
            best_supplier_id=best_supplier_id,
            savings_opportunity=savings_opportunity,
            confidence_score=0.85 if len(recent_quotes) > 10 else 0.6
        )
        
    def _calculate_price_trend(self, prices: List[float]) -> PriceMovement:
        """
        Determine if prices are rising, falling, stable, or volatile
        """
        if len(prices) < 3:
            return PriceMovement.STABLE
            
        # Calculate moving averages
        recent_avg = statistics.mean(prices[-5:])
        older_avg = statistics.mean(prices[-10:-5]) if len(prices) > 10 else prices[0]
        
        # Calculate volatility
        std_dev = statistics.stdev(prices)
        volatility = std_dev / statistics.mean(prices)
        
        if volatility > 0.2:
            return PriceMovement.VOLATILE
        elif recent_avg > older_avg * 1.05:
            return PriceMovement.RISING
        elif recent_avg < older_avg * 0.95:
            return PriceMovement.FALLING
        else:
            return PriceMovement.STABLE
            
    def _forecast_price(self, prices: List[float]) -> float:
        """
        Simple price forecast for next 7 days
        """
        if len(prices) < 3:
            return prices[-1] if prices else 0
            
        # Simple linear regression forecast
        # In production, use Azure ML for sophisticated forecasting
        recent_trend = (prices[-1] - prices[-7]) / 7 if len(prices) >= 7 else 0
        forecast = prices[-1] + (recent_trend * 7)
        
        return max(0, forecast)  # Ensure non-negative
        
    def _get_user_average_price(self, product_name: str) -> float:
        """
        Get the average price the user has been paying
        """
        # This would look at the user's order history
        # For now, return a placeholder
        return 0
        
    async def generate_price_alerts(self, user_id: int) -> List[PriceAlert]:
        """
        Generate personalized price alerts for a user
        """
        alerts = []
        
        # Get user's frequently purchased products
        user_products = self._get_user_frequent_products(user_id)
        
        for product in user_products:
            insight = await self.analyze_product_prices(product)
            
            if not insight:
                continue
                
            # Check for significant price drops
            if insight.change_percentage < -self.price_change_threshold * 100:
                alerts.append(PriceAlert(
                    alert_type='price_drop',
                    product_name=product,
                    price_change=insight.current_price - insight.average_price,
                    percentage_change=insight.change_percentage,
                    supplier_id=insight.best_supplier_id,
                    action_required=f"Lock in {product} at ${insight.current_price:.2f}/unit",
                    expires_at=datetime.utcnow() + timedelta(days=3),
                    priority='high' if insight.change_percentage < -10 else 'medium'
                ))
                
            # Check for new historical lows
            if insight.current_price <= insight.min_price * 1.02:
                alerts.append(PriceAlert(
                    alert_type='new_low',
                    product_name=product,
                    price_change=insight.current_price - insight.average_price,
                    percentage_change=insight.change_percentage,
                    supplier_id=insight.best_supplier_id,
                    action_required=f"Historical low price for {product}!",
                    expires_at=datetime.utcnow() + timedelta(days=1),
                    priority='urgent'
                ))
                
            # Check for rising prices (buy before increase)
            if insight.price_trend == PriceMovement.RISING and insight.change_percentage > 5:
                alerts.append(PriceAlert(
                    alert_type='price_rise',
                    product_name=product,
                    price_change=insight.current_price - insight.average_price,
                    percentage_change=insight.change_percentage,
                    supplier_id=None,
                    action_required=f"Stock up on {product} - prices rising {insight.change_percentage:.1f}%",
                    expires_at=datetime.utcnow() + timedelta(days=7),
                    priority='medium'
                ))
                
        # Check for bulk discount opportunities
        bulk_alerts = await self._check_bulk_discounts(user_id)
        alerts.extend(bulk_alerts)
        
        return alerts
        
    def _get_user_frequent_products(self, user_id: int) -> List[str]:
        """
        Get products frequently purchased by the user
        """
        # Query user's RFQ history
        frequent_products = self.db.query(RFQ.product_name, func.count(RFQ.id).label('count')).filter(
            RFQ.buyer_id == user_id,
            RFQ.created_at >= datetime.utcnow() - timedelta(days=90)
        ).group_by(RFQ.product_name).order_by(func.count(RFQ.id).desc()).limit(10).all()
        
        return [p[0] for p in frequent_products]
        
    async def _check_bulk_discounts(self, user_id: int) -> List[PriceAlert]:
        """
        Check for bulk discount opportunities
        """
        alerts = []
        
        # Get user's typical order quantities
        user_orders = self.db.query(RFQ).filter(
            RFQ.buyer_id == user_id,
            RFQ.created_at >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        # Group by product and sum quantities
        product_quantities = {}
        for order in user_orders:
            if order.product_name not in product_quantities:
                product_quantities[order.product_name] = 0
            product_quantities[order.product_name] += order.quantity
            
        # Check if combining orders would unlock bulk discounts
        for product, total_quantity in product_quantities.items():
            if total_quantity > 100:  # Threshold for bulk
                alerts.append(PriceAlert(
                    alert_type='bulk_discount',
                    product_name=product,
                    price_change=-total_quantity * 0.1,  # Estimated 10% discount
                    percentage_change=-10,
                    supplier_id=None,
                    action_required=f"Combine {product} orders for 10% bulk discount",
                    expires_at=datetime.utcnow() + timedelta(days=14),
                    priority='medium'
                ))
                
        return alerts
        
    async def market_comparison_report(self, product_categories: List[str]) -> Dict[str, Any]:
        """
        Generate comprehensive market comparison report
        """
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'categories': {},
            'summary': {
                'total_savings_opportunity': 0,
                'trending_up': [],
                'trending_down': [],
                'best_deals': []
            }
        }
        
        for category in product_categories:
            # Get all products in category
            products = self._get_products_in_category(category)
            
            category_data = {
                'products': {},
                'average_change': 0,
                'volatility': 'low'
            }
            
            changes = []
            
            for product in products:
                insight = await self.analyze_product_prices(product)
                if insight:
                    category_data['products'][product] = {
                        'current_price': insight.current_price,
                        'change': insight.change_percentage,
                        'trend': insight.price_trend.value,
                        'best_price': insight.min_price,
                        'savings': insight.savings_opportunity
                    }
                    
                    changes.append(insight.change_percentage)
                    report['summary']['total_savings_opportunity'] += insight.savings_opportunity
                    
                    if insight.change_percentage > 5:
                        report['summary']['trending_up'].append(product)
                    elif insight.change_percentage < -5:
                        report['summary']['trending_down'].append(product)
                        
                    if insight.savings_opportunity > 15:
                        report['summary']['best_deals'].append({
                            'product': product,
                            'savings': f"{insight.savings_opportunity:.1f}%",
                            'supplier_id': insight.best_supplier_id
                        })
                        
            if changes:
                category_data['average_change'] = statistics.mean(changes)
                
            report['categories'][category] = category_data
            
        return report
        
    def _get_products_in_category(self, category: str) -> List[str]:
        """
        Get all products in a category
        """
        # In production, query product catalog
        # For now, return mock data
        category_products = {
            'produce': ['Tomatoes', 'Lettuce', 'Onions', 'Potatoes'],
            'dairy': ['Milk', 'Cheese', 'Yogurt', 'Butter'],
            'meat': ['Chicken', 'Beef', 'Pork', 'Lamb'],
            'seafood': ['Salmon', 'Shrimp', 'Tuna', 'Cod']
        }
        
        return category_products.get(category, [])


class PriceMonitoringService:
    """
    Background service for continuous price monitoring
    """
    
    def __init__(self):
        self.check_interval = 1800  # 30 minutes
        self.is_running = False
        
    async def start(self):
        """
        Start price monitoring service
        """
        self.is_running = True
        logger.info("Starting price monitoring service")
        
        while self.is_running:
            try:
                await self._monitor_prices()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Price monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute on error
                
    async def _monitor_prices(self):
        """
        Monitor prices and send alerts
        """
        db = next(get_db())
        agent = PriceIntelligenceAgent(db)
        
        # Get all active buyers
        buyers = db.query(User).filter(
            User.is_active == True,
            User.role == 'buyer'
        ).all()
        
        alerts_sent = 0
        
        for buyer in buyers:
            try:
                # Generate price alerts
                alerts = await agent.generate_price_alerts(buyer.id)
                
                # Send high priority alerts immediately
                urgent_alerts = [a for a in alerts if a.priority in ['high', 'urgent']]
                
                if urgent_alerts:
                    await self._send_price_alerts(buyer, urgent_alerts)
                    alerts_sent += len(urgent_alerts)
                    
            except Exception as e:
                logger.error(f"Error monitoring prices for buyer {buyer.id}: {str(e)}")
                
        logger.info(f"Price monitoring complete. Sent {alerts_sent} alerts")
        db.close()
        
    async def _send_price_alerts(self, buyer: User, alerts: List[PriceAlert]):
        """
        Send price alerts to buyer
        """
        # Format alert message
        message = f"Hi {buyer.name},\n\nPrice alerts for you:\n\n"
        
        for alert in alerts:
            icon = "📉" if alert.alert_type == 'price_drop' else "📈"
            message += f"{icon} {alert.product_name}: {alert.action_required}\n"
            message += f"   Change: {alert.percentage_change:+.1f}%\n\n"
            
        message += "View details in your dashboard."
        
        # In production, send via email/SMS/push notification
        logger.info(f"Sending {len(alerts)} price alerts to buyer {buyer.id}")
        
    async def stop(self):
        """
        Stop price monitoring service
        """
        self.is_running = False
        logger.info("Stopping price monitoring service")


# Global service instance
price_monitoring = PriceMonitoringService()