import pytest
from unittest.mock import patch
import os

from chat_api.config import Settings, settings


class TestSettings:
    """Test Settings class."""

    def test_default_values(self):
        """Test default settings values."""
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings()
            assert test_settings.MCP_SERVER_URL == "http://localhost:9000"
            assert test_settings.OLLAMA_SERVER_URL == "http://localhost:11434"

    def test_custom_values_from_env(self):
        """Test settings with custom environment variables."""
        with patch.dict(os.environ, {
            "MCP_SERVER_URL": "http://custom-mcp:9000",
            "OLLAMA_SERVER_URL": "http://custom-ollama:11434"
        }, clear=True):
            test_settings = Settings()
            assert test_settings.MCP_SERVER_URL == "http://custom-mcp:9000"
            assert test_settings.OLLAMA_SERVER_URL == "http://custom-ollama:11434"

    def test_partial_env_override(self):
        """Test settings with partial environment override."""
        with patch.dict(os.environ, {
            "MCP_SERVER_URL": "http://custom-mcp:9000"
        }, clear=True):
            test_settings = Settings()
            assert test_settings.MCP_SERVER_URL == "http://custom-mcp:9000"
            assert test_settings.OLLAMA_SERVER_URL == "http://localhost:11434"

    def test_settings_instance(self):
        """Test that settings instance is created."""
        assert isinstance(settings, Settings)
        assert hasattr(settings, 'MCP_SERVER_URL')
        assert hasattr(settings, 'OLLAMA_SERVER_URL')

    def test_settings_singleton_behavior(self):
        """Test that settings instance is a singleton."""
        from chat_api.config import settings as settings2
        assert settings is settings2

    def test_settings_model_dump(self):
        """Test settings model dump."""
        test_settings = Settings()
        dumped = test_settings.model_dump()
        assert "MCP_SERVER_URL" in dumped
        assert "OLLAMA_SERVER_URL" in dumped
        assert dumped["MCP_SERVER_URL"] == "http://localhost:9000"
        assert dumped["OLLAMA_SERVER_URL"] == "http://localhost:11434"
