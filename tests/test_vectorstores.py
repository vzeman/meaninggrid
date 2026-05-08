from meaninggrid_vectorstores import (
    VectorCollectionSpec,
    content_collection_name,
    create_qdrant_client,
    default_content_collection_spec,
    ensure_collection,
)
from meaninggrid_vectorstores.collections import PayloadIndexSpec


def test_content_collection_name_is_stable_and_qdrant_safe() -> None:
    assert (
        content_collection_name(
            provider="local",
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            content_kind="content_chunks",
        )
        == "mg_local_sentence_transformers_all_minilm_l6_v2_content_chunks"
    )


def test_default_content_collection_spec_uses_required_payload_indexes() -> None:
    spec = default_content_collection_spec()

    assert spec.dimension == 384
    assert spec.distance == "cosine"
    assert {index.field_name for index in spec.payload_indexes} >= {
        "tenant_id",
        "workspace_id",
        "dataset_id",
        "entity_id",
        "content_unit_id",
        "content_chunk_id",
        "visibility",
        "sensitivity",
    }


def test_qdrant_adapter_creates_collection_with_vector_contract() -> None:
    client = create_qdrant_client()
    spec = VectorCollectionSpec(
        name="mg_test_content_contract",
        dimension=4,
        distance="cosine",
        payload_indexes=(
            PayloadIndexSpec("tenant_id", "keyword"),
            PayloadIndexSpec("dataset_id", "keyword"),
        ),
    )
    client.delete_collection(spec.name)

    try:
        ensure_collection(client, spec)
        ensure_collection(client, spec)

        collection = client.get_collection(spec.name)
        vectors = collection.config.params.vectors
        assert vectors.size == 4
        assert vectors.distance.value == "Cosine"
    finally:
        client.delete_collection(spec.name)
