# Open Source And Enterprise Strategy

## Strategy

MeaningGrid should be open-source infrastructure first.

The open-source project should be genuinely useful:

- local installation
- import data
- build entities
- embed content
- run analysis
- expose MCP
- view dashboards
- create reports

The company sells:

- managed cloud
- private deployments
- enterprise scale
- security and governance
- premium connectors
- support
- compliance help
- custom integrations

## Positioning

Open-source:

```text
MeaningGrid is the open semantic context engine for AI agents.
```

Enterprise:

```text
MeaningGrid deploys a private semantic context layer over your business data.
```

## Community Edition

Should include:

- Docker Compose deployment
- Postgres + pgvector
- optional Qdrant
- website connector
- CSV/XLSX/JSONL import
- basic database connector
- entity mapper
- embedding provider abstraction
- local embedding support
- semantic analysis engine
- cluster/outlier/cohort analysis
- periodic sync foundation
- source event log
- basic web UI
- MCP server
- headless mode
- context-pack builder
- report export
- API tokens

The community edition must be good enough that developers trust the project.

## Enterprise Edition

Paid features/services can include:

- managed SaaS
- private VPC deployment
- managed headless agent infrastructure
- Helm/Kubernetes enterprise package
- high availability
- backup/restore automation
- advanced RBAC/ABAC
- SSO/OIDC/SAML
- audit log explorer
- PII policy engine
- data retention policies
- premium connectors
- connector support SLAs
- high-volume streaming ingestion
- Kafka/Redpanda/cloud event-bus adapters
- managed backfills and reprocessing
- advanced monitoring
- cost controls
- multi-region deployment
- air-gapped deployment support
- commercial license
- support and training

## License Options

### Apache 2.0

Pros:

- maximum adoption
- enterprise-friendly
- simple mental model

Cons:

- competitors can host it as SaaS
- less protection for infrastructure business

### AGPL 3.0

Pros:

- protects against hosted proprietary forks
- encourages contributions
- supports dual licensing

Cons:

- some enterprises avoid AGPL
- can reduce adoption

### Dual License

Recommended path:

```text
Server/core: AGPL-3.0
Client SDKs: Apache-2.0
Examples/docs: permissive
Enterprise distribution: commercial license
```

This balances openness, protection, and enterprise sales.

Open question:

- Choose Apache if adoption is the only priority.
- Choose AGPL + commercial if business defensibility matters more.

## Business Model

Revenue streams:

1. Managed MeaningGrid Cloud
2. Private cloud deployment
3. Enterprise support subscription
4. Premium connectors
5. Compliance/security package
6. Air-gapped deployment support
7. Custom analysis templates
8. Custom integration work
9. Training and implementation

## Enterprise Buyer Value

Enterprise buyers pay because they need:

- private data handling
- safe agent access
- connector reliability
- security controls
- scale
- auditability
- support
- deployment expertise
- predictable operations

The selling point is not "we host open source". It is:

```text
We give your AI agents governed semantic access to your internal business data.
```

## Moat

Moat should come from:

- connector ecosystem
- deployment expertise
- community adoption
- analysis templates
- agent context patterns
- enterprise trust
- governance features
- operational excellence
- integrations with AI-agent tools

Do not rely on closed code as the moat.

## Community Growth

Good first demos:

- website audit
- CSV company benchmark
- sales-call transcript analysis
- support-ticket import
- MCP context server demo

Developer messaging:

```bash
docker compose up
meaninggrid import website https://example.com
meaninggrid analyze
meaninggrid mcp start
```

Content ideas:

- "How to give Claude/Codex safe context over your website"
- "Build a local semantic map of your support tickets"
- "Open-source MCP server for entity intelligence"
- "From CSV to semantic cohort analysis"

## Governance Model

Early:

- single-maintainer project
- clear roadmap
- contribution guidelines
- issue templates
- security policy

Later:

- technical steering group
- connector maintainers
- plugin marketplace
- contributor recognition

## Repository Strategy

Start monorepo:

```text
meaninggrid/
  apps/
  packages/
  deployments/
  examples/
  docs/
```

Avoid splitting repositories until boundaries are stable.
