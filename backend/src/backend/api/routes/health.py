from fastapi import APIRouter, HTTPException, status

from backend.db.database import check_database
from backend.db.redis import check_redis

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "IT_Agent_System"}


@router.get("/db")
async def database_health() -> dict[str, str]:
    try:
        await check_database()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "service": "database", "error": exc.__class__.__name__},
        ) from exc
    return {"status": "ok", "service": "database"}


@router.get("/redis")
async def redis_health() -> dict[str, str]:
    try:
        await check_redis()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "service": "redis", "error": exc.__class__.__name__},
        ) from exc
    return {"status": "ok", "service": "redis"}
