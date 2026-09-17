import uuid

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies.auth import get_current_user
from backend.db.database import get_session
from backend.db.models.document import Document
from backend.db.models.user import User
from backend.rag.service import ingest_document, list_documents, save_upload
from backend.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
    IngestResponse,
)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Document:
    return await save_upload(session, file)


@router.post("/{document_id}/ingest", response_model=IngestResponse)
async def ingest(document_id: uuid.UUID, _: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> IngestResponse:
    return IngestResponse(document_id=document_id, chunks=await ingest_document(session, document_id))


@router.get("", response_model=DocumentListResponse)
async def documents(_: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> DocumentListResponse:
    return DocumentListResponse(items=await list_documents(session))


@router.get("/{document_id}", response_model=DocumentResponse)
async def document(document_id: uuid.UUID, _: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> Document:
    doc = await session.get(Document, document_id)
    if doc is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Document not found")
    return doc
