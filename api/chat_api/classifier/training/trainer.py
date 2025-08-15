"""
Training orchestrator for the CSV classifier.
"""

import logging
from typing import List
from ..models import QueryPattern
from .csv_loader import CSVPatternLoader
from .ml_classifier import MLClassifier
from ..persistence import ModelPersistence

logger = logging.getLogger(__name__)

class ClassifierTrainer:
    """Handles the complete training process for the CSV classifier."""
    
    def __init__(self, data_dir: str = "api/chat_api/classifier/training/patterns"):
        self.data_dir = data_dir
        self.patterns: List[QueryPattern] = []
        self.ml_classifier: MLClassifier = None
        
    def train(self) -> MLClassifier:
        """Complete training process."""
        logger.info("🤖 Starting classifier training process...")
        
        # Step 1: Load patterns from CSV
        logger.info("📂 Step 1: Loading patterns from CSV files...")
        loader = CSVPatternLoader(self.data_dir)
        self.patterns = loader.load_patterns_from_csv()
        
        if not self.patterns:
            logger.warning("⚠️ No patterns loaded from CSV files")
            return None
        
        # Step 2: Initialize and train ML classifier
        logger.info("🧠 Step 2: Training ML classifier...")
        self.ml_classifier = MLClassifier(self.patterns)
        self.ml_classifier.train()
        
        logger.info(f"✅ Training completed successfully!")
        logger.info(f"   - Patterns loaded: {len(self.patterns)}")
        logger.info(f"   - ML classifier trained: {self.ml_classifier.is_trained}")
        
        return self.ml_classifier
    
    def save_trained_model(self, filepath: str):
        """Save the trained model to disk."""
        if self.ml_classifier and self.ml_classifier.is_trained:
            ModelPersistence.save_model(
                filepath, 
                self.ml_classifier.pipeline, 
                self.patterns
            )
            logger.info(f"💾 Trained model saved to {filepath}")
        else:
            logger.warning("⚠️ No trained model to save")
    
    def get_training_stats(self) -> dict:
        """Get training statistics."""
        if not self.patterns:
            return {"error": "No patterns loaded"}
        
        # Count patterns by type
        type_counts = {}
        entity_counts = {}
        intent_counts = {}
        
        for pattern in self.patterns:
            type_counts[pattern.query_type] = type_counts.get(pattern.query_type, 0) + 1
            entity_counts[pattern.entity] = entity_counts.get(pattern.entity, 0) + 1
            intent_counts[pattern.intent] = intent_counts.get(pattern.intent, 0) + 1
        
        return {
            "total_patterns": len(self.patterns),
            "pattern_types": type_counts,
            "entities": entity_counts,
            "intents": intent_counts,
            "is_trained": self.ml_classifier.is_trained if self.ml_classifier else False
        }
