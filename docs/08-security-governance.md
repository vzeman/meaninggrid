# Security And Governance

## Security Goals

MeaningGrid will handle sensitive business data:

- transcripts
- emails
- tickets
- CRM records
- company data
- internal documents
- website analytics
- customer identifiers

Security cannot be added later. The platform should be designed as a governed
context layer from the beginning.

## Tenancy

Every persistent object should carry:

```text
tenant_id
workspace_id
dataset_id where applicable
```

Rules:

- all API queries must be tenant-scoped
- all vector queries must include tenant/workspace filters
- all object storage paths must include tenant/workspace/dataset prefixes
- audit logs must include tenant and actor
- background jobs must include tenant context

## Authentication

Community version:

- local admin account
- API tokens

SaaS:

- email/password or magic links
- OAuth providers
- organization invitations
- API tokens

Enterprise:

- SSO via OIDC
- SAML later if required
- SCIM provisioning later
- service accounts

## Authorization

Use RBAC first, ABAC later.

Initial roles:

```text
owner
admin
analyst
viewer
agent_readonly
connector_operator
security_admin
```

Permissions:

```text
workspace:read
workspace:admin
dataset:create
dataset:read
dataset:update
dataset:delete
dataset:export
source:configure
source:sync
entity:read
metric:read
analysis:create
analysis:read
insight:update
context_pack:create
mcp:read
mcp:act
raw_source:read
pii:read
audit:read
```

ABAC examples:

- user can only access assigned workspaces
- agent can only access redacted context
- support analyst can read tickets but not raw customer PII
- vendor can read report artifacts but not source data

## Data Classification

Classify content at import time:

```text
public
internal
confidential
restricted
pii
secret
```

Classification can be:

- connector-provided
- rule-based
- user-configured
- detected by PII scanner

## PII Handling

PII detection targets:

- names
- email addresses
- phone numbers
- addresses
- account IDs
- payment identifiers
- national IDs where detectable

PII controls:

- redaction in context packs
- redaction in MCP responses
- raw source access permission
- export restrictions
- audit log for PII access
- dataset-level policy

Redaction modes:

```text
none
mask
pseudonymize
remove
```

Examples:

```text
jane@example.com -> [EMAIL_1]
+421 900 123 456 -> [PHONE_1]
Jane Novak -> [PERSON_1]
```

## Prompt Injection Defense

Imported text must be treated as untrusted evidence.

Risk examples:

- a ticket says "ignore previous instructions"
- a web page contains hidden prompt injection
- a transcript includes instructions for the AI
- a document asks the agent to export secrets

Rules:

1. Source content is evidence, not instruction.
2. Context packs must label source content clearly.
3. Tool policies cannot be changed by retrieved text.
4. MCP tools must enforce permissions server-side.
5. Write/export tools require explicit permission.
6. Raw source access should be audited.

Context pack template should separate:

```text
system/context instructions
dataset metadata
source evidence
allowed actions
forbidden actions
```

## MCP Security

MCP server risks:

- overbroad tools
- unsafe exports
- prompt injection through resources
- confused deputy attacks
- agent accesses data user cannot access

Controls:

- user-scoped MCP sessions
- short-lived tokens
- explicit tool permissions
- read-only mode by default
- action tools disabled unless configured
- resource access checks
- result redaction
- audit logs
- rate limits
- per-tool descriptions that state boundaries

Tool naming should be clear and non-deceptive. Avoid lookalike tools.

## Headless Agent Security

Headless mode increases the importance of agent identity and tool policy.

Requirements:

- authenticated MCP sessions except explicit local-only mode
- user-delegated or service-account identity
- read-only tools by default
- explicit allowlist for action tools
- export tools disabled unless configured
- raw source access audited
- agent session logs
- rate limits per agent and user
- denied tool calls logged
- prompt-injection defenses applied to all retrieved content

## Audit Logging

Audit events:

- login
- SSO login
- API token creation
- connector configured
- connector sync started/finished
- source event received
- backfill started/finished
- reprocessing job started/finished
- dataset imported
- raw source accessed
- context pack created
- MCP tool called
- export created
- insight accepted/rejected
- permission changed
- dataset deleted

Fields:

- event_id
- tenant_id
- workspace_id
- dataset_id
- actor_user_id
- actor_type
- action
- target_type
- target_id
- ip_address
- user_agent
- timestamp
- metadata_json

High-volume audit logs can move to ClickHouse while critical metadata remains
in Postgres.

## Retention And Deletion

Policies:

- raw source retention
- source event retention
- metric history retention
- vector retention
- analysis artifact retention
- context pack retention
- audit log retention
- export retention

Deletion requirements:

- delete dataset metadata
- delete raw objects
- delete source events where retention policy permits
- delete stream cursors and webhook secrets
- delete vectors from Qdrant/pgvector
- delete analysis artifacts
- delete generated reports
- retain audit tombstones if legally required

Enterprise should support:

- legal hold
- tenant export
- dataset export
- right-to-delete workflows

## Secrets

Connector secrets should never be stored in plain text.

Options:

- local encrypted secrets for community mode
- cloud secret manager for SaaS
- customer secret manager for enterprise
- Vault for standalone enterprise

Secrets should be referenced by ID:

```text
config_ref = secret://tenant/source/credential
```

## Network Security

Enterprise deployment:

- private networking
- no public database access
- optional outbound allowlist
- optional no-outbound mode
- TLS everywhere
- ingress restrictions
- network policies in Kubernetes

## Compliance Direction

Potential future targets:

- SOC 2
- ISO 27001
- GDPR readiness
- HIPAA-capable deployments if needed

Do not claim compliance early. Build controls that make later compliance
possible.
