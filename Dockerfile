FROM python:3.12-slim-bookworm


RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    apt clean && \
    rm -rf /var/cache/apt/* && \
    pip install poetry==1.7.0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

COPY pyproject.toml poetry.lock ./

COPY rinha_backend_2024_q1_fastapi ./rinha_backend_2024_q1_fastapi

RUN touch README.md && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-root && rm -rf $POETRY_CACHE_DIR

COPY --chown=app:app ./rinha_backend_2024_q1_fastapi /rinha_backend_2024_q1_fastapi


ENV DB_HOST=postgres

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "rinha_backend_2024_q1_fastapi.main:app", "--host", "0.0.0.0", "--port", "8000"]

 
