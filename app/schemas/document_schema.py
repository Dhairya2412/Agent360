"""Document upload and metadata schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    id: str
    filename: str
    file_type: str
    size_bytes: int
    chunk_count: int
    status: str
    created_at: datetime


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    chunk_count: int
    message: str
