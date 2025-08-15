"""
ML-based joint intent classification and slot filling for product operations.
"""

from .joint_classifier import JointIntentSlotClassifier
from .models import Slot, IntentSlotResult
from .patterns import INTENT_PATTERNS, SLOT_PATTERNS
from .processors import VALUE_PROCESSORS
from .extractors import (
    extract_create_slots,
    extract_update_slots,
    extract_delete_slots,
    extract_get_slots,
    extract_slot,
    extract_description_fallback
)

__all__ = [
    'JointIntentSlotClassifier',
    'Slot',
    'IntentSlotResult',
    'INTENT_PATTERNS',
    'SLOT_PATTERNS',
    'VALUE_PROCESSORS',
    'extract_create_slots',
    'extract_update_slots',
    'extract_delete_slots',
    'extract_get_slots',
    'extract_slot',
    'extract_description_fallback'
]
