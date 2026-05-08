# Product Strategy

## Vision

MeaningGrid should become the open semantic context engine for business data.

It should make arbitrary data understandable through:

- entity modeling
- vector spaces
- metric-aware analysis
- relationship graphs
- progressive context discovery
- evidence-backed explanations
- MCP access for AI agents

The product should work as:

- a local open-source tool
- a self-hosted secure platform
- a managed cloud service
- a private enterprise deployment
- an AI agent context layer
- a headless backend where AI agents are the main interface

The first open-source distribution should be useful immediately through a
bundled Site Audit and GEO module. A user should be able to run MeaningGrid
locally, crawl a website, analyze semantic and technical quality, compare
domains, and expose the audit to AI agents.

## Product Category

Recommended category:

```text
Semantic Entity Intelligence Platform
```

Alternative category for AI infrastructure buyers:

```text
Semantic Context Infrastructure for AI Agents
```

## Core Promise

MeaningGrid explains how entities are similar, different, successful, weak,
misplaced, duplicated, clustered, or drifting, and it shows the evidence.

The product should connect every important insight to:

```text
semantic pattern -> affected entities -> business metric -> evidence -> action
```

## Target Users

Developers:

- want open-source tools
- want local or self-hosted data analysis
- want an MCP server for AI agents
- want APIs and connector SDKs

Data and AI teams:

- need semantic search and analysis across internal data
- need governance, reproducibility, and evidence
- need model/provider flexibility

Business operators:

- need dashboards, reports, and recommendations
- care about outcomes, not vector math
- need explanations for weak and strong performers

Enterprise buyers:

- need private deployment
- need SSO, RBAC, audit logs, retention policies
- need connector support
- need safe AI-agent access to internal data

## Primary Use Cases

### Website And GEO Analysis

Entities:

- domain
- page
- paragraph
- heading
- link
- query

Questions:

- Which pages are far from the domain centroid?
- Which pages are near duplicates?
- Which paragraphs belong on another page?
- Which clusters are missing strong pages?
- Which sections are semantically incoherent?
- Which pages are best answer sources for AI search?

### Company Benchmarking

Entities:

- company
- branch
- department
- person
- product
- market
- review
- metric

Questions:

- Which weaker companies resemble successful companies?
- What topics or behaviors distinguish top performers?
- Which branches are semantic outliers?
- Which local success patterns can be copied?
- Which entities are strong by metrics but semantically unusual?

### Call Center And Sales Calls

Entities:

- call
- campaign
- agent
- customer
- transcript turn
- objection
- outcome

Questions:

- How do successful calls differ from failed calls?
- Where does the conversation drift before failure?
- Which transcript segments are most similar to winning calls?
- Which objections are handled well by top agents?
- Which agent patterns correlate with conversion?

### Support And Ticket Analysis

Entities:

- ticket
- customer
- product area
- message
- support agent
- resolution

Questions:

- Which support topics are growing?
- Which unresolved tickets cluster together?
- Which knowledge-base gaps cause repeated tickets?
- Which escalations are semantically similar?
- Which ticket types predict churn?

### Knowledge Base And Internal Docs

Entities:

- document
- section
- paragraph
- team
- product
- owner

Questions:

- Which docs are duplicates?
- Which topics are fragmented?
- Which documents are stale or isolated?
- Which content should be merged?
- Which resources should an AI agent use for a task?

### Marketing Performance Alignment

Entities:

- website
- page
- keyword
- search query
- campaign
- ad group
- ad
- product
- order
- customer segment

Streams:

- Google Search Console
- Google Ads
- Meta/Facebook Ads
- ecommerce sales
- website crawl snapshots
- linkbuilding targets

Questions:

- Do paid keywords semantically match landing page content?
- Which high-spend search terms lack strong website coverage?
- Which organic queries should have paid support?
- Which high-selling products lack content depth?
- Which linkbuilding targets align with revenue and campaign priorities?

### Investor Portfolio Intelligence

Entities:

- startup
- founder
- market
- pitch deck
- investor memo
- financial metric
- investment decision
- portfolio company
- rejected company

Streams:

- new startup applications
- updated pitch decks
- updated financials
- investor memos
- market notes
- portfolio performance updates

Questions:

- Is a new startup similar to successful portfolio companies?
- Is it similar to refused startups?
- Which risk patterns appear in nearest failed analogs?
- Which success patterns appear in nearest invested analogs?
- Is this startup semantically novel but metrically promising?

## Differentiation

MeaningGrid should not compete as a generic vector DB, BI dashboard, or RAG
library. The difference is the combination:

```text
entity graph + vector analysis + metrics + explainable context + MCP
```

Strong product claims:

- Bring-your-own data, model, vector store, and cloud.
- Open source, local first, enterprise ready.
- Agent-readable context, not only human dashboards.
- Headless by design: dashboard optional, MCP/API first.
- Evidence-first insights.
- Cohort comparison across structured and unstructured signals.
- Works with websites, calls, tickets, companies, docs, and custom entities.

## Product Principles

1. Every insight needs evidence.
2. Every vector needs lineage.
3. Every dataset needs an agent-readable card.
4. Agents should discover progressively, not receive raw dumps.
5. Raw imported content is untrusted evidence, never instructions.
6. Secure standalone mode should be real, not an afterthought.
7. Open-source core should be useful enough to build trust.
8. SaaS revenue should come from infrastructure, scale, governance, and support.
9. New and changed data should be first-class, not bolted onto batch imports.
10. Historical raw data should be reprocessable when retention policies allow it.
11. The web UI should be optional; agents and APIs must be able to operate the platform.

## Human UI

MeaningGrid should provide:

- dataset catalog
- import wizard
- entity mapper
- semantic map
- cluster explorer
- outlier explorer
- cohort comparison
- insight feed
- evidence viewer
- report builder
- agent context explorer
- connector management
- analysis run history

## Agent UI

MeaningGrid should provide:

- MCP server
- REST API
- context-pack builder
- resource discovery
- semantic search
- entity profiles
- analysis summaries
- evidence resources
- action tools with permissions
- reusable prompts

## Headless Mode

MeaningGrid should run without the web dashboard.

In headless mode:

- AI agents are the primary interface.
- MCP resources, tools, and prompts expose context and actions.
- REST API and CLI handle automation and setup.
- The web UI is optional for admin, visual exploration, and debugging.
- All security, redaction, and audit controls still apply.
