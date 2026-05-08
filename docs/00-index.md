# MeaningGrid Planning Index

This folder is the starting product and technical plan for MeaningGrid.

MeaningGrid is not only a vector database UI. It is a semantic entity
intelligence platform and context layer for AI agents.

## Documents

1. [Product Strategy](01-product-strategy.md)
   - Vision, use cases, product principles, target users, differentiation.

2. [System Architecture](02-system-architecture.md)
   - Runtime components, deployment modes, service boundaries, data flow.

3. [Data Model](03-data-model.md)
   - Universal entity model, content units, metrics, relations, embeddings,
     analysis artifacts, context packs.

4. [Context Layer And MCP](04-context-layer-mcp.md)
   - Progressive discovery, context packs, MCP resources, MCP tools, MCP
     prompts, agent memory, evidence.

5. [Analysis Engine](05-analysis-engine.md)
   - Centroids, radius, clustering, outliers, cohorts, drift, gap detection,
     semantic maps, explainability.

6. [Connectors And Ingestion](06-connectors-ingestion.md)
   - Connector framework, crawling, files, databases, support tools, call
     transcripts, validation, incremental sync.

7. [Storage And Infrastructure](07-storage-infrastructure.md)
   - Postgres, pgvector, Qdrant, ClickHouse, object storage, queues, workers,
     cloud portability, standalone mode.

8. [Security And Governance](08-security-governance.md)
   - Tenancy, RBAC, ABAC, PII, prompt injection, audit logs, retention,
     evidence controls.

9. [Open Source And Enterprise Strategy](09-open-source-enterprise.md)
   - License options, community edition, enterprise edition, business model,
     moat.

10. [Build Roadmap](10-build-roadmap.md)
    - Milestones, MVP scope, sequencing, team roles, quality gates.

11. [API And MCP Surface](11-api-and-mcp-surface.md)
    - REST API shape, MCP resource URIs, MCP tools, prompt templates.

12. [Decisions And Open Questions](12-decisions-and-open-questions.md)
    - Initial technical decisions, assumptions, risks, unresolved choices.

13. [Use Case Templates](13-use-case-templates.md)
    - Website/GEO, company benchmark, call center, support tickets, knowledge
      base, and custom entity analysis templates.

14. [Implementation Backlog](14-implementation-backlog.md)
    - Epics, tasks, acceptance criteria, first sprint plan, and release gates.

15. [Streaming And Incremental Data](15-streaming-incremental-data.md)
    - Streams, CDC, periodic sync, append/update/delete handling, snapshots,
      reprocessing, backfills, and time-aware analysis.

16. [Headless Agent Infrastructure](16-headless-agent-infrastructure.md)
    - Agent-first deployment, MCP/API control plane, no-dashboard operation,
      context contracts, agent sessions, and enterprise headless use.

17. [Modular Architecture And Example Modules](17-modular-architecture-and-modules.md)
    - Module contracts, registry, lifecycle, interfaces, MCP exposure, and
      detailed module examples for site audit, marketing, VC, sales, support,
      ecommerce, product events, legal, HR, knowledge bases, and more.

18. [Detailed Module Specs](modules/README.md)
    - Separate implementation-oriented specs for Site Audit/GEO, Marketing,
      VC, Sales, Support, Knowledge Base, Ecommerce, Product Events, Legal, HR,
      Procurement, and Compliance modules.

19. [Module Feature Mapping](modules/module-feature-mapping.md)
    - What each module does, why customers need it, what tasks it supports, and
      how its features map to MeaningGrid core subsystems.

20. [Data Push, Labeling, And Filtering](18-data-push-labeling-filtering.md)
    - Push APIs, accepted formats, canonical envelopes, labels, metadata,
      classification, ACLs, filter grammar, vector payloads, and MCP filtering.

21. [Streaming Agent Context Engine](19-streaming-agent-context-engine.md)
    - Streaming-first context fabric for long-running agents, fast/batch event
      routing, context units, MCP subscriptions, delivery semantics, shared
      memory, and implementation phases.

22. [Local Docker Infrastructure And Flexible Schema](20-local-docker-infrastructure-and-flexible-schema.md)
    - Local appliance-style Docker distribution, service profiles, volumes,
      boot sequence, table families, flexible schema rules, and the bundled
      Site Audit/GEO module.

23. [Language And Runtime Strategy](21-language-and-runtime-strategy.md)
    - Programming language recommendations for backend, UI, workers, MCP, CLI,
      modules, streaming, infrastructure, SDKs, tests, and later performance
      escape hatches.

24. [MVP Scope And Acceptance](22-mvp-scope-and-acceptance.md)
    - Frozen v0.1 Site Audit scope, exclusions, happy path, acceptance
      criteria, quality gates, and fixture requirements.

25. [Initial Database Schema V0](23-initial-database-schema-v0.md)
    - Implementation-grade Postgres schema conventions, tables, columns,
      indexes, migration order, and seed requirements for v0.1.

26. [Site Audit V0 Pipeline And Analysis](24-site-audit-v0-pipeline-and-analysis.md)
    - Crawl, extraction, entity mapping, chunking, embeddings, technical
      analysis, semantic analysis, GEO scoring, artifacts, and insights.

27. [API Contract V0](25-api-contract-v0.md)
    - First REST API shape for workspaces, datasets, crawls, jobs, pages,
      analyses, insights, evidence, search, context packs, reports, and MCP.

28. [Worker Jobs And State Machines](26-worker-jobs-and-state-machines.md)
    - Job types, statuses, transitions, progress reporting, idempotency,
      retries, cancellation, queues, and worker acceptance tests.

29. [UI Information Architecture V0](27-ui-information-architecture-v0.md)
    - First web app routes, screens, tables, filters, detail views, reports,
      MCP setup, loading/error states, and Playwright smoke flow.

30. [Development Skeleton And First Sprints](28-development-skeleton-and-first-sprints.md)
    - Monorepo skeleton, tooling, Docker Compose, sprint sequence, demos, CI,
      and implementation risks.

31. [Engineering Decisions V0](29-engineering-decisions-v0.md)
    - Locked v0 choices for package tools, backend, workers, frontend,
      embeddings, crawler libraries, IDs, auth, storage, MCP, and fixture site.

## First Implementation Target

The first useful release should allow a developer to run this locally:

```bash
docker compose up
meaninggrid import website https://example.com
meaninggrid analyze
meaninggrid mcp start
```

For implementation, start with:

```text
22 MVP Scope -> 23 Schema -> 24 Pipeline -> 25 API -> 26 Jobs -> 27 UI -> 28 Sprints -> 29 Decisions
```

Then an AI agent can ask through MCP:

```text
What datasets exist?
What are the main semantic clusters?
Which entities are outliers?
Build a context pack for GEO analysis.
Compare successful and unsuccessful cohorts.
Subscribe me to important context changes.
Give me evidence for this insight.
```

The web UI should be optional. MeaningGrid must also run as headless
infrastructure where AI agents are the main user interface.
