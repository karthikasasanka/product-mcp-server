"""
Data models for ML-based joint intent classification and slot filling.
"""

from dataclasses import dataclass
from typing import List, Any

@dataclass
class Slot:
    """Represents a slot (argument) with its value and confidence."""
    name: str
    value: Any
    confidence: float
    start_pos: int
    end_pos: int

@dataclass
class IntentSlotResult:
    """Result of joint intent classification and slot filling."""
    intent: str  # tool_name
    intent_confidence: float
    slots: List[Slot]
    raw_text: str
