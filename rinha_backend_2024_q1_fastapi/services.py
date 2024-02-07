from pydantic.types import PositiveInt
from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .exceptions import ClienteNaoEncontradoException, SaldoInsuficienteException
from .models import (
    Cliente,
    RespostaExtrato,
    TipoTransacao,
    Transacao,
)


async def buscar_cliente_por_id(session: AsyncSession, id: int) -> Cliente:
    query = select(Cliente).where(Cliente.id == id)
    resultado = await session.exec(query)
    cliente = resultado.one_or_none()
    if not cliente or not cliente.id:
        raise ClienteNaoEncontradoException()
    return cliente


async def gerar_extrato(session: AsyncSession, cliente_id: int) -> RespostaExtrato:
    query = (
        select(Cliente)
        .options(joinedload(Cliente.ultimas_transacoes))  # type: ignore
        .where(Cliente.id == cliente_id)
    )
    resultado = await session.exec(query)
    cliente = resultado.unique().one_or_none()

    if not cliente:
        raise ClienteNaoEncontradoException()

    return RespostaExtrato(
        saldo=cliente,
        ultimas_transacoes=cliente.ultimas_transacoes,  # type: ignore
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
    await session.refresh(cliente)
    return cliente
