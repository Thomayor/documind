from app.parsers.base import BaseParser


class TxtParser(BaseParser):
    def parse(self, file_bytes: bytes) -> list[tuple[str, int]]:
        text = file_bytes.decode("utf-8", errors="ignore").strip()
        return [(text, 1)] if text else []
