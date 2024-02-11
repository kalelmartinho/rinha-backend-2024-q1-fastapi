import asyncpg

from .config import settings


async def get_pool() -> asyncpg.pool.Pool:
    pool = await asyncpg.create_pool(
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        min_size=settings.DB_MIN_SIZE,
        max_size=settings.DB_MAX_SIZE,
    )
    if not pool:
        raise Exception("Could not create pool")
    return pool


async def init_db(pool: asyncpg.pool.Pool) -> None:
    if settings.TESTING:
        async with pool.acquire() as conn:
            stmt_users = """
            CREATE TABLE IF NOT EXISTS cliente (
                saldo INTEGER NOT NULL, 
                limite INTEGER NOT NULL, 
                id SERIAL NOT NULL, 
                PRIMARY KEY (id)
            );
            """
            stmt_tipo_transacao = (
                "CREATE TYPE IF NOT EXISTS tipotransacao AS ENUM ('c', 'd');"
            )
            stmt_transacao = """
            CREATE TABLE transacao IF NOT EXISTS(
                valor INTEGER NOT NULL, 
                tipo tipotransacao NOT NULL, 
                descricao VARCHAR(10) NOT NULL, 
                id SERIAL NOT NULL, 
                realizada_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP, 
                cliente_id INTEGER NOT NULL, 
                PRIMARY KEY (id), 
                FOREIGN KEY(cliente_id) REFERENCES cliente (id)
            );
            """
            stmt_constraint = """
            ALTER TABLE IF EXISTS transacao
                ADD CONSTRAINT "transacao_cliente_id_fk" FOREIGN KEY (cliente_id) REFERENCES cliente (id);
            """
            stmt_idx = "CREATE INDEX IF NOT EXISTS transacao_cliente_id_id_idx ON transacao (cliente_id, id);"
            stmt_clientes = """
            INSERT INTO cliente (id, saldo, limite)
            SELECT new_values.id, new_values.saldo, new_values.limite
            FROM (VALUES
                (1, 0, 100000),
                (2, 0, 80000),
                (3, 0, 1000000),
                (4, 0, 10000000),
                (5, 0, 500000)
            ) AS new_values (id, saldo, limite)
            LEFT JOIN cliente ON new_values.id = cliente.id
            WHERE cliente.id IS NULL;
            """

            async with conn.transaction():
                await conn.execute(stmt_tipo_transacao)
                await conn.execute(stmt_users)
                await conn.execute(stmt_transacao)
                await conn.execute(stmt_constraint)
                await conn.execute(stmt_idx)
                await conn.execute(stmt_clientes)
