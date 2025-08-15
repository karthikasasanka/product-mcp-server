"""
Test script for the new NLP module.
"""

import asyncio
import os
import logging
from chat_api.nlp import extract_tool_and_args_nlp, get_model_info, list_available_models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_nlp_extraction():
    """Test NLP extraction with different model configurations."""
    
    # Test message
    message = "Create a new product called iPhone 15 with price 999 and amazing camera features"
    
    logger.info("🧪 Testing NLP extraction...")
    logger.info(f"📝 Message: {message}")
    
    try:
        # Get current model info
        model_info = get_model_info()
        logger.info(f"🤖 Current model: {model_info}")
        
        # Test extraction
        result = await extract_tool_and_args_nlp(message)
        logger.info(f"✅ Extraction result: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Extraction failed: {e}")
        return None


async def test_model_switching():
    """Test switching between different models."""
    
    test_message = "List all products"
    
    # Test with llama3.1:8b
    os.environ["NLP_MODEL_NAME"] = "llama3.1:8b"
    os.environ["NLP_TIMEOUT"] = "300.0"
    
    logger.info("🔄 Testing with llama3.1:8b...")
    try:
        result1 = await extract_tool_and_args_nlp(test_message)
        logger.info(f"✅ llama3.1:8b result: {result1}")
    except Exception as e:
        logger.error(f"❌ llama3.1:8b failed: {e}")
    
    # Test with qwen2.5:3b
    os.environ["NLP_MODEL_NAME"] = "qwen2.5:3b-instruct-q4_K_M"
    os.environ["NLP_TIMEOUT"] = "120.0"
    
    logger.info("🔄 Testing with qwen2.5:3b...")
    try:
        result2 = await extract_tool_and_args_nlp(test_message)
        logger.info(f"✅ qwen2.5:3b result: {result2}")
    except Exception as e:
        logger.error(f"❌ qwen2.5:3b failed: {e}")


def test_available_models():
    """Test listing available models."""
    logger.info("📋 Available models:")
    models = list_available_models()
    for model in models:
        logger.info(f"  - {model['name']}: {model['details'].get('use_case', 'N/A')}")


async def main():
    """Main test function."""
    logger.info("🚀 Starting NLP module tests...")
    
    # Test available models
    test_available_models()
    
    # Test current model extraction
    await test_nlp_extraction()
    
    # Test model switching
    await test_model_switching()
    
    logger.info("✅ NLP module tests completed!")


if __name__ == "__main__":
    asyncio.run(main())


