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
