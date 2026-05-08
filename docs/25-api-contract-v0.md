# API Contract V0

## Purpose

This document defines the first REST API surface for MeaningGrid v0.1.

The API should support the web UI, CLI, and MCP server. It should not expose
every future capability.

## API Principles

- JSON request/response.
- Tenant/workspace scoped internally, even in local mode.
- Long-running work returns a job ID.
- Every read response includes stable IDs.
- Raw source access is explicit.
- Errors are structured.
- API models should be implemented with Pydantic.

Base URL:

```text
http://localhost:8000
```

## Error Shape

```json
{
  "error": {
    "code": "dataset_not_found",
    "message": "Dataset was not found.",
    "details": {}
  }
}
```

## Health

### GET /health

Response:

```json
{
  "status": "ok",
  "version": "0.1.0",
  "database": "ok",
  "queue": "ok"
}
```

### GET /version

Response:

```json
{
  "version": "0.1.0",
  "commit": "dev",
  "build_time": null
}
```

## Workspaces

### GET /workspaces

Response:

```json
{
  "workspaces": [
    {
      "id": "ws_...",
      "name": "Default Workspace",
      "slug": "default"
    }
  ]
}
```

## Modules

### GET /modules

Response:

```json
{
  "modules": [
    {
      "module_key": "site_audit",
      "name": "Site Audit And GEO Intelligence",
      "current_version": "0.1.0",
      "bundled": true,
      "status": "active"
    }
  ]
}
```

### GET /workspaces/{workspace_id}/modules

Returns installed modules for a workspace.

## Datasets

### GET /workspaces/{workspace_id}/datasets

Query:

```text
kind=site_audit
status=active
```

Response:

```json
{
  "datasets": [
    {
      "id": "ds_...",
      "name": "Example Site",
      "dataset_kind": "site_audit",
      "status": "active",
      "freshness_at": "2026-05-08T10:00:00Z",
      "entity_count": 123,
      "content_unit_count": 830
    }
  ]
}
```

### POST /workspaces/{workspace_id}/datasets

Request:

```json
{
  "name": "Example Site",
  "dataset_kind": "site_audit",
  "description": "Audit of example.com",
  "labels": {
    "module": "site_audit"
  }
}
```

Response:

```json
{
  "id": "ds_...",
  "name": "Example Site",
  "dataset_kind": "site_audit",
  "status": "draft"
}
```

### GET /datasets/{dataset_id}

Returns dataset detail with counts and latest job/analysis status.

### GET /datasets/{dataset_id}/card

Returns an agent/UI-friendly dataset summary.

Response:

```json
{
  "id": "ds_...",
  "name": "Example Site",
  "dataset_kind": "site_audit",
  "summary": "Website crawl with 87 pages, 412 paragraphs, and 12 open insights.",
  "entity_types": ["domain", "page", "crawl_run"],
  "metrics": ["technical_score", "geo_readiness_score"],
  "freshness_at": "2026-05-08T10:00:00Z",
  "next_resources": []
}
```

## Site Audit Workflow

### POST /datasets/{dataset_id}/site-audit/crawls

Starts a crawl job.

Request:

```json
{
  "base_url": "https://example.com",
  "max_pages": 100,
  "respect_robots": true,
  "render_javascript": false,
  "include_patterns": [],
  "exclude_patterns": []
}
```

Response:

```json
{
  "job_id": "job_...",
  "dataset_id": "ds_...",
  "status": "queued"
}
```

### POST /datasets/{dataset_id}/site-audit/run

Starts the full pipeline or continues from existing crawl data.

Request:

```json
{
  "preset": "site_audit_v0",
  "crawl": {
    "base_url": "https://example.com",
    "max_pages": 100
  }
}
```

Response:

```json
{
  "job_id": "job_...",
  "status": "queued"
}
```

## Jobs

### GET /jobs/{job_id}

Response:

```json
{
  "id": "job_...",
  "job_type": "run_site_audit_v0",
  "status": "running",
  "progress_current": 42,
  "progress_total": 100,
  "progress_message": "Embedding page chunks",
  "started_at": "2026-05-08T10:00:00Z",
  "finished_at": null,
  "error": null
}
```

### GET /jobs/{job_id}/events

Returns progress events.

### POST /jobs/{job_id}/cancel

Best-effort cancellation.

## Entities And Pages

### GET /datasets/{dataset_id}/entities

Query:

```text
entity_type=page
limit=50
offset=0
q=pricing
```

Response:

```json
{
  "items": [
    {
      "id": "ent_...",
      "entity_type": "page",
      "label": "Pricing",
      "canonical_uri": "https://example.com/pricing",
      "properties": {
        "status_code": 200,
        "title": "Pricing"
      }
    }
  ],
  "total": 87
}
```

### GET /entities/{entity_id}

Returns entity profile.

### GET /entities/{entity_id}/content-units

Returns page title, meta description, headings, main content, paragraphs.

### GET /entities/{entity_id}/metrics

Returns latest metric values grouped by metric name.

### GET /entities/{entity_id}/relations

Returns links and semantic relations.

## Site Audit Views

These endpoints are optimized for UI convenience and backed by artifacts/core
tables.

### GET /datasets/{dataset_id}/site-audit/overview

Response:

```json
{
  "pages_crawled": 87,
  "technical_score_avg": 78.4,
  "geo_readiness_avg": 61.2,
  "open_insights": 18,
  "top_issue_types": [
    {"type": "missing_meta_description", "count": 12}
  ]
}
```

### GET /datasets/{dataset_id}/site-audit/pages

Returns page table rows with key metrics.

### GET /datasets/{dataset_id}/site-audit/issues

Query:

```text
severity=high
issue_type=duplicate_content
```

### GET /datasets/{dataset_id}/site-audit/clusters

Returns semantic clusters.

### GET /datasets/{dataset_id}/site-audit/outliers

Returns outlier pages.

### GET /datasets/{dataset_id}/site-audit/duplicates

Returns duplicate or near-duplicate page pairs.

### GET /datasets/{dataset_id}/site-audit/internal-link-opportunities

Returns suggested internal links.

### GET /datasets/{dataset_id}/site-audit/geo-readiness

Returns GEO scores and component breakdowns.

## Embeddings And Search

### POST /datasets/{dataset_id}/embedding-runs

Request:

```json
{
  "target": "content_chunks",
  "model": "default_local"
}
```

Response:

```json
{
  "embedding_run_id": "emb_run_...",
  "job_id": "job_..."
}
```

### POST /datasets/{dataset_id}/search/semantic

Request:

```json
{
  "query": "invoice approval workflow",
  "filters": {
    "eq": {
      "field": "entity_type",
      "value": "page"
    }
  },
  "limit": 10
}
```

Response:

```json
{
  "results": [
    {
      "score": 0.84,
      "entity_id": "ent_...",
      "content_chunk_id": "chk_...",
      "title": "Pricing",
      "text": "Relevant excerpt...",
      "resource_uri": "meaninggrid://entity/ent_..."
    }
  ]
}
```

## Analysis

### POST /datasets/{dataset_id}/analysis-runs

Request:

```json
{
  "analysis_type": "site_audit",
  "analysis_preset": "site_audit_v0",
  "input_spec": {}
}
```

Response:

```json
{
  "analysis_run_id": "an_...",
  "job_id": "job_...",
  "status": "queued"
}
```

### GET /analysis-runs/{analysis_run_id}

Returns status and metadata.

### GET /analysis-runs/{analysis_run_id}/artifacts

Returns artifact list.

### GET /analysis-runs/{analysis_run_id}/artifacts/{artifact_type}

Returns artifact JSON or signed artifact URL.

## Insights And Evidence

### GET /datasets/{dataset_id}/insights

Query:

```text
type=semantic_outlier
severity=high
status=open
```

### GET /insights/{insight_id}

Returns full insight.

### GET /insights/{insight_id}/evidence

Response:

```json
{
  "evidence": [
    {
      "entity_id": "ent_...",
      "content_unit_id": "cu_...",
      "quote": "The duplicated paragraph...",
      "score": 0.91,
      "explanation": "This paragraph is similar to another page."
    }
  ]
}
```

## Context Packs

### POST /datasets/{dataset_id}/context-packs

Request:

```json
{
  "task": "Prepare a GEO audit summary",
  "budget_tokens": 16000,
  "filters": {}
}
```

Response:

```json
{
  "context_pack_id": "ctx_...",
  "resource_uri": "meaninggrid://context-pack/ctx_..."
}
```

### GET /context-packs/{context_pack_id}

Returns pack JSON.

## Reports

### POST /datasets/{dataset_id}/reports

Request:

```json
{
  "template": "geo_readiness_report",
  "analysis_run_id": "an_..."
}
```

Response:

```json
{
  "report_id": "rep_...",
  "job_id": "job_..."
}
```

### GET /reports/{report_id}

Returns report metadata and artifact URL.

## Raw Source

### GET /raw-objects/{raw_object_id}

V0 can return metadata only by default.

Raw HTML access should require explicit query:

```text
?include_content=true
```

## MCP Equivalence

MCP server should call the same application services as the API.

MCP resources in v0:

```text
meaninggrid://workspaces
meaninggrid://dataset/{dataset_id}/card
meaninggrid://dataset/{dataset_id}/site-audit/overview
meaninggrid://entity/{entity_id}/profile
meaninggrid://insight/{insight_id}
meaninggrid://insight/{insight_id}/evidence
meaninggrid://context-pack/{context_pack_id}
```

MCP tools in v0:

```text
list_datasets()
get_dataset_card(dataset_id)
semantic_search(dataset_id, query, filters, limit)
get_entity_profile(entity_id)
build_context_pack(dataset_id, task, budget_tokens, filters)
get_evidence(insight_id, limit)
```

## OpenAPI Requirement

FastAPI should expose:

```text
/openapi.json
/docs
```

The TypeScript client should be generated from OpenAPI.
