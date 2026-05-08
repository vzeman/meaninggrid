# Compliance And Audit Intelligence Module

## Purpose

Compliance and Audit Intelligence maps policies, controls, requirements,
evidence, incidents, findings, owners, systems, and audit readiness.

The module answers:

```text
Do we have the right evidence for the right controls, and where are the gaps?
```

## Target Users

- compliance teams
- internal audit
- security teams
- risk teams
- control owners
- external audit preparation teams

## Jobs To Be Done

- Map controls to evidence.
- Find missing or stale evidence.
- Summarize audit readiness.
- Cluster incidents and findings.
- Compare policies to requirements.
- Detect duplicate or overlapping controls.
- Prepare auditor context packs.
- Track remediation progress.

## Connected Sources

Initial:

- policy documents
- control spreadsheets
- evidence folders
- incident reports
- audit findings CSV/JSONL

Later:

- GRC platforms
- ticketing systems
- cloud security tools
- evidence collection systems
- document repositories
- SIEM exports

## Entity Types

```text
policy
control
requirement
evidence
incident
finding
owner
system
audit
remediation
framework
```

## Relations

```text
policy implements requirement
control satisfies requirement
evidence supports control
incident relates_to control
finding concerns control
owner owns control
system scoped_by control
remediation addresses finding
audit reviews framework
```

## Metrics

```text
control_status
evidence_age_days
risk_score
finding_severity
remediation_time
owner_response_time
evidence_completeness
audit_readiness_score
```

## Content And Embeddings

Embed:

- policy sections
- control descriptions
- requirement text
- evidence descriptions
- incident summaries
- finding text
- remediation notes

## Core Analyses Used

- semantic alignment
- gap detection
- duplicate detection
- cluster detection
- outlier detection
- temporal monitoring

## Module-Specific Analyses

### Control To Evidence Coverage

Maps evidence to controls and flags weak support.

### Missing Evidence

Finds controls without sufficient evidence.

### Stale Evidence

Finds important evidence older than policy thresholds.

### Requirement To Policy Alignment

Compares framework requirements to internal policy/control text.

### Incident Theme Clustering

Clusters incidents and links them to controls.

### Audit Readiness Pack

Builds context for auditors or internal reviewers.

## Dashboards

- Audit readiness overview
- Control coverage
- Missing evidence
- Stale evidence
- Findings and remediation
- Incident themes
- Owner workload

## Reports

- Audit readiness report
- Missing evidence report
- Control gap report
- Incident theme report
- Remediation status report

## Headless Agent Workflows

User asks:

```text
Prepare context for our access-control audit.
```

Agent:

1. Finds relevant controls and requirements.
2. Retrieves supporting evidence.
3. Flags stale or missing evidence.
4. Summarizes open findings.
5. Produces audit context pack.

## AI Agent Decision Support And Automation

AI agents should help compliance teams prepare evidence, understand gaps, and
track remediation without weakening control ownership.

Decision support:

- decide which controls are least audit-ready
- recommend evidence that best supports a control
- identify missing or stale evidence
- explain why a requirement is not fully covered
- prioritize findings by severity, age, and affected systems
- summarize incident themes relevant to controls
- recommend remediation owners based on system/control ownership
- prepare auditor-ready context with evidence links

Automation tasks:

- build audit context packs
- generate missing evidence task lists
- monitor stale evidence
- classify incidents by control area
- draft remediation summaries
- map policy text to framework requirements
- create owner-specific control gap reports
- alert when evidence expires or becomes stale

Agent guardrails:

- agent should not mark controls compliant without human approval
- raw evidence access must be audited
- security-sensitive evidence should be restricted
- context packs should show freshness and evidence age
- generated audit summaries should distinguish evidence from interpretation

## MCP Prompts

```text
/prepare_audit_context_pack
/find_missing_evidence
/summarize_control_gaps
/explain_incident_themes
/prepare_remediation_summary
```

## Security Notes

- Evidence can expose sensitive system details.
- Raw evidence access should be tightly controlled.
- Audit exports should be tracked.
- Framework-specific evidence retention policies may apply.

## MVP Scope

- control/evidence CSV import
- policy document import
- control-to-evidence semantic alignment
- missing evidence report
- audit context pack

## Later Phases

- GRC connectors
- evidence automation
- framework mappings
- remediation workflow
- audit-room exports
