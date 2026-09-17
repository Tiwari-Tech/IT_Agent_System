from langchain_ollama import ChatOllama
from pydantic import BaseModel

from backend.core.config import get_settings


def get_llm(*, temperature: float = 0.2) -> ChatOllama:
    settings = get_settings()
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_llm_model,
        temperature=temperature,
        timeout=settings.ollama_timeout_seconds,
    )


async def generate_text(prompt: str, *, temperature: float = 0.2) -> str:
    try:
        response = await get_llm(temperature=temperature).ainvoke(prompt)
    except Exception as exc:
        raise RuntimeError("Ollama text generation failed") from exc
    return str(response.content)


async def generate_structured(prompt: str, schema: type[BaseModel], *, temperature: float = 0.2) -> BaseModel:
    try:
        return await get_llm(temperature=temperature).with_structured_output(schema).ainvoke(prompt)
    except Exception as exc:
        raise RuntimeError("Ollama structured generation failed") from exc
