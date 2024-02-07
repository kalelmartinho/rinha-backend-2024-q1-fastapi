from typing import AsyncGenerator, List

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from .config import settings
from .models import Cliente

engine: AsyncEngine = create_async_engine(settings.DB_URL)


def dados_simulacao() -> List[Cliente]:
    return [
        Cliente(id=1, limite=100000, saldo=0),
        Cliente(id=2, limite=80000, saldo=0),
        Cliente(id=3, limite=1000000, saldo=0),
        Cliente(id=4, limite=10000000, saldo=0),
        Cliente(id=5, limite=500000, saldo=0),
    ]


async def iniciar_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine) as session:
        async with session.begin():
            clientes: List[Cliente] = dados_simulacao()
            session.add_all(clientes)


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
