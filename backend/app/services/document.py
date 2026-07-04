import logging
import sys

from sqlalchemy.orm import Session

from app.models.document import Chunk, Document
from app.parsers import get_parser
from app.rag.chunker import RecursiveChunker
from app.rag.embedder import embedder
from app.repositories.document import ChunkRepository, DocumentRepository

logger = logging.getLogger(__name__)
BATCH_SIZE = 32


class DocumentService:
    def __init__(self, db: Session):
        self.doc_repo = DocumentRepository(db)
        self.chunk_repo = ChunkRepository(db)
        self.chunker = RecursiveChunker()

    def ingest(self, filename: str, content_type: str, file_bytes: bytes) -> Document:
        try:
            print(f"[ingest] parsing {filename} ({len(file_bytes)} bytes)")
            parser = get_parser(content_type)
            pages = parser.parse(file_bytes)

            document = Document(filename=filename, content_type=content_type)
            self.doc_repo.db.add(document)
            self.doc_repo.db.flush()

            all_chunks = []
            for text, page_number in pages:
                all_chunks.extend(self.chunker.chunk(text, page_number))

            print(f"[ingest] {len(all_chunks)} chunks, embedding in batches of {BATCH_SIZE}")

            for batch_start in range(0, len(all_chunks), BATCH_SIZE):
                batch = all_chunks[batch_start:batch_start + BATCH_SIZE]
                texts = [c["content"] for c in batch]
                embeddings = embedder.embed_batch(texts)
                print(f"[ingest] batch {batch_start}-{batch_start+len(batch)} embedded")

                for i, (chunk_data, embedding) in enumerate(zip(batch, embeddings)):
                    self.doc_repo.db.add(
                        Chunk(
                            document_id=document.id,
                            content=chunk_data["content"],
                            page_number=chunk_data["page_number"],
                            chunk_index=batch_start + i,
                            embedding=embedding,
                        )
                    )

            self.doc_repo.db.commit()
            self.doc_repo.db.refresh(document)
            print(f"[ingest] done — document {document.id}")
            return document

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.doc_repo.db.rollback()
            raise
