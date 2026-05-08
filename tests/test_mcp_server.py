from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from meaninggrid_api.main import app as api_app
from meaninggrid_mcp.main import app as mcp_app


def test_mcp_resources_include_workspace_index() -> None:
    with TestClient(mcp_app) as client:
        response = client.get("/mcp/resources")

    assert response.status_code == 200
    resources = response.json()["resources"]
    assert any(resource["uri"] == "meaninggrid://workspaces" for resource in resources)


def test_mcp_site_audit_semantic_search_returns_evidence() -> None:
    fixture_index = (Path("examples/site-audit/fixture-site/index.html").resolve()).as_uri()
    with TestClient(api_app) as api_client:
        workspace_id = api_client.get("/workspaces").json()["workspaces"][0]["id"]
        dataset = api_client.post(
            f"/workspaces/{workspace_id}/datasets",
            json={
                "name": f"MCP Fixture Crawl {uuid4().hex[:8]}",
                "dataset_kind": "site_audit",
                "labels": {"module": "site_audit", "source": "mcp-test"},
            },
        ).json()
        queued = api_client.post(
            f"/datasets/{dataset['id']}/site-audit/crawls",
            json={
                "base_url": fixture_index,
                "max_pages": 5,
                "respect_robots": False,
                "render_javascript": False,
            },
        ).json()
        api_client.post(f"/jobs/{queued['job_id']}/run-now")

    with TestClient(mcp_app) as mcp_client:
        response = mcp_client.post(
            "/mcp/tools/site-audit/semantic-search",
            json={
                "dataset_id": dataset["id"],
                "query": "pricing plans checkout automation",
                "limit": 5,
            },
        )
        clusters = mcp_client.get(f"/mcp/resource/dataset/{dataset['id']}/site-audit/clusters")
        duplicates = mcp_client.get(
            f"/mcp/resource/dataset/{dataset['id']}/site-audit/duplicates"
        )

    assert response.status_code == 200
    results = response.json()["results"]
    assert results
    assert results[0]["payload"]["dataset_id"] == dataset["id"]
    assert any("pricing" in result["text"].lower() for result in results)
    assert clusters.status_code == 200
    cluster_body = clusters.json()
    assert cluster_body["cluster_count"] >= 1
    assert cluster_body["clusters"][0]["members"]
    assert duplicates.status_code == 200
    duplicate_body = duplicates.json()
    assert duplicate_body["duplicate_count"] >= 1
    assert duplicate_body["duplicates"][0]["source_entity_id"]
