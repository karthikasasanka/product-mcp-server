"""
Utility functions for NLP model implementation.
"""

import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def format_response_message(tool_name: str, parsed_result: Any) -> str:
    """Format response message based on tool and result."""
    
    # Common intent to message mapping
    INTENT_TO_MESSAGE = {
        "product.create": "Added! Here's the product:",
        "product.update": "Updated! Here's the product:",
        "product.delete": "Deleted! Product removed successfully.",
        "product.get": "Found! Here's the product:",
        "product.list": "Here are the products:",
    }
    
    base_message = INTENT_TO_MESSAGE.get(tool_name, "ok")
    
    # Special handling for product.list - adjust message based on number of products
    if tool_name == "product.list" and isinstance(parsed_result, list):
        if len(parsed_result) == 1:
            return "Here's the product:"
        elif len(parsed_result) == 0:
            return "No products found."
        else:
            return "Here are the products:"
    
    return base_message


def validate_extraction_result(data: Dict[str, Any]) -> bool:
    """Validate that extraction result has required fields."""
    required_fields = ["tool_name", "tool_args"]
    return all(field in data for field in required_fields)


def log_extraction_details(model_name: str, tool_name: str, tool_args: Dict[str, Any], confidence: float, extraction_time: float):
    """Log detailed extraction information."""
    logger.info(f"🎯 {model_name} selected tool: {tool_name}")
    logger.info(f"🔧 Extracted arguments: {tool_args}")
    logger.info(f"📊 Confidence: {confidence}")
    logger.info(f"⏱️ Extraction took {extraction_time:.2f} seconds")


def get_model_info() -> Dict[str, Any]:
    """Get information about the current NLP model configuration."""
    from chat_api.nlp.config import (
        NLP_MODEL_NAME,
        NLP_TIMEOUT,
        NLP_TEMPERATURE,
        CURRENT_MODEL_DETAILS,
        CURRENT_PERFORMANCE
    )
    
    return {
        "model_name": NLP_MODEL_NAME,
        "timeout": NLP_TIMEOUT,
        "temperature": NLP_TEMPERATURE,
        "details": CURRENT_MODEL_DETAILS,
        "performance": CURRENT_PERFORMANCE
    }


def list_available_models() -> List[Dict[str, Any]]:
    """List all available models and their configurations."""
    from chat_api.nlp.config import MODEL_DETAILS, PERFORMANCE
    
    models = []
    for model_name, details in MODEL_DETAILS.items():
        models.append({
            "name": model_name,
            "details": details,
            "performance": PERFORMANCE.get(model_name, {})
        })
    
    return models


