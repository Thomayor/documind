class RecursiveChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 150):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self._separators = ["\n\n", "\n", ". ", " "]

    def chunk(self, text: str, page_number: int = 1) -> list[dict]:
        if not text.strip():
            return []
        chunks = self._split(text)
        return [
            {"content": chunk, "page_number": page_number, "chunk_index": i}
            for i, chunk in enumerate(chunks)
        ]

    def _split(self, text: str) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]

        for separator in self._separators:
            if separator in text:
                return self._split_on_separator(text, separator)

        return self._split_hard(text)

    def _split_on_separator(self, text: str, separator: str) -> list[str]:
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            if end >= len(text):
                chunks.append(text[start:].strip())
                break

            split_pos = text.rfind(separator, start, end)
            if split_pos <= start:
                split_pos = end

            chunk = text[start:split_pos].strip()
            if chunk:
                chunks.append(chunk)

            start = max(split_pos - self.overlap, start + 1)

        return [c for c in chunks if c]

    def _split_hard(self, text: str) -> list[str]:
        chunks = []
        start = 0
        while start < len(text):
            chunks.append(text[start:start + self.chunk_size])
            start += self.chunk_size - self.overlap
        return chunks
