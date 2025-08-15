import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
import json

from chat_api.main import app


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_mcp_session():
    """Mock MCP client session."""
    mock_session = AsyncMock()
    mock_session.initialize = AsyncMock()
    
    # Mock tool call response
    mock_content = Mock()
    mock_content.text = json.dumps([{"id": 1, "name": "Test Product"}])
    mock_response = Mock()
    mock_response.content = [mock_content]
    mock_session.call_tool = AsyncMock(return_value=mock_response)
    
    return mock_session


@pytest.fixture
def mock_mcp_client():
    """Mock MCP HTTP client."""
    mock_client = AsyncMock()
    mock_read = AsyncMock()
    mock_write = AsyncMock()
    
    # Mock the context manager behavior
    mock_client.__aenter__ = AsyncMock(return_value=(mock_read, mock_write, None))
    mock_client.__aexit__ = AsyncMock(return_value=None)
    
    return mock_client


@pytest.fixture
def mock_openapi_response():
    """Mock OpenAPI response."""
    return {
        "paths": {
            "/products": {
                "get": {
                    "operationId": "product.list",
                    "summary": "List all products",
                    "description": "Get a list of all products",
                    "tags": ["products"]
                }
            },
            "/products/{id}": {
                "get": {
                    "operationId": "product.get",
                    "summary": "Get product by ID",
                    "description": "Get a specific product by its ID",
                    "tags": ["products"]
                }
            }
        }
    }
