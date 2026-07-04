from unittest.mock import MagicMock
from uuid import uuid4

from app.rag.generator import PromptBuilder


def make_chunk(content: str, page_number: int):
    chunk = MagicMock()
    chunk.content = content
    chunk.page_number = page_number
    chunk.document_id = uuid4()
    return chunk


def test_prompt_contains_question():
    builder = PromptBuilder()
    chunks = [(make_chunk("Some context.", 1), 0.3)]
    prompt = builder.build("What is Q-learning?", chunks)
    assert "What is Q-learning?" in prompt


def test_prompt_contains_chunk_content():
    builder = PromptBuilder()
    chunks = [(make_chunk("Q-learning uses rewards.", 5), 0.3)]
    prompt = builder.build("question", chunks)
    assert "Q-learning uses rewards." in prompt


def test_prompt_contains_page_number():
    builder = PromptBuilder()
    chunks = [(make_chunk("Some text.", 42), 0.3)]
    prompt = builder.build("question", chunks)
    assert "page 42" in prompt


def test_prompt_with_multiple_chunks():
    builder = PromptBuilder()
    chunks = [
        (make_chunk("First chunk.", 1), 0.2),
        (make_chunk("Second chunk.", 2), 0.3),
    ]
    prompt = builder.build("question", chunks)
    assert "First chunk." in prompt
    assert "Second chunk." in prompt


def test_prompt_with_no_chunks():
    builder = PromptBuilder()
    prompt = builder.build("question", [])
    assert "question" in prompt
    assert "QUESTION" in prompt
