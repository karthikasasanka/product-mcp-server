import os
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class Base(DeclarativeBase):
    pass


def _build_db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        # Normalize to async driver if sync URL provided
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url.startswith("postgresql+psycopg2://"):
            return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
        return url
    # Default to Postgres on localhost if not provided
    user = os.getenv("PGUSER", "postgres")
    password = os.getenv("PGPASSWORD", "postgres")
    host = os.getenv("PGHOST", "127.0.0.1")
    port = os.getenv("PGPORT", "5432")
    dbname = os.getenv("PGDATABASE", "products")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"


DATABASE_URL = _build_db_url()

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False, autocommit=False)


async def get_db():
    async with SessionLocal() as session:
        yield session


