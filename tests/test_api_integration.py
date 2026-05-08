from uuid import uuid4

from fastapi.testclient import TestClient
from meaninggrid_api.main import app
from meaninggrid_db.database import session_scope
from meaninggrid_db.seed import ensure_local_seed


def test_local_seed_is_idempotent() -> None:
    with session_scope() as session:
        first = ensure_local_seed(session)
        second = ensure_local_seed(session)

    assert first["tenant_id"] == second["tenant_id"]
    assert first["workspace_id"] == second["workspace_id"]
    assert first["site_audit_module_id"] == second["site_audit_module_id"]


def test_workspace_module_dataset_and_job_flow() -> None:
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["database"] == "ok"
        assert health.json()["queue"] == "ok"

        workspaces = client.get("/workspaces")
        assert workspaces.status_code == 200
        workspace_items = workspaces.json()["workspaces"]
        assert len(workspace_items) >= 1
        workspace_id = workspace_items[0]["id"]

        modules = client.get("/modules")
        assert modules.status_code == 200
        module_items = modules.json()["modules"]
        assert any(module["module_key"] == "site_audit" for module in module_items)

        installed_modules = client.get(f"/workspaces/{workspace_id}/modules")
        assert installed_modules.status_code == 200
        installed_items = installed_modules.json()["modules"]
        assert installed_items[0]["resource_count"] > 0

        dataset_name = f"Integration Site Audit {uuid4().hex[:8]}"
        created = client.post(
            f"/workspaces/{workspace_id}/datasets",
            json={
                "name": dataset_name,
                "dataset_kind": "site_audit",
                "labels": {"module": "site_audit", "source": "test"},
            },
        )
        assert created.status_code == 201
        dataset = created.json()
        assert dataset["name"] == dataset_name
        assert dataset["dataset_kind"] == "site_audit"
        assert dataset["status"] == "draft"
        assert dataset["labels"]["source"] == "test"

        listed = client.get(f"/workspaces/{workspace_id}/datasets?kind=site_audit")
        assert listed.status_code == 200
        assert any(item["id"] == dataset["id"] for item in listed.json()["datasets"])

        detail = client.get(f"/datasets/{dataset['id']}")
        assert detail.status_code == 200
        assert detail.json()["id"] == dataset["id"]

        card = client.get(f"/datasets/{dataset['id']}/card")
        assert card.status_code == 200
        card_body = card.json()
        assert "page" in card_body["entity_types"]
        assert "technical_score" in card_body["metrics"]

        crawl = client.post(
            f"/datasets/{dataset['id']}/site-audit/crawls",
            json={
                "base_url": "https://example.com",
                "max_pages": 5,
                "respect_robots": True,
                "render_javascript": False,
            },
        )
        assert crawl.status_code == 202
        queued_job = crawl.json()
        assert queued_job["dataset_id"] == dataset["id"]
        assert queued_job["status"] == "queued"

        job = client.get(f"/jobs/{queued_job['job_id']}")
        assert job.status_code == 200
        job_body = job.json()
        assert job_body["job_type"] == "crawl_website"
        assert job_body["progress_total"] == 5

        events = client.get(f"/jobs/{queued_job['job_id']}/events")
        assert events.status_code == 200
        assert events.json()["events"][0]["event_type"] == "job_queued"

        cancel = client.post(f"/jobs/{queued_job['job_id']}/cancel")
        assert cancel.status_code == 200
        assert cancel.json()["status"] == "canceled"


def test_api_error_shape_for_missing_dataset() -> None:
    with TestClient(app) as client:
        response = client.get(f"/datasets/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "dataset_not_found"
