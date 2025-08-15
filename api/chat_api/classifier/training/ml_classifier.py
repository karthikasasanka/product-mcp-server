"""
ML fallback classifier for the CSV classifier.
"""

import logging
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from ..models import QueryPattern, ClassificationResult

logger = logging.getLogger(__name__)

class MLClassifier:
    """ML-based classifier for text-to-tool classification."""
    
    def __init__(self, patterns: List[QueryPattern]):
        self.patterns = patterns
        self.pipeline = None
        self.is_trained = False
    
    def train(self):
        """Train the ML classifier on patterns."""
        if not self.patterns:
            logger.warning("⚠️ No patterns available for ML training")
            return
        
        # Prepare training data
        texts = [pattern.query_pattern for pattern in self.patterns]
        tool_names = [pattern.tool_name for pattern in self.patterns]
        
        # Create and train pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2),
                max_features=1000,
                stop_words='english'
            )),
            ('classifier', MultinomialNB())
        ])
        
        # Train the model
        self.pipeline.fit(texts, tool_names)
        
        self.is_trained = True
        logger.info(f"✅ ML classifier trained on {len(self.patterns)} patterns")
    
    def classify(self, message: str) -> ClassificationResult:
        """Classify message using ML classifier."""
        if not self.is_trained:
            self.train()
        
        if not self.pipeline:
            return self._default_result(message)
        
        # Predict tool name
        predicted_tool = self.pipeline.predict([message])[0]
        
        # Get prediction probability
        proba = self.pipeline.predict_proba([message])[0]
        confidence = max(proba)
        
        # Find the best matching pattern for the predicted tool
        best_pattern = None
        best_similarity = 0
        
        for pattern in self.patterns:
            if pattern.tool_name == predicted_tool:
                # Calculate similarity between message and pattern
                similarity = self._calculate_similarity(message, pattern.query_pattern)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_pattern = pattern
        
        if best_pattern:
            # Use the tool_args from the best matching pattern
            import ast
            try:
                tool_args = ast.literal_eval(best_pattern.tool_args)
            except:
                tool_args = {}
            
            return ClassificationResult(
                tool_name=best_pattern.tool_name,
                tool_args=tool_args,
                confidence=confidence * best_pattern.confidence,
                method="ml_classifier",
                query_type=best_pattern.query_type,
                entity=best_pattern.entity,
                intent=best_pattern.intent,
                description=best_pattern.description
            )
        
        return self._default_result(message)
    
    def _calculate_similarity(self, message: str, pattern: str) -> float:
        """Calculate similarity between message and pattern."""
        # Simple word overlap similarity
        message_words = set(message.lower().split())
        pattern_words = set(pattern.lower().split())
        
        if not pattern_words:
            return 0.0
        
        intersection = message_words.intersection(pattern_words)
        union = message_words.union(pattern_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _default_result(self, message: str) -> ClassificationResult:
        """Default result when classification fails."""
        return ClassificationResult(
            tool_name="product.list",
            tool_args={},
            confidence=0.5,
            method="default",
            query_type="simple",
            entity="products",
            intent="list",
            description="Default fallback"
        )
