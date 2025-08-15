"""
Joint Intent Classification and Slot Filling using ML-based approach.
Handles both tool selection and argument extraction in a single model.
"""

import json
import logging
import re
from typing import Dict, Any, List, Tuple

from .models import Slot, IntentSlotResult
from .patterns import INTENT_PATTERNS
from .extractors import (
    extract_create_slots,
    extract_update_slots,
    extract_delete_slots,
    extract_get_slots,
    extract_description_fallback
)

logger = logging.getLogger(__name__)

class JointIntentSlotClassifier:
    """
    Joint Intent Classification and Slot Filling classifier.
    Uses rule-based patterns enhanced with ML-like confidence scoring.
    """
    
    def __init__(self):
        self.intent_patterns = INTENT_PATTERNS
    
    def classify(self, text: str) -> IntentSlotResult:
        """
        Perform joint intent classification and slot filling.
        
        Args:
            text: Input text to classify
            
        Returns:
            IntentSlotResult with intent and extracted slots
        """
        text_lower = text.lower()
        
        # Step 1: Intent Classification
        intent, intent_confidence = self._classify_intent(text_lower)
        
        # Step 2: Slot Filling
        slots = self._extract_slots(text, text_lower, intent)
        
        # Step 3: Post-processing and validation
        slots = self._post_process_slots(slots, intent, text)
        
        logger.info(f"🎯 Intent: {intent} (confidence: {intent_confidence:.2f})")
        logger.info(f"🔧 Slots: {[f'{s.name}={s.value}' for s in slots]}")
        
        return IntentSlotResult(
            intent=intent,
            intent_confidence=intent_confidence,
            slots=slots,
            raw_text=text
        )
    
    def _classify_intent(self, text: str) -> Tuple[str, float]:
        """Classify the intent (tool name) from text."""
        best_intent = "product.list"  # default
        best_confidence = 0.5
        
        for intent, patterns in self.intent_patterns.items():
            for pattern, base_confidence in patterns:
                match = re.search(pattern, text)
                if match:
                    # Boost confidence based on pattern specificity
                    confidence = base_confidence
                    if len(pattern) > 20:  # More specific patterns get higher confidence
                        confidence += 0.05
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_intent = intent
        
        return best_intent, best_confidence
    
    def _extract_slots(self, text: str, text_lower: str, intent: str) -> List[Slot]:
        """Extract slots (arguments) from text."""
        slots = []
        
        # Extract slots based on intent
        if intent == "product.create":
            slots.extend(extract_create_slots(text, text_lower))
        elif intent == "product.update":
            slots.extend(extract_update_slots(text, text_lower))
        elif intent == "product.delete":
            slots.extend(extract_delete_slots(text, text_lower))
        elif intent == "product.get":
            slots.extend(extract_get_slots(text, text_lower))
        
        return slots
    
    def _post_process_slots(self, slots: List[Slot], intent: str, text: str) -> List[Slot]:
        """Post-process slots for better accuracy."""
        # For create operations, try to extract description from remaining text
        if intent == "product.create":
            existing_slots = {slot.name for slot in slots}
            if "description" not in existing_slots:
                desc_slot = extract_description_fallback(text, slots)
                if desc_slot:
                    slots.append(desc_slot)
        
        return slots
    
    def to_dict(self, result: IntentSlotResult) -> Dict[str, Any]:
        """Convert result to dictionary format compatible with existing API."""
        tool_args = {}
        for slot in result.slots:
            tool_args[slot.name] = slot.value
        
        # Special handling for "recent" products
        if result.intent == "product.list" and any(word in result.raw_text.lower() for word in ["recent", "latest", "newest"]):
            tool_args["limit"] = 1
            tool_args["recent_only"] = True
        
        return {
            "tool_name": result.intent,
            "tool_args": tool_args,
            "confidence": result.intent_confidence,
            "method": "ml_joint_classifier",
            "slots": [
                {
                    "name": slot.name,
                    "value": slot.value,
                    "confidence": slot.confidence
                }
                for slot in result.slots
            ]
        }

# Global instance
joint_classifier = JointIntentSlotClassifier()
