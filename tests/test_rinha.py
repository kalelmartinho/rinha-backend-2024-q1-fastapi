from typing import List

import pytest
from httpx import AsyncClient

from rinha_backend_2024_q1_fastapi.models import Cliente


@pytest.mark.asyncio
async def test_api(client: AsyncClient) -> None:
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_clientes(dados_clientes: List[Cliente]) -> None:
    assert len(dados_clientes) == 5
    assert dados_clientes[0].limite == 100000
    assert dados_clientes[0].saldo == 0
    assert dados_clientes[1].limite == 80000
    assert dados_clientes[1].saldo == 0
    assert dados_clientes[2].limite == 1000000
    assert dados_clientes[2].saldo == 0
    assert dados_clientes[3].limite == 10000000
    assert dados_clientes[3].saldo == 0
    assert dados_clientes[4].limite == 500000
    assert dados_clientes[4].saldo == 0


@pytest.mark.asyncio
async def test_extrato(client: AsyncClient) -> None:
    for cliente_id in range(1, 6):
        response = await client.get(f"/clientes/{cliente_id}/extrato")
        assert response.status_code == 200
        data = response.json()
        assert "saldo" in data
        assert "ultimas_transacoes" in data


@pytest.mark.asyncio
async def test_extrato_inexistente(client: AsyncClient) -> None:
    response = await client.get("/clientes/6/extrato")
    assert response.status_code == 404
