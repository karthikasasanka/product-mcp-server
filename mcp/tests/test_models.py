import pytest
from sqlalchemy import inspect
from mcp_api.product.models import Product


class TestProductModel:
    """Test the Product SQLAlchemy model."""

    def test_product_table_name(self):
        """Test that Product has the correct table name."""
        assert Product.__tablename__ == "products"

    def test_product_columns_exist(self):
        """Test that Product has all expected columns."""
        columns = [column.name for column in inspect(Product).columns]
        expected_columns = ['id', 'name', 'description', 'price']
        
        for expected_col in expected_columns:
            assert expected_col in columns

    def test_product_id_column(self):
        """Test the id column configuration."""
        id_column = inspect(Product).columns['id']
        assert id_column.primary_key is True
        assert id_column.index is True

    def test_product_name_column(self):
        """Test the name column configuration."""
        name_column = inspect(Product).columns['name']
        assert name_column.nullable is False
        assert name_column.index is True
        assert name_column.type.length == 200

    def test_product_description_column(self):
        """Test the description column configuration."""
        desc_column = inspect(Product).columns['description']
        assert desc_column.nullable is True

    def test_product_price_column(self):
        """Test the price column configuration."""
        price_column = inspect(Product).columns['price']
        assert price_column.nullable is False

    def test_product_mapped_columns(self):
        """Test that all columns are properly mapped."""
        assert hasattr(Product, 'id')
        assert hasattr(Product, 'name')
        assert hasattr(Product, 'description')
        assert hasattr(Product, 'price')

    def test_product_inheritance(self):
        """Test that Product inherits from Base."""
        from mcp_api.datbase import Base
        assert issubclass(Product, Base)

    def test_product_instantiation(self):
        """Test that Product can be instantiated."""
        product = Product(
            name="Test Product",
            price=99.99,
            description="A test product"
        )
        assert product.name == "Test Product"
        assert product.price == 99.99
        assert product.description == "A test product"

    def test_product_instantiation_minimal(self):
        """Test that Product can be instantiated with minimal data."""
        product = Product(
            name="Test Product",
            price=99.99
        )
        assert product.name == "Test Product"
        assert product.price == 99.99
        assert product.description is None

    def test_product_repr(self):
        """Test that Product has a meaningful string representation."""
        product = Product(
            id=1,
            name="Test Product",
            price=99.99
        )
        repr_str = repr(product)
        assert "Product" in repr_str
        # SQLAlchemy models don't include field values in repr by default
        assert "object at" in repr_str
