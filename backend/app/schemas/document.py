import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    filename: str
    content_type: str
    created_at: datetime


class ChunkOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    document_id: uuid.UUID
    content: str
    page_number: int | None
    chunk_index: int


class AskRequest(BaseModel):
    question: str
    document_id: uuid.UUID | None = None


class SourceOut(BaseModel):
    page_number: int | None = None
    preview: str
    origin: str = "document"
    url: str | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceOut]


class SummaryOut(BaseModel):
    document_id: str
    filename: str
    summary: str
    key_concepts: list[str]


class QueryHistoryCreate(BaseModel):
    question: str
    answer: str
    document_id: uuid.UUID | None = None


class QueryHistoryOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    question: str
    answer: str
    document_id: uuid.UUID | None
    created_at: datetime
