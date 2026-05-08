# Legal Contract Intelligence Module

## Purpose

Legal Contract Intelligence compares contracts, clauses, templates,
obligations, vendors, customers, deals, and risk outcomes.

The module answers:

```text
What is unusual, risky, missing, or important in this contract corpus?
```

## Target Users

- legal teams
- contract managers
- procurement
- sales/legal operations
- compliance teams
- AI legal assistants

## Jobs To Be Done

- Compare a contract to approved templates.
- Detect unusual or risky clauses.
- Find missing clauses.
- Summarize obligations.
- Compare vendor/customer terms.
- Monitor renewals and notice periods.
- Prepare contract risk briefs.
- Find similar prior contracts.

## Connected Sources

Initial:

- PDF/DOCX contract import
- contract metadata CSV
- clause library CSV/JSONL

Later:

- CLM platforms
- SharePoint/Drive
- Salesforce/HubSpot deal docs
- procurement systems
- e-signature platforms

## Entity Types

```text
contract
party
clause
obligation
risk
vendor
customer
deal
jurisdiction
template
renewal
```

## Relations

```text
contract has_party party
contract contains clause
clause creates obligation
contract based_on template
contract belongs_to vendor
contract belongs_to customer
contract relates_to deal
contract governed_by jurisdiction
renewal applies_to contract
```

## Metrics

```text
risk_score
contract_value
renewal_date
notice_period_days
liability_cap
payment_terms_days
deviation_count
clause_confidence
obligation_count
```

## Content And Embeddings

Embed:

- full contract sections
- clauses
- obligation text
- template clauses
- risk notes
- negotiation comments

## Core Analyses Used

- clause similarity
- duplicate detection
- outlier detection
- semantic search
- gap detection
- cohort comparison

## Module-Specific Analyses

### Template Deviation

Compares clauses against approved templates.

### Unusual Clause Detection

Finds clauses far from normal patterns.

### Missing Clause Detection

Checks required clauses by contract type/jurisdiction.

### Obligation Map

Extracts obligations, owners, dates, and conditions.

### Renewal Risk

Combines renewal date, notice periods, contract value, and risk clauses.

### Vendor/Customer Term Comparison

Compares terms across parties and contract cohorts.

## Dashboards

- Contract overview
- Template deviations
- Unusual clauses
- Missing clauses
- Obligation map
- Renewal risk
- Vendor term comparison

## Reports

- Contract risk brief
- Template deviation report
- Obligation summary
- Renewal risk report

## Headless Agent Workflows

User asks:

```text
Compare this contract to our standard vendor template and show risky deviations.
```

Agent:

1. Gets contract profile.
2. Compares clauses to template.
3. Retrieves risky deviations.
4. Summarizes obligations.
5. Produces brief with evidence.

## AI Agent Decision Support And Automation

AI agents should help legal and business teams triage contracts and understand
risk, while keeping legal judgment with humans.

Decision support:

- recommend which contracts need legal review first
- explain material deviations from standard templates
- identify missing clauses based on contract type
- summarize obligations, deadlines, and owners
- highlight clauses that are unusual compared to prior contracts
- compare vendor/customer terms across a portfolio
- prioritize renewals based on risk, value, and notice periods
- identify where business approval is needed

Automation tasks:

- draft contract risk briefs
- create obligation checklists
- create renewal monitor alerts
- extract clause libraries from existing contracts
- draft redline issue lists for legal review
- summarize negotiation history from comments/notes
- route contracts by risk type or business owner
- generate due diligence contract summaries

Agent guardrails:

- agent should not provide final legal advice
- agent should not approve contracts
- raw contract access and exports must be audited
- agent should cite exact clauses behind every risk statement
- sensitive contracts should default to restricted context packs

## MCP Prompts

```text
/compare_contract_to_template
/find_unusual_clauses
/summarize_obligations
/prepare_contract_risk_brief
/find_missing_clauses
```

## Security Notes

- Raw source access should be restricted by default.
- Export tools should be disabled unless explicitly configured.
- Legal text should be evidence, not legal advice.
- Audit all raw contract access.

## MVP Scope

- PDF/DOCX text import
- clause chunking
- template comparison
- unusual clause detection
- contract risk context pack

## Later Phases

- CLM connectors
- obligation workflow
- jurisdiction-specific templates
- renewal monitors
- negotiation pattern analysis
