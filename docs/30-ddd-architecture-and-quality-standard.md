# DDD Architecture And Quality Standard

## Purpose

MeaningGrid must stay easy to read, extend, test, and refactor as it grows into
a modular semantic intelligence platform.

The codebase should follow Domain-Driven Design principles. The goal is not to
create ceremony. The goal is to keep business meaning visible in code and keep
framework details from taking over the product model.

## Required Layering

MeaningGrid code should move through these layers:

```text
interface -> application -> domain -> infrastructure
```

### Interface Layer

Examples:

```text
apps/api
apps/web
apps/cli
apps/mcp-server
```

Responsibilities:

- HTTP routes, CLI commands, MCP adapters, UI screens.
- Request and response DTO mapping.
- Authentication and interface-specific error mapping.
- No business workflows hidden in route handlers.
- No direct persistence decisions except dependency/session creation.

### Application Layer

Examples:

```text
packages/application
```

Responsibilities:

- Use cases.
- Commands and application services.
- Transaction boundaries.
- Orchestration across repositories, modules, workers, and domain services.
- Calling module pipelines such as Site Audit crawl/extraction.

Application services should read like product capabilities:

```text
create_site_audit_dataset
start_site_audit_crawl
build_dataset_card
run_crawl_job_now
```

### Domain Layer

Examples:

```text
packages/core/meaninggrid_core/domain
packages/analysis/meaninggrid_analysis/site_audit/domain
```

Responsibilities:

- Business concepts, invariants, value objects, policies, and pure domain
  services.
- No FastAPI, SQLAlchemy sessions, Celery, Redis, or HTTP clients.
- Deterministic and cheap to unit test.

V0 may still use SQLAlchemy models as persistence records while the domain model
is extracted. New complex behavior should prefer domain objects first.

### Infrastructure Layer

Examples:

```text
packages/db
packages/vectorstores
packages/objectstore
packages/connectors
```

Responsibilities:

- SQLAlchemy models, migrations, concrete repositories.
- HTTP clients, filesystem/object storage, queues, vector store adapters.
- Framework-specific implementation details behind interfaces or application
  services.

## Module Boundary Rule

Each module must separate:

```text
module domain -> module application pipeline -> module infrastructure adapters
```

For Site Audit:

```text
site audit concepts: page, crawl, extracted content, technical metrics
site audit pipeline: crawl -> extract -> persist -> score
site audit adapters: HTTP/file fetcher, HTML parser, DB persistence
```

## Testing Rule

A feature is not done until tests cover it.

Minimum expectations:

- Domain rules: unit tests with no database.
- Application use cases: integration tests with the local DB when persistence
  matters.
- API endpoints: route tests for happy path and error shape.
- UI: at least TypeScript typecheck; add component/e2e tests when UI logic
  becomes non-trivial.
- Migrations: exercised through Docker `migrate` in test flow.
- Every bug fix gets a regression test.

Do not merge code by weakening tests, skipping lint, or using `|| true` around
quality gates.

Required local gate:

```bash
make test
make lint
```

## Refactoring Rule

When a file becomes hard to scan, extract a concept, not a random helper.

Good extraction names:

```text
DatasetApplicationService
SiteAuditApplicationService
JobApplicationService
DatasetCardBuilder
TechnicalMetricPolicy
WebsiteCrawler
HtmlPageExtractor
```

Poor extraction names:

```text
utils
helpers
misc
common
manager
```

## API Route Rule

FastAPI route handlers should be thin:

```text
validate request -> call application service -> map response
```

They should not:

- construct persistence records directly,
- contain SQL query details,
- update job state,
- compute module metrics,
- implement crawling/extraction behavior.

## Current V0 Direction

The current codebase is moving toward this structure:

```text
apps/api
  HTTP route adapters and Pydantic DTOs

packages/application
  workspace, module, dataset, job, and site-audit use cases

packages/analysis
  Site Audit crawl/extraction pipeline

packages/db
  SQLAlchemy persistence records and migrations

packages/core
  config, health, shared domain concepts as they are extracted
```

The first refactor target is removing business workflows from
`apps/api/meaninggrid_api/main.py` into application services.
