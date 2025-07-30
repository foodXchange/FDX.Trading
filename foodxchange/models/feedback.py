"""
Feedback model for machine learning improvement
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, Boolean
from sqlalchemy.sql import func
from ..database import Base

class ProductFeedback(Base):
    """Store user feedback on product analysis results"""
    __tablename__ = "product_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Original analysis data
    image_url = Column(String(500))
    original_vision_result = Column(JSON)  # Raw Azure Vision API response
    original_analysis = Column(JSON)  # Our processed analysis
    original_brief = Column(JSON)  # Generated brief
    
    # User feedback
    feedback_type = Column(String(50))  # 'incorrect', 'partial', 'missing_info'
    feedback_text = Column(Text)  # User's explanation
    
    # Corrections provided by user
    correct_product_name = Column(String(255))
    correct_brand = Column(String(255))
    correct_company = Column(String(255))
    correct_category = Column(String(255))
    correct_packaging = Column(String(255))
    correct_weight = Column(String(100))
    additional_info = Column(JSON)  # Any other corrections
    
    # ML improvement tracking
    confidence_before = Column(Float)
    confidence_after = Column(Float)
    improvement_applied = Column(Boolean, default=False)
    
    # Metadata
    user_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Analysis session ID to link feedback to specific analysis
    analysis_session_id = Column(String(100))

class MLTrainingData(Base):
    """Aggregated training data from feedback"""
    __tablename__ = "ml_training_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Pattern recognition
    vision_tags = Column(JSON)  # Tags that appeared in vision API
    vision_description = Column(String(500))
    detected_brands = Column(JSON)
    detected_objects = Column(JSON)
    
    # Correct labels from user feedback
    actual_product_name = Column(String(255))
    actual_brand = Column(String(255))
    actual_company = Column(String(255))
    actual_category = Column(String(255))
    actual_packaging = Column(String(255))
    
    # Training metrics
    times_corrected = Column(Integer, default=1)
    last_correction = Column(DateTime(timezone=True))
    confidence_score = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())