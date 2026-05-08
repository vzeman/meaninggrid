# Connectors And Ingestion

## Goal

Connectors should bring data into MeaningGrid without forcing each connector to
understand the full final analysis model.

The pipeline should be:

```text
source system -> raw object -> normalized proposal -> entity/content/metric model
```

For continuous sources, the pipeline should be:

```text
source event -> raw object -> normalized entity change -> current state + history
```

Detailed push formats, canonical event envelopes, labels, and filtering are
defined in [Data Push, Labeling, And Filtering](18-data-push-labeling-filtering.md).

## Connector Principles

1. Capture raw source payloads first.
2. Keep sync state explicit and recoverable.
3. Normalize into proposals, then validate.
4. Make schema mapping visible to users.
5. Support incremental sync.
6. Store source lineage for every entity and content unit.
7. Treat source text as untrusted evidence.
8. Make every event idempotent.
9. Preserve enough raw data to reprocess later when policies allow it.
10. Attach labels, classification, and source metadata consistently.

## Connector SDK

Each connector should implement:

```text
describe()
configure()
test_connection()
discover_schema()
sync_full()
sync_incremental()
handle_webhook(payload)
read_stream(cursor)
normalize(raw_object)
```

Connector manifest:

```json
{
  "name": "zendesk",
  "display_name": "Zendesk",
  "version": "0.1.0",
  "auth": ["api_token", "oauth"],
  "supports_incremental_sync": true,
  "supports_webhooks": false,
  "supports_backfill": true,
  "entities": ["ticket", "user", "organization", "message"],
  "content_units": ["ticket_message"],
  "metrics": ["status", "priority", "resolution_time"]
}
```

## Raw Object Stage

Raw objects should be immutable by content hash.

Raw objects should carry:

- source_id
- external_id
- content_hash
- labels
- classification
- ACL/access policy
- source timestamps

Examples:

- HTML page snapshot
- sitemap XML
- API JSON response
- webhook payload
- stream event payload
- CDC payload
- CSV file
- spreadsheet sheet
- transcript file
- ticket message payload

Object storage path example:

```text
s3://meaninggrid/{tenant_id}/{workspace_id}/{dataset_id}/raw/{source_id}/{hash}
```

Standalone path example:

```text
minio://meaninggrid/{tenant_id}/{workspace_id}/{dataset_id}/raw/{source_id}/{hash}
```

## Normalized Proposal Stage

Before final insertion, connectors emit normalized proposals:

```json
{
  "entity_type": "ticket",
  "external_id": "123",
  "label": "Login problem",
  "properties": {
    "status": "solved",
    "priority": "high"
  },
  "content_units": [
    {
      "unit_kind": "ticket_message",
      "text": "I cannot log in after the latest update.",
      "order_index": 0
    }
  ],
  "metrics": [
    {
      "name": "resolution_time_hours",
      "value_number": 5.2
    }
  ],
  "relations": []
}
```

Normalized proposals may include:

- labels
- properties
- classification
- ACL hints
- metric dimensions
- source lineage

## Streaming And Periodic Sync

Connectors may run as periodic syncs, webhooks, streams, or CDC readers.

Modes:

```text
batch
periodic
webhook
stream
cdc
```

Every incoming item should first become a source event, then a normalized
entity change.

```text
external item -> source_event -> raw_object -> normalized proposal -> entity change
```

For streaming-agent use cases, connectors should also populate or allow
MeaningGrid to derive:

- event id
- source
- type
- subject
- occurred time
- partition key
- sequence or cursor
- priority hint
- route hint
- labels
- classification
- ACL hints

These fields let the Streaming Agent Context Engine route events into fast
notifications, batch context units, archive-only storage, or dead-letter
handling without exposing connector-specific payloads to agents.

Periodic sync examples:

- pull Google Search Console daily
- pull Google Ads hourly
- pull ecommerce orders every 15 minutes
- crawl changed website pages weekly

Webhook examples:

- new support ticket
- new ecommerce order
- new call transcript
- new startup application

CDC examples:

- product table changed
- order table changed
- deal stage changed

Idempotency is required. Duplicate events should not create duplicate entities,
content units, metric values, or embeddings.

## Backfills

Backfills import historical data into an existing stream.

Examples:

- last 16 months of Search Console data
- last 2 years of ad spend
- historical ecommerce sales
- all previously refused startup applications

Backfills need:

- date range
- checkpointing
- rate-limit handling
- resumability
- deduplication
- progress reporting
- partial failure recovery

## Entity Mapper

The entity mapper turns source data into the universal model.

Features:

- auto-detect entity types
- suggest labels
- suggest text fields
- suggest metric fields
- identify relation fields
- preview normalized entities
- allow user override
- save mapping template

For CSV/XLSX:

- one row can be one entity
- selected columns become text
- selected columns become metrics
- selected columns become relations

For websites:

- URL becomes page entity
- domain becomes domain entity
- paragraphs and headings become content units
- links become relations

For calls:

- call ID becomes call entity
- agent/customer become entities
- transcript turns become content units
- outcome becomes metric

## Initial Connectors

### Website Crawler

Features:

- robots.txt handling
- sitemap discovery
- sitemap-only mode
- URL include/exclude filters
- crawl limits
- canonical URL detection
- noindex handling
- main content extraction
- paragraph extraction
- heading extraction
- link extraction
- metadata extraction

This can reuse concepts from the existing `site-audit` project.

### CSV/XLSX Upload

Features:

- sheet selection
- header detection
- column type inference
- entity mapping
- text field selection
- metric field selection
- relation field selection
- preview
- validation

### JSONL Upload

Useful for developers and custom exports.

Each line can represent:

- raw object
- entity proposal
- content unit
- metric value

### Database Connector

Initial:

- Postgres read-only connector

Later:

- MySQL
- SQL Server
- BigQuery
- Snowflake

Features:

- read-only credentials
- query templates
- schema discovery
- incremental sync by timestamp or primary key

### Support Connectors

Priority:

- Zendesk
- LiveAgent
- Intercom
- Freshdesk

Entities:

- ticket
- customer
- agent
- organization
- message
- tag

Metrics:

- status
- priority
- resolution time
- satisfaction
- escalation
- product area

### CRM And Sales Connectors

Priority:

- HubSpot
- Salesforce
- Pipedrive

Entities:

- company
- contact
- deal
- activity
- call
- email

Metrics:

- deal stage
- deal value
- closed won/lost
- close date
- owner

### Call Transcript Connectors

Sources:

- uploaded transcripts
- Gong
- Chorus
- Aircall
- Twilio
- custom ASR output

Features:

- speaker diarization fields
- transcript turn parsing
- call phase detection
- objection detection
- sentiment extraction

## Chunking

Chunking should be strategy-based and versioned.

Strategies:

```text
paragraph
sentence_window
token_window
speaker_turn
semantic_section
html_block
markdown_section
spreadsheet_row
```

Chunk metadata:

- source offsets
- page URL or document path
- speaker
- timestamp
- heading path
- language
- parent entity

## Embedding Pipeline

Steps:

1. collect chunks needing embeddings
2. group by embedding model
3. batch by token length
4. call embedding provider
5. normalize if needed
6. write vector to store
7. write embedding metadata
8. record failures and retries

Embedding providers:

- OpenAI
- Anthropic if embeddings become available through chosen route
- Cohere
- Voyage
- local sentence-transformers
- BGE/E5 models
- custom HTTP provider

## Incremental Sync

Need to detect:

- new raw objects
- changed raw objects
- deleted source objects
- new source events
- changed metrics
- changed relations

For changed content:

- compute new content hash
- re-chunk if chunking strategy changed
- re-embed changed chunks
- invalidate affected analysis artifacts
- schedule incremental analysis

## Reprocessing

Reprocessing should run when:

- a new metric extractor is added
- a new embedding model is configured
- chunking strategy changes
- entity mapping improves
- PII policy changes
- a new analysis template is introduced

The connector should not need to re-fetch everything if raw source events and
raw objects are retained. The platform should replay from stored raw data where
possible.

## Data Quality Checks

Checks:

- empty text
- duplicate external IDs
- invalid metrics
- unknown language
- unsupported file type
- missing labels
- huge text fields
- low extraction quality
- failed chunking
- failed embeddings

Data quality should be visible in dataset cards.
