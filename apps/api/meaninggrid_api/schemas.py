from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

JsonObject = dict[str, Any]


class ErrorBody(BaseModel):
    code: str
    message: str
    details: JsonObject = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorBody


class WorkspaceSummary(BaseModel):
    id: UUID
    name: str
    slug: str


class ModuleSummary(BaseModel):
    module_key: str
    name: str
    current_version: str
    bundled: bool
    status: str


class ModuleInstallationSummary(BaseModel):
    id: UUID
    module_key: str
    name: str
    module_version: str
    enabled: bool
    resource_count: int


class DatasetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    dataset_kind: str = Field(default="site_audit", min_length=1, max_length=80)
    description: str | None = None
    labels: JsonObject = Field(default_factory=dict)
    classification: JsonObject = Field(default_factory=dict)


class DatasetSummary(BaseModel):
    id: UUID
    name: str
    dataset_kind: str
    status: str
    freshness_at: datetime | None
    entity_count: int
    content_unit_count: int


class DatasetDetail(DatasetSummary):
    workspace_id: UUID
    slug: str | None
    description: str | None
    source_count: int
    labels: JsonObject
    classification: JsonObject
    created_at: datetime
    updated_at: datetime | None


class DatasetCard(BaseModel):
    id: UUID
    name: str
    dataset_kind: str
    summary: str
    entity_types: list[str]
    metrics: list[str]
    freshness_at: datetime | None
    next_resources: list[str]


class SiteCrawlCreate(BaseModel):
    base_url: str = Field(min_length=1, max_length=2000)
    max_pages: int = Field(default=100, ge=1, le=10000)
    respect_robots: bool = True
    render_javascript: bool = False
    include_patterns: list[str] = Field(default_factory=list)
    exclude_patterns: list[str] = Field(default_factory=list)


class SiteAuditRunCreate(BaseModel):
    preset: str = "site_audit_v0"
    crawl: SiteCrawlCreate | None = None


class JobSummary(BaseModel):
    id: UUID
    job_type: str
    status: str
    progress_current: int
    progress_total: int | None
    progress_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    error: JsonObject | None


class JobQueuedResponse(BaseModel):
    job_id: UUID
    dataset_id: UUID | None = None
    status: str


class JobEventSummary(BaseModel):
    id: UUID
    event_type: str
    message: str | None
    progress_current: int | None
    progress_total: int | None
    payload: JsonObject
    created_at: datetime


class SiteAuditOverview(BaseModel):
    pages_crawled: int
    technical_score_avg: float | None
    geo_readiness_avg: float | None
    open_insights: int
    top_issue_types: list[JsonObject]


class SiteAuditPageRow(BaseModel):
    entity_id: UUID
    label: str
    canonical_uri: str | None
    title: str | None
    status_code: int | None
    word_count: int | None
    technical_score: float | None
