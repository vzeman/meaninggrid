# Data Push, Labeling, And Filtering

## Purpose

MeaningGrid must make it easy for users, systems, modules, and AI agents to
push data into the core system and later retrieve it using rich labels,
metadata, permissions, time windows, and semantic filters.

This document defines:

- push methods
- accepted data formats
- canonical event envelopes
- document/entity labels
- metadata and dimensions
- source lineage
- ACL and classification labels
- filter grammar
- vector payload design
- MCP/API query behavior

## Design Goals

1. Accept data from simple scripts and enterprise streams.
2. Preserve raw data for reprocessing when retention policy allows it.
3. Normalize everything into entities, content units, metrics, and relations.
4. Support rich labeling at every layer.
5. Make labels usable in SQL, vector search, MCP, dashboards, and reports.
6. Keep access control and data classification separate from user tags.
7. Make every pushed event idempotent.

## Push Methods

### CLI

Good for local work, demos, and batch jobs.

Examples:

```bash
meaninggrid push jsonl ./tickets.jsonl --dataset support
meaninggrid push csv ./companies.csv --dataset vc --mapping vc_startups
meaninggrid push document ./contract.pdf --dataset legal --entity-type contract
meaninggrid push event ./event.json --stream google_ads
```

### REST API

Good for applications, scripts, and custom integrations.

Endpoints:

```text
POST /datasets/{dataset_id}/push/events
POST /datasets/{dataset_id}/push/entities
POST /datasets/{dataset_id}/push/documents
POST /datasets/{dataset_id}/push/metrics
POST /datasets/{dataset_id}/push/relations
POST /datasets/{dataset_id}/push/batch
```

### Webhook

Good for third-party systems that send events.

Endpoint:

```text
POST /webhooks/{source_id}/{stream_id}
```

### Event Stream

Good for high-volume enterprise use.

Supported later:

- Kafka
- Redpanda
- NATS JetStream
- AWS Kinesis
- Google Pub/Sub
- Azure Event Hubs

### File Drop

Good for secure environments.

The system watches a folder or object storage prefix:

```text
s3://bucket/meaninggrid/inbox/{workspace}/{dataset}/
minio://meaninggrid/inbox/
/data/meaninggrid/inbox/
```

### MCP Tool

Useful when an authorized AI agent creates annotations, notes, labels, or new
derived documents.

Examples:

```text
save_agent_note()
label_entity()
create_document()
push_metric_value()
create_relation()
```

## Accepted Formats

### JSONL

Preferred for developers and streaming-like batch imports.

One event per line.

```json
{"type":"entity.upsert","entity_type":"company","external_id":"acme","label":"ACME Ltd.","properties":{"country":"SK"}}
{"type":"content.add","entity_ref":"acme","unit_kind":"description","text":"ACME builds invoice automation software."}
{"type":"metric.observe","entity_ref":"acme","metric":"arr","value":1200000,"observed_at":"2026-05-08T00:00:00Z"}
```

### JSON Batch

Good for API calls.

```json
{
  "events": [
    {
      "type": "entity.upsert",
      "entity_type": "startup",
      "external_id": "startup_123",
      "label": "InvoiceFlow",
      "properties": {
        "stage": "seed",
        "market": "fintech"
      }
    }
  ]
}
```

### CSV

Good for business users and exports.

Needs mapping:

```yaml
entity_type: company
external_id_column: company_id
label_column: company_name
text_columns:
  - description
  - notes
metric_columns:
  revenue:
    column: revenue
    value_type: number
labels:
  source: crm_export
```

### XLSX

Good for multi-sheet business imports.

Mapping can define:

- sheet to entity type
- column to property
- column to text field
- column to metric
- column to relation

### Documents

Supported:

- PDF
- DOCX
- TXT
- Markdown
- HTML
- JSON
- XML

Each document should be pushed with metadata and labels.

### Multipart Upload

For binary documents:

```text
POST /datasets/{dataset_id}/push/documents
Content-Type: multipart/form-data

file=@contract.pdf
metadata={...json...}
```

## Canonical Push Envelope

Every pushed item should be wrapped or convertible into a canonical envelope.

```json
{
  "idempotency_key": "source:external-id:updated-at:hash",
  "type": "document.upsert",
  "source": {
    "source_id": "src_123",
    "external_id": "doc_456",
    "external_url": "https://example.com/doc/456",
    "system": "google_drive"
  },
  "time": {
    "occurred_at": "2026-05-08T09:00:00Z",
    "source_updated_at": "2026-05-08T08:55:00Z"
  },
  "labels": {
    "module": "legal",
    "project": "vendor_review",
    "environment": "production"
  },
  "classification": {
    "level": "confidential",
    "pii": false,
    "restricted": true
  },
  "acl": {
    "workspace_roles": ["legal_admin", "legal_viewer"],
    "users": [],
    "groups": ["legal"]
  },
  "payload": {}
}
```

## Streaming Envelope Extension

For event streams and long-running agent subscriptions, pushed items should be
convertible into a CloudEvents-compatible envelope. MeaningGrid can keep its
own fields, but should also expose standard event identity and routing fields.

Additional fields:

```json
{
  "specversion": "1.0",
  "id": "evt_01J...",
  "source": "meaninggrid://source/google_ads/src_123",
  "type": "marketing.search_term.observed",
  "subject": "keyword:kw_123",
  "time": "2026-05-08T09:15:00Z",
  "datacontenttype": "application/json",
  "dataschema": "meaninggrid://schema/marketing.search_term.observed/v1",
  "partitionkey": "dataset:ds_123:keyword:kw_123",
  "sequence": "18422",
  "traceparent": "00-...",
  "priority_hint": "normal",
  "route_hint": "batch"
}
```

MeaningGrid should derive these fields when the producer does not send them.

Rules:

- `source` plus `id` is the preferred event deduplication key.
- `partitionkey` is required for per-entity ordering and agent notification
  replay.
- `sequence` is required when the source has a stable ordering cursor.
- `subject` should identify the logical entity affected by the event.
- `priority_hint` and `route_hint` are advisory; MeaningGrid still computes the
  final route.
- labels, classification, ACLs, and source lineage remain mandatory for secure
  filtering.

## Event Types

### Entity Events

```text
entity.upsert
entity.delete
entity.restore
entity.label
entity.merge
```

### Content Events

```text
content.add
content.upsert
content.delete
content.label
document.upsert
document.delete
```

### Metric Events

```text
metric.define
metric.observe
metric.delete
```

### Relation Events

```text
relation.upsert
relation.delete
```

### Annotation Events

```text
annotation.add
annotation.update
annotation.delete
agent_note.add
human_feedback.add
```

## Entity Upsert Format

```json
{
  "type": "entity.upsert",
  "entity_type": "startup",
  "external_id": "invoiceflow",
  "label": "InvoiceFlow",
  "description": "AI invoice approval workflow platform.",
  "properties": {
    "stage": "seed",
    "country": "US",
    "market": "fintech"
  },
  "labels": {
    "module": "vc",
    "source": "application_form",
    "decision_status": "new"
  }
}
```

## Document Upsert Format

```json
{
  "type": "document.upsert",
  "entity_type": "contract",
  "external_id": "contract_2026_001",
  "label": "ACME Vendor Agreement",
  "document": {
    "filename": "vendor-agreement.pdf",
    "mime_type": "application/pdf",
    "uri": "s3://bucket/contracts/vendor-agreement.pdf",
    "text": null,
    "language": "en"
  },
  "labels": {
    "module": "legal",
    "contract_type": "vendor",
    "jurisdiction": "EU",
    "business_unit": "finance"
  },
  "classification": {
    "level": "restricted",
    "pii": false
  }
}
```

## Metric Observe Format

```json
{
  "type": "metric.observe",
  "entity_ref": {
    "entity_type": "keyword",
    "external_id": "kw_123"
  },
  "metric": "cost",
  "value": 152.42,
  "value_type": "number",
  "observed_at": "2026-05-08T00:00:00Z",
  "window": {
    "from": "2026-05-07T00:00:00Z",
    "to": "2026-05-08T00:00:00Z",
    "grain": "day"
  },
  "dimensions": {
    "campaign": "brand_search",
    "country": "SK",
    "device": "mobile"
  },
  "labels": {
    "module": "marketing",
    "channel": "paid_search"
  }
}
```

## Relation Upsert Format

```json
{
  "type": "relation.upsert",
  "from": {
    "entity_type": "campaign",
    "external_id": "cmp_1"
  },
  "to": {
    "entity_type": "page",
    "external_id": "https://example.com/pricing"
  },
  "relation_type": "links_to",
  "weight": 1.0,
  "confidence": 1.0,
  "labels": {
    "module": "marketing",
    "source": "google_ads"
  }
}
```

## Labeling Model

Labels should exist at multiple levels:

```text
dataset labels
source labels
stream labels
raw object labels
entity labels
relation labels
content unit labels
content chunk labels
metric labels
analysis labels
insight labels
context pack labels
```

## Label Types

### User Labels

Flexible tags from users or agents.

Examples:

```text
priority:high
owner:marketing
status:needs_review
topic:pricing
```

### Module Labels

Labels created by module templates.

Examples:

```text
module:marketing
campaign_type:paid_search
contract_type:vendor
startup_stage:seed
ticket_type:bug
```

### System Labels

Labels managed by MeaningGrid.

Examples:

```text
ingestion_status:processed
embedding_status:embedded
analysis_status:stale
pii_detected:true
```

### Classification Labels

Security-sensitive labels.

Examples:

```text
classification:public
classification:internal
classification:confidential
classification:restricted
contains_pii:true
contains_secret:true
```

### Access Labels

Used by policy engine.

Examples:

```text
workspace:marketing
group:legal
role:contract_viewer
tenant:customer_a
```

## Labels Vs Properties Vs Metrics

Use labels for filtering and grouping.

Use properties for descriptive attributes.

Use metrics for measured values over time.

Examples:

```text
label: module=marketing
property: product_name="Invoice Automation"
metric: revenue=120000 over day/country/channel
```

## Recommended Label Schema

Every pushed object can include:

```json
{
  "labels": {
    "module": "marketing",
    "project": "q2_growth",
    "owner": "content_team",
    "status": "needs_review",
    "topic": ["pricing", "workflow"],
    "language": "en",
    "country": "SK"
  }
}
```

Rules:

- keys should be snake_case
- values can be string, number, boolean, or string array
- avoid deeply nested labels
- high-cardinality values should usually be properties, not labels
- security classification should use `classification`, not ordinary labels

## Filtering

Filtering must work across:

- API
- MCP tools
- dashboards
- reports
- vector search payloads
- analysis runs
- context packs

## Filter Grammar

Canonical filter object:

```json
{
  "and": [
    {"eq": {"field": "entity_type", "value": "page"}},
    {"eq": {"field": "labels.module", "value": "marketing"}},
    {"gte": {"field": "metrics.cost", "value": 100}},
    {"between": {"field": "observed_at", "from": "2026-05-01", "to": "2026-05-08"}},
    {"in": {"field": "labels.country", "values": ["SK", "CZ"]}}
  ]
}
```

Supported operators:

```text
eq
neq
in
not_in
exists
not_exists
gt
gte
lt
lte
between
contains
prefix
full_text
semantic
and
or
not
```

## Filterable Field Names

Common fields:

```text
tenant_id
workspace_id
dataset_id
source_id
stream_id
entity_type
entity_id
content_unit_id
content_chunk_id
relation_type
unit_kind
language
created_at
updated_at
observed_at
source_updated_at
labels.*
properties.*
classification.*
dimensions.*
metrics.*
```

## Example Filters

Marketing:

```json
{
  "and": [
    {"eq": {"field": "labels.module", "value": "marketing"}},
    {"eq": {"field": "entity_type", "value": "keyword"}},
    {"gte": {"field": "metrics.cost", "value": 100}},
    {"lt": {"field": "analysis.best_page_alignment", "value": 0.72}}
  ]
}
```

VC:

```json
{
  "and": [
    {"eq": {"field": "labels.module", "value": "vc"}},
    {"eq": {"field": "entity_type", "value": "startup"}},
    {"in": {"field": "properties.stage", "values": ["seed", "series_a"]}},
    {"eq": {"field": "labels.decision_status", "value": "new"}}
  ]
}
```

Support:

```json
{
  "and": [
    {"eq": {"field": "entity_type", "value": "ticket"}},
    {"eq": {"field": "labels.product_area", "value": "billing"}},
    {"eq": {"field": "properties.escalated", "value": true}},
    {"between": {"field": "created_at", "from": "2026-05-01", "to": "2026-05-08"}}
  ]
}
```

Legal:

```json
{
  "and": [
    {"eq": {"field": "entity_type", "value": "contract"}},
    {"eq": {"field": "labels.contract_type", "value": "vendor"}},
    {"eq": {"field": "classification.level", "value": "restricted"}},
    {"lte": {"field": "metrics.notice_period_days", "value": 60}}
  ]
}
```

## Vector Payload Labels

Every vector point should include enough payload metadata for safe filtered
search.

Qdrant payload example:

```json
{
  "tenant_id": "t_1",
  "workspace_id": "ws_1",
  "dataset_id": "ds_1",
  "source_id": "src_1",
  "stream_id": "str_1",
  "entity_type": "page",
  "entity_id": "ent_1",
  "content_unit_id": "cu_1",
  "content_chunk_id": "cc_1",
  "unit_kind": "paragraph",
  "language": "en",
  "labels": {
    "module": "marketing",
    "topic": ["pricing", "workflow"],
    "country": "SK"
  },
  "classification": {
    "level": "internal",
    "pii": false
  },
  "access_policy_id": "pol_1",
  "created_at": "2026-05-08T10:00:00Z",
  "source_updated_at": "2026-05-08T09:45:00Z"
}
```

Rules:

- always include tenant/workspace/dataset
- include entity/content IDs for evidence lookup
- include classification and access policy
- include module labels
- include time fields
- avoid storing sensitive raw text in vector payload

## Label Propagation

Labels should propagate downward unless overridden:

```text
dataset -> source -> stream -> raw object -> entity -> content unit -> chunk -> embedding
```

Example:

If a source is labeled:

```text
module=marketing
client=acme
channel=paid_search
```

Then imported keyword entities, metric values, and chunk vectors inherit those
labels unless a more specific value is provided.

## Label Governance

The system should prevent label chaos.

Features:

- label registry per workspace
- suggested labels from modules
- allowed values for controlled labels
- warnings for misspelled labels
- merge/rename labels
- label usage statistics
- protected labels for security fields

Protected prefixes:

```text
classification.*
acl.*
system.*
tenant_id
workspace_id
dataset_id
access_policy_id
```

## MCP Usage

MCP tools should accept the same filter grammar.

Example:

```json
{
  "dataset_id": "ds_marketing",
  "query": "invoice approval workflow",
  "filters": {
    "and": [
      {"eq": {"field": "labels.module", "value": "marketing"}},
      {"eq": {"field": "entity_type", "value": "page"}},
      {"eq": {"field": "language", "value": "en"}}
    ]
  },
  "limit": 10
}
```

The MCP server must apply access filters automatically even if the agent does
not provide them.

## Analysis Filtering

Analysis runs should be scoped by filters.

Example:

```json
{
  "analysis_type": "semantic_alignment",
  "scope": {
    "source_filter": {
      "eq": {
        "field": "entity_type",
        "value": "keyword"
      }
    },
    "target_filter": {
      "eq": {
        "field": "entity_type",
        "value": "page"
      }
    }
  }
}
```

This allows analyses like:

- only English pages
- only Q2 campaigns
- only confidential contracts
- only seed-stage startups
- only escalated support tickets
- only high-value customers

## Data Validation

Push endpoints should validate:

- required IDs
- valid event type
- valid entity type
- valid metric type
- allowed label keys
- allowed classification values
- timestamp format
- idempotency key
- payload size
- permission to write into dataset

Invalid records should go to:

```text
rejected_events
dead_letter_queue
import_error_report
```

## Idempotency

Every pushed event should include or derive an idempotency key.

Preferred:

```text
source_id + external_event_id
```

Fallback:

```text
source_id + event_type + external_object_id + source_updated_at + payload_hash
```

## Reprocessing

Labels and metadata are critical for reprocessing.

Examples:

- re-embed only `labels.module=marketing`
- re-run PII detection only `classification.level=confidential`
- reprocess only documents from `source_id=google_drive`
- recompute metrics only for `dimensions.channel=paid_search`
- run new legal clause extractor only `labels.contract_type=vendor`

## Recommended MVP

MVP should implement:

- JSONL push
- JSON batch push
- document upload
- CSV mapping
- labels on datasets, entities, content units, metric values
- classification fields
- idempotency keys
- basic filter grammar
- vector payload labels
- MCP filters
- label propagation

Later:

- label registry UI
- controlled vocabularies
- advanced ACL labels
- Kafka/PubSub adapters
- file drop ingestion
- label merge/rename tools
- schema inference for labels and properties
