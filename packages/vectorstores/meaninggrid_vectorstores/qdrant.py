from meaninggrid_core.config import get_settings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PayloadSchemaType, PointStruct, VectorParams

from meaninggrid_vectorstores.collections import (
    VectorCollectionSpec,
    default_content_collection_spec,
)

QDRANT_DISTANCE_BY_NAME = {
    "cosine": Distance.COSINE,
    "dot": Distance.DOT,
    "euclid": Distance.EUCLID,
    "manhattan": Distance.MANHATTAN,
}


def check_qdrant() -> str:
    settings = get_settings()
    if settings.vector_backend != "qdrant":
        return "disabled"

    client = QdrantClient(url=settings.qdrant_url, timeout=2)
    client.get_collections()
    return "ok"


def create_qdrant_client() -> QdrantClient:
    settings = get_settings()
    return QdrantClient(url=settings.qdrant_url, timeout=5)


def ensure_default_content_collection(client: QdrantClient | None = None) -> VectorCollectionSpec:
    spec = default_content_collection_spec()
    ensure_collection(client or create_qdrant_client(), spec)
    return spec


def ensure_collection(client: QdrantClient, spec: VectorCollectionSpec) -> None:
    if not client.collection_exists(spec.name):
        client.create_collection(
            collection_name=spec.name,
            vectors_config=VectorParams(
                size=spec.dimension,
                distance=_distance(spec.distance),
            ),
        )

    for payload_index in spec.payload_indexes:
        client.create_payload_index(
            collection_name=spec.name,
            field_name=payload_index.field_name,
            field_schema=_payload_schema(payload_index.field_schema),
        )


def upsert_points(
    client: QdrantClient,
    collection_name: str,
    points: list[tuple[str, list[float], dict]],
) -> None:
    if not points:
        return
    client.upsert(
        collection_name=collection_name,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload=payload,
            )
            for point_id, vector, payload in points
        ],
        wait=True,
    )


def _distance(value: str) -> Distance:
    try:
        return QDRANT_DISTANCE_BY_NAME[value]
    except KeyError as exc:
        raise ValueError(f"Unsupported Qdrant distance metric: {value}") from exc


def _payload_schema(value: str) -> PayloadSchemaType:
    try:
        return PayloadSchemaType(value)
    except ValueError as exc:
        raise ValueError(f"Unsupported Qdrant payload schema: {value}") from exc
