"""
Model persistence for the CSV classifier.
"""

import pickle
import logging
from typing import Dict, Any
from .models import QueryPattern

logger = logging.getLogger(__name__)

class ModelPersistence:
    """Handles saving and loading of trained models."""
    
    @staticmethod
    def save_model(filepath: str, pipeline: Any, patterns: list[QueryPattern]):
        """Save the trained model to disk."""
        try:
            model_data = {
                'pipeline': pipeline,
                'patterns': patterns
            }
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            logger.info(f"💾 Model saved to {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to save model: {e}")
    
    @staticmethod
    def load_model(filepath: str) -> Dict[str, Any]:
        """Load a trained model from disk."""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            logger.info(f"📂 Model loaded from {filepath}")
            return model_data
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return {}
