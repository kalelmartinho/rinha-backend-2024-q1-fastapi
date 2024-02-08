from typing import List

import pytest
from httpx import AsyncClient

from rinha_backend_2024_q1_fastapi.models import Cliente


@pytest.mark.asyncio
async def test_api(client: AsyncClient) -> None:
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_extrato(client: AsyncClient, dados_clientes: List[Cliente]) -> None:
    for cliente in dados_clientes:
        response = await client.get(f"/clientes/{cliente.id}/extrato")
        assert response.status_code == 200
        data = response.json()
        assert "saldo" in data
        assert "ultimas_transacoes" in data
        assert data["saldo"]["limite"] == cliente.limite
        assert data["saldo"]["total"] == cliente.saldo


@pytest.mark.asyncio
async def test_extrato_inexistente(client: AsyncClient) -> None:
    response = await client.get("/clientes/6/extrato")
    assert response.status_code == 404
