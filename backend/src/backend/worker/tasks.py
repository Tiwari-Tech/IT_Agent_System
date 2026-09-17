import asyncio
import uuid

from backend.db.database import session_scope
from backend.rag.service import ingest_document
from backend.worker.celery_app import celery_app


@celery_app.task(name="documents.ingest")
def ingest_document_task(document_id: str) -> dict[str, str | int]:
    async def run() -> int:
        async with session_scope() as session:
            return await ingest_document(session, uuid.UUID(document_id))

    return {"document_id": document_id, "chunks": asyncio.run(run())}
