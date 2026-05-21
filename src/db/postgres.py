"""
PostgreSQL async connection via SQLAlchemy + asyncpg.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.core.config import get_settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


# ── Engine & session factory (created lazily) ───────────

_engine = None
_session_factory = None


def _get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_size=5,
            max_overflow=10,
        )
        logger.info("Created async PostgreSQL engine")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the async session factory (creates engine on first call)."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            _get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def init_db() -> None:
    """Create all tables (call once at startup)."""
    # Import models so they're registered on Base.metadata
    import src.auth.models  # noqa: F401

    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created / verified")


async def close_db() -> None:
    """Dispose engine (call at shutdown)."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database engine disposed")
