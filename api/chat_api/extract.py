import json
import logging
import httpx
from typing import Dict, Any
from chat_api.config import settings
from chat_api.classifier.csv_classifier import classify_message_csv

# -----------------------------------------------------------------------------
# Models used:
# - nomic-embed-text: For vector embeddings (semantic search) - in services.py
# - llama3.1:8b: For tool selection and argument extraction (this file)
# 
# Product creation and update logic:
# - name: Product name only
# - price: Numeric price value only  
# - description: Everything else (features, specs, categories, etc.)
# - accessories: Not used
# -----------------------------------------------------------------------------

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


def _fast_pattern_match(message: str) -> Dict[str, Any]:
    """Fast CSV-based pattern matching (sub-second response)."""
    return classify_message_csv(message)


async def extract_tool_and_args(message: str, use_fast_fallback: bool = True) -> Dict[str, Any]:
    """Extract tool name and arguments using Llama 3.1 with fast fallback."""
    
    # Fast rule-based fallback for common cases (sub-second response)
    if use_fast_fallback:
        fast_result = _fast_pattern_match(message)
        if fast_result:
            return fast_result
    
    # Get OpenAPI spec
    openapi_spec = await get_openapi_spec()
    
    # Build tool descriptions from OpenAPI
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
    
    # Create tools text
    tools_text = "\n".join([
        f"- {op_id}: {info['summary']} (needs: {', '.join(info['required_params']) if info['required_params'] else 'none'})"
        for op_id, info in tools_info.items()
    ])
    
    system = (
        "You are a router+arg-extractor. "
        "Pick the best operationId and fill its args. "
        "Only include fields that the tool expects. "
        "For product creation and updates: "
        "- name: Product name only "
        "- price: Numeric price value only "
        "- description: Everything else (features, specs, categories, etc.) "
        "- Do NOT use accessories field "
        "You MUST return ONLY valid JSON with no additional text, explanations, or formatting. "
        "The response must be a single JSON object: {\"tool_name\": string, \"tool_args\": object, \"confidence\": number}"
    )
    
    user = f"""User text: {message}

Available tools:
{tools_text}"""

    try:
        logger.info("🤖 Sending request to Llama 3.1...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.OLLAMA_SERVER_URL}/api/chat",
                json={
                    "model": "llama3.1:8b",
                    "format": "json",
                    "stream": False,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "options": {"temperature": 0.0}
                },
                timeout=120.0  # Increased timeout for llama3.1:8b model
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
            
            logger.info("✅ Llama extraction successful")
            
            tool_name = data.get("tool_name", "product.list")
            tool_args = data.get("tool_args", {})
            confidence = data.get("confidence", 0.8)
            
            # Special handling for "recent" products
            if tool_name == "product.list" and any(word in message.lower() for word in ["recent", "latest", "newest"]):
                tool_args["limit"] = 1
                tool_args["recent_only"] = True
            
            return {
                "tool_name": tool_name,
                "tool_args": tool_args,
                "confidence": confidence
            }
            
    except Exception as e:
        logger.error(f"❌ Llama extraction failed: {e}")
        raise Exception(f"Tool extraction failed: {e}")
