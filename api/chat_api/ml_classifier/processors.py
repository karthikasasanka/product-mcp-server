"""
Value processors for ML-based joint intent classification and slot filling.
"""

import re
from typing import Any, Optional

def process_name(value: str) -> Optional[str]:
    """Process name value."""
    # Clean up and capitalize
    name = re.sub(r'\s+', ' ', value).strip()
    return name.title() if name else None

def process_price(value: str) -> Optional[float]:
    """Process price value."""
    try:
        return float(value)
    except ValueError:
        return None

def process_id(value: str) -> Optional[int]:
    """Process ID value."""
    try:
        return int(value)
    except ValueError:
        return None

def process_description(value: str) -> Optional[str]:
    """Process description value."""
    desc = re.sub(r'\s+', ' ', value).strip()
    return desc if desc else None

# Slot value processors mapping
VALUE_PROCESSORS = {
    "name": process_name,
    "price": process_price,
    "id": process_id,
    "description": process_description,
}
