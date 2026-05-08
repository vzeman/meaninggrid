from __future__ import annotations

from dataclasses import dataclass

from meaninggrid_core.config import Settings, get_settings


@dataclass(frozen=True)
class PayloadIndexSpec:
    field_name: str
    field_schema: str


@dataclass(frozen=True)
class VectorCollectionSpec:
    name: str
    dimension: int
    distance: str
    payload_indexes: tuple[PayloadIndexSpec, ...]


DEFAULT_CONTENT_PAYLOAD_INDEXES = (
    PayloadIndexSpec("tenant_id", "keyword"),
    PayloadIndexSpec("workspace_id", "keyword"),
    PayloadIndexSpec("dataset_id", "keyword"),
    PayloadIndexSpec("entity_type", "keyword"),
    PayloadIndexSpec("entity_id", "keyword"),
    PayloadIndexSpec("content_unit_id", "keyword"),
    PayloadIndexSpec("content_chunk_id", "keyword"),
    PayloadIndexSpec("language", "keyword"),
    PayloadIndexSpec("module", "keyword"),
    PayloadIndexSpec("visibility", "keyword"),
    PayloadIndexSpec("sensitivity", "keyword"),
    PayloadIndexSpec("content_hash", "keyword"),
)


def default_content_collection_spec(settings: Settings | None = None) -> VectorCollectionSpec:
    resolved = settings or get_settings()
    return VectorCollectionSpec(
        name=content_collection_name(
            provider=resolved.embedding_provider,
            model_name=resolved.embedding_model,
            content_kind="content_chunks",
        ),
        dimension=resolved.embedding_dimension,
        distance="cosine",
        payload_indexes=DEFAULT_CONTENT_PAYLOAD_INDEXES,
    )


def content_collection_name(provider: str, model_name: str, content_kind: str) -> str:
    return "_".join(
        part
        for part in (
            "mg",
            _slugify(provider),
            _slugify(model_name),
            _slugify(content_kind),
        )
        if part
    )


def _slugify(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_")
