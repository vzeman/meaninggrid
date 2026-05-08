import math

import pytest
from meaninggrid_embeddings import embed_text


def test_local_embedding_is_deterministic_and_normalized() -> None:
    first = embed_text("Pricing workflow and checkout automation", 16)
    second = embed_text("Pricing workflow and checkout automation", 16)

    assert first == second
    assert len(first) == 16
    assert math.isclose(sum(value * value for value in first), 1.0)


def test_local_embedding_rejects_invalid_dimension() -> None:
    with pytest.raises(ValueError):
        embed_text("anything", 0)
