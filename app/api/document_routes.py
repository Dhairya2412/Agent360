"""Document upload and knowledge base API routes."""

import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.database.repositories import document_repo
from app.utils.document_parser import chunk_text, parse_document
from app.vectorstore.ingest import delete_document_chunks, ingest_chunks

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".csv", ".md", ".markdown"}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    settings = get_settings()
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    doc_id = str(uuid4())
    safe_name = f"{doc_id}{ext}"
    file_path = upload_dir / safe_name

    try:
        content = await file.read()
        if len(content) > settings.max_upload_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_upload_size_mb}MB",
            )

        with file_path.open("wb") as f:
            f.write(content)

        text = parse_document(str(file_path), ext.lstrip("."))
        chunks = chunk_text(text)

        if not chunks:
            raise HTTPException(status_code=400, detail="No text content extracted from document")

        chunk_count = await ingest_chunks(chunks, source=file.filename or safe_name, document_id=doc_id)

        doc = await document_repo.create({
            "id": doc_id,
            "filename": file.filename,
            "file_type": ext.lstrip("."),
            "size_bytes": file_path.stat().st_size,
            "chunk_count": chunk_count,
            "status": "indexed",
            "file_path": str(file_path),
        })

        return {
            "id": doc.get("id", doc_id),
            "filename": file.filename,
            "chunk_count": chunk_count,
            "message": f"Indexed {chunk_count} chunks successfully",
        }
    except HTTPException:
        raise
    except Exception as exc:
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="Failed to process document upload") from exc


@router.get("")
async def list_documents():
    return await document_repo.list_all()


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    doc = await document_repo.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = doc.get("file_path")
    if file_path and Path(file_path).exists():
        os.remove(file_path)

    await delete_document_chunks(document_id)
    await document_repo.delete(document_id)
    return {"message": "Document deleted", "id": document_id}
