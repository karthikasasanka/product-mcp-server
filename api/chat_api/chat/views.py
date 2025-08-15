import json
import logging
import time
from typing import Any
from fastapi import APIRouter, HTTPException, Depends, Request
from chat_api.chat.schemas import ChatIn
from chat_api.nlp import extract_tool_and_args
from chat_api.nlp import extract_tool_and_args_nlp
from chat_api.classifier.csv_classifier import CSVBasedClassifier
from chat_api.ml_classifier.joint_classifier import joint_classifier
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession
from chat_api.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

chat_router = APIRouter()

# Common intent to message mapping for all endpoints
INTENT_TO_MESSAGE = {
    "product.create": "Added! Here's the product:",
    "product.update": "Updated! Here's the product:",
    "product.delete": "Deleted! Product removed successfully.",
    "product.get": "Found! Here's the product:",
    "product.list": "Here are the products:",
}

def get_response_message(tool_name: str, parsed_result: Any) -> str:
    """Get appropriate response message based on tool and result."""
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

def get_csv_classifier(request: Request) -> CSVBasedClassifier:
    """Dependency to get the CSV classifier instance from app state."""
    # Try to get from app state first (pre-loaded at startup)
    if hasattr(request.app.state, 'csv_classifier'):
        classifier = request.app.state.csv_classifier
        if classifier and classifier.is_loaded:
            logger.info("✅ Using pre-loaded CSV classifier from app startup")
            return classifier
    
    # Fallback: create new instance
    logger.info("📂 Creating new CSV classifier instance (fallback)")
    classifier = CSVBasedClassifier()
    classifier.load_model()
    return classifier

@chat_router.post("/v1")
async def chat(inp: ChatIn):
    """
    Chat endpoint using configurable NLP model for tool selection and argument extraction.
    
    V1 Evolution Reason:
    - Unified approach using configurable NLP models via environment variables
    - Can use llama3.1:8b, qwen2.5:3b-instruct-q4_K_M, or any other Ollama model
    - Model selection controlled by NLP_MODEL_NAME environment variable
    - Provides flexibility to choose between speed and intelligence
    - Use case: All scenarios - model choice based on requirements
    """
    logger.info(f"🚀 Chat request received: {inp.message}")
    
    try:
        # Use configurable NLP model to extract tool and arguments
        logger.info("🤖 Using configurable NLP model for tool selection and argument extraction...")
        start_time = time.perf_counter()
        extraction_result = await extract_tool_and_args(inp.message)
        extraction_time = time.perf_counter() - start_time
        logger.info(f"⏱️ NLP extraction took {extraction_time:.2f} seconds")
        
        tool_name = extraction_result.get("tool_name")
        tool_args = extraction_result.get("tool_args", {})
        confidence = extraction_result.get("confidence", 0.8)
        method = extraction_result.get("method", "nlp_model")
        model_name = extraction_result.get("model", "unknown")
        
        logger.info(f"🎯 {model_name} selected tool: {tool_name}")
        logger.info(f"🔧 Extracted arguments: {tool_args}")
        logger.info(f"📊 Confidence: {confidence}")
        
        # Call the MCP tool with extracted arguments
        logger.info(f"🔗 Connecting to MCP server: {settings.MCP_SERVER_URL}")
        async with streamablehttp_client(settings.MCP_SERVER_URL + "/mcp") as (read, write, _):
            async with ClientSession(read, write) as session:
                # Initialize the session
                logger.info("🔄 Initializing MCP session...")
                await session.initialize()
                logger.info("✅ MCP session initialized")
                
                # Call the tool with extracted arguments
                try:
                    logger.info(f"🛠️ Calling tool: {tool_name} with arguments: {tool_args}")
                    res = await session.call_tool(tool_name, tool_args)
                    result = res.content[0].text
                    logger.info(f"✅ Tool response received: {result[:200]}...")
                except Exception as tool_error:
                    logger.error(f"❌ Tool call failed: {tool_error}")
                    raise
                
        # Parse and return the result
        parsed_result = json.loads(result)
        logger.info("✅ Chat request processed successfully")

        # Get appropriate response message
        minimal_message = get_response_message(tool_name, parsed_result)
        
        return {
            "message": minimal_message,
            "data": parsed_result,
            "method": method,
            "confidence": confidence,
            "extraction_time": extraction_time
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@chat_router.post("/v2")
async def chat_v2(inp: ChatIn):
    """
    Chat endpoint using ML-based joint intent classification and slot filling.
    
    V2 Evolution Reason:
    - Needed faster, more structured approach than v1 (Llama 3.1)
    - Joint intent-slot classification handles both tool selection and argument extraction simultaneously
    - Rule-based patterns with ML confidence scoring for better accuracy
    - Much faster than v1 while maintaining good flexibility
    - Trade-off: Requires pattern training, less flexible than LLM
    - Use case: Standard queries with predictable patterns
    """
    logger.info(f"🚀 Chat v2 request received: {inp.message}")
    
    try:
        # Use ML-based joint intent classification and slot filling
        logger.info("🤖 Using ML-based joint intent classification and slot filling...")
        start_time = time.perf_counter()
        
        # Perform joint classification
        result = joint_classifier.classify(inp.message)
        classification_dict = joint_classifier.to_dict(result)
        
        extraction_time = time.perf_counter() - start_time
        logger.info(f"⏱️ ML joint classification took {extraction_time:.4f} seconds")
        
        tool_name = classification_dict.get("tool_name")
        tool_args = classification_dict.get("tool_args", {})
        confidence = classification_dict.get("confidence", 0.0)
        method = classification_dict.get("method", "ml_joint_classifier")
        slots = classification_dict.get("slots", [])
        
        logger.info(f"🎯 ML joint classifier selected tool: {tool_name}")
        logger.info(f"🔧 Extracted arguments: {tool_args}")
        logger.info(f"📊 Confidence: {confidence}")
        logger.info(f"🔍 Method: {method}")
        logger.info(f"🎯 Slots: {slots}")
        
        # Call the MCP tool with extracted arguments
        logger.info(f"🔗 Connecting to MCP server: {settings.MCP_SERVER_URL}")
        async with streamablehttp_client(settings.MCP_SERVER_URL + "/mcp") as (read, write, _):
            async with ClientSession(read, write) as session:
                # Initialize the session
                logger.info("🔄 Initializing MCP session...")
                await session.initialize()
                logger.info("✅ MCP session initialized")
                
                # Call the tool with extracted arguments
                try:
                    logger.info(f"🛠️ Calling tool: {tool_name} with arguments: {tool_args}")
                    res = await session.call_tool(tool_name, tool_args)
                    result_text = res.content[0].text
                    logger.info(f"✅ Tool response received: {result_text[:200]}...")
                except Exception as tool_error:
                    logger.error(f"❌ Tool call failed: {tool_error}")
                    raise
                
        # Parse and return the result (minimal response)
        parsed_result = json.loads(result_text)
        logger.info("✅ Chat v2 request processed successfully")

        # Get appropriate response message
        minimal_message = get_response_message(tool_name, parsed_result)

        return {
            "message": minimal_message,
            "data": parsed_result,
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing chat v2 request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@chat_router.post("/v3")
async def chat_v3(
    inp: ChatIn, 
    classifier: CSVBasedClassifier = Depends(get_csv_classifier)
):
    """
    Chat endpoint using CSV-based ML classifier for tool selection.
    
    V3 Evolution Reason:
    - Needed fastest possible response for production use
    - CSV-based pattern matching with ML fallback for sub-second responses
    - Rule-based approach with dynamic argument extraction
    - Fastest of all three endpoints, optimized for high-throughput scenarios
    - Trade-off: Requires explicit pattern training, least flexible
    - Use case: High-throughput production scenarios
    """
    logger.info(f"🚀 Chat v3 request received: {inp.message}")
    
    try:
        # Use CSV-based ML classifier for tool selection
        logger.info("🤖 Using CSV-based ML classifier for tool selection...")
        start_time = time.perf_counter()
        
        classification_result = classifier.classify(inp.message)
        
        extraction_time = time.perf_counter() - start_time
        logger.info(f"⏱️ CSV classifier extraction took {extraction_time:.4f} seconds")
        
        tool_name = classification_result.get("tool_name")
        tool_args = classification_result.get("tool_args", {})
        confidence = classification_result.get("confidence", 0.0)
        method = classification_result.get("method", "csv_classifier")
        
        logger.info(f"🎯 CSV classifier selected tool: {tool_name}")
        logger.info(f"🔧 Extracted arguments: {tool_args}")
        logger.info(f"📊 Confidence: {confidence}")
        logger.info(f"🔍 Method: {method}")
        
        # Call the MCP tool with extracted arguments
        logger.info(f"🔗 Connecting to MCP server: {settings.MCP_SERVER_URL}")
        async with streamablehttp_client(settings.MCP_SERVER_URL + "/mcp") as (read, write, _):
            async with ClientSession(read, write) as session:
                # Initialize the session
                logger.info("🔄 Initializing MCP session...")
                await session.initialize()
                logger.info("✅ MCP session initialized")
                
                # Call the tool with extracted arguments
                try:
                    logger.info(f"🛠️ Calling tool: {tool_name} with arguments: {tool_args}")
                    res = await session.call_tool(tool_name, tool_args)
                    result = res.content[0].text
                    logger.info(f"✅ Tool response received: {result[:200]}...")
                except Exception as tool_error:
                    logger.error(f"❌ Tool call failed: {tool_error}")
                    raise
                
        # Parse and return the result (minimal response)
        parsed_result = json.loads(result)
        logger.info("✅ Chat v3 request processed successfully")

        # Get appropriate response message
        minimal_message = get_response_message(tool_name, parsed_result)
        
        return {
            "message": minimal_message,
            "data": parsed_result,
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing chat v3 request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")



@chat_router.get("/test")
async def test():
    """Test endpoint for basic API health check."""
    return {"status": "ok", "message": "Chat API is running"}

@chat_router.get("/tools")
async def list_tools():
    """List available tools from the MCP server."""
    try:
        from chat_api.nlp.extractor import get_openapi_spec
        openapi_spec = await get_openapi_spec()
        
        tools_info = {}
        if "paths" in openapi_spec:
            for path, methods in openapi_spec["paths"].items():
                for method, details in methods.items():
                    if method.lower() in ["get", "post", "put", "delete"]:
                        operation_id = details.get("operationId", f"{method}_{path}")
                        summary = details.get("summary", f"{method.upper()} {path}")
                        
                        # Get required parameters
                        required_params = []
                        if "parameters" in details:
                            for param in details["parameters"]:
                                if param.get("required", False):
                                    required_params.append(param["name"])
                        
                        tools_info[operation_id] = {
                            "summary": summary,
                            "required_params": required_params,
                            "method": method.upper(),
                            "path": path
                        }
        
        return {"tools": tools_info}
        
    except Exception as e:
        logger.error(f"❌ Error listing tools: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing tools: {str(e)}")
