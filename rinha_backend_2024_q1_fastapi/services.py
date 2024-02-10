from pydantic.types import PositiveInt
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from .core.exceptions import ClienteNaoEncontradoException, SaldoInsuficienteException
from .models import (
    Cliente,
    RespostaExtrato,
    TipoTransacao,
    Transacao,
)


async def buscar_cliente_por_id(session: AsyncSession, id: int) -> Cliente:
    cliente = await session.get(Cliente, id)
    if not cliente:
        raise ClienteNaoEncontradoException()
    return cliente


async def gerar_extrato(session: AsyncSession, cliente_id: int) -> RespostaExtrato:
    cliente = await buscar_cliente_por_id(session, cliente_id)
    stmt = (
        select(Transacao)
        .where(Transacao.cliente_id == cliente_id)
        .order_by(desc(Transacao.id))
        .limit(10)
    )
    result = await session.exec(stmt)
    ultimas_transacoes = result.all()
    if not cliente:
        raise ClienteNaoEncontradoException()
    return RespostaExtrato(
        saldo=cliente,
        ultimas_transacoes=ultimas_transacoes,  # type: ignore
    )


async def transacionar(
    session: AsyncSession,
    cliente_id: int,
    valor: PositiveInt,
    tipo: TipoTransacao,
    descricao: str,
) -> Cliente:
    cliente = await buscar_cliente_por_id(session, cliente_id)
    cliente_id = cliente.id or 0

    if tipo == TipoTransacao.CREDITO:
        cliente.saldo += valor
    else:
        if cliente.saldo - valor < -cliente.limite:
            raise SaldoInsuficienteException()
        cliente.saldo -= valor

    transacao = Transacao(
        cliente_id=cliente_id, valor=valor, tipo=tipo, descricao=descricao
    )

    session.add(transacao)
    await session.commit()
    return cliente
