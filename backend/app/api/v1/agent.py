from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.document import ChunkRepository
from app.rag.agent import agent
from app.schemas.document import AskRequest, AskResponse, SourceOut

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/ask", response_model=AskResponse)
def agent_ask(body: AskRequest, db: Session = Depends(get_db)):
    chunk_repo = ChunkRepository(db)
    result = agent.invoke({
        "question": body.question,
        "document_id": str(body.document_id) if body.document_id else None,
        "chunks": [],
        "web_results": [],
        "answer": "",
        "sources": [],
        "source_type": "none",
        "_chunk_repo": chunk_repo,
    })
    sources = [SourceOut(**s) for s in result["sources"]]
    return AskResponse(answer=result["answer"], sources=sources)
