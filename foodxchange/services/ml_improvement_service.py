"""
Machine Learning Improvement Service
Uses feedback data to improve product analysis accuracy
"""

import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

logger = logging.getLogger(__name__)

class MLImprovementService:
    """Service for improving analysis based on user feedback"""
    
    def __init__(self):
        self.min_corrections_threshold = 3  # Minimum corrections before applying learning
    
    def check_for_corrections(self, vision_tags: List[str], objects: List[str], 
                            brands: List[str], db: Session) -> Optional[Dict[str, Any]]:
        """
        Check if we have learned corrections for this type of product
        
        Args:
            vision_tags: Tags detected by vision API
            objects: Objects detected by vision API
            brands: Brands detected by vision API
            db: Database session
            
        Returns:
            Corrections if found, None otherwise
        """
        try:
            from ..models.feedback import MLTrainingData
            
            # Look for exact tag matches first
            exact_match = db.query(MLTrainingData).filter(
                MLTrainingData.vision_tags == vision_tags,
                MLTrainingData.times_corrected >= self.min_corrections_threshold
            ).order_by(desc(MLTrainingData.times_corrected)).first()
            
            if exact_match:
                return {
                    "product_name": exact_match.actual_product_name,
                    "brand": exact_match.actual_brand,
                    "company": exact_match.actual_company,
                    "category": exact_match.actual_category,
                    "packaging": exact_match.actual_packaging,
                    "confidence_boost": min(0.1 * exact_match.times_corrected, 0.3)
                }
            
            # Look for partial matches
            if vision_tags:
                # Find training data with similar tags
                all_training = db.query(MLTrainingData).filter(
                    MLTrainingData.times_corrected >= self.min_corrections_threshold
                ).all()
                
                best_match = None
                best_score = 0
                
                for training in all_training:
                    if training.vision_tags:
                        # Calculate similarity score
                        common_tags = set(vision_tags) & set(training.vision_tags)
                        score = len(common_tags) / max(len(vision_tags), len(training.vision_tags))
                        
                        if score > best_score and score > 0.5:  # At least 50% match
                            best_score = score
                            best_match = training
                
                if best_match:
                    return {
                        "product_name": best_match.actual_product_name,
                        "brand": best_match.actual_brand,
                        "company": best_match.actual_company,
                        "category": best_match.actual_category,
                        "packaging": best_match.actual_packaging,
                        "confidence_boost": min(0.05 * best_match.times_corrected * best_score, 0.2)
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking for corrections: {e}")
            return None
    
    def apply_learning_to_analysis(self, analysis_result: Dict[str, Any], 
                                 corrections: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply learned corrections to analysis result
        
        Args:
            analysis_result: Original analysis result
            corrections: Corrections from ML training data
            
        Returns:
            Updated analysis result
        """
        if corrections:
            # Update with learned values
            if corrections.get("product_name"):
                analysis_result["product_name"] = corrections["product_name"]
            
            if corrections.get("category"):
                analysis_result["category"] = corrections["category"]
            
            # Boost confidence score
            if corrections.get("confidence_boost"):
                current_confidence = analysis_result.get("confidence_score", 0.9)
                analysis_result["confidence_score"] = min(
                    current_confidence + corrections["confidence_boost"], 
                    0.99
                )
            
            # Mark as ML-enhanced
            analysis_result["ml_enhanced"] = True
            
        return analysis_result
    
    def apply_learning_to_brief(self, brief_result: Dict[str, Any], 
                              corrections: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply learned corrections to product brief
        
        Args:
            brief_result: Original brief result
            corrections: Corrections from ML training data
            
        Returns:
            Updated brief result
        """
        if corrections:
            # Update with learned values
            if corrections.get("product_name"):
                brief_result["product_name"] = corrections["product_name"]
            
            if corrections.get("brand"):
                brief_result["brand_name"] = corrections["brand"]
            
            if corrections.get("company"):
                brief_result["producing_company"] = corrections["company"]
            
            if corrections.get("category"):
                brief_result["category"] = corrections["category"]
            
            if corrections.get("packaging"):
                brief_result["packaging_type"] = corrections["packaging"]
            
            # Mark as ML-enhanced
            brief_result["ml_enhanced"] = True
            
        return brief_result
    
    def get_feedback_stats(self, db: Session) -> Dict[str, Any]:
        """Get statistics about feedback and improvements"""
        try:
            from ..models.feedback import ProductFeedback, MLTrainingData
            
            total_feedback = db.query(func.count(ProductFeedback.id)).scalar()
            total_training_patterns = db.query(func.count(MLTrainingData.id)).scalar()
            
            # Get most corrected products
            most_corrected = db.query(
                MLTrainingData.actual_product_name,
                MLTrainingData.times_corrected
            ).order_by(desc(MLTrainingData.times_corrected)).limit(5).all()
            
            return {
                "total_feedback": total_feedback,
                "total_training_patterns": total_training_patterns,
                "most_corrected_products": [
                    {"name": name, "corrections": count} 
                    for name, count in most_corrected
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting feedback stats: {e}")
            return {
                "total_feedback": 0,
                "total_training_patterns": 0,
                "most_corrected_products": []
            }

# Create global instance
ml_improvement_service = MLImprovementService()