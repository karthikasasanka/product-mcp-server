"""
Slot extraction logic for ML-based joint intent classification and slot filling.
"""

import re
import logging
from typing import List, Optional
from .models import Slot
from .patterns import SLOT_PATTERNS
from .processors import VALUE_PROCESSORS

logger = logging.getLogger(__name__)

def extract_create_slots(text: str, text_lower: str) -> List[Slot]:
    """Extract slots for product creation."""
    slots = []
    
    # Extract name
    name_slot = extract_slot("name", text, text_lower)
    if name_slot:
        slots.append(name_slot)
    
    # Extract price
    price_slot = extract_slot("price", text, text_lower)
    if price_slot:
        slots.append(price_slot)
    
    # Extract description
    desc_slot = extract_slot("description", text, text_lower)
    if desc_slot:
        slots.append(desc_slot)
    
    return slots

def extract_update_slots(text: str, text_lower: str) -> List[Slot]:
    """Extract slots for product updates."""
    slots = []
    
    # Extract ID (required for updates)
    id_slot = extract_slot("id", text, text_lower)
    if id_slot:
        slots.append(id_slot)
    
    # Extract other fields
    name_slot = extract_slot("name", text, text_lower)
    if name_slot:
        slots.append(name_slot)
    
    price_slot = extract_slot("price", text, text_lower)
    if price_slot:
        slots.append(price_slot)
    
    desc_slot = extract_slot("description", text, text_lower)
    if desc_slot:
        slots.append(desc_slot)
    
    return slots

def extract_delete_slots(text: str, text_lower: str) -> List[Slot]:
    """Extract slots for product deletion."""
    slots = []
    
    id_slot = extract_slot("id", text, text_lower)
    if id_slot:
        slots.append(id_slot)
    
    return slots

def extract_get_slots(text: str, text_lower: str) -> List[Slot]:
    """Extract slots for product retrieval."""
    slots = []
    
    id_slot = extract_slot("id", text, text_lower)
    if id_slot:
        slots.append(id_slot)
    
    return slots

def extract_slot(slot_name: str, text: str, text_lower: str) -> Optional[Slot]:
    """Extract a specific slot from text."""
    if slot_name not in SLOT_PATTERNS:
        return None
    
    patterns = SLOT_PATTERNS[slot_name]
    
    for pattern, base_confidence in patterns:
        match = re.search(pattern, text_lower)
        if match:
            raw_value = match.group(1).strip()
            
            # Process the value
            processor = VALUE_PROCESSORS.get(slot_name)
            if processor:
                processed_value = processor(raw_value)
                if processed_value is not None:
                    return Slot(
                        name=slot_name,
                        value=processed_value,
                        confidence=base_confidence,
                        start_pos=match.start(1),
                        end_pos=match.end(1)
                    )
    
    return None

def extract_description_fallback(text: str, existing_slots: List[Slot]) -> Optional[Slot]:
    """Fallback method to extract description from remaining text."""
    text_lower = text.lower()
    
    # Remove extracted slots from text
    temp_text = text_lower
    for slot in existing_slots:
        if slot.name == "name":
            # Remove name patterns
            temp_text = re.sub(rf'(?:add|create|new product called?|product called?|named?)\s+{re.escape(slot.value.lower())}', '', temp_text)
        elif slot.name == "price":
            # Remove price patterns
            temp_text = re.sub(rf'price\s*\$?{slot.value}|${slot.value}|{slot.value}\s*dollars?', '', temp_text)
    
    # Clean up remaining text
    temp_text = re.sub(r'^\s*[,]\s*', '', temp_text)
    temp_text = re.sub(r'\s+', ' ', temp_text).strip()
    
    if temp_text and len(temp_text) > 2:
        return Slot(
            name="description",
            value=temp_text,
            confidence=0.7,  # Lower confidence for fallback
            start_pos=0,
            end_pos=len(temp_text)
        )
    
    return None
