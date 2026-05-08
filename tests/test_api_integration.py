from uuid import uuid4

from fastapi.testclient import TestClient
from meaninggrid_api.main import app
from meaninggrid_db.database import session_scope
from meaninggrid_db.models import (
    ContentChunk,
    ContentUnit,
    Dataset,
    Entity,
    EntityRelation,
    Job,
    JobEvent,
    MetricDefinition,
    MetricValue,
    RawObject,
    SourceEvent,
)
from meaninggrid_db.seed import ensure_local_seed
from sqlalchemy import func, select


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


def test_fixture_site_crawl_extracts_entities_content_metrics_and_events() -> None:
    fixture_index = _fixture_index_url()
    with TestClient(app) as client:
        workspace_id = client.get("/workspaces").json()["workspaces"][0]["id"]
        dataset = client.post(
            f"/workspaces/{workspace_id}/datasets",
            json={
                "name": f"Fixture Crawl {uuid4().hex[:8]}",
                "dataset_kind": "site_audit",
                "labels": {"module": "site_audit", "source": "fixture"},
            },
        ).json()
        queued = client.post(
            f"/datasets/{dataset['id']}/site-audit/crawls",
            json={
                "base_url": fixture_index,
                "max_pages": 5,
                "respect_robots": False,
                "render_javascript": False,
            },
        ).json()
        run = client.post(f"/jobs/{queued['job_id']}/run-now")
        assert run.status_code == 200
        assert run.json()["status"] == "succeeded"

        overview = client.get(f"/datasets/{dataset['id']}/site-audit/overview")
        assert overview.status_code == 200
        overview_body = overview.json()
        assert overview_body["pages_crawled"] == 5
        assert overview_body["technical_score_avg"] < 100
        assert {"type": "missing_meta_description", "count": 1} in overview_body["top_issue_types"]

        pages_response = client.get(f"/datasets/{dataset['id']}/site-audit/pages")
        assert pages_response.status_code == 200
        page_rows = pages_response.json()["pages"]
        assert len(page_rows) == 5
        assert any(row["title"] == "MeaningGrid Fixture Site" for row in page_rows)

    with session_scope() as session:
        stored_dataset = session.get(Dataset, dataset["id"])
        assert stored_dataset is not None
        assert stored_dataset.status == "active"
        assert stored_dataset.entity_count >= 7
        assert stored_dataset.content_unit_count >= 20

        job = session.get(Job, queued["job_id"])
        assert job is not None
        assert job.result_json["pages_fetched"] == 5
        assert job.result_json["pages_failed"] == 0

        assert _count(session, RawObject, dataset["id"]) == 5
        assert _count(session, SourceEvent, dataset["id"]) == 5
        assert _count(session, ContentChunk, dataset["id"]) >= 15
        assert _count(session, EntityRelation, dataset["id"]) >= 8

        pages = session.scalars(
            select(Entity).where(
                Entity.dataset_id == stored_dataset.id,
                Entity.labels_json["entity_type"].astext == "page",
            )
        ).all()
        assert len(pages) == 5

        missing_meta_page = next(page for page in pages if "missing-meta" in page.canonical_uri)
        title_metric = _latest_metric(
            session,
            stored_dataset.id,
            missing_meta_page.id,
            "title_length",
        )
        meta_metric = _latest_metric(
            session,
            stored_dataset.id,
            missing_meta_page.id,
            "meta_description_length",
        )
        assert title_metric == 0
        assert meta_metric == 0

        pricing_units = session.scalars(
            select(ContentUnit)
            .join(Entity, Entity.id == ContentUnit.entity_id)
            .where(
                ContentUnit.dataset_id == stored_dataset.id,
                Entity.canonical_uri == fixture_index.replace("index.html", "pricing.html"),
                ContentUnit.unit_kind == "paragraph",
            )
        ).all()
        assert len(pricing_units) == 3

        job_event_types = session.scalars(
            select(JobEvent.event_type).where(JobEvent.job_id == job.id)
        ).all()
        assert "job_started" in job_event_types
        assert "page_extracted" in job_event_types
        assert "job_succeeded" in job_event_types


def _fixture_index_url() -> str:
    from pathlib import Path

    return (Path("examples/site-audit/fixture-site/index.html").resolve()).as_uri()


def _count(session, model, dataset_id: str) -> int:
    return session.scalar(
        select(func.count()).select_from(model).where(model.dataset_id == dataset_id)
    )


def _latest_metric(session, dataset_id: str, entity_id: str, metric_name: str) -> float:
    return session.scalar(
        select(MetricValue.value_number)
        .join(MetricDefinition, MetricDefinition.id == MetricValue.metric_definition_id)
        .where(
            MetricValue.dataset_id == dataset_id,
            MetricValue.entity_id == entity_id,
            MetricDefinition.name == metric_name,
        )
        .order_by(MetricValue.created_at.desc())
        .limit(1)
    )
