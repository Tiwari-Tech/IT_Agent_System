from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes.health import router as health_router
from backend.core.logging import configure_logging
from backend.db.database import close_database
from backend.db.redis import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    yield
    await close_database()
    await close_redis()


app = FastAPI(
    title="IT_Agent_System Backend",
    version="0.1.0",
    description="Backend foundation for IT operations automation.",
    lifespan=lifespan,
)
app.include_router(health_router)
