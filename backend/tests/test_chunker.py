import pytest
from app.rag.chunker import RecursiveChunker


@pytest.fixture
def chunker():
    return RecursiveChunker(chunk_size=100, overlap=20)


def test_short_text_returns_single_chunk(chunker):
    text = "Hello world"
    result = chunker.chunk(text, page_number=1)
    assert len(result) == 1
    assert result[0]["content"] == "Hello world"
    assert result[0]["page_number"] == 1
    assert result[0]["chunk_index"] == 0


def test_long_text_splits_into_multiple_chunks(chunker):
    # 300 chars > chunk_size=100, doit créer plusieurs chunks
    text = "A" * 300
    result = chunker.chunk(text, page_number=2)
    assert len(result) > 1


def test_overlap_means_chunks_share_content():
    chunker = RecursiveChunker(chunk_size=50, overlap=10)
    # crée un texte avec des séparateurs clairs
    text = "word " * 30  # 150 chars
    result = chunker.chunk(text, page_number=1)
    assert len(result) > 1
    # le début du chunk N+1 chevauche la fin du chunk N
    first_end = result[0]["content"][-10:]
    second_start = result[1]["content"][:10]
    # ils partagent du contenu (overlap)
    assert len(set(first_end) & set(second_start)) > 0


def test_empty_text_returns_no_chunks(chunker):
    result = chunker.chunk("", page_number=1)
    assert result == []


def test_chunk_index_is_sequential(chunker):
    text = "sentence one. " * 20
    result = chunker.chunk(text, page_number=1)
    indices = [c["chunk_index"] for c in result]
    assert indices == list(range(len(result)))


def test_no_infinite_loop_on_separator_at_start():
    # cas qui causait le bug : texte commençant par \n\n
    chunker = RecursiveChunker(chunk_size=50, overlap=10)
    text = "\n\n" + "content " * 20
    result = chunker.chunk(text, page_number=1)
    assert len(result) > 0


def test_page_number_preserved(chunker):
    text = "x " * 100
    result = chunker.chunk(text, page_number=42)
    for chunk in result:
        assert chunk["page_number"] == 42
