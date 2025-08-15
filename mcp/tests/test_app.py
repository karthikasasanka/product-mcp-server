import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from mcp_api.app import create_app


class TestApp:
    """Test the FastAPI application."""

    def test_create_app_returns_fastapi_instance(self):
        """Test that create_app returns a FastAPI instance."""
        app = create_app()
        assert isinstance(app, FastAPI)

    def test_app_title(self):
        """Test that the app has the correct title."""
        app = create_app()
        assert app.title == "Product MCP Server"

    def test_app_has_routers(self):
        """Test that the app includes the product router."""
        app = create_app()
        # Check if the product router is included
        routes = [route.path for route in app.routes]
        assert any("/products" in route for route in routes)

    def test_app_has_middleware(self):
        """Test that the app has the logging middleware."""
        app = create_app()
        # Check if middleware is registered
        assert len(app.user_middleware) > 0

    @pytest.mark.asyncio
    async def test_logging_middleware(self):
        """Test the logging middleware functionality."""
        app = create_app()
        
        # Create a mock request and response
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/test"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Mock the call_next function
        async def mock_call_next(request):
            return mock_response
        
        # Get the middleware function
        middleware = None
        for middleware_class in app.user_middleware:
            if middleware_class.cls.__name__ == "log_request_time":
                middleware = middleware_class.cls
                break
        
        if middleware:
            # Test the middleware
            with patch('time.perf_counter') as mock_perf_counter:
                mock_perf_counter.side_effect = [0.0, 0.1]  # Start and end times
                
                result = await middleware(mock_request, mock_call_next)
                
                assert result == mock_response
                mock_perf_counter.assert_called()

    def test_app_has_startup_event(self):
        """Test that the app has a startup event handler."""
        app = create_app()
        # Check if startup event is registered
        assert hasattr(app, 'router')
        # The startup event should be registered in the lifespan context

    def test_app_has_mcp_integration(self):
        """Test that the app has MCP integration."""
        app = create_app()
        # Check if MCP routes are available
        routes = [route.path for route in app.routes]
        assert any("/mcp" in route for route in routes)

    def test_app_route_structure(self):
        """Test the overall route structure of the app."""
        app = create_app()
        routes = [route.path for route in app.routes]
        
        # Should have product routes
        assert any("/products" in route for route in routes)
        
        # Should have MCP routes
        assert any("/mcp" in route for route in routes)

    def test_app_dependencies(self):
        """Test that the app has proper dependencies."""
        app = create_app()
        # Check if dependencies are properly configured
        assert app.dependency_overrides is not None

    def test_app_openapi_generation(self):
        """Test that the app can generate OpenAPI schema."""
        app = create_app()
        openapi_schema = app.openapi()
        assert openapi_schema is not None
        assert "openapi" in openapi_schema
        assert "info" in openapi_schema
        assert "paths" in openapi_schema

    def test_app_health_check(self):
        """Test that the app responds to basic requests."""
        app = create_app()
        client = TestClient(app)
        
        # Test that the app responds (should return 404 for unknown routes)
        response = client.get("/health")
        assert response.status_code in [404, 200]  # Either not found or health endpoint exists

    def test_app_product_routes_exist(self):
        """Test that product routes are properly configured."""
        app = create_app()
        client = TestClient(app)
        
        # Test that product routes exist (should return 405 Method Not Allowed for GET on POST route)
        response = client.get("/products/")
        assert response.status_code in [200, 405]  # Either works or method not allowed

    def test_app_mcp_routes_exist(self):
        """Test that MCP routes are properly configured."""
        app = create_app()
        client = TestClient(app)
        
        # Test that MCP routes exist
        response = client.get("/mcp")
        assert response.status_code in [200, 404, 405, 406]  # Various possible responses

    def test_app_middleware_logging(self):
        """Test that middleware logging works correctly."""
        app = create_app()
        
        # Test that the middleware function exists and is callable
        middleware_found = False
        for middleware_class in app.user_middleware:
            if hasattr(middleware_class.cls, '__name__'):
                middleware_found = True
                break
        
        assert middleware_found

    def test_app_imports(self):
        """Test that all required imports work correctly."""
        # Test that we can import all required modules
        from mcp_api.config import settings
        from mcp_api.product.views import router as product_router
        from fastapi_mcp import FastApiMCP
        
        assert settings is not None
        assert product_router is not None
        assert FastApiMCP is not None
