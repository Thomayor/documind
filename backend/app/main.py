from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.documents import router as documents_router
from app.api.v1.history import router as history_router
from app.api.v1.qa import router as qa_router
from app.core.config import settings
from app.core.exceptions import unhandled_exception_handler
from app.core.logging import setup_logging
from app.core.middleware import LoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(debug=settings.DEBUG)
    from app.rag.embedder import embedder
    embedder.model  # charge le modèle au démarrage
    yield


app = FastAPI(title="DocuMind", version="0.1.0", debug=settings.DEBUG, lifespan=lifespan)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(documents_router, prefix="/api/v1")
app.include_router(qa_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "debug": settings.DEBUG}
