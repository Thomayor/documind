import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.document import ChunkRepository
from app.rag.agent import agent
from app.schemas.document import AskRequest, AskResponse, SourceOut

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/ask", response_model=AskResponse)
def agent_ask(body: AskRequest, db: Session = Depends(get_db)):
    from app.main import rag_requests_total, rag_latency_seconds

    chunk_repo = ChunkRepository(db)
    t0 = time.time()

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

    rag_latency_seconds.observe(time.time() - t0)
    rag_requests_total.labels(source_type=result["source_type"]).inc()

    sources = [SourceOut(**s) for s in result["sources"]]
    return AskResponse(answer=result["answer"], sources=sources)
