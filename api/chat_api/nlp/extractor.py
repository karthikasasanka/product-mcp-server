import json
import logging
import httpx
from typing import Dict, Any
from chat_api.config import settings
from chat_api.nlp.config import (
    NLP_MODEL_NAME, 
    NLP_TIMEOUT, 
    NLP_TEMPERATURE, 
    SYSTEM_PROMPT,
    CURRENT_MODEL_DETAILS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_openapi_spec() -> Dict[str, Any]:
    """Get OpenAPI spec from MCP server."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.MCP_SERVER_URL}/openapi.json", timeout=10.0)
            return response.json()
    except Exception as e:
        logger.error(f"Failed to get OpenAPI spec: {e}")
        return {}


def extract_tools_from_openapi(openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Extract tool information from OpenAPI specification."""
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
    return tools_info


def build_tools_text(tools_info: Dict[str, Any]) -> str:
    """Build tools description text from tools info."""
    return "\n".join([
        f"- {op_id}: {info['summary']} (needs: {', '.join(info['required_params']) if info['required_params'] else 'none'})"
        for op_id, info in tools_info.items()
    ])


def handle_recent_products(tool_name: str, tool_args: Dict[str, Any], message: str) -> Dict[str, Any]:
    """Handle special case for 'recent' products."""
    if tool_name == "product.list" and any(word in message.lower() for word in ["recent", "latest", "newest"]):
        tool_args["limit"] = 1
        tool_args["recent_only"] = True
    return tool_args


async def extract_tool_and_args_nlp(message: str) -> Dict[str, Any]:
    """
    Extract tool name and arguments using configurable NLP model.
    
    This function replaces the separate llama3.1 and qwen implementations
    since they both do the same task - tool selection and argument extraction.
    
    The model can be configured via environment variables:
    - NLP_MODEL_NAME: The model to use (default: llama3.1:8b)
    - NLP_TIMEOUT: Request timeout (default: 300.0 for llama3.1:8b)
    - NLP_TEMPERATURE: Model temperature (default: 0.0 for deterministic)
    """
    
    # Get OpenAPI spec
    openapi_spec = await get_openapi_spec()
    
    # Build tool descriptions from OpenAPI
    tools_info = extract_tools_from_openapi(openapi_spec)
    
    # Create tools text
    tools_text = build_tools_text(tools_info)
    
    system = SYSTEM_PROMPT
    
    user = f"""User text: {message}

Available tools:
{tools_text}"""

    try:
        logger.info(f"🤖 Sending request to {NLP_MODEL_NAME}...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.OLLAMA_SERVER_URL}/api/chat",
                json={
                    "model": NLP_MODEL_NAME,
                    "format": "json",
                    "stream": False,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "options": {"temperature": NLP_TEMPERATURE}
                },
                timeout=NLP_TIMEOUT
            )
            
            logger.info(f"📝 HTTP Status: {response.status_code}")
            logger.info(f"📝 Response Headers: {response.headers}")
            
            if response.status_code != 200:
                logger.error(f"❌ HTTP Error: {response.status_code} - {response.text}")
                raise Exception(f"HTTP Error {response.status_code}: {response.text}")
            
            try:
                result = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON Decode Error: {e}")
                logger.error(f"❌ Response Text: {response.text}")
                raise Exception(f"Invalid JSON response from Ollama: {e}")
            
            # For /api/chat, the response is in result.message.content
            data = result.get("message", {}).get("content", "{}")
            
            logger.info(f"📝 Raw result: {result}")
            logger.info(f"📝 Raw data: {data}")
            
            # Parse JSON response
            if isinstance(data, str):
                data = json.loads(data)
            
            logger.info(f"✅ {NLP_MODEL_NAME} extraction successful")
            
            tool_name = data.get("tool_name", "product.list")
            tool_args = data.get("tool_args", {})
            confidence = data.get("confidence", 0.8)
            
            # Special handling for "recent" products
            tool_args = handle_recent_products(tool_name, tool_args, message)
            
            return {
                "tool_name": tool_name,
                "tool_args": tool_args,
                "confidence": confidence,
                "method": CURRENT_MODEL_DETAILS.get("method", "nlp_model"),
                "model": NLP_MODEL_NAME
            }
            
    except Exception as e:
        logger.error(f"❌ {NLP_MODEL_NAME} extraction failed: {e}")
        raise Exception(f"Tool extraction failed: {e}")


# Alias for backward compatibility
extract_tool_and_args = extract_tool_and_args_nlp


