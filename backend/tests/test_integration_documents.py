import io
import pytest


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_documents_empty(client):
    r = client.get("/api/v1/documents/")
    assert r.status_code == 200
    assert r.json() == []


def test_upload_txt_document(client):
    content = b"Hello, this is a test document with enough content to be chunked properly."
    r = client.post(
        "/api/v1/documents/",
        files={"file": ("test.txt", io.BytesIO(content), "text/plain")},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["filename"] == "test.txt"
    assert "id" in data


def test_upload_unsupported_type(client):
    r = client.post(
        "/api/v1/documents/",
        files={"file": ("image.png", io.BytesIO(b"fake"), "image/png")},
    )
    assert r.status_code == 415


def test_list_documents_after_upload(client):
    content = b"Document for listing test. " * 10
    client.post(
        "/api/v1/documents/",
        files={"file": ("list_test.txt", io.BytesIO(content), "text/plain")},
    )
    r = client.get("/api/v1/documents/")
    assert r.status_code == 200
    filenames = [d["filename"] for d in r.json()]
    assert "list_test.txt" in filenames


def test_delete_document(client):
    content = b"Document to be deleted. " * 5
    upload = client.post(
        "/api/v1/documents/",
        files={"file": ("to_delete.txt", io.BytesIO(content), "text/plain")},
    )
    doc_id = upload.json()["id"]

    r = client.delete(f"/api/v1/documents/{doc_id}")
    assert r.status_code == 204

    r = client.get("/api/v1/documents/")
    ids = [d["id"] for d in r.json()]
    assert doc_id not in ids


def test_delete_nonexistent_document(client):
    r = client.delete("/api/v1/documents/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
