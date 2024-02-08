from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from .core.database import get_session
from .models import RequisicaoTransacao, RespostaExtrato, RespostaTransacao
from .services import gerar_extrato, transacionar

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("/{cliente_id}/transacoes", response_model=RespostaTransacao)
async def post_transacao(
    cliente_id: int,
    transacao: RequisicaoTransacao,
    session: AsyncSession = Depends(get_session),
):
    """Faz uma transação na conta de um cliente, creditando ou debitando o valor informado.

    Uma transação de débito nunca pode deixar o saldo do cliente menor que seu limite disponível.
    Por exemplo, um cliente com limite de 1000 (R$ 10) nunca deverá ter o saldo menor que -1000 (R$ -10).
    Nesse caso, um saldo de -1001 ou menor significa inconsistência na Rinha de Backend!
    """
    response = await transacionar(
        session, cliente_id, transacao.valor, transacao.tipo, transacao.descricao
    )
    return response


@router.get("/{cliente_id}/extrato", response_model=RespostaExtrato)
async def get_extrato(cliente_id: int, session: AsyncSession = Depends(get_session)):
    """Retorna o saldo e as últimas transações de um cliente."""
    response = await gerar_extrato(session, cliente_id)
    return response
