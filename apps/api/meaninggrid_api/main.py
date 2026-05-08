from contextlib import asynccontextmanager
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from meaninggrid_analysis.site_audit import run_crawl_job
from meaninggrid_core.config import get_settings
from meaninggrid_core.health import build_health_status
from meaninggrid_db.database import check_database, session_scope
from meaninggrid_db.models import (
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
from meaninggrid_db.seed import ensure_local_seed
from redis import Redis
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from meaninggrid_api.dependencies import get_db
from meaninggrid_api.errors import ApiError, api_error_handler
from meaninggrid_api.schemas import (
    DatasetCard,
    DatasetCreate,
    DatasetDetail,
    DatasetSummary,
    JobEventSummary,
    JobQueuedResponse,
    JobSummary,
    ModuleInstallationSummary,
    ModuleSummary,
    SiteAuditOverview,
    SiteAuditPageRow,
    SiteAuditRunCreate,
    SiteCrawlCreate,
    WorkspaceSummary,
)

settings = get_settings()
DbSession = Annotated[Session, Depends(get_db)]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    with session_scope() as session:
        ensure_local_seed(session)
    yield


app = FastAPI(
    title="MeaningGrid API",
    description="Semantic intelligence and context management API.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_exception_handler(ApiError, api_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        settings.public_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    status = build_health_status()
    status["database"] = _safe_check(check_database)
    status["queue"] = _safe_check(_check_queue)
    if status["database"] != "ok" or status["queue"] != "ok":
        status["status"] = "degraded"
    return status


@app.get("/version", tags=["system"])
def version() -> dict[str, str | None]:
    return {
        "version": "0.1.0",
        "commit": None,
        "build_time": None,
    }


@app.get("/workspaces", tags=["workspaces"])
def list_workspaces(db: DbSession) -> dict[str, list[WorkspaceSummary]]:
    workspaces = db.scalars(select(Workspace).order_by(Workspace.created_at.asc())).all()
    return {
        "workspaces": [
            WorkspaceSummary(id=workspace.id, name=workspace.name, slug=workspace.slug)
            for workspace in workspaces
        ]
    }


@app.get("/modules", tags=["modules"])
def list_modules(db: DbSession) -> dict[str, list[ModuleSummary]]:
    modules = db.scalars(select(Module).order_by(Module.module_key.asc())).all()
    return {
        "modules": [
            ModuleSummary(
                module_key=module.module_key,
                name=module.name,
                current_version=module.current_version,
                bundled=module.bundled,
                status=module.status,
            )
            for module in modules
        ]
    }


@app.get("/workspaces/{workspace_id}/modules", tags=["modules"])
def list_workspace_modules(
    workspace_id: UUID,
    db: DbSession,
) -> dict[str, list[ModuleInstallationSummary]]:
    _get_workspace(db, workspace_id)
    rows = db.execute(
        select(ModuleInstallation, Module, func.count(ModuleResource.id))
        .join(Module, Module.id == ModuleInstallation.module_id)
        .outerjoin(ModuleResource, ModuleResource.module_installation_id == ModuleInstallation.id)
        .where(ModuleInstallation.workspace_id == workspace_id)
        .group_by(ModuleInstallation.id, Module.id)
        .order_by(Module.module_key.asc())
    ).all()
    return {
        "modules": [
            ModuleInstallationSummary(
                id=installation.id,
                module_key=module.module_key,
                name=module.name,
                module_version=installation.module_version,
                enabled=installation.enabled,
                resource_count=resource_count,
            )
            for installation, module, resource_count in rows
        ]
    }


@app.get("/workspaces/{workspace_id}/datasets", tags=["datasets"])
def list_workspace_datasets(
    workspace_id: UUID,
    db: DbSession,
    kind: str | None = None,
    status: str | None = None,
) -> dict[str, list[DatasetSummary]]:
    _get_workspace(db, workspace_id)
    query = select(Dataset).where(Dataset.workspace_id == workspace_id)
    if kind:
        query = query.where(Dataset.dataset_kind == kind)
    if status:
        query = query.where(Dataset.status == status)
    datasets = db.scalars(query.order_by(Dataset.created_at.desc())).all()
    return {"datasets": [_dataset_summary(dataset) for dataset in datasets]}


@app.post("/workspaces/{workspace_id}/datasets", tags=["datasets"], status_code=201)
def create_dataset(
    workspace_id: UUID,
    payload: DatasetCreate,
    db: DbSession,
) -> DatasetDetail:
    workspace = _get_workspace(db, workspace_id)
    slug = _slugify(payload.name)
    dataset = Dataset(
        tenant_id=workspace.tenant_id,
        workspace_id=workspace.id,
        name=payload.name,
        slug=slug,
        description=payload.description,
        dataset_kind=payload.dataset_kind,
        status="draft",
        labels_json=payload.labels,
        classification_json=payload.classification,
    )
    db.add(dataset)
    db.flush()
    _create_job_eventless_dataset_setup(db, dataset)
    db.commit()
    db.refresh(dataset)
    return _dataset_detail(dataset)


@app.get("/datasets/{dataset_id}", tags=["datasets"])
def get_dataset(dataset_id: UUID, db: DbSession) -> DatasetDetail:
    return _dataset_detail(_get_dataset(db, dataset_id))


@app.get("/datasets/{dataset_id}/card", tags=["datasets"])
def get_dataset_card(dataset_id: UUID, db: DbSession) -> DatasetCard:
    dataset = _get_dataset(db, dataset_id)
    entity_types = db.scalars(
        select(EntityType.name)
        .where(
            EntityType.workspace_id == dataset.workspace_id,
            EntityType.dataset_id.is_(None),
        )
        .order_by(EntityType.name.asc())
    ).all()
    metrics = db.scalars(
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
    return DatasetCard(
        id=dataset.id,
        name=dataset.name,
        dataset_kind=dataset.dataset_kind,
        summary=summary,
        entity_types=list(entity_types),
        metrics=list(metrics),
        freshness_at=dataset.freshness_at,
        next_resources=[
            f"meaninggrid://dataset/{dataset.id}/site-audit/overview",
            f"meaninggrid://dataset/{dataset.id}/context",
        ],
    )


@app.get("/datasets/{dataset_id}/site-audit/overview", tags=["site-audit"])
def get_site_audit_overview(dataset_id: UUID, db: DbSession) -> SiteAuditOverview:
    dataset = _get_dataset(db, dataset_id)
    pages_crawled = db.scalar(
        select(func.count()).select_from(_page_entities_query(dataset.id).subquery())
    )
    technical_avg = _metric_average(db, dataset.id, "technical_score")
    meta_missing = _metric_count(db, dataset.id, "meta_description_length", 0)
    title_missing = _metric_count(db, dataset.id, "title_length", 0)
    top_issue_types = []
    if meta_missing:
        top_issue_types.append({"type": "missing_meta_description", "count": meta_missing})
    if title_missing:
        top_issue_types.append({"type": "missing_title", "count": title_missing})
    return SiteAuditOverview(
        pages_crawled=pages_crawled or 0,
        technical_score_avg=technical_avg,
        geo_readiness_avg=None,
        open_insights=0,
        top_issue_types=top_issue_types,
    )


@app.get("/datasets/{dataset_id}/site-audit/pages", tags=["site-audit"])
def list_site_audit_pages(dataset_id: UUID, db: DbSession) -> dict[str, list[SiteAuditPageRow]]:
    dataset = _get_dataset(db, dataset_id)
    pages = db.scalars(_page_entities_query(dataset.id).order_by(Entity.canonical_uri.asc())).all()
    rows = []
    for page in pages:
        rows.append(
            SiteAuditPageRow(
                entity_id=page.id,
                label=page.label,
                canonical_uri=page.canonical_uri,
                title=page.properties_json.get("title"),
                status_code=page.properties_json.get("status_code"),
                word_count=_metric_value(db, dataset.id, page.id, "word_count"),
                technical_score=_metric_value(db, dataset.id, page.id, "technical_score"),
            )
        )
    return {"pages": rows}


@app.post("/datasets/{dataset_id}/site-audit/crawls", tags=["site-audit"], status_code=202)
def start_site_audit_crawl(
    dataset_id: UUID,
    payload: SiteCrawlCreate,
    db: DbSession,
) -> JobQueuedResponse:
    dataset = _get_dataset(db, dataset_id)
    source, stream = _ensure_website_source(db, dataset, payload)
    job = _create_job(
        db,
        dataset=dataset,
        source=source,
        job_type="crawl_website",
        payload={
            "crawl": payload.model_dump(),
            "data_stream_id": str(stream.id),
        },
        progress_total=payload.max_pages,
        progress_message="Queued website crawl",
    )
    db.commit()
    db.refresh(job)
    return JobQueuedResponse(job_id=job.id, dataset_id=dataset.id, status=job.status)


@app.post("/datasets/{dataset_id}/site-audit/run", tags=["site-audit"], status_code=202)
def run_site_audit(
    dataset_id: UUID,
    payload: SiteAuditRunCreate,
    db: DbSession,
) -> JobQueuedResponse:
    dataset = _get_dataset(db, dataset_id)
    source = None
    stream = None
    if payload.crawl is not None:
        source, stream = _ensure_website_source(db, dataset, payload.crawl)
    job = _create_job(
        db,
        dataset=dataset,
        source=source,
        job_type="run_site_audit_v0",
        payload={
            "preset": payload.preset,
            "crawl": payload.crawl.model_dump() if payload.crawl else None,
            "data_stream_id": str(stream.id) if stream else None,
        },
        progress_total=100,
        progress_message="Queued Site Audit pipeline",
    )
    db.commit()
    db.refresh(job)
    return JobQueuedResponse(job_id=job.id, dataset_id=dataset.id, status=job.status)


@app.get("/jobs/{job_id}", tags=["jobs"])
def get_job(job_id: UUID, db: DbSession) -> JobSummary:
    return _job_summary(_get_job(db, job_id))


@app.get("/jobs/{job_id}/events", tags=["jobs"])
def list_job_events(
    job_id: UUID,
    db: DbSession,
) -> dict[str, list[JobEventSummary]]:
    _get_job(db, job_id)
    events = db.scalars(
        select(JobEvent).where(JobEvent.job_id == job_id).order_by(JobEvent.created_at.asc())
    ).all()
    return {
        "events": [
            JobEventSummary(
                id=event.id,
                event_type=event.event_type,
                message=event.message,
                progress_current=event.progress_current,
                progress_total=event.progress_total,
                payload=event.payload_json,
                created_at=event.created_at,
            )
            for event in events
        ]
    }


@app.post("/jobs/{job_id}/cancel", tags=["jobs"])
def cancel_job(job_id: UUID, db: DbSession) -> JobSummary:
    job = _get_job(db, job_id)
    if job.status in {"queued", "running"}:
        job.status = "canceled"
        job.progress_message = "Canceled by user"
        db.add(
            JobEvent(
                job_id=job.id,
                event_type="job_canceled",
                message="Job canceled by user.",
                payload_json={},
            )
        )
        db.commit()
        db.refresh(job)
    return _job_summary(job)


@app.post("/jobs/{job_id}/run-now", tags=["jobs"])
def run_job_now(job_id: UUID, db: DbSession) -> JobSummary:
    job = _get_job(db, job_id)
    if job.job_type != "crawl_website":
        raise ApiError(400, "unsupported_job_type", "Only crawl_website jobs can run locally now.")
    if job.status not in {"queued", "failed"}:
        raise ApiError(409, "job_not_runnable", "Job is not in a runnable state.")
    run_crawl_job(db, str(job.id))
    db.refresh(job)
    return _job_summary(job)


def _safe_check(check: Any) -> str:
    try:
        return check()
    except Exception as exc:
        return f"error: {exc.__class__.__name__}"


def _check_queue() -> str:
    Redis.from_url(settings.redis_url).ping()
    return "ok"


def _get_workspace(db: Session, workspace_id: UUID) -> Workspace:
    workspace = db.get(Workspace, workspace_id)
    if workspace is None:
        raise ApiError(404, "workspace_not_found", "Workspace was not found.")
    return workspace


def _get_dataset(db: Session, dataset_id: UUID) -> Dataset:
    dataset = db.get(Dataset, dataset_id)
    if dataset is None:
        raise ApiError(404, "dataset_not_found", "Dataset was not found.")
    return dataset


def _get_job(db: Session, job_id: UUID) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise ApiError(404, "job_not_found", "Job was not found.")
    return job


def _dataset_summary(dataset: Dataset) -> DatasetSummary:
    return DatasetSummary(
        id=dataset.id,
        name=dataset.name,
        dataset_kind=dataset.dataset_kind,
        status=dataset.status,
        freshness_at=dataset.freshness_at,
        entity_count=dataset.entity_count,
        content_unit_count=dataset.content_unit_count,
    )


def _dataset_detail(dataset: Dataset) -> DatasetDetail:
    return DatasetDetail(
        **_dataset_summary(dataset).model_dump(),
        workspace_id=dataset.workspace_id,
        slug=dataset.slug,
        description=dataset.description,
        source_count=dataset.source_count,
        labels=dataset.labels_json,
        classification=dataset.classification_json,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at,
    )


def _job_summary(job: Job) -> JobSummary:
    return JobSummary(
        id=job.id,
        job_type=job.job_type,
        status=job.status,
        progress_current=job.progress_current,
        progress_total=job.progress_total,
        progress_message=job.progress_message,
        started_at=job.started_at,
        finished_at=job.finished_at,
        error=job.error_json,
    )


def _page_entities_query(dataset_id: UUID):
    return select(Entity).join(EntityType, EntityType.id == Entity.entity_type_id).where(
        Entity.dataset_id == dataset_id,
        EntityType.name == "page",
    )


def _metric_value(db: Session, dataset_id: UUID, entity_id: UUID, metric_name: str) -> float | None:
    return db.scalar(
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


def _metric_average(db: Session, dataset_id: UUID, metric_name: str) -> float | None:
    value = db.scalar(
        select(func.avg(MetricValue.value_number))
        .join(MetricDefinition, MetricDefinition.id == MetricValue.metric_definition_id)
        .where(
            MetricValue.dataset_id == dataset_id,
            MetricDefinition.name == metric_name,
        )
    )
    return float(value) if value is not None else None


def _metric_count(db: Session, dataset_id: UUID, metric_name: str, value: float) -> int:
    count = db.scalar(
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


def _slugify(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "dataset"


def _create_job_eventless_dataset_setup(db: Session, dataset: Dataset) -> None:
    if dataset.dataset_kind != "site_audit":
        return
    db.add(
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


def _ensure_website_source(
    db: Session,
    dataset: Dataset,
    payload: SiteCrawlCreate,
) -> tuple[Source, DataStream]:
    source = db.scalar(
        select(Source).where(
            Source.dataset_id == dataset.id,
            Source.connector_type == "website_crawler",
            Source.display_name == payload.base_url,
        )
    )
    if source is None:
        source = Source(
            tenant_id=dataset.tenant_id,
            workspace_id=dataset.workspace_id,
            dataset_id=dataset.id,
            connector_type="website_crawler",
            connector_version="0.1.0",
            display_name=payload.base_url,
            labels_json={"module": "site_audit"},
            config_json={"base_url": payload.base_url},
        )
        db.add(source)
        db.flush()
        dataset.source_count += 1

    stream = db.scalar(
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
        db.add(stream)
        db.flush()
    return source, stream


def _create_job(
    db: Session,
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
    db.add(job)
    db.flush()
    db.add(
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
