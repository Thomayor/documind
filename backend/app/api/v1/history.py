from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.document import HistoryRepository
from app.schemas.document import QueryHistoryOut

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/", response_model=list[QueryHistoryOut])
def list_history(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return HistoryRepository(db).get_all(skip=skip, limit=limit)
