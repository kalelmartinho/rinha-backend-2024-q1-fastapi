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
    """Testa se o cadastro inicial de clientes está correto."""
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
    """Testa se a rota de extrato está funcionando corretamente."""
    response = await client.get("/clientes/1/extrato")
    assert response.status_code == 200
    data = response.json()
    assert "saldo" in data
    assert "ultimas_transacoes" in data


@pytest.mark.asyncio
async def test_extrato_inexistente(client: AsyncClient) -> None:
    """Testa se a rota de extrato retorna 404 para cliente inexistente."""
    response = await client.get("/clientes/6/extrato")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_transacao_credito(client: AsyncClient) -> None:
    """Testa se a rota de transação de crédito está funcionando corretamente."""
    payload = {"valor": 1000, "tipo": "c", "descricao": "descricao"}
    response = await client.post("/clientes/1/transacoes", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "limite" in data
    assert data["saldo"] == payload["valor"]


@pytest.mark.asyncio
async def test_transacao_debito(client: AsyncClient) -> None:
    """Testa se a rota de transação de débito está funcionando corretamente."""
    payload = {"valor": 1000, "tipo": "d", "descricao": "descricao"}
    response = await client.post("/clientes/1/transacoes", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "limite" in data
    assert data["saldo"] == -1000


@pytest.mark.asyncio
async def test_transacao_inexistente(client: AsyncClient) -> None:
    """Testa se a rota de transação retorna 404 para cliente inexistente."""
    payload = {"valor": 1000, "tipo": "c", "descricao": "descricao"}
    response = await client.post("/clientes/6/transacoes", json=payload)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_transacao_descricao_longa(client: AsyncClient) -> None:
    """Testa se a rota de transação retorna 422 para descrição maior que 10 caracteres."""
    payload = {"valor": 1000, "tipo": "c", "descricao": "a" * 11}
    response = await client.post("/clientes/1/transacoes", json=payload)
    assert response.status_code == 422
