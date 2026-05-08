from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from meaninggrid_api.main import app as api_app
from meaninggrid_db.database import session_scope
from meaninggrid_db.models import Job
from meaninggrid_mcp.main import app as mcp_app


def main() -> None:
    fixture_url = (Path("examples/site-audit/fixture-site/index.html").resolve()).as_uri()

    with TestClient(api_app) as api_client:
        workspace_id = api_client.get("/workspaces").json()["workspaces"][0]["id"]
        dataset = _post_json(
            api_client,
            f"/workspaces/{workspace_id}/datasets",
            {
                "name": f"Smoke Site Audit {uuid4().hex[:8]}",
                "dataset_kind": "site_audit",
                "labels": {"module": "site_audit", "source": "smoke"},
                "classification": {"visibility": "internal", "sensitivity": "standard"},
            },
        )
        queued = _post_json(
            api_client,
            f"/datasets/{dataset['id']}/site-audit/crawls",
            {
                "base_url": fixture_url,
                "max_pages": 5,
                "respect_robots": False,
                "render_javascript": False,
            },
        )
        job = _post_json(api_client, f"/jobs/{queued['job_id']}/run-now", {})
        overview = _get_json(api_client, f"/datasets/{dataset['id']}/site-audit/overview")
        pages = _get_json(api_client, f"/datasets/{dataset['id']}/site-audit/pages")
        search = _post_json(
            api_client,
            f"/datasets/{dataset['id']}/site-audit/search",
            {"query": "pricing plans checkout automation", "limit": 5},
        )
        semantic_map = _get_json(
            api_client,
            f"/datasets/{dataset['id']}/site-audit/semantic-map",
        )

    with session_scope() as session:
        stored_job = session.get(Job, queued["job_id"])
        if stored_job is None:
            raise AssertionError("crawl job was not persisted")
        result_json = stored_job.result_json

    with TestClient(mcp_app) as mcp_client:
        mcp_resources = _get_json(mcp_client, "/mcp/resources")
        mcp_search = _post_json(
            mcp_client,
            "/mcp/tools/site-audit/semantic-search",
            {
                "dataset_id": dataset["id"],
                "query": "pricing plans checkout automation",
                "limit": 5,
            },
        )

    _assert_equal(job["status"], "succeeded", "crawl job succeeds")
    _assert_at_least(result_json["chunks_embedded"], 1, "crawl job embeds chunks")
    _assert_equal(overview["pages_crawled"], 5, "fixture crawls five pages")
    _assert_at_least(len(pages["pages"]), 5, "page table is populated")
    _assert_at_least(len(search["results"]), 1, "API semantic search returns evidence")
    _assert_at_least(len(semantic_map["nearest_pairs"]), 1, "semantic map has similar pairs")
    _assert_at_least(len(semantic_map["outliers"]), 1, "semantic map has outliers")
    _assert_at_least(len(mcp_resources["resources"]), 1, "MCP resources are discoverable")
    _assert_at_least(len(mcp_search["results"]), 1, "MCP semantic search returns evidence")

    print("MeaningGrid Site Audit smoke test passed")
    print(f"dataset_id={dataset['id']}")
    print(f"pages={overview['pages_crawled']}")
    print(f"chunks_embedded={result_json['chunks_embedded']}")
    print(f"semantic_results={len(search['results'])}")
    print(f"nearest_pairs={len(semantic_map['nearest_pairs'])}")
    print(f"mcp_resources={len(mcp_resources['resources'])}")


def _get_json(client: TestClient, path: str) -> dict:
    response = client.get(path)
    response.raise_for_status()
    return response.json()


def _post_json(client: TestClient, path: str, payload: dict) -> dict:
    response = client.post(path, json=payload)
    response.raise_for_status()
    return response.json()


def _assert_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def _assert_at_least(actual: int, minimum: int, label: str) -> None:
    if actual < minimum:
        raise AssertionError(f"{label}: expected at least {minimum}, got {actual}")


if __name__ == "__main__":
    main()
