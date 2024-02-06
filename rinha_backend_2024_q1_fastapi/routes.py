from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from .database import get_session
from .models import RequisicaoTransacao, RespostaExtrato, RespostaTransacao
from .services import gerar_extrato, transacionar

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("/{cliente_id}/transacoes", response_model=RespostaTransacao)
async def post_transacao(
    cliente_id: int,
    transacao: RequisicaoTransacao,
    session: AsyncSession = Depends(get_session),
):
    response = await transacionar(
        session, cliente_id, transacao.valor, transacao.tipo, transacao.descricao
    )
    return response


@router.get("/{cliente_id}/extrato", response_model=RespostaExtrato)
async def get_extrato(cliente_id: int, session: AsyncSession = Depends(get_session)):
    response = await gerar_extrato(session, cliente_id)
    return response
