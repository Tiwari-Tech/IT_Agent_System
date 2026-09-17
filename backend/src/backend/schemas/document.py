import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    source: str | None
    file_type: str | None
    storage_path: str | None
    content_hash: str | None
    metadata_: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]


class IngestResponse(BaseModel):
    document_id: uuid.UUID
    chunks: int


class RetrievedChunk(BaseModel):
    document_id: uuid.UUID
    chunk_id: uuid.UUID
    title: str
    content: str
    score: float
    source: str | None
    page: int | None
    chunk_index: int
