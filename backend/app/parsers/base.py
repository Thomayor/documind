from abc import ABC, abstractmethod


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_bytes: bytes) -> list[tuple[str, int]]:
        """Retourne une liste de (texte, numéro de page)."""
