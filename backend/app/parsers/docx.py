import io

from docx import Document

from app.parsers.base import BaseParser


class DocxParser(BaseParser):
    def parse(self, file_bytes: bytes) -> list[tuple[str, int]]:
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return [(text, 1)] if text else []
