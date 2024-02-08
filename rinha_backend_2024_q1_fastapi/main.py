from contextlib import asynccontextmanager

from fastapi import FastAPI

from .core.database import iniciar_db
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await iniciar_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)


def start_server():
    import uvicorn

    uvicorn.run(
        "rinha_backend_2024_q1_fastapi.main:app", host="0.0.0.0", port=8000, reload=True
    )
