# API And MCP Surface

## API Principles

The API should mirror the universal model and support both UI and automation.

Rules:

- all endpoints tenant-scoped through auth
- no raw source access without explicit permission
- long-running operations return job/run IDs
- analysis artifacts are immutable
- context pack creation is explicit and logged

## REST API Draft

### Health

```text
GET /health
GET /version
```

### Agent Sessions

```text
POST /agent-sessions
GET /agent-sessions/{session_id}
DELETE /agent-sessions/{session_id}
GET /agent-sessions/{session_id}/audit-events
```

### Workspaces

```text
GET /workspaces
POST /workspaces
GET /workspaces/{workspace_id}
PATCH /workspaces/{workspace_id}
DELETE /workspaces/{workspace_id}
```

### Datasets

```text
GET /workspaces/{workspace_id}/datasets
POST /workspaces/{workspace_id}/datasets
GET /datasets/{dataset_id}
PATCH /datasets/{dataset_id}
DELETE /datasets/{dataset_id}
GET /datasets/{dataset_id}/card
GET /datasets/{dataset_id}/quality
```

### Modules

```text
GET /modules
GET /modules/{module_key}
POST /workspaces/{workspace_id}/modules/{module_key}/install
DELETE /workspaces/{workspace_id}/modules/{module_key}
GET /workspaces/{workspace_id}/modules
GET /workspaces/{workspace_id}/modules/{module_key}/resources
```

### Sources And Connectors

```text
GET /connectors
GET /connectors/{connector_type}/manifest
POST /datasets/{dataset_id}/sources
GET /sources/{source_id}
POST /sources/{source_id}/test
POST /sources/{source_id}/sync
GET /sources/{source_id}/sync-runs
```

### Streams And Changes

```text
GET /datasets/{dataset_id}/streams
POST /datasets/{dataset_id}/streams
GET /streams/{stream_id}
PATCH /streams/{stream_id}
POST /streams/{stream_id}/sync
POST /streams/{stream_id}/backfill
GET /streams/{stream_id}/events
GET /datasets/{dataset_id}/changes
POST /webhooks/{source_id}/{stream_id}
```

### Import

```text
POST /datasets/{dataset_id}/import/csv
POST /datasets/{dataset_id}/import/jsonl
POST /datasets/{dataset_id}/import/website
GET /import-jobs/{job_id}
```

### Push API

```text
POST /datasets/{dataset_id}/push/events
POST /datasets/{dataset_id}/push/entities
POST /datasets/{dataset_id}/push/documents
POST /datasets/{dataset_id}/push/metrics
POST /datasets/{dataset_id}/push/relations
POST /datasets/{dataset_id}/push/batch
```

### Labels

```text
GET /workspaces/{workspace_id}/labels
POST /workspaces/{workspace_id}/labels
PATCH /workspaces/{workspace_id}/labels/{label_key}
GET /datasets/{dataset_id}/labels
POST /datasets/{dataset_id}/labels/merge
```

### Entity Model

```text
GET /datasets/{dataset_id}/entity-types
POST /datasets/{dataset_id}/entity-types
GET /entity-types/{entity_type_id}
PATCH /entity-types/{entity_type_id}

GET /datasets/{dataset_id}/entities
GET /entities/{entity_id}
PATCH /entities/{entity_id}
GET /entities/{entity_id}/relations
GET /entities/{entity_id}/content-units
GET /entities/{entity_id}/metrics
```

### Content

```text
GET /datasets/{dataset_id}/content-units
GET /content-units/{content_unit_id}
GET /content-units/{content_unit_id}/chunks
GET /content-chunks/{content_chunk_id}
```

### Metrics

```text
GET /datasets/{dataset_id}/metric-definitions
POST /datasets/{dataset_id}/metric-definitions
GET /entities/{entity_id}/metric-values
POST /datasets/{dataset_id}/metric-values
```

### Embeddings

```text
POST /datasets/{dataset_id}/embedding-runs
GET /embedding-runs/{run_id}
GET /datasets/{dataset_id}/embedding-status
```

### Search

```text
POST /datasets/{dataset_id}/search/semantic
POST /datasets/{dataset_id}/search/hybrid
POST /entities/{entity_id}/similar
POST /content-chunks/{content_chunk_id}/similar
```

### Analysis

```text
POST /datasets/{dataset_id}/analysis-runs
GET /datasets/{dataset_id}/analysis-runs
GET /analysis-runs/{analysis_run_id}
GET /analysis-runs/{analysis_run_id}/artifacts
GET /analysis-runs/{analysis_run_id}/artifacts/{artifact_type}
```

### Insights

```text
GET /datasets/{dataset_id}/insights
GET /insights/{insight_id}
GET /insights/{insight_id}/evidence
POST /insights/{insight_id}/accept
POST /insights/{insight_id}/reject
```

### Context Packs

```text
POST /datasets/{dataset_id}/context-packs
POST /datasets/{dataset_id}/context-packs/delta
GET /context-packs/{context_pack_id}
GET /context-packs/{context_pack_id}/resources
DELETE /context-packs/{context_pack_id}
```

### Streaming Agent Context

```text
GET /datasets/{dataset_id}/context-units
GET /context-units/{context_unit_id}
GET /context-units/{context_unit_id}/evidence
GET /entities/{entity_id}/context-units

POST /datasets/{dataset_id}/context-subscriptions
GET /datasets/{dataset_id}/context-subscriptions
GET /context-subscriptions/{subscription_id}
DELETE /context-subscriptions/{subscription_id}
GET /context-subscriptions/{subscription_id}/notifications
POST /context-subscriptions/{subscription_id}/resume

POST /context-notifications/{notification_id}/ack
POST /source-events/{source_event_id}/routing-feedback
GET /datasets/{dataset_id}/event-routes
```

### Reports And Exports

```text
POST /datasets/{dataset_id}/reports
GET /reports/{report_id}
POST /analysis-runs/{analysis_run_id}/exports
GET /exports/{export_id}
```

## MCP Resource URIs

```text
meaninggrid://workspaces
meaninggrid://agent-session/{session_id}
meaninggrid://workspace/{workspace_id}/overview
meaninggrid://workspace/{workspace_id}/datasets
meaninggrid://workspace/{workspace_id}/modules
meaninggrid://module/{module_key}/card
meaninggrid://dataset/{dataset_id}/card
meaninggrid://dataset/{dataset_id}/schema
meaninggrid://dataset/{dataset_id}/metrics
meaninggrid://dataset/{dataset_id}/quality
meaninggrid://dataset/{dataset_id}/labels
meaninggrid://dataset/{dataset_id}/analysis-runs
meaninggrid://dataset/{dataset_id}/streams
meaninggrid://dataset/{dataset_id}/recent-changes
meaninggrid://context-stream/{dataset_id}
meaninggrid://context-stream/{dataset_id}/subscription/{subscription_id}
meaninggrid://stream/{stream_id}/status
meaninggrid://entity-type/{entity_type_id}/card
meaninggrid://entity/{entity_id}/profile
meaninggrid://entity/{entity_id}/content
meaninggrid://entity/{entity_id}/metrics
meaninggrid://entity/{entity_id}/context-units
meaninggrid://cluster/{cluster_id}/summary
meaninggrid://analysis/{analysis_id}/summary
meaninggrid://analysis/{analysis_id}/artifact/{artifact_type}
meaninggrid://insight/{insight_id}
meaninggrid://insight/{insight_id}/evidence
meaninggrid://context-unit/{context_unit_id}
meaninggrid://context-unit/{context_unit_id}/evidence
meaninggrid://context-pack/{context_pack_id}
meaninggrid://agent-subscription/{subscription_id}
meaninggrid://shared-memory/{memory_item_id}
meaninggrid://source/{raw_object_id}/raw
```

## MCP Tools Draft

### list_datasets

Input:

```json
{
  "workspace_id": "ws_123"
}
```

Output:

```json
{
  "datasets": [
    {
      "id": "ds_123",
      "name": "Website Crawl",
      "kind": "website",
      "freshness_at": "2026-05-08T07:00:00Z"
    }
  ]
}
```

### list_streams

Input:

```json
{
  "dataset_id": "ds_123"
}
```

Output:

```json
{
  "streams": [
    {
      "id": "str_123",
      "name": "Google Search Console",
      "sync_mode": "periodic",
      "watermark_at": "2026-05-08T06:00:00Z",
      "status": "active"
    }
  ]
}
```

### build_context_pack

Input:

```json
{
  "dataset_id": "ds_123",
  "task": "Find outliers and explain why they matter",
  "budget_tokens": 30000,
  "filters": {
    "entity_type": "page"
  }
}
```

Output:

```json
{
  "context_pack_id": "ctx_123",
  "resource_uri": "meaninggrid://context-pack/ctx_123",
  "summary": "Context pack created with dataset card, schema, outlier table, and evidence links."
}
```

### build_delta_context_pack

Input:

```json
{
  "dataset_id": "ds_123",
  "since": "2026-05-01T00:00:00Z",
  "task": "Summarize new keyword/content mismatches",
  "budget_tokens": 20000
}
```

Output:

```json
{
  "context_pack_id": "ctx_delta_123",
  "resource_uri": "meaninggrid://context-pack/ctx_delta_123",
  "summary": "Delta context pack created from 428 changed metrics, 12 changed pages, and 73 new keywords."
}
```

### semantic_search

Input:

```json
{
  "dataset_id": "ds_123",
  "query": "pricing objections",
  "filters": {
    "entity_type": "call"
  },
  "limit": 10
}
```

### compare_cohorts

Input:

```json
{
  "dataset_id": "ds_123",
  "cohort_a": {
    "name": "won calls",
    "filter": {
      "metric": "sale_closed",
      "equals": true
    }
  },
  "cohort_b": {
    "name": "lost calls",
    "filter": {
      "metric": "sale_closed",
      "equals": false
    }
  },
  "metric_ids": ["sale_closed", "duration"]
}
```

### get_evidence

Input:

```json
{
  "insight_id": "ins_123",
  "limit": 20,
  "redaction": "policy_default"
}
```

### run_backfill

Input:

```json
{
  "stream_id": "str_123",
  "date_from": "2025-01-01",
  "date_to": "2026-05-08"
}
```

### create_monitor

Input:

```json
{
  "dataset_id": "ds_123",
  "name": "Paid keywords without content match",
  "condition": {
    "type": "semantic_alignment_below_threshold",
    "source_entity_type": "search_term",
    "target_entity_type": "page",
    "threshold": 0.72,
    "metric_filter": {
      "cost": {
        "gt": 100
      }
    }
  }
}
```

### subscribe_context

Input:

```json
{
  "dataset_id": "ds_marketing",
  "filters": {
    "and": [
      {"eq": {"field": "labels.module", "value": "marketing"}},
      {"gte": {"field": "metrics.cost", "value": 100}},
      {"lt": {"field": "analysis.best_page_alignment", "value": 0.72}}
    ]
  },
  "semantic_interest": "paid keywords without enough supporting website content",
  "priority_min": "p1",
  "delivery": "notify_then_pull"
}
```

Output:

```json
{
  "subscription_id": "sub_123",
  "resource_uri": "meaninggrid://context-stream/ds_marketing/subscription/sub_123",
  "summary": "Subscription created for high-priority marketing context changes."
}
```

### list_changed_context

Input:

```json
{
  "subscription_id": "sub_123",
  "after_sequence": "18422",
  "limit": 20
}
```

Output:

```json
{
  "notifications": [
    {
      "notification_id": "ntf_123",
      "sequence": "18423",
      "priority": "p1",
      "resource_uri": "meaninggrid://context-unit/cu_123",
      "summary": "New paid search term has weak page alignment."
    }
  ]
}
```

### ack_context_notification

Input:

```json
{
  "notification_id": "ntf_123",
  "verdict": "appropriate"
}
```

### read_context_unit

Input:

```json
{
  "context_unit_id": "cu_123"
}
```

## Prompt Templates

### analyze_dataset

Purpose:

Produce a structured overview of a dataset.

Inputs:

- dataset_id
- audience
- budget_tokens

Output:

- summary
- key clusters
- outliers
- quality concerns
- recommended next analyses

### compare_cohorts

Purpose:

Explain how two cohorts differ and what actions follow.

Inputs:

- dataset_id
- cohort_a
- cohort_b
- metric focus

Output:

- strongest semantic differences
- business impact
- evidence
- recommended actions

### explain_outlier

Purpose:

Explain why an entity is semantically unusual.

Inputs:

- entity_id
- comparison population

Output:

- outlier reason
- nearest neighbors
- parent drift
- evidence
- possible actions

### prepare_executive_report

Purpose:

Create a concise report for business users.

Inputs:

- dataset_id
- analysis_run_id
- audience
- length

Output:

- executive summary
- findings
- evidence references
- recommendations
- risks

## CLI Draft

```bash
meaninggrid init
meaninggrid serve
meaninggrid import website https://example.com --max-pages 500
meaninggrid import csv ./companies.csv --dataset "Companies"
meaninggrid import jsonl ./calls.jsonl --dataset "Calls"
meaninggrid stream create google-search-console --dataset "Marketing"
meaninggrid stream sync str_123
meaninggrid stream backfill str_123 --from 2025-01-01 --to 2026-05-08
meaninggrid embed ds_123
meaninggrid analyze ds_123
meaninggrid search ds_123 "pricing objections"
meaninggrid context-pack ds_123 "Compare won and lost calls"
meaninggrid context-pack-delta ds_123 --since 2026-05-01 "Summarize new keyword gaps"
meaninggrid context subscribe ds_123 --filter ./filters/high-cost-gap.json
meaninggrid context changes sub_123 --after 18422
meaninggrid mcp start
```
