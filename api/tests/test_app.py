import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

from chat_api.main import app
from chat_api.app import create_app


class TestApp:
    """Test FastAPI app."""

    def test_app_creation(self):
        """Test that app is created successfully."""
        assert app is not None

    def test_app_docs_url(self, client):
        """Test that docs are available at root."""
        response = client.get("/")
        assert response.status_code == 200

    def test_app_title(self, client):
        """Test app title."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        openapi_data = response.json()
        assert openapi_data["info"]["title"] == "AI Chat Service"

    def test_chat_endpoint_exists(self, client):
        """Test that chat endpoint exists."""
        response = client.post("/chat", json={"message": "test"})
        # Should return 500 because Ollama is not available in tests
        assert response.status_code == 500

    def test_create_app_function(self):
        """Test create_app function."""
        test_app = create_app()
        assert test_app is not None
        assert test_app.title == "AI Chat Service"
        assert test_app.docs_url == "/"


class TestLifespan:
    """Test lifespan events."""

    @pytest.mark.asyncio
    async def test_lifespan_startup(self):
        """Test lifespan startup event."""
        from chat_api.app import lifespan
        
        # Create mock app
        mock_app = Mock()
        
        # Test lifespan context manager
        async with lifespan(mock_app) as _:
            # Verify lifespan works without vector store initialization
            pass


class TestRouterIntegration:
    """Test router integration."""

    def test_routers_initialized(self):
        """Test that routers are initialized."""
        test_app = create_app()
        
        # Check that chat router is included
        routes = [route.path for route in test_app.routes]
        assert "/chat" in routes
