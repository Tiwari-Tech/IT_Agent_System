import hashlib
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai.embeddings import embed_documents, embed_text
from backend.core.config import get_settings
from backend.db.models.document import Document, DocumentChunk
from backend.rag.chunking import chunk_text
from backend.rag.extractors import extract_text
from backend.schemas.document import RetrievedChunk

ALLOWED_TYPES = {"pdf", "docx", "xlsx", "html", "htm", "txt"}


async def save_upload(session: AsyncSession, upload: UploadFile) -> Document:
    suffix = Path(upload.filename or "").suffix.lower().lstrip(".")
    if suffix not in ALLOWED_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")
    content = await upload.read()
    digest = hashlib.sha256(content).hexdigest()
    existing = await session.scalar(select(Document).where(Document.content_hash == digest))
    if existing:
        return existing

    storage = Path(get_settings().document_storage_dir)
    storage.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}.{suffix}"
    path = storage / filename
    path.write_bytes(content)
    doc = Document(
        title=upload.filename or filename,
        source=upload.filename,
        file_type=suffix,
        storage_path=str(path),
        content_hash=digest,
        metadata_={"size": len(content)},
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return doc


async def ingest_document(session: AsyncSession, document_id: uuid.UUID) -> int:
    document = await session.get(Document, document_id)
    if document is None or not document.storage_path or not document.file_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    text, metadata = extract_text(Path(document.storage_path), document.file_type)
    settings = get_settings()
    chunks = chunk_text(text, size=settings.rag_chunk_size, overlap=settings.rag_chunk_overlap)
    if not chunks:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No text extracted")
    vectors = await embed_documents(chunks)
    for index, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True)):
        session.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                embedding=vector,
                source=document.source,
                metadata_=metadata,
            )
        )
    await session.commit()
    return len(chunks)


async def list_documents(session: AsyncSession) -> list[Document]:
    return list(await session.scalars(select(Document).order_by(Document.created_at.desc())))


async def retrieve(session: AsyncSession, query: str, *, top_k: int | None = None) -> list[RetrievedChunk]:
    vector = await embed_text(query)
    distance = DocumentChunk.embedding.cosine_distance(vector).label("distance")
    rows = await session.execute(
        select(DocumentChunk, Document, distance)
        .join(Document, Document.id == DocumentChunk.document_id)
        .order_by(distance)
        .limit(top_k or get_settings().rag_top_k)
    )
    return [
        RetrievedChunk(
            document_id=document.id,
            chunk_id=chunk.id,
            title=document.title,
            content=chunk.content,
            score=float(distance_value),
            source=chunk.source,
            page=chunk.page,
            chunk_index=chunk.chunk_index,
        )
        for chunk, document, distance_value in rows
    ]
