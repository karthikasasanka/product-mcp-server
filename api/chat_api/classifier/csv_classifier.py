"""
Main CSV-based classifier that loads pre-trained models.
"""

import logging
from typing import Dict, Any
from .models import QueryPattern, ClassificationResult
from .training.ml_classifier import MLClassifier
from .persistence import ModelPersistence
from .argument_extractor import ArgumentExtractor

logger = logging.getLogger(__name__)

class CSVBasedClassifier:
    """CSV-based text classifier for tool selection."""
    
    def __init__(self, model_path: str = "api/csv_classifier.pkl"):
        self.model_path = model_path
        self.patterns: list[QueryPattern] = []
        self.ml_classifier: MLClassifier = None
        self.argument_extractor = ArgumentExtractor()
        self.is_loaded = False
        
    def load_model(self):
        """Load a pre-trained model from disk."""
        logger.info(f"📂 Loading pre-trained model from {self.model_path}")
        
        model_data = ModelPersistence.load_model(self.model_path)
        
        if model_data:
            self.patterns = model_data.get('patterns', [])
            self.ml_classifier = MLClassifier(self.patterns)
            
            if 'pipeline' in model_data:
                self.ml_classifier.pipeline = model_data['pipeline']
                self.ml_classifier.is_trained = True
            
            self.is_loaded = True
            logger.info(f"✅ Model loaded successfully with {len(self.patterns)} patterns")
        else:
            logger.error(f"❌ Failed to load model from {self.model_path}")
            raise Exception(f"Model file not found: {self.model_path}")
    
    def classify(self, message: str) -> Dict[str, Any]:
        """Classify user message using pre-trained model."""
        if not self.is_loaded:
            self.load_model()
        
        # Use pre-trained ML classifier
        ml_result = self.ml_classifier.classify(message)
        
        # Enhance with dynamic argument extraction
        enhanced_result = self._enhance_with_dynamic_extraction(message, ml_result)
        
        return self._result_to_dict(enhanced_result)
    
    def _enhance_with_dynamic_extraction(self, message: str, result: ClassificationResult) -> ClassificationResult:
        """Enhance classification result with dynamic argument extraction."""
        # Extract dynamic arguments from the user message
        dynamic_args = self.argument_extractor.extract_arguments(
            message, 
            result.tool_name, 
            result.tool_args
        )
        
        # Special handling for "recent" products
        if result.tool_name == "product.list" and any(word in message.lower() for word in ["recent", "latest", "newest"]):
            dynamic_args["limit"] = 1
            dynamic_args["recent_only"] = True
        
        # Update the result with dynamic arguments
        return ClassificationResult(
            tool_name=result.tool_name,
            tool_args=dynamic_args,
            confidence=result.confidence,
            method=result.method,
            query_type=result.query_type,
            entity=result.entity,
            intent=result.intent,
            description=result.description
        )
    
    def _result_to_dict(self, result: ClassificationResult) -> Dict[str, Any]:
        """Convert ClassificationResult to dictionary."""
        return {
            "tool_name": result.tool_name,
            "tool_args": result.tool_args,
            "confidence": result.confidence,
            "method": result.method,
            "query_type": result.query_type,
            "entity": result.entity,
            "intent": result.intent,
            "description": result.description
        }

# Global CSV classifier instance
csv_classifier = CSVBasedClassifier()

def classify_message_csv(message: str) -> Dict[str, Any]:
    """Fast CSV-based classification of user message to tool selection."""
    return csv_classifier.classify(message)
