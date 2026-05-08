"""Vector store infrastructure adapters for MeaningGrid."""

from meaninggrid_vectorstores.collections import (
    PayloadIndexSpec,
    VectorCollectionSpec,
    content_collection_name,
    default_content_collection_spec,
)
from meaninggrid_vectorstores.qdrant import (
    check_qdrant,
    create_qdrant_client,
    ensure_collection,
    ensure_default_content_collection,
)

__all__ = [
    "PayloadIndexSpec",
    "VectorCollectionSpec",
    "check_qdrant",
    "content_collection_name",
    "create_qdrant_client",
    "default_content_collection_spec",
    "ensure_collection",
    "ensure_default_content_collection",
]
