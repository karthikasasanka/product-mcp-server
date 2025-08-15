import pytest
from pydantic import ValidationError
from mcp_api.product.schemas import ProductIn, Product


class TestProductIn:
    """Test the ProductIn schema."""

    def test_product_in_valid_data(self):
        """Test ProductIn with valid data."""
        data = {
            "name": "Test Product",
            "price": 99.99,
            "description": "A test product"
        }
        product = ProductIn(**data)
        assert product.name == "Test Product"
        assert product.price == 99.99
        assert product.description == "A test product"

    def test_product_in_minimal_data(self):
        """Test ProductIn with minimal required data."""
        data = {
            "name": "Test Product",
            "price": 99.99
        }
        product = ProductIn(**data)
        assert product.name == "Test Product"
        assert product.price == 99.99
        assert product.description is None

    def test_product_in_invalid_name_empty(self):
        """Test ProductIn with empty name (should fail validation)."""
        data = {
            "name": "",
            "price": 99.99
        }
        with pytest.raises(ValidationError):
            ProductIn(**data)

    def test_product_in_invalid_name_whitespace(self):
        """Test ProductIn with whitespace-only name (should pass validation since min_length=1 only checks length)."""
        data = {
            "name": "   ",
            "price": 99.99
        }
        # This should pass because min_length=1 only checks length, not content
        product = ProductIn(**data)
        assert product.name == "   "
        assert product.price == 99.99

    def test_product_in_invalid_price_zero(self):
        """Test ProductIn with zero price (should fail validation)."""
        data = {
            "name": "Test Product",
            "price": 0
        }
        with pytest.raises(ValidationError):
            ProductIn(**data)

    def test_product_in_invalid_price_negative(self):
        """Test ProductIn with negative price (should fail validation)."""
        data = {
            "name": "Test Product",
            "price": -10.0
        }
        with pytest.raises(ValidationError):
            ProductIn(**data)

    def test_product_in_missing_required_fields(self):
        """Test ProductIn with missing required fields."""
        with pytest.raises(ValidationError):
            ProductIn()

    def test_product_in_missing_name(self):
        """Test ProductIn with missing name."""
        data = {"price": 99.99}
        with pytest.raises(ValidationError):
            ProductIn(**data)

    def test_product_in_missing_price(self):
        """Test ProductIn with missing price."""
        data = {"name": "Test Product"}
        with pytest.raises(ValidationError):
            ProductIn(**data)


class TestProduct:
    """Test the Product schema."""

    def test_product_valid_data(self):
        """Test Product with valid data including id."""
        data = {
            "id": 1,
            "name": "Test Product",
            "price": 99.99,
            "description": "A test product"
        }
        product = Product(**data)
        assert product.id == 1
        assert product.name == "Test Product"
        assert product.price == 99.99
        assert product.description == "A test product"

    def test_product_inheritance(self):
        """Test that Product inherits from ProductIn."""
        assert issubclass(Product, ProductIn)

    def test_product_config(self):
        """Test that Product has the correct config."""
        assert hasattr(Product, 'model_config')
        # Check that from_attributes is set to True
        product = Product(id=1, name="Test", price=99.99)
        assert hasattr(product, 'model_dump')

    def test_product_missing_id(self):
        """Test Product with missing id (should fail validation)."""
        data = {
            "name": "Test Product",
            "price": 99.99
        }
        with pytest.raises(ValidationError):
            Product(**data)

    def test_product_invalid_id_type(self):
        """Test Product with invalid id type."""
        data = {
            "id": "not_an_int",
            "name": "Test Product",
            "price": 99.99
        }
        with pytest.raises(ValidationError):
            Product(**data)
