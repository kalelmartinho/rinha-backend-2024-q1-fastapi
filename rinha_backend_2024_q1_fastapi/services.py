from async_lru import alru_cache

from .core.exceptions import ClienteNaoEncontradoException, SaldoInsuficienteException
from .core.utils import utcnow
from .schemas import RequisicaoTransacao as Transacao
from .schemas import TipoTransacao


async def gerar_extrato(conn, cliente_id: int):
    stmt = (
        "SELECT c.saldo, c.limite, t.valor, t.tipo, t.descricao, t.realizada_em "
        "FROM cliente c LEFT JOIN transacao t ON c.id = t.cliente_id "
        "WHERE c.id = $1 ORDER BY t.id DESC LIMIT 10 "
    )

    rows = await conn.fetch(stmt, cliente_id)

    if not rows:
        raise ClienteNaoEncontradoException()

    extrato = {
        "saldo": {
            "total": rows[0]["saldo"],
            "limite": rows[0]["limite"],
            "data": utcnow().astimezone().isoformat(),
        },
        "ultimas_transacoes": [
            {
                "valor": row["valor"],
                "tipo": row["tipo"],
                "descricao": row["descricao"],
                "realizada_em": row["realizada_em"],
            }
            for row in rows
            if row.get("valor")
        ],
    }

    return extrato


@alru_cache(maxsize=512)
async def buscar_limite_por_cliente_id(conn, cliente_id: int) -> int:
    """Busca o limite pelo ID do cliente, cacheado já que o limite não muda."""
    stmt = "SELECT limite FROM cliente WHERE id = $1"
    limite = await conn.fetchval(stmt, cliente_id)
    if not limite:
        raise ClienteNaoEncontradoException()
    return limite


async def buscar_limite_saldo_por_cliente_id(conn, cliente_id: int) -> int:
    """Busca o saldo pelo ID do cliente, não cacheado já que o saldo muda."""
    stmt = "SELECT saldo FROM cliente WHERE id = $1 FOR UPDATE"
    saldo = await conn.fetchval(stmt, cliente_id)
    return saldo


async def gerar_transacao(
    conn,
    cliente_id: int,
    transacao: Transacao,
    novo_saldo: int,
) -> None:
    transacao_stmt = (
        "INSERT INTO transacao (cliente_id, valor, tipo, descricao) "
        "VALUES ($1, $2, $3, $4)"
    )
    cliente_stmt = "UPDATE cliente SET saldo = $1 WHERE id = $2"
    await conn.execute(cliente_stmt, novo_saldo, cliente_id)
    await conn.execute(
        transacao_stmt,
        cliente_id,
        transacao.valor,
        transacao.tipo,
        transacao.descricao,
    )


async def transacionar(
    conn,
    cliente_id: int,
    transacao: Transacao,
):
    limite = await buscar_limite_por_cliente_id(conn, cliente_id)
    async with conn.transaction():
        saldo = await buscar_limite_saldo_por_cliente_id(conn, cliente_id)

        if transacao.tipo == TipoTransacao.CREDITO:
            novo_saldo = saldo + transacao.valor
        else:
            novo_saldo = saldo - transacao.valor
            if novo_saldo < -limite:
                raise SaldoInsuficienteException()
        await gerar_transacao(conn, cliente_id, transacao, novo_saldo)
    return {"saldo": novo_saldo, "limite": limite}
