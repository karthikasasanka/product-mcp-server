import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from mcp_api.product.crud import (
    create_product, get_product, list_products, 
    update_product, delete_product
)
from mcp_api.product.schemas import ProductIn
from mcp_api.product.models import Product


class TestCRUD:
    """Test the CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_product_success(self):
        """Test successful product creation."""
        # Mock database session
        mock_session = AsyncMock(spec=AsyncSession)
        mock_product = Product(id=1, name="Test Product", price=99.99)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Test data
        product_data = ProductIn(name="Test Product", price=99.99, description="Test description")

        # Call the function
        result = await create_product(mock_session, product_data)

        # Assertions
        assert result.name == "Test Product"
        assert result.price == 99.99
        assert result.description == "Test description"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_product_found(self):
        """Test getting an existing product."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_product = Product(id=1, name="Test Product", price=99.99)
        mock_session.get = AsyncMock(return_value=mock_product)

        result = await get_product(mock_session, 1)

        assert result == mock_product
        mock_session.get.assert_called_once_with(Product, 1)

    @pytest.mark.asyncio
    async def test_get_product_not_found(self):
        """Test getting a non-existing product."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.get = AsyncMock(return_value=None)

        result = await get_product(mock_session, 999)

        assert result is None
        mock_session.get.assert_called_once_with(Product, 999)

    @pytest.mark.asyncio
    async def test_list_products_success(self):
        """Test listing products successfully."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            Product(id=1, name="Product 1", price=99.99),
            Product(id=2, name="Product 2", price=149.99)
        ]
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await list_products(mock_session, skip=0, limit=10)

        assert len(result) == 2
        assert result[0].name == "Product 1"
        assert result[1].name == "Product 2"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_products_with_pagination(self):
        """Test listing products with pagination parameters."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        await list_products(mock_session, skip=10, limit=5)

        # Verify the select statement was called with correct parameters
        call_args = mock_session.execute.call_args[0][0]
        assert "OFFSET" in str(call_args).upper()
        assert "LIMIT" in str(call_args).upper()

    @pytest.mark.asyncio
    async def test_update_product_success(self):
        """Test successful product update."""
        mock_session = AsyncMock(spec=AsyncSession)
        existing_product = Product(id=1, name="Old Name", price=99.99, description="Old description")
        mock_session.get = AsyncMock(return_value=existing_product)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        update_data = ProductIn(name="New Name", price=149.99, description="New description")

        result = await update_product(mock_session, 1, update_data)

        assert result.name == "New Name"
        assert result.price == 149.99
        assert result.description == "New description"
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_product_partial(self):
        """Test partial product update."""
        mock_session = AsyncMock(spec=AsyncSession)
        existing_product = Product(id=1, name="Old Name", price=99.99, description="Old description")
        mock_session.get = AsyncMock(return_value=existing_product)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Only update name, leave other fields unchanged
        update_data = ProductIn(name="New Name", price=99.99)

        result = await update_product(mock_session, 1, update_data)

        assert result.name == "New Name"
        assert result.price == 99.99
        assert result.description == "Old description"  # Should remain unchanged

    @pytest.mark.asyncio
    async def test_update_product_not_found(self):
        """Test updating a non-existing product."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.get = AsyncMock(return_value=None)

        update_data = ProductIn(name="New Name", price=149.99)

        result = await update_product(mock_session, 999, update_data)

        assert result is None
        mock_session.get.assert_called_once_with(Product, 999)

    @pytest.mark.asyncio
    async def test_delete_product_success(self):
        """Test successful product deletion."""
        mock_session = AsyncMock(spec=AsyncSession)
        existing_product = Product(id=1, name="Test Product", price=99.99)
        mock_session.get = AsyncMock(return_value=existing_product)
        mock_session.delete = AsyncMock()
        mock_session.commit = AsyncMock()

        result = await delete_product(mock_session, 1)

        assert result is True
        mock_session.delete.assert_called_once_with(existing_product)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_product_not_found(self):
        """Test deleting a non-existing product."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.get = AsyncMock(return_value=None)

        result = await delete_product(mock_session, 999)

        assert result is False
        mock_session.get.assert_called_once_with(Product, 999)
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_products_import_statement(self):
        """Test that the import statement in list_products works correctly."""
        # This test ensures the 'from sqlalchemy import select' import is covered
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # This should not raise any import errors
        result = await list_products(mock_session, skip=0, limit=10)
        
        assert isinstance(result, list)
