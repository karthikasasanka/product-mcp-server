import pytest
import asyncio
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from mcp_api.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """Create a mock database session for testing."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "name": "Test Product",
        "price": 99.99,
        "description": "A test product for testing purposes"
    }


@pytest.fixture
def sample_product_in():
    """Sample ProductIn object for testing."""
    from mcp_api.product.schemas import ProductIn
    return ProductIn(
        name="Test Product",
        price=99.99,
        description="A test product for testing purposes"
    )


@pytest.fixture
def sample_product_model():
    """Sample Product model instance for testing."""
    from mcp_api.product.models import Product
    return Product(
        id=1,
        name="Test Product",
        price=99.99,
        description="A test product for testing purposes"
    )


@pytest.fixture
def sample_product_list():
    """Sample list of Product model instances for testing."""
    from mcp_api.product.models import Product
    return [
        Product(id=1, name="Product 1", price=99.99, description="First product"),
        Product(id=2, name="Product 2", price=149.99, description="Second product"),
        Product(id=3, name="Product 3", price=199.99, description="Third product")
    ]
