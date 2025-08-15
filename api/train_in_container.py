#!/usr/bin/env python3
"""
Training script for use in Docker container.
"""

import sys
import os

# Add the app directory to the path
sys.path.append('/app')

from chat_api.classifier.training import ClassifierTrainer

def main():
    """Train the CSV classifier."""
    print("🤖 Training CSV classifier in container...")
    
    try:
        # Initialize trainer
        trainer = ClassifierTrainer()
        
        # Train the classifier
        ml_classifier = trainer.train()
        
        if ml_classifier:
            # Save the trained model
            model_path = 'api/csv_classifier.pkl'
            trainer.save_trained_model(model_path)
            
            # Print training statistics
            stats = trainer.get_training_stats()
            print(f"✅ CSV classifier trained successfully!")
            print(f"   Total patterns: {stats['total_patterns']}")
            print(f"   Model saved to: {model_path}")
            return True
        else:
            print("❌ Failed to train CSV classifier")
            return False
            
    except Exception as e:
        print(f"❌ Training failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
