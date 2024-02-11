from contextlib import asynccontextmanager

from fastapi import FastAPI

from .core.database import get_pool
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.pool = await get_pool()
        # await init_db(app.state.pool)
        yield
    finally:
        await app.state.pool.close()


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
app.include_router(router)
