import datetime


def utcnow() -> datetime.datetime:
    """Retorna a data e hora atual em UTC."""
    return datetime.datetime.now(datetime.UTC)
