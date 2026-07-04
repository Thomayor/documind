import pytest
from app.parsers import get_parser, PARSERS
from app.parsers.txt import TxtParser


def test_get_parser_returns_correct_type():
    parser = get_parser("application/pdf")
    assert parser.__class__.__name__ == "PDFParser"

    parser = get_parser("text/plain")
    assert isinstance(parser, TxtParser)


def test_get_parser_raises_on_unknown_type():
    with pytest.raises(ValueError, match="non supporté"):
        get_parser("image/jpeg")


def test_txt_parser_extracts_text():
    parser = TxtParser()
    content = "Hello world\nSecond line"
    result = parser.parse(content.encode("utf-8"))
    assert len(result) == 1
    text, page = result[0]
    assert "Hello world" in text
    assert page == 1


def test_txt_parser_empty_file():
    parser = TxtParser()
    result = parser.parse(b"")
    assert result == []


def test_parsers_dict_has_expected_keys():
    assert "application/pdf" in PARSERS
    assert "text/plain" in PARSERS
    assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in PARSERS
