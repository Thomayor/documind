from app.parsers.docx import DocxParser
from app.parsers.pdf import PDFParser
from app.parsers.txt import TxtParser

PARSERS = {
    "application/pdf": PDFParser,
    "text/plain": TxtParser,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocxParser,
}


def get_parser(content_type: str) -> PDFParser | TxtParser | DocxParser:
    parser_class = PARSERS.get(content_type)
    if not parser_class:
        raise ValueError(f"Type de fichier non supporté : {content_type}")
    return parser_class()
