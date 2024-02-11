from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse

from .schemas import RequisicaoTransacao
from .services import gerar_extrato, transacionar

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("/{cliente_id}/transacoes", response_class=ORJSONResponse)
async def post_transacao(
    request: Request,
    cliente_id: int,
    transacao: RequisicaoTransacao,
):
    """Faz uma transação na conta de um cliente, creditando ou debitando o valor informado.

    Uma transação de débito nunca pode deixar o saldo do cliente menor que seu limite disponível.
    Por exemplo, um cliente com limite de 1000 (R$ 10) nunca deverá ter o saldo menor que -1000 (R$ -10).
    Nesse caso, um saldo de -1001 ou menor significa inconsistência na Rinha de Backend!
    """

    async with request.app.state.pool.acquire() as conn:
        response = await transacionar(
            conn,
            cliente_id,
            transacao,
        )
    return response


@router.get("/{cliente_id}/extrato", response_class=ORJSONResponse)
async def get_extrato(request: Request, cliente_id: int):
    """Retorna o saldo e as últimas transações de um cliente."""
    async with request.app.state.pool.acquire() as conn:
        response = await gerar_extrato(conn, cliente_id)
    return response
