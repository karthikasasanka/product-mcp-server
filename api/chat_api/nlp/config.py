"""
Configuration module for NLP model implementation (configurable for different models).
"""

import os
from typing import Dict, Any

# Model configuration - configurable from environment variables
NLP_MODEL_NAME = os.getenv("NLP_MODEL_NAME", "llama3.1:8b")  # Default to llama3.1:8b
NLP_TIMEOUT = float(os.getenv("NLP_TIMEOUT", "300.0"))  # Default to 5 minutes for llama3.1:8b
NLP_TEMPERATURE = float(os.getenv("NLP_TEMPERATURE", "0.0"))  # Default to deterministic

# Model details based on common models
MODEL_DETAILS = {
    "llama3.1:8b": {
        "name": "llama3.1:8b",
        "size": "~8GB",
        "memory_usage": "~8GB RAM during inference",
        "speed": "2-5 minutes per request",
        "method": "llama3.1_8b",
        "use_case": "Complex queries requiring deep reasoning"
    },
    "qwen2.5:3b-instruct-q4_K_M": {
        "name": "qwen2.5:3b-instruct-q4_K_M",
        "quantization": "q4_K_M (4-bit quantization with K-quants)",
        "size": "~2GB (quantized from ~7GB)",
        "memory_usage": "~4GB RAM during inference",
        "speed": "2-5 seconds per request",
        "method": "qwen2.5_3b_instruct_q4",
        "use_case": "Balanced scenarios requiring both speed and intelligence"
    }
}

# Get current model details
CURRENT_MODEL_DETAILS = MODEL_DETAILS.get(NLP_MODEL_NAME, {
    "name": NLP_MODEL_NAME,
    "method": "custom_model",
    "use_case": "Custom model configuration"
})

# System prompt - same for all models since they do the same task
SYSTEM_PROMPT = (
    "You are a router+arg-extractor. "
    "Pick the best operationId and fill its args. "
    "Only include fields that the tool expects. "
    "For product creation and updates: "
    "- name: Product name only (extract the product name) "
    "- price: Numeric price value only (extract the price number) "
    "- description: Extract descriptive text about features, specs, categories, etc. "
    "  IMPORTANT: For description, extract ONLY the descriptive text, NOT the price information. "
    "  Example: 'add iPhone, amazing camera and price is $999' → description should be 'amazing camera' "
    "  Example: 'add Laptop, gaming features and costs $1299' → description should be 'gaming features' "
    "- Do NOT use accessories field "
    "For product queries: "
    "- 'recent', 'latest', 'newest' → use product.list with recent_only=True "
    "- 'get product by ID' → use product.get with specific product_id "
    "- 'list products', 'show products' → use product.list "
    "- 'find product by name' → use product.list with name filter "
    "You MUST return ONLY valid JSON with no additional text, explanations, or formatting. "
    "The response must be a single JSON object: {\"tool_name\": string, \"tool_args\": object, \"confidence\": number}"
)

# Performance characteristics based on current model
PERFORMANCE = {
    "llama3.1:8b": {
        "speed": "Slow (2-5 minutes)",
        "flexibility": "Very High",
        "resource_usage": "High",
        "intelligence": "Very High",
        "use_case": "Complex queries requiring deep reasoning"
    },
    "qwen2.5:3b-instruct-q4_K_M": {
        "speed": "Medium (2-5s)",
        "flexibility": "High",
        "resource_usage": "Medium",
        "intelligence": "High",
        "use_case": "Balanced scenarios requiring both speed and intelligence"
    }
}

CURRENT_PERFORMANCE = PERFORMANCE.get(NLP_MODEL_NAME, {
    "speed": "Unknown",
    "flexibility": "Unknown",
    "resource_usage": "Unknown",
    "intelligence": "Unknown",
    "use_case": "Custom model configuration"
})


