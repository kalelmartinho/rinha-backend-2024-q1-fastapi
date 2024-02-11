from enum import Enum

from pydantic import BaseModel, Field, PositiveInt


class TipoTransacao(str, Enum):
    """Enum de tipo de transação"""

    CREDITO = "c"
    DEBITO = "d"


class RequisicaoTransacao(BaseModel):
    valor: PositiveInt
    tipo: TipoTransacao
    descricao: str = Field(..., min_length=1, max_length=10)
