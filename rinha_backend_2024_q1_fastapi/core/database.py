from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from .config import settings

engine: AsyncEngine = create_async_engine(
    settings.DB_URL, pool_size=settings.DB_POOL, max_overflow=settings.DB_OVERFLOW
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        try:
            yield session
        except:  # noqa
            await session.rollback()
        finally:
            await session.close()
