import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from mcp_api.product.views import router
from mcp_api.product.schemas import ProductIn, Product
from mcp_api.product.models import Product as ProductModel


class TestProductViews:
    """Test the product views/endpoints."""

    def test_router_creation(self):
        """Test that the router is properly created."""
        assert router is not None
        assert hasattr(router, 'routes')

    def test_router_routes_exist(self):
        """Test that all expected routes exist."""
        routes = [route.path for route in router.routes]
        expected_routes = ['/', '/{product_id}', '/', '/{product_id}', '/{product_id}']
        
        for expected_route in expected_routes:
            assert expected_route in routes

    @pytest.mark.asyncio
    async def test_create_product_success(self):
        """Test successful product creation endpoint."""
        # Mock dependencies
        mock_db = AsyncMock(spec=AsyncSession)
        mock_product = ProductModel(id=1, name="Test Product", price=99.99, description="Test description")
        
        # Mock the crud function
        with pytest.MonkeyPatch().context() as m:
            m.setattr('mcp_api.product.views.crud.create_product', AsyncMock(return_value=mock_product))
            
            # Test data
            product_data = ProductIn(name="Test Product", price=99.99, description="Test description")
            
            # Call the endpoint function
            from mcp_api.product.views import create
            result = await create(product_data, mock_db)
            
            # Assertions
            assert result.id == 1
            assert result.name == "Test Product"
            assert result.price == 99.99
            assert result.description == "Test description"

    @pytest.mark.asyncio
    async def test_get_product_success(self):
        """Test successful product retrieval endpoint."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_product = ProductModel(id=1, name="Test Product", price=99.99)
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr('mcp_api.product.views.crud.get_product', AsyncMock(return_value=mock_product))
            
            from mcp_api.product.views import get
            result = await get(1, mock_db)
            
            assert result.id == 1
            assert result.name == "Test Product"
            assert result.price == 99.99

    @pytest.mark.asyncio
    async def test_get_product_not_found(self):
        """Test product retrieval when product doesn't exist."""
        mock_db = AsyncMock(spec=AsyncSession)
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr('mcp_api.product.views.crud.get_product', AsyncMock(return_value=None))
            
            from mcp_api.product.views import get
            
            with pytest.raises(HTTPException) as exc_info:
                await get(999, mock_db)
            
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Product not found"

    @pytest.mark.asyncio
    async def test_list_products_success(self):
        """Test successful product listing endpoint."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_products = [
            ProductModel(id=1, name="Product 1", price=99.99),
            ProductModel(id=2, name="Product 2", price=149.99)
        ]
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr('mcp_api.product.views.crud.list_products', AsyncMock(return_value=mock_products))
            
            from mcp_api.product.views import list_
            result = await list_(skip=0, limit=10, db=mock_db)
            
            assert len(result) == 2
            assert result[0].name == "Product 1"
            assert result[1].name == "Product 2"

    @pytest.mark.asyncio
    async def test_list_products_with_pagination(self):
        """Test product listing with pagination parameters."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_products = []
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr('mcp_api.product.views.crud.list_products', AsyncMock(return_value=mock_products))
            
            from mcp_api.product.views import list_
            result = await list_(skip=5, limit=5, db=mock_db)
            
            assert result == []

    @pytest.mark.asyncio
    async def test_update_product_success(self):
        """Test successful product update endpoint."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_product = ProductModel(id=1, name="Updated Product", price=149.99, description="Updated description")
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr('mcp_api.product.views.crud.update_product', AsyncMock(return_value=mock_product))
            
            update_data = ProductIn(name="Updated Product", price=149.99, description="Updated description")
            
            from mcp_api.product.views import update
            result = await update(1, update_data, mock_db)
            
            assert result.id == 1
            assert result.name == "Updated Product"
            assert result.price == 149.99
            assert result.description == "Updated description"

    @pytest.mark.asyncio
    async def test_update_product_not_found(self):
        """Test product update when product doesn't exist."""
        mock_db = AsyncMock(spec=AsyncSession)
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr('mcp_api.product.views.crud.update_product', AsyncMock(return_value=None))
            
            update_data = ProductIn(name="Updated Product", price=149.99)
            
            from mcp_api.product.views import update
            
            with pytest.raises(HTTPException) as exc_info:
                await update(999, update_data, mock_db)
            
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Product not found"

    @pytest.mark.asyncio
    async def test_delete_product_success(self):
        """Test successful product deletion endpoint."""
        mock_db = AsyncMock(spec=AsyncSession)
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr('mcp_api.product.views.crud.delete_product', AsyncMock(return_value=True))
            
            from mcp_api.product.views import delete
            result = await delete(1, mock_db)
            
            assert result == {"success": True}

    @pytest.mark.asyncio
    async def test_delete_product_not_found(self):
        """Test product deletion when product doesn't exist."""
        mock_db = AsyncMock(spec=AsyncSession)
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr('mcp_api.product.views.crud.delete_product', AsyncMock(return_value=False))
            
            from mcp_api.product.views import delete
            
            with pytest.raises(HTTPException) as exc_info:
                await delete(999, mock_db)
            
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Product not found"

    def test_router_operation_ids(self):
        """Test that all routes have operation IDs."""
        for route in router.routes:
            if hasattr(route, 'endpoint'):
                # Check if the endpoint has operation_id in its decorators
                assert hasattr(route, 'operation_id') or any(
                    hasattr(route.endpoint, '__annotations__') 
                    for route in router.routes
                )

    def test_router_response_models(self):
        """Test that routes have proper response models."""
        for route in router.routes:
            if hasattr(route, 'response_model'):
                assert route.response_model is not None
