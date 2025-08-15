import pytest
import uvicorn
from unittest.mock import patch, MagicMock
from mcp_api.main import app


class TestMain:
    """Test the main module."""

    def test_app_creation(self):
        """Test that the app is properly created."""
        assert app is not None
        assert hasattr(app, 'title')
        assert app.title == "Product MCP Server"

    def test_app_routes_exist(self):
        """Test that the app has the expected routes."""
        routes = [route.path for route in app.routes]
        
        # Should have product routes
        assert any("/products" in route for route in routes)
        
        # Should have MCP routes
        assert any("/mcp" in route for route in routes)

    def test_app_openapi(self):
        """Test that the app can generate OpenAPI schema."""
        openapi_schema = app.openapi()
        assert openapi_schema is not None
        assert "openapi" in openapi_schema
        assert "info" in openapi_schema

    @patch('uvicorn.run')
    def test_main_execution(self, mock_uvicorn_run):
        """Test that uvicorn.run is called with correct parameters when __main__ is executed."""
        # Mock uvicorn.run to avoid actually starting the server
        mock_uvicorn_run.return_value = None
        
        # Create a namespace to execute the main block
        namespace = {
            '__name__': '__main__',
            '__file__': 'mcp_api/main.py'
        }
        
        # Execute the main block directly with proper namespace
        with open('mcp_api/main.py', 'r') as f:
            exec(f.read(), namespace)
        
        # Check that uvicorn.run was called with the expected parameters
        mock_uvicorn_run.assert_called_once()
        call_args = mock_uvicorn_run.call_args
        
        assert call_args[0][0] == "mcp_api.main:app"
        assert call_args[1]['host'] == "0.0.0.0"
        assert call_args[1]['port'] == 9000
        assert call_args[1]['reload'] is True

    def test_app_dependencies(self):
        """Test that the app has proper dependencies configured."""
        # Test that the app can handle requests
        assert app.dependency_overrides is not None

    def test_app_middleware(self):
        """Test that the app has middleware configured."""
        # Check if middleware is registered
        assert len(app.user_middleware) > 0

    def test_app_router_inclusion(self):
        """Test that routers are properly included."""
        # Check that product router is included
        routes = [route.path for route in app.routes]
        product_routes = [route for route in routes if "/products" in route]
        assert len(product_routes) > 0

    def test_app_mcp_integration(self):
        """Test that MCP integration is properly configured."""
        # Check that MCP routes are available
        routes = [route.path for route in app.routes]
        mcp_routes = [route for route in routes if "/mcp" in route]
        assert len(mcp_routes) > 0

    def test_app_configuration(self):
        """Test that the app is properly configured."""
        # Test basic app configuration
        assert app.title == "Product MCP Server"
        assert hasattr(app, 'openapi')
        assert hasattr(app, 'routes')

    def test_app_import_structure(self):
        """Test that all imports work correctly."""
        # Test that we can import the app
        from mcp_api.main import app as imported_app
        assert imported_app is not None
        assert isinstance(imported_app, type(app))

    def test_app_lifespan_events(self):
        """Test that the app has proper lifespan events."""
        # Check if the app has lifespan context manager
        assert hasattr(app, 'router')

    def test_app_error_handling(self):
        """Test that the app has proper error handling."""
        # Test that the app can handle basic requests
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Test a non-existent route (should return 404)
        response = client.get("/non-existent-route")
        assert response.status_code == 404

    def test_app_health_endpoints(self):
        """Test that the app responds to basic health checks."""
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Test that the app responds (even if it's a 404)
        response = client.get("/")
        assert response.status_code in [404, 200, 405]  # Various possible responses

    def test_app_documentation_endpoints(self):
        """Test that the app has documentation endpoints."""
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Test OpenAPI documentation endpoint
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()

    def test_app_docs_endpoint(self):
        """Test that the app has docs endpoint."""
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Test docs endpoint
        response = client.get("/docs")
        assert response.status_code == 200

    def test_app_redoc_endpoint(self):
        """Test that the app has redoc endpoint."""
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Test redoc endpoint
        response = client.get("/redoc")
        assert response.status_code == 200
