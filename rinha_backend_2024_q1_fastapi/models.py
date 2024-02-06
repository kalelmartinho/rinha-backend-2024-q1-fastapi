from sqlmodel import Column, DateTime, SQLModel, Field, Relationship
from datetime import datetime
from enum import Enum
from typing import Optional, List
from .utils import utcnow
from pydantic import PositiveInt


class TipoTransacao(str, Enum):
    """Enum de tipo de transação"""

    CREDITO = "c"
    DEBITO = "d"


# Modelos Base


class TransacaoBase(SQLModel):
    valor: PositiveInt
    tipo: TipoTransacao
    descricao: str = Field(..., max_length=10)


class SaldoBase(SQLModel):
    saldo: int
    limite: int


class SaldoExtrato(SaldoBase):
    data_extrato: datetime = utcnow()


class TransacaoExtrato(TransacaoBase):
    realizada_em: datetime


# Schemas


class RequisicaoTransacao(TransacaoBase):
    """Schema de requisição de transação"""

    pass


class RespostaTransacao(SaldoBase):
    """Schema de resposta de transação"""

    pass


class RespostaExtrato(SQLModel):
    """Schema de resposta de extrato"""

    saldo: SaldoExtrato
    ultimas_transacoes: List[TransacaoExtrato]


# Tabelas


class Transacao(TransacaoBase, table=True):
    """Tabela de transações"""

    id: Optional[int] = Field(default=None, primary_key=True)
    realizada_em: datetime = Field(
        default_factory=utcnow, sa_column=Column(DateTime(timezone=True))
    )

    cliente_id: int = Field(foreign_key="cliente.id")
    cliente: "Cliente" = Relationship(back_populates="ultimas_transacoes")


class Cliente(SaldoBase, table=True):
    """Tabela cliente"""

    id: Optional[int] = Field(default=None, primary_key=True)
    ultimas_transacoes: List[Transacao] = Relationship(back_populates="cliente")