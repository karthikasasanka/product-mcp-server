#!/usr/bin/env python3
"""
Standalone script to train the CSV classifier.
"""

import sys
import os
import logging

# Add the parent directory to the path so we can import the classifier
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from chat_api.classifier.training import ClassifierTrainer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main training function."""
    logger.info("🚀 Starting CSV Classifier Training")
    logger.info("=" * 50)
    
    try:
        # Initialize trainer
        trainer = ClassifierTrainer()
        
        # Train the classifier
        ml_classifier = trainer.train()
        
        if ml_classifier:
            # Save the trained model
            model_path = "csv_classifier.pkl"
            trainer.save_trained_model(model_path)
            
            # Print training statistics
            stats = trainer.get_training_stats()
            logger.info("\n📊 Training Statistics:")
            logger.info(f"   Total patterns: {stats['total_patterns']}")
            logger.info(f"   Pattern types: {stats['pattern_types']}")
            logger.info(f"   Entities: {stats['entities']}")
            logger.info(f"   Intents: {stats['intents']}")
            logger.info(f"   Model trained: {stats['is_trained']}")
            
            logger.info(f"\n✅ Training completed successfully!")
            logger.info(f"   Model saved to: {model_path}")
            logger.info(f"   Ready for use in production!")
            
        else:
            logger.error("❌ Training failed - no classifier returned")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Training failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
