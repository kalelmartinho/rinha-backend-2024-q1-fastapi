from contextlib import asynccontextmanager

from .database import iniciar_db
from .routes import router
from fastapi import FastAPI


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
