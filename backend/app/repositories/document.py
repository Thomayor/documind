from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Chunk, Document, QueryHistory
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, db: Session):
        super().__init__(Document, db)


class ChunkRepository(BaseRepository[Chunk]):
    def __init__(self, db: Session):
        super().__init__(Chunk, db)

    def get_by_document(self, document_id: UUID) -> list[Chunk]:
        return (
            self.db.execute(
                select(Chunk)
                .where(Chunk.document_id == document_id)
                .order_by(Chunk.chunk_index)
            )
            .scalars()
            .all()
        )

    def similarity_search(
        self, embedding: list[float], limit: int = 5, max_distance: float = 0.5
    ) -> list[tuple[Chunk, float]]:
        distance = Chunk.embedding.cosine_distance(embedding).label("distance")
        rows = (
            self.db.execute(
                select(Chunk, distance)
                .where(Chunk.embedding.isnot(None))
                .where(func.length(Chunk.content) >= 50)
                .where(distance <= max_distance)
                .order_by(distance)
                .limit(limit)
            )
            .all()
        )
        return [(chunk, float(dist)) for chunk, dist in rows]


class HistoryRepository(BaseRepository[QueryHistory]):
    def __init__(self, db: Session):
        super().__init__(QueryHistory, db)
