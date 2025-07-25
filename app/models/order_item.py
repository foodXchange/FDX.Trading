"""
Order Item model for line items within orders
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class OrderItem(Base):
    """
    Individual line items within an order
    """
    __tablename__ = "order_items"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Order association
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Product information
    product_id = Column(Integer, ForeignKey("products.id"))
    product_name = Column(String(200), nullable=False)  # Stored in case product changes
    product_sku = Column(String(100))
    product_description = Column(Text)
    
    # Quantity and units
    quantity = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)  # kg, lb, case, etc.
    
    # Pricing (stored in cents)
    unit_price = Column(Integer, nullable=False)  # Price per unit
    total_amount = Column(Integer, nullable=False)  # quantity * unit_price
    currency = Column(String(3), default="USD")
    
    # Original quote reference
    quote_item_id = Column(Integer)  # Reference to quote line item if applicable
    
    # Specifications
    specifications = Column(JSON)  # Size, grade, packaging, etc.
    
    # Delivery
    requested_delivery_date = Column(DateTime)
    confirmed_delivery_date = Column(DateTime)
    
    # Status tracking
    quantity_shipped = Column(Float, default=0)
    quantity_received = Column(Float, default=0)
    quantity_invoiced = Column(Float, default=0)
    
    # Notes
    notes = Column(Text)
    supplier_notes = Column(Text)
    
    # Quality
    quality_requirements = Column(Text)
    certifications_required = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<OrderItem {self.product_name} - {self.quantity} {self.unit}>"
    
    @property
    def display_unit_price(self):
        """Get formatted unit price"""
        return f"{self.currency} {self.unit_price / 100:.2f}"
    
    @property
    def display_total(self):
        """Get formatted total amount"""
        return f"{self.currency} {self.total_amount / 100:.2f}"
    
    @property
    def is_fully_delivered(self):
        """Check if item is fully delivered"""
        return self.quantity_received >= self.quantity
    
    @property
    def pending_quantity(self):
        """Get quantity still to be delivered"""
        return max(0, self.quantity - self.quantity_received)
    
    def calculate_total(self):
        """Calculate total amount from quantity and unit price"""
        self.total_amount = int(self.quantity * self.unit_price)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "product_name": self.product_name,
            "product_sku": self.product_sku,
            "quantity": self.quantity,
            "unit": self.unit,
            "unit_price": self.display_unit_price,
            "total_amount": self.display_total,
            "quantity_received": self.quantity_received,
            "pending_quantity": self.pending_quantity,
            "specifications": self.specifications or {}
        }