import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.document import ChunkRepository
from app.rag.agent import agent
from app.schemas.document import AskRequest, AskResponse, SourceOut
from app.core.tracing import get_langfuse

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/ask", response_model=AskResponse)
def agent_ask(body: AskRequest, db: Session = Depends(get_db)):
    from app.main import rag_requests_total, rag_latency_seconds

    chunk_repo = ChunkRepository(db)
    t0 = time.time()

    # Trace LangFuse (no-op si non configuré)
    lf = get_langfuse()
    trace = lf.trace(
        name="rag-agent",
        input={"question": body.question, "document_id": str(body.document_id)},
    ) if lf else None

    # Span retrieve
    span_retrieve = trace.span(name="retrieve") if trace else None
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
    if span_retrieve:
        span_retrieve.end(output={"chunks_found": len(result["chunks"]), "source_type": result["source_type"]})

    duration = time.time() - t0
    rag_latency_seconds.observe(duration)
    rag_requests_total.labels(source_type=result["source_type"]).inc()

    # Finalise la trace
    if trace:
        trace.update(
            output={"answer": result["answer"][:200], "source_type": result["source_type"]},
            metadata={"duration_seconds": round(duration, 2)},
        )
        lf.flush()

    sources = [SourceOut(**s) for s in result["sources"]]
    return AskResponse(answer=result["answer"], sources=sources)
