from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document import QueryHistory
from app.rag.embedder import embedder
from app.rag.generator import generator, prompt_builder
from app.repositories.document import ChunkRepository, HistoryRepository


class QAService:
    def __init__(self, db: Session):
        self.chunk_repo = ChunkRepository(db)
        self.history_repo = HistoryRepository(db)
        self.db = db

    def ask(self, question: str, document_id: UUID | None = None) -> dict:
        query_vec = embedder.embed_query(question)
        chunks = self.chunk_repo.similarity_search(query_vec, limit=5)

        if document_id:
            chunks = [(c, d) for c, d in chunks if c.document_id == document_id]

        if not chunks:
            return {
                "answer": "Je n'ai pas trouvé de contexte pertinent pour répondre à cette question.",
                "sources": [],
            }

        prompt = prompt_builder.build(question, chunks)
        answer = generator.generate(prompt, max_new_tokens=512)

        self.history_repo.create(
            QueryHistory(
                question=question,
                answer=answer,
                document_id=document_id,
            )
        )

        sources = [
            {"page_number": chunk.page_number, "preview": chunk.content[:150]}
            for chunk, _ in chunks
        ]

        return {"answer": answer, "sources": sources}
