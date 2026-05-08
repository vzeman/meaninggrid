from meaninggrid_core.config import get_settings
from qdrant_client import QdrantClient


def check_qdrant() -> str:
    settings = get_settings()
    if settings.vector_backend != "qdrant":
        return "disabled"

    client = QdrantClient(url=settings.qdrant_url, timeout=2)
    client.get_collections()
    return "ok"
