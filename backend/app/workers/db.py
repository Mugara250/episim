"""Async DB access for Celery tasks.

Each task run gets a fresh NullPool engine: asyncpg connections are bound to the
event loop that created them, and `asyncio.run()` in a prefork worker spins up a
new loop per call, so a pooled connection from a previous run would be unusable.
"""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings


@asynccontextmanager
async def worker_session() -> AsyncIterator:
    engine = create_async_engine(settings.database_url, poolclass=NullPool)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with maker() as session:
            yield session
    finally:
        await engine.dispose()
