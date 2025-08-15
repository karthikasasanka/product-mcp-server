"""
Data models for the CSV-based classifier.
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class QueryPattern:
    """Query pattern loaded from CSV."""
    query_pattern: str
    tool_name: str
    tool_args: str
    confidence: float
    query_type: str
    entity: str
    intent: str
    description: str

@dataclass
class ClassificationResult:
    """Result of text classification."""
    tool_name: str
    tool_args: Dict[str, Any]
    confidence: float
    method: str
    query_type: str
    entity: str
    intent: str
    description: str
