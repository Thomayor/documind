import os
from langfuse import Langfuse

_client: Langfuse | None = None


def get_langfuse() -> Langfuse | None:
    """Retourne le client LangFuse si configuré, None sinon."""
    global _client
    if _client is not None:
        return _client

    public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
    host = os.getenv("LANGFUSE_HOST", "http://localhost:3002")

    if not public_key or not secret_key:
        return None

    _client = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host=host,
    )
    return _client
