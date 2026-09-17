import httpx

from backend.core.config import get_settings


async def check_ollama() -> bool:
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=settings.ollama_timeout_seconds) as client:
            response = await client.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags")
            response.raise_for_status()
    except Exception as exc:
        raise RuntimeError("Ollama unavailable") from exc
    return True
