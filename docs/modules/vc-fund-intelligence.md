# VC Fund Intelligence Module

## Purpose

VC Fund Intelligence helps investors compare new startups against portfolio
companies, rejected companies, founder patterns, market theses, pitch decks,
investment memos, and financial outcomes.

The module answers:

```text
Have we seen something like this before, and what happened?
```

## Target Users

- VC partners
- associates and analysts
- angel syndicates
- family offices
- accelerators
- corporate venture teams
- AI agents preparing diligence briefs

## Jobs To Be Done

- Compare a new startup to invested companies.
- Compare a new startup to rejected companies.
- Find success and failure analogs.
- Detect thesis fit and thesis drift.
- Find market clusters in dealflow.
- Surface repeated risk themes.
- Prepare investment context packs.
- Learn from past investment decisions.

## Connected Sources

Initial:

- startup application CSV/JSONL
- pitch decks as PDF/text
- investor memos as markdown/docx/pdf text
- financial metrics spreadsheets
- decision history CSV

Later:

- Affinity
- Airtable
- HubSpot/Salesforce
- Google Drive/Dropbox
- email ingestion
- market research databases
- portfolio reporting tools

## Entity Types

```text
startup
founder
market
pitch_deck
memo
financial_metric
investment_decision
portfolio_company
rejected_company
thesis
fund
partner
round
customer_segment
competitor
```

## Relations

```text
startup has_founder founder
startup belongs_to market
startup submitted pitch_deck
partner wrote memo
memo evaluates startup
startup has_decision investment_decision
startup matches thesis
startup competes_with startup
portfolio_company is startup
rejected_company is startup
round funds startup
```

## Metrics

```text
revenue
arr
mrr
growth_rate
burn_rate
runway_months
gross_margin
valuation
team_size
investment_amount
ownership_percent
decision
follow_on_rate
return_multiple
portfolio_status
```

Metric dimensions:

```text
date
round
market
stage
geography
partner
fund
decision_type
```

## Content And Embeddings

Embed:

- startup one-liner
- company description
- pitch deck text
- investor memo
- founder bios
- market thesis docs
- customer/problem sections
- risk notes
- rejection reasons
- portfolio update summaries

Useful vector spaces:

- startup profile vectors
- pitch deck vectors
- memo/risk vectors
- market thesis vectors
- founder background vectors

## Core Analyses Used

- nearest-neighbor similarity
- cohort comparison
- cluster assignment
- centroid comparison
- success pattern mining
- outlier detection
- semantic gap detection

## Module-Specific Analyses

### New Startup Similarity

Compares a new startup to invested and rejected cohorts.

Outputs:

- nearest invested analogs
- nearest rejected analogs
- similarity reasons
- metric differences
- evidence from decks/memos

### Thesis Fit

Compares startup language and market to fund theses.

### Risk Theme Match

Finds risk themes shared with rejected or failed companies.

### Success Pattern Match

Finds patterns shared with strong portfolio companies.

### Dealflow Cluster Map

Maps dealflow by market/problem/customer segment.

### Novelty Detection

Flags startups far from prior invested/rejected clusters.

## Dashboards

- Dealflow semantic map
- New startup review
- Portfolio clusters
- Rejected-company analogs
- Thesis coverage
- Risk themes
- Partner decision patterns

## Reports

- Investment context brief
- Similar-company memo
- Thesis fit report
- Risk analog report
- Portfolio pattern report

## Headless Agent Workflows

### New Startup Review

User asks:

```text
This startup applied today. Compare it to our portfolio and rejected companies.
```

Agent:

1. Finds recently added startup.
2. Builds investment context pack.
3. Searches invested and rejected analogs.
4. Retrieves evidence from decks and memos.
5. Produces diligence questions.

### Portfolio Learning

User asks:

```text
What patterns did our best B2B infrastructure investments share?
```

Agent compares successful investments against weak/refused cohorts.

## AI Agent Decision Support And Automation

AI agents should help investment teams make better, faster, more consistent
decisions, without replacing partner judgment.

Decision support:

- prepare first-pass investment context packs for new startups
- summarize how a startup fits or conflicts with fund theses
- identify nearest invested, failed, and rejected analogs
- generate diligence questions based on similar prior risks
- highlight contradictions between pitch claims and financial metrics
- compare founder-market fit evidence across historical deals
- flag crowded dealflow clusters and semantically novel opportunities
- summarize partner notes and prior decision rationale
- recommend which partner or associate should review a startup based on thesis fit

Automation tasks:

- route new applications to market/thesis clusters
- draft investment committee briefs with citations
- maintain watchlists for startups similar to high-performing portfolio companies
- generate rejection reason drafts based on consistent historical patterns
- enrich startup profiles from pitch decks and memos
- detect missing diligence materials
- produce weekly dealflow summaries
- monitor portfolio updates for risk-theme changes

Agent guardrails:

- agent should never make final investment decisions
- agent should show analogs and evidence, not opaque scores only
- agent should preserve confidentiality of memos and partner notes
- agent should mark weak evidence and missing financials clearly

## MCP Prompts

```text
/analyze_new_startup
/compare_to_portfolio
/compare_to_rejected_startups
/prepare_investment_context_pack
/find_portfolio_success_patterns
/find_repeated_risk_themes
```

## Security Notes

- Pitch decks and memos are highly confidential.
- Raw memo access should be restricted.
- Partner notes may need per-user visibility.
- Exported investment briefs should be audited.
- Portfolio and rejected-company data should be isolated by fund/workspace.

## MVP Scope

- CSV/JSONL startup import
- PDF/text pitch deck extraction
- invested/refused cohort mapping
- nearest analog analysis
- investment context pack
- VC MCP prompts

## Later Phases

- dealflow CRM connectors
- Google Drive integration
- cap table/financial imports
- partner decision analytics
- thesis evolution monitoring
- fund-level benchmarking
