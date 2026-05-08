from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from meaninggrid_analysis.site_audit import run_crawl_job
from meaninggrid_core.config import get_settings
from meaninggrid_db.models import (
    ContentChunk,
    ContentUnit,
    Dataset,
    DataStream,
    Entity,
    EntityType,
    Job,
    JobEvent,
    MetricDefinition,
    MetricValue,
    Module,
    ModuleInstallation,
    ModuleResource,
    Source,
    Workspace,
)
from meaninggrid_embeddings import embed_text
from meaninggrid_vectorstores import (
    create_qdrant_client,
    default_content_collection_spec,
    search_points,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session


class ApplicationError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


@dataclass(frozen=True)
class CreateDatasetCommand:
    workspace_id: UUID
    name: str
    dataset_kind: str
    description: str | None
    labels: dict[str, Any]
    classification: dict[str, Any]


@dataclass(frozen=True)
class StartSiteAuditCrawlCommand:
    dataset_id: UUID
    base_url: str
    max_pages: int
    respect_robots: bool
    render_javascript: bool
    include_patterns: list[str]
    exclude_patterns: list[str]

    def as_payload(self) -> dict[str, Any]:
        return {
            "base_url": self.base_url,
            "max_pages": self.max_pages,
            "respect_robots": self.respect_robots,
            "render_javascript": self.render_javascript,
            "include_patterns": self.include_patterns,
            "exclude_patterns": self.exclude_patterns,
        }


@dataclass(frozen=True)
class RunSiteAuditCommand:
    dataset_id: UUID
    preset: str
    crawl: StartSiteAuditCrawlCommand | None


class WorkspaceApplicationService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_workspaces(self) -> list[Workspace]:
        return list(
            self.session.scalars(select(Workspace).order_by(Workspace.created_at.asc())).all()
        )

    def get_workspace(self, workspace_id: UUID) -> Workspace:
        workspace = self.session.get(Workspace, workspace_id)
        if workspace is None:
            raise ApplicationError(404, "workspace_not_found", "Workspace was not found.")
        return workspace


class ModuleApplicationService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_modules(self) -> list[Module]:
        return list(self.session.scalars(select(Module).order_by(Module.module_key.asc())).all())

    def list_workspace_modules(self, workspace_id: UUID):
        WorkspaceApplicationService(self.session).get_workspace(workspace_id)
        return self.session.execute(
            select(ModuleInstallation, Module, func.count(ModuleResource.id))
            .join(Module, Module.id == ModuleInstallation.module_id)
            .outerjoin(
                ModuleResource,
                ModuleResource.module_installation_id == ModuleInstallation.id,
            )
            .where(ModuleInstallation.workspace_id == workspace_id)
            .group_by(ModuleInstallation.id, Module.id)
            .order_by(Module.module_key.asc())
        ).all()


class DatasetApplicationService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_workspace_datasets(
        self,
        workspace_id: UUID,
        kind: str | None = None,
        status: str | None = None,
    ) -> list[Dataset]:
        WorkspaceApplicationService(self.session).get_workspace(workspace_id)
        query = select(Dataset).where(Dataset.workspace_id == workspace_id)
        if kind:
            query = query.where(Dataset.dataset_kind == kind)
        if status:
            query = query.where(Dataset.status == status)
        return list(self.session.scalars(query.order_by(Dataset.created_at.desc())).all())

    def create_dataset(self, command: CreateDatasetCommand) -> Dataset:
        workspace = WorkspaceApplicationService(self.session).get_workspace(command.workspace_id)
        dataset = Dataset(
            tenant_id=workspace.tenant_id,
            workspace_id=workspace.id,
            name=command.name,
            slug=slugify(command.name),
            description=command.description,
            dataset_kind=command.dataset_kind,
            status="draft",
            labels_json=command.labels,
            classification_json=command.classification,
        )
        self.session.add(dataset)
        self.session.flush()
        self._create_dataset_created_job(dataset)
        self.session.commit()
        self.session.refresh(dataset)
        return dataset

    def get_dataset(self, dataset_id: UUID) -> Dataset:
        dataset = self.session.get(Dataset, dataset_id)
        if dataset is None:
            raise ApplicationError(404, "dataset_not_found", "Dataset was not found.")
        return dataset

    def build_dataset_card(self, dataset_id: UUID) -> dict[str, Any]:
        dataset = self.get_dataset(dataset_id)
        entity_types = self.session.scalars(
            select(EntityType.name)
            .where(
                EntityType.workspace_id == dataset.workspace_id,
                EntityType.dataset_id.is_(None),
            )
            .order_by(EntityType.name.asc())
        ).all()
        metrics = self.session.scalars(
            select(MetricDefinition.name)
            .where(
                MetricDefinition.workspace_id == dataset.workspace_id,
                MetricDefinition.dataset_id.is_(None),
            )
            .order_by(MetricDefinition.name.asc())
        ).all()
        summary = (
            f"{dataset.dataset_kind} dataset with {dataset.entity_count} entities, "
            f"{dataset.content_unit_count} content units, and {dataset.source_count} sources."
        )
        return {
            "dataset": dataset,
            "summary": summary,
            "entity_types": list(entity_types),
            "metrics": list(metrics),
            "next_resources": [
                f"meaninggrid://dataset/{dataset.id}/site-audit/overview",
                f"meaninggrid://dataset/{dataset.id}/context",
            ],
        }

    def _create_dataset_created_job(self, dataset: Dataset) -> None:
        if dataset.dataset_kind != "site_audit":
            return
        self.session.add(
            Job(
                tenant_id=dataset.tenant_id,
                workspace_id=dataset.workspace_id,
                dataset_id=dataset.id,
                job_type="dataset_created",
                status="finished",
                progress_current=1,
                progress_total=1,
                progress_message="Dataset record created",
                payload_json={"dataset_kind": dataset.dataset_kind},
            )
        )


class SiteAuditApplicationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.datasets = DatasetApplicationService(session)

    def overview(self, dataset_id: UUID) -> dict[str, Any]:
        dataset = self.datasets.get_dataset(dataset_id)
        pages_crawled = self.session.scalar(
            select(func.count()).select_from(self._page_entities_query(dataset.id).subquery())
        )
        technical_avg = self._metric_average(dataset.id, "technical_score")
        meta_missing = self._metric_count(dataset.id, "meta_description_length", 0)
        title_missing = self._metric_count(dataset.id, "title_length", 0)
        top_issue_types = []
        if meta_missing:
            top_issue_types.append({"type": "missing_meta_description", "count": meta_missing})
        if title_missing:
            top_issue_types.append({"type": "missing_title", "count": title_missing})
        return {
            "pages_crawled": pages_crawled or 0,
            "technical_score_avg": technical_avg,
            "geo_readiness_avg": None,
            "open_insights": 0,
            "top_issue_types": top_issue_types,
        }

    def pages(self, dataset_id: UUID) -> list[dict[str, Any]]:
        dataset = self.datasets.get_dataset(dataset_id)
        pages = self.session.scalars(
            self._page_entities_query(dataset.id).order_by(Entity.canonical_uri.asc())
        ).all()
        return [
            {
                "entity": page,
                "title": page.properties_json.get("title"),
                "status_code": page.properties_json.get("status_code"),
                "word_count": self._metric_value(dataset.id, page.id, "word_count"),
                "technical_score": self._metric_value(dataset.id, page.id, "technical_score"),
            }
            for page in pages
        ]

    def semantic_search(self, dataset_id: UUID, query: str, limit: int) -> list[dict[str, Any]]:
        dataset = self.datasets.get_dataset(dataset_id)
        collection = default_content_collection_spec()
        query_vector = embed_text(query, get_settings().embedding_dimension)
        points = search_points(
            create_qdrant_client(),
            collection.name,
            query_vector,
            str(dataset.id),
            limit,
        )
        return [self._build_search_result(point) for point in points]

    def start_crawl(self, command: StartSiteAuditCrawlCommand) -> Job:
        dataset = self.datasets.get_dataset(command.dataset_id)
        source, stream = self._ensure_website_source(dataset, command)
        job = self._create_job(
            dataset=dataset,
            source=source,
            job_type="crawl_website",
            payload={
                "crawl": command.as_payload(),
                "data_stream_id": str(stream.id),
            },
            progress_total=command.max_pages,
            progress_message="Queued website crawl",
        )
        self.session.commit()
        self.session.refresh(job)
        return job

    def start_run(self, command: RunSiteAuditCommand) -> Job:
        dataset = self.datasets.get_dataset(command.dataset_id)
        source = None
        stream = None
        if command.crawl is not None:
            source, stream = self._ensure_website_source(dataset, command.crawl)
        job = self._create_job(
            dataset=dataset,
            source=source,
            job_type="run_site_audit_v0",
            payload={
                "preset": command.preset,
                "crawl": command.crawl.as_payload() if command.crawl else None,
                "data_stream_id": str(stream.id) if stream else None,
            },
            progress_total=100,
            progress_message="Queued Site Audit pipeline",
        )
        self.session.commit()
        self.session.refresh(job)
        return job

    def _ensure_website_source(
        self,
        dataset: Dataset,
        command: StartSiteAuditCrawlCommand,
    ) -> tuple[Source, DataStream]:
        source = self.session.scalar(
            select(Source).where(
                Source.dataset_id == dataset.id,
                Source.connector_type == "website_crawler",
                Source.display_name == command.base_url,
            )
        )
        if source is None:
            source = Source(
                tenant_id=dataset.tenant_id,
                workspace_id=dataset.workspace_id,
                dataset_id=dataset.id,
                connector_type="website_crawler",
                connector_version="0.1.0",
                display_name=command.base_url,
                labels_json={"module": "site_audit"},
                config_json={"base_url": command.base_url},
            )
            self.session.add(source)
            self.session.flush()
            dataset.source_count += 1

        stream = self.session.scalar(
            select(DataStream).where(
                DataStream.dataset_id == dataset.id,
                DataStream.source_id == source.id,
                DataStream.name == "default_crawl",
            )
        )
        if stream is None:
            stream = DataStream(
                tenant_id=dataset.tenant_id,
                workspace_id=dataset.workspace_id,
                dataset_id=dataset.id,
                source_id=source.id,
                name="default_crawl",
                stream_type="website_pages",
                sync_mode="snapshot",
                labels_json={"module": "site_audit"},
            )
            self.session.add(stream)
            self.session.flush()
        return source, stream

    def _create_job(
        self,
        dataset: Dataset,
        source: Source | None,
        job_type: str,
        payload: dict[str, Any],
        progress_total: int,
        progress_message: str,
    ) -> Job:
        job = Job(
            tenant_id=dataset.tenant_id,
            workspace_id=dataset.workspace_id,
            dataset_id=dataset.id,
            source_id=source.id if source else None,
            job_type=job_type,
            status="queued",
            progress_current=0,
            progress_total=progress_total,
            progress_message=progress_message,
            payload_json=payload,
        )
        self.session.add(job)
        self.session.flush()
        self.session.add(
            JobEvent(
                job_id=job.id,
                event_type="job_queued",
                message=progress_message,
                progress_current=0,
                progress_total=progress_total,
                payload_json={"job_type": job_type},
            )
        )
        return job

    def _page_entities_query(self, dataset_id: UUID):
        return select(Entity).join(EntityType, EntityType.id == Entity.entity_type_id).where(
            Entity.dataset_id == dataset_id,
            EntityType.name == "page",
        )

    def _metric_value(self, dataset_id: UUID, entity_id: UUID, metric_name: str) -> float | None:
        return self.session.scalar(
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

    def _metric_average(self, dataset_id: UUID, metric_name: str) -> float | None:
        value = self.session.scalar(
            select(func.avg(MetricValue.value_number))
            .join(MetricDefinition, MetricDefinition.id == MetricValue.metric_definition_id)
            .where(
                MetricValue.dataset_id == dataset_id,
                MetricDefinition.name == metric_name,
            )
        )
        return float(value) if value is not None else None

    def _metric_count(self, dataset_id: UUID, metric_name: str, value: float) -> int:
        count = self.session.scalar(
            select(func.count())
            .select_from(MetricValue)
            .join(MetricDefinition, MetricDefinition.id == MetricValue.metric_definition_id)
            .where(
                MetricValue.dataset_id == dataset_id,
                MetricDefinition.name == metric_name,
                MetricValue.value_number == value,
            )
        )
        return count or 0

    def _build_search_result(self, point: Any) -> dict[str, Any]:
        payload = point.payload or {}
        chunk_id = payload.get("content_chunk_id")
        chunk = self.session.get(ContentChunk, chunk_id) if chunk_id else None
        if chunk is None:
            return {
                "content_chunk_id": chunk_id,
                "content_unit_id": payload.get("content_unit_id"),
                "entity_id": payload.get("entity_id"),
                "score": float(point.score),
                "text": "",
                "unit_kind": payload.get("unit_kind"),
                "page_label": None,
                "canonical_uri": None,
                "payload": payload,
            }
        unit = self.session.get(ContentUnit, chunk.content_unit_id)
        entity = self.session.get(Entity, chunk.entity_id) if chunk.entity_id else None
        return {
            "content_chunk_id": chunk.id,
            "content_unit_id": chunk.content_unit_id,
            "entity_id": chunk.entity_id,
            "score": float(point.score),
            "text": chunk.text,
            "unit_kind": unit.unit_kind if unit else None,
            "page_label": entity.label if entity else None,
            "canonical_uri": entity.canonical_uri if entity else None,
            "payload": payload,
        }


class JobApplicationService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_job(self, job_id: UUID) -> Job:
        job = self.session.get(Job, job_id)
        if job is None:
            raise ApplicationError(404, "job_not_found", "Job was not found.")
        return job

    def list_job_events(self, job_id: UUID) -> list[JobEvent]:
        self.get_job(job_id)
        return list(
            self.session.scalars(
                select(JobEvent)
                .where(JobEvent.job_id == job_id)
                .order_by(JobEvent.created_at.asc())
            ).all()
        )

    def cancel_job(self, job_id: UUID) -> Job:
        job = self.get_job(job_id)
        if job.status in {"queued", "running"}:
            job.status = "canceled"
            job.progress_message = "Canceled by user"
            self.session.add(
                JobEvent(
                    job_id=job.id,
                    event_type="job_canceled",
                    message="Job canceled by user.",
                    payload_json={},
                )
            )
            self.session.commit()
            self.session.refresh(job)
        return job

    def run_job_now(self, job_id: UUID) -> Job:
        job = self.get_job(job_id)
        if job.job_type != "crawl_website":
            raise ApplicationError(
                400,
                "unsupported_job_type",
                "Only crawl_website jobs can run locally now.",
            )
        if job.status not in {"queued", "failed"}:
            raise ApplicationError(409, "job_not_runnable", "Job is not in a runnable state.")
        run_crawl_job(self.session, str(job.id))
        self.session.refresh(job)
        return job


def slugify(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "dataset"
