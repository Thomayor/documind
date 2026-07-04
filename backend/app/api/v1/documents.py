from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.document import DocumentRepository
from app.schemas.document import DocumentOut, SummaryOut
from app.services.document import DocumentService
from app.services.summary import SummaryService

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.post("/", response_model=DocumentOut, status_code=201)
async def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Type de fichier non supporté")

    file_bytes = await file.read()
    service = DocumentService(db)
    document = service.ingest(file.filename, file.content_type, file_bytes)
    return document


@router.get("/", response_model=list[DocumentOut])
def list_documents(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    repo = DocumentRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{document_id}/summary", response_model=SummaryOut)
def get_summary(document_id: UUID, db: Session = Depends(get_db)):
    result = SummaryService(db).summarize(document_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Document introuvable")
    return result


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: UUID, db: Session = Depends(get_db)):
    repo = DocumentRepository(db)
    document = repo.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document introuvable")
    repo.delete(document)
