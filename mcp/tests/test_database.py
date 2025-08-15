import os
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from mcp_api.datbase import Base, _build_db_url, DATABASE_URL, engine, SessionLocal, get_db


class TestDatabase:
    """Test the database module."""

    def test_base_class(self):
        """Test that Base class is properly defined."""
        assert Base.__name__ == "Base"
        assert hasattr(Base, 'metadata')

    def test_build_db_url_with_existing_url(self, monkeypatch):
        """Test _build_db_url with existing DATABASE_URL."""
        test_url = "postgresql://user:pass@host:5432/db"
        monkeypatch.setenv("DATABASE_URL", test_url)
        result = _build_db_url()
        assert result == "postgresql+asyncpg://user:pass@host:5432/db"

    def test_build_db_url_postgresql_normalization(self, monkeypatch):
        """Test _build_db_url normalizes postgresql:// to postgresql+asyncpg://."""
        test_url = "postgresql://user:pass@host:5432/db"
        monkeypatch.setenv("DATABASE_URL", test_url)
        result = _build_db_url()
        assert result == "postgresql+asyncpg://user:pass@host:5432/db"

    def test_build_db_url_postgresql_psycopg2_normalization(self, monkeypatch):
        """Test _build_db_url normalizes postgresql+psycopg2:// to postgresql+asyncpg://."""
        test_url = "postgresql+psycopg2://user:pass@host:5432/db"
        monkeypatch.setenv("DATABASE_URL", test_url)
        result = _build_db_url()
        assert result == "postgresql+asyncpg://user:pass@host:5432/db"

    def test_build_db_url_other_urls(self, monkeypatch):
        """Test _build_db_url returns other URLs unchanged."""
        test_url = "sqlite:///test.db"
        monkeypatch.setenv("DATABASE_URL", test_url)
        result = _build_db_url()
        assert result == test_url

    def test_build_db_url_default_postgres(self, monkeypatch):
        """Test _build_db_url defaults to PostgreSQL when no DATABASE_URL is set."""
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("PGUSER", raising=False)
        monkeypatch.delenv("PGPASSWORD", raising=False)
        monkeypatch.delenv("PGHOST", raising=False)
        monkeypatch.delenv("PGPORT", raising=False)
        monkeypatch.delenv("PGDATABASE", raising=False)
        result = _build_db_url()
        assert result == "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/products"

    def test_database_url_constant(self):
        """Test that DATABASE_URL is properly set."""
        assert DATABASE_URL is not None
        assert isinstance(DATABASE_URL, str)

    def test_engine_creation(self):
        """Test that engine is properly created."""
        assert engine is not None
        assert hasattr(engine, 'begin')

    def test_session_local_creation(self):
        """Test that SessionLocal is properly created."""
        assert SessionLocal is not None
        assert hasattr(SessionLocal, '__call__')

    @pytest.mark.asyncio
    async def test_get_db_generator(self):
        """Test that get_db is a proper async generator."""
        db_gen = get_db()
        assert hasattr(db_gen, '__anext__')
        
        # Test that it yields an AsyncSession
        session = await db_gen.__anext__()
        assert isinstance(session, AsyncSession)
        
        # Clean up
        try:
            await db_gen.__anext__()
        except StopAsyncIteration:
            pass

    def test_base_metadata(self):
        """Test that Base has metadata for table creation."""
        assert hasattr(Base, 'metadata')
        assert hasattr(Base.metadata, 'create_all')
