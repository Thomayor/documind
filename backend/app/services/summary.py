from uuid import UUID

from sqlalchemy.orm import Session

from app.rag.generator import generator
from app.repositories.document import ChunkRepository, DocumentRepository


class SummaryService:
    def __init__(self, db: Session):
        self.doc_repo = DocumentRepository(db)
        self.chunk_repo = ChunkRepository(db)

    def summarize(self, document_id: UUID) -> dict:
        document = self.doc_repo.get(document_id)
        if not document:
            return None

        chunks = self.chunk_repo.get_by_document(document_id)
        if not chunks:
            return {"summary": "Aucun contenu disponible.", "key_concepts": []}

        # on prend les 5 premiers chunks pour avoir le contexte général
        sample = chunks[:5]
        context = "\n\n".join(c.content for c in sample)

        prompt = (
            f"Voici le début d'un document intitulé \"{document.filename}\".\n\n"
            f"{context}\n\n"
            f"1. Fais un résumé en 3-5 phrases.\n"
            f"2. Liste 5 concepts clés sous forme de mots-clés séparés par des virgules.\n\n"
            f"Réponds exactement dans ce format :\n"
            f"RÉSUMÉ: <résumé>\n"
            f"CONCEPTS: <mot1, mot2, mot3, mot4, mot5>"
        )

        raw = generator.generate(prompt, max_new_tokens=200)

        summary = ""
        concepts = []
        for line in raw.splitlines():
            if line.startswith("RÉSUMÉ:"):
                summary = line.replace("RÉSUMÉ:", "").strip()
            elif line.startswith("CONCEPTS:"):
                concepts = [c.strip() for c in line.replace("CONCEPTS:", "").split(",")]

        return {
            "document_id": str(document_id),
            "filename": document.filename,
            "summary": summary or raw,
            "key_concepts": concepts,
        }
