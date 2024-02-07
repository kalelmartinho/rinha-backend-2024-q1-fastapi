from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from rinha_backend_2024_q1_fastapi.database import dados_simulacao, get_session
from rinha_backend_2024_q1_fastapi.main import app

engine = create_async_engine("sqlite+aiosqlite:///:memory:")


async def create_tabelas():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def drop_tabelas():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        yield session

        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
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


@pytest.fixture(scope="function", autouse=True)
async def criar_dados_para_testes(session: AsyncSession) -> None:
    clientes = dados_simulacao()
    session.add_all(clientes)
    await session.commit()
