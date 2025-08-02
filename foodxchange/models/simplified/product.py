"""Simplified Product model - basic product catalog"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, Boolean, func
from sqlalchemy.orm import relationship
from foodxchange.database import Base

class Product(Base):
    """Simple product catalog"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Supplier who offers this product
    supplier_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Product information
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), index=True)
    price = Column(DECIMAL(10, 2))
    description = Column(Text)
    image_url = Column(String(500))
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    supplier = relationship("User", back_populates="products")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', category='{self.category}')>"