from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from rinha_backend_2024_q1_fastapi.core.database import get_session
from rinha_backend_2024_q1_fastapi.main import app
from rinha_backend_2024_q1_fastapi.models import Cliente

engine = create_async_engine("sqlite+aiosqlite:///:memory:")


async def criar_tabelas():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


@pytest_asyncio.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        await criar_tabelas()

        yield session

    await engine.dispose()


@pytest.fixture(scope="function")
def test_session(session: AsyncSession):
    async def get_test_session():
        yield session

    return get_test_session


@pytest_asyncio.fixture
async def client(test_session) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP asyncrono para testes."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        app.dependency_overrides[get_session] = test_session
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function", autouse=True)
async def dados_clientes(session: AsyncSession) -> AsyncGenerator[list, None]:
    clientes = [
        Cliente(id=1, limite=100000, saldo=0),
        Cliente(id=2, limite=80000, saldo=0),
        Cliente(id=3, limite=1000000, saldo=0),
        Cliente(id=4, limite=10000000, saldo=0),
        Cliente(id=5, limite=500000, saldo=0),
    ]
    session.add_all(clientes)
    await session.commit()
    yield clientes
