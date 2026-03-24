"""Database infrastructure."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional, Type

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import DeclarativeBase

from infrastructure.config import get_config

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""
    pass


class DatabaseManager:
    """Database connection manager."""
    
    def __init__(self, database_url: Optional[str] = None) -> None:
        self.database_url = database_url or get_config().database.url
        self._engine = None
        self._session_factory = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize database connection."""
        if self._initialized:
            return
        
        self._engine = create_async_engine(
            self.database_url,
            echo=get_config().database.echo,
            poolclass=NullPool,
        )
        
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        self._initialized = True
        logger.info(f"Database initialized: {self.database_url}")
    
    async def close(self) -> None:
        """Close database connection."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            self._initialized = False
            logger.info("Database connection closed")
    
    async def create_tables(self) -> None:
        """Create all tables."""
        if not self._initialized:
            await self.initialize()
        
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")
    
    async def drop_tables(self) -> None:
        """Drop all tables."""
        if not self._initialized:
            await self.initialize()
        
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped")
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session context manager."""
        if not self._initialized:
            await self.initialize()
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    def get_session(self) -> AsyncSession:
        """Get a database session (for dependency injection)."""
        if not self._initialized:
            raise RuntimeError("Database not initialized")
        return self._session_factory()
    
    async def execute_raw(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute raw SQL query."""
        async with self.session() as session:
            result = await session.execute(text(query), params or {})
            return result
    
    async def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> None:
        """Execute raw SQL query with multiple parameter sets."""
        async with self.session() as session:
            for params in params_list:
                await session.execute(text(query), params)
    
    async def health_check(self) -> bool:
        """Check database health."""
        try:
            async with self.session() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def set_db_manager(manager: DatabaseManager) -> None:
    """Set the global database manager instance."""
    global _db_manager
    _db_manager = manager


async def get_db() -> AsyncSession:
    """Get database session (for FastAPI dependency injection)."""
    manager = get_db_manager()
    if not manager._initialized:
        await manager.initialize()
    return manager.get_session()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with context manager."""
    async with get_db_manager().session() as session:
        yield session
