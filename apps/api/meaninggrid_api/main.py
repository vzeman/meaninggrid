from contextlib import asynccontextmanager
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from meaninggrid_application import (
    ApplicationError,
    DatasetApplicationService,
    JobApplicationService,
    ModuleApplicationService,
    SiteAuditApplicationService,
    WorkspaceApplicationService,
)
from meaninggrid_application.services import (
    CreateDatasetCommand,
    RunSiteAuditCommand,
    StartSiteAuditCrawlCommand,
)
from meaninggrid_core.config import get_settings
from meaninggrid_core.health import build_health_status
from meaninggrid_db.database import check_database, session_scope
from meaninggrid_db.models import Dataset, Job
from meaninggrid_db.seed import ensure_local_seed
from meaninggrid_vectorstores import check_qdrant
from redis import Redis
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


@app.exception_handler(ApplicationError)
async def application_error_handler(request, exc: ApplicationError):
    return await api_error_handler(
        request,
        ApiError(exc.status_code, exc.code, exc.message, exc.details),
    )

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
    status["vector_store"] = _safe_check(check_qdrant)
    if any(status[key] != "ok" for key in ("database", "queue", "vector_store")):
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
    workspaces = WorkspaceApplicationService(db).list_workspaces()
    return {
        "workspaces": [
            WorkspaceSummary(id=workspace.id, name=workspace.name, slug=workspace.slug)
            for workspace in workspaces
        ]
    }


@app.get("/modules", tags=["modules"])
def list_modules(db: DbSession) -> dict[str, list[ModuleSummary]]:
    modules = ModuleApplicationService(db).list_modules()
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
    rows = ModuleApplicationService(db).list_workspace_modules(workspace_id)
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
    datasets = DatasetApplicationService(db).list_workspace_datasets(workspace_id, kind, status)
    return {"datasets": [_dataset_summary(dataset) for dataset in datasets]}


@app.post("/workspaces/{workspace_id}/datasets", tags=["datasets"], status_code=201)
def create_dataset(
    workspace_id: UUID,
    payload: DatasetCreate,
    db: DbSession,
) -> DatasetDetail:
    dataset = DatasetApplicationService(db).create_dataset(
        CreateDatasetCommand(
            workspace_id=workspace_id,
            name=payload.name,
            dataset_kind=payload.dataset_kind,
            description=payload.description,
            labels=payload.labels,
            classification=payload.classification,
        )
    )
    return _dataset_detail(dataset)


@app.get("/datasets/{dataset_id}", tags=["datasets"])
def get_dataset(dataset_id: UUID, db: DbSession) -> DatasetDetail:
    return _dataset_detail(DatasetApplicationService(db).get_dataset(dataset_id))


@app.get("/datasets/{dataset_id}/card", tags=["datasets"])
def get_dataset_card(dataset_id: UUID, db: DbSession) -> DatasetCard:
    card = DatasetApplicationService(db).build_dataset_card(dataset_id)
    dataset = card["dataset"]
    return DatasetCard(
        id=dataset.id,
        name=dataset.name,
        dataset_kind=dataset.dataset_kind,
        summary=card["summary"],
        entity_types=card["entity_types"],
        metrics=card["metrics"],
        freshness_at=dataset.freshness_at,
        next_resources=card["next_resources"],
    )


@app.get("/datasets/{dataset_id}/site-audit/overview", tags=["site-audit"])
def get_site_audit_overview(dataset_id: UUID, db: DbSession) -> SiteAuditOverview:
    return SiteAuditOverview(**SiteAuditApplicationService(db).overview(dataset_id))


@app.get("/datasets/{dataset_id}/site-audit/pages", tags=["site-audit"])
def list_site_audit_pages(dataset_id: UUID, db: DbSession) -> dict[str, list[SiteAuditPageRow]]:
    rows = []
    for row in SiteAuditApplicationService(db).pages(dataset_id):
        page = row["entity"]
        rows.append(
            SiteAuditPageRow(
                entity_id=page.id,
                label=page.label,
                canonical_uri=page.canonical_uri,
                title=row["title"],
                status_code=row["status_code"],
                word_count=row["word_count"],
                technical_score=row["technical_score"],
            )
        )
    return {"pages": rows}


@app.post("/datasets/{dataset_id}/site-audit/crawls", tags=["site-audit"], status_code=202)
def start_site_audit_crawl(
    dataset_id: UUID,
    payload: SiteCrawlCreate,
    db: DbSession,
) -> JobQueuedResponse:
    job = SiteAuditApplicationService(db).start_crawl(
        _crawl_command(dataset_id, payload),
    )
    return JobQueuedResponse(job_id=job.id, dataset_id=dataset_id, status=job.status)


@app.post("/datasets/{dataset_id}/site-audit/run", tags=["site-audit"], status_code=202)
def run_site_audit(
    dataset_id: UUID,
    payload: SiteAuditRunCreate,
    db: DbSession,
) -> JobQueuedResponse:
    job = SiteAuditApplicationService(db).start_run(
        RunSiteAuditCommand(
            dataset_id=dataset_id,
            preset=payload.preset,
            crawl=_crawl_command(dataset_id, payload.crawl) if payload.crawl else None,
        )
    )
    return JobQueuedResponse(job_id=job.id, dataset_id=dataset_id, status=job.status)


@app.get("/jobs/{job_id}", tags=["jobs"])
def get_job(job_id: UUID, db: DbSession) -> JobSummary:
    return _job_summary(JobApplicationService(db).get_job(job_id))


@app.get("/jobs/{job_id}/events", tags=["jobs"])
def list_job_events(
    job_id: UUID,
    db: DbSession,
) -> dict[str, list[JobEventSummary]]:
    events = JobApplicationService(db).list_job_events(job_id)
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
    return _job_summary(JobApplicationService(db).cancel_job(job_id))


@app.post("/jobs/{job_id}/run-now", tags=["jobs"])
def run_job_now(job_id: UUID, db: DbSession) -> JobSummary:
    return _job_summary(JobApplicationService(db).run_job_now(job_id))


def _safe_check(check: Any) -> str:
    try:
        return check()
    except Exception as exc:
        return f"error: {exc.__class__.__name__}"


def _check_queue() -> str:
    Redis.from_url(settings.redis_url).ping()
    return "ok"


def _crawl_command(dataset_id: UUID, payload: SiteCrawlCreate) -> StartSiteAuditCrawlCommand:
    return StartSiteAuditCrawlCommand(
        dataset_id=dataset_id,
        base_url=payload.base_url,
        max_pages=payload.max_pages,
        respect_robots=payload.respect_robots,
        render_javascript=payload.render_javascript,
        include_patterns=payload.include_patterns,
        exclude_patterns=payload.exclude_patterns,
    )


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
