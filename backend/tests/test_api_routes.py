from fastapi.testclient import TestClient

from backend.ai.embeddings import get_embeddings
from backend.ai.llm import get_llm
from backend.main import app


def test_user_and_ticket_routes_registered() -> None:
    client = TestClient(app)

    assert client.get("/api/v1/users/me").status_code == 401
    assert client.get("/api/v1/users/00000000-0000-0000-0000-000000000000").status_code == 401
    assert client.get("/api/v1/tickets").status_code == 401
    assert client.get("/api/v1/tickets/00000000-0000-0000-0000-000000000000").status_code == 401


def test_ollama_factories_do_not_call_network() -> None:
    assert get_llm().model == "gemma3:4b"
    assert get_embeddings().model == "bge-m3"
