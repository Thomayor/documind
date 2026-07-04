import pymupdf

from app.parsers.base import BaseParser


class PDFParser(BaseParser):
    def parse(self, file_bytes: bytes) -> list[tuple[str, int]]:
        results = []
        with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text = page.get_text().strip()
                if text:
                    results.append((text, page.number + 1))
        return results
