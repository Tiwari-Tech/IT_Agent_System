from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.auth import router as auth_router
from backend.api.routes.documents import router as documents_router
from backend.api.routes.health import router as health_router
from backend.api.routes.jira import router as jira_router
from backend.api.routes.tickets import router as tickets_router
from backend.api.routes.users import router as users_router
from backend.api.routes.workflows import router as workflows_router
from backend.api.routes.ws import router as ws_router
from backend.core.config import get_settings
from backend.core.errors import install_error_handlers
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
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
install_error_handlers(app)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tickets_router)
app.include_router(documents_router)
app.include_router(jira_router)
app.include_router(workflows_router)
app.include_router(ws_router)
app.include_router(health_router)
