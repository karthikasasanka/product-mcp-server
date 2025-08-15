import os
import pytest
from mcp_api.config import Settings, settings


class TestSettings:
    """Test the Settings class and settings instance."""

    def test_settings_default_values(self):
        """Test that settings have correct default values."""
        assert settings.app_name == "Product MCP Server"
        assert settings.debug is False

    def test_settings_debug_true(self, monkeypatch):
        """Test settings when DEBUG environment variable is set to true."""
        monkeypatch.setenv("DEBUG", "true")
        # The settings instance is created at module import time, so we need to reload
        import importlib
        import mcp_api.config
        importlib.reload(mcp_api.config)
        assert mcp_api.config.settings.debug is True

    def test_settings_debug_false(self, monkeypatch):
        """Test settings when DEBUG environment variable is set to false."""
        monkeypatch.setenv("DEBUG", "false")
        # The settings instance is created at module import time, so we need to reload
        import importlib
        import mcp_api.config
        importlib.reload(mcp_api.config)
        assert mcp_api.config.settings.debug is False

    def test_settings_debug_invalid(self, monkeypatch):
        """Test settings when DEBUG environment variable is set to invalid value."""
        monkeypatch.setenv("DEBUG", "invalid")
        # The settings instance is created at module import time, so we need to reload
        import importlib
        import mcp_api.config
        importlib.reload(mcp_api.config)
        assert mcp_api.config.settings.debug is False

    def test_settings_model_validation(self):
        """Test that Settings model validation works correctly."""
        # Test with valid data
        valid_settings = Settings(app_name="Test App", debug=True)
        assert valid_settings.app_name == "Test App"
        assert valid_settings.debug is True

    def test_settings_inheritance(self):
        """Test that Settings inherits from BaseModel correctly."""
        assert hasattr(settings, 'model_dump')
        assert hasattr(settings, 'model_validate')
