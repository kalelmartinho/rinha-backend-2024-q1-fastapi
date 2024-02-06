from enum import Enum

from fastapi import HTTPException, status


class MensagemErro(str, Enum):
    CLIENTE_NAO_ENCONTRADO = "Cliente não encontrado"
    SALDO_INSUFICIENTE = "A transação não pode ser realizada por saldo insuficiente"


class BaseException(HTTPException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DETAIL = "Erro genérico"

    def __init__(self, **kwargs):
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL, **kwargs)


class SaldoInsuficienteException(BaseException):
    STATUS_CODE = status.HTTP_422_UNPROCESSABLE_ENTITY
    DETAIL = MensagemErro.SALDO_INSUFICIENTE


class ClienteNaoEncontradoException(BaseException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DETAIL = MensagemErro.CLIENTE_NAO_ENCONTRADO
