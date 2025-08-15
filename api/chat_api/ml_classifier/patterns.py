"""
Pattern definitions for ML-based joint intent classification and slot filling.
"""

# Intent patterns with confidence scores
INTENT_PATTERNS = {
    "product.create": [
        (r"\b(?:add|create|new product|insert)\b", 0.9),
        (r"\b(?:add|create)\s+(?:a\s+)?(?:new\s+)?product\b", 0.95),
    ],
    "product.update": [
        (r"\b(?:update|modify|change|edit)\b", 0.9),
        (r"\b(?:update|modify|change|edit)\s+(?:product\s+)?(?:id\s+)?\d+\b", 0.95),
    ],
    "product.delete": [
        (r"\b(?:delete|remove|drop)\b", 0.9),
        (r"\b(?:delete|remove|drop)\s+(?:product\s+)?(?:id\s+)?\d+\b", 0.95),
    ],
    "product.get": [
        (r"\b(?:get|find|retrieve|show|display|view)\b", 0.8),
        (r"\b(?:get|find|retrieve|show|display|view)\s+(?:product\s+)?(?:id\s+)?\d+\b", 0.9),
    ],
    "product.list": [
        (r"\b(?:list|show|display|view|get)\s+(?:all\s+)?products?\b", 0.95),
        (r"\b(?:what\s+)?products?\s+(?:do\s+you\s+)?have\b", 0.9),
        (r"\b(?:catalog|inventory)\b", 0.85),
        (r"\b(?:get|show)\s+recent\s+(?:created\s+)?products?\b", 0.95),
        (r"\b(?:show|get)\s+(?:latest|newest)\s+products?\b", 0.95),
        (r"\b(?:recent|latest|newest)\s+products?\b", 0.9),
    ]
}

# Slot extraction patterns
SLOT_PATTERNS = {
    "name": [
        (r"(?:add|create|new product called?|product called?|named?)\s+([^,]+?)(?:\s*,|\s+with|\s+price|$)", 0.9),
        (r"(?:add|create)\s+([^,]+?)(?:\s*,|\s+with|\s+price|$)", 0.85),
    ],
    "price": [
        (r"price\s*\$?(\d+(?:\.\d{2})?)", 0.95),
        (r"\$(\d+(?:\.\d{2})?)", 0.9),
        (r"(\d+(?:\.\d{2})?)\s*dollars?", 0.85),
    ],
    "id": [
        (r"(?:product\s+)?id\s+(\d+)", 0.95),
        (r"(?:update|modify|change|edit|delete|remove|drop|get|find|retrieve)\s+(?:product\s+)?(\d+)", 0.9),
    ],
    "description": [
        (r"with\s+([^,]+?)(?:\s*,|\s+price|$)", 0.9),
        (r"description[:\s]+([^,]+?)(?:\s*,|\s+price|$)", 0.95),
        (r"features?[:\s]+([^,]+?)(?:\s*,|\s+price|$)", 0.9),
    ]
}
