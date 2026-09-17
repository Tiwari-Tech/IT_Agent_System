from langchain_ollama import OllamaEmbeddings

from backend.core.config import get_settings


def get_embeddings() -> OllamaEmbeddings:
    settings = get_settings()
    return OllamaEmbeddings(base_url=settings.ollama_base_url, model=settings.ollama_embedding_model)


async def embed_text(text: str) -> list[float]:
    try:
        return await get_embeddings().aembed_query(text)
    except Exception as exc:
        raise RuntimeError("Ollama embedding failed") from exc


async def embed_documents(texts: list[str]) -> list[list[float]]:
    try:
        return await get_embeddings().aembed_documents(texts)
    except Exception as exc:
        raise RuntimeError("Ollama batch embedding failed") from exc
