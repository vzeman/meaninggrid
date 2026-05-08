# Modular Architecture And Example Modules

## Purpose

MeaningGrid core should stay generic:

- entities
- relations
- content units
- metrics
- embeddings
- vector search
- analysis runs
- context packs
- MCP/API/CLI
- security
- streaming
- reprocessing

Specialized business value should be added through modules.

Detailed customer/task/core mapping for all major modules:
[Module Feature Mapping To MeaningGrid Core](modules/module-feature-mapping.md).

Examples:

- Site Audit And GEO Intelligence
- Marketing Intelligence
- VC Fund Intelligence
- Sales Intelligence
- Customer Support Intelligence
- Knowledge Base Intelligence
- Ecommerce Intelligence
- Product Event Intelligence
- Legal Contract Intelligence
- HR/Talent Intelligence
- Procurement/Vendor Intelligence
- M&A/Due Diligence Intelligence

Modules should not fork the platform. They should plug into the core through a
stable module contract.

The default open-source distribution should bundle and enable the Site Audit
And GEO module. Other specialized modules can be optional, paid, enterprise, or
community packages.

Modules should also define recommended labels, metadata fields, and filter
presets. Detailed push and filter behavior is defined in
[Data Push, Labeling, And Filtering](18-data-push-labeling-filtering.md).

## Core Vs Module Boundary

### Core Owns

```text
tenancy
auth
permissions
workspace/dataset lifecycle
entity model
content/chunk model
metrics model
relations
raw/source event storage
embedding pipeline
vector store adapters
analysis execution framework
artifact storage
context packs
MCP server
API server
CLI
web shell
streaming/reprocessing framework
audit logs
security/redaction
```

### Modules Own

```text
domain schema
domain terminology
connectors
mapping presets
metric definitions
relation definitions
analysis presets
domain-specific analyses
context-pack templates
MCP prompts
dashboard layouts
report templates
monitors and alerts
recommended workflows
sample data
documentation
```

## Module Package Structure

Recommended structure:

```text
modules/
  site-audit/
    module.yaml
    schema/
    analyses/
    dashboards/
    reports/
    prompts/
  marketing/
    module.yaml
    schema/
      entity-types.yaml
      relations.yaml
      metrics.yaml
    connectors/
      google_search_console.yaml
      google_ads.yaml
      meta_ads.yaml
      ecommerce_orders.yaml
    mappings/
      gsc_default.yaml
      google_ads_default.yaml
    analyses/
      keyword_page_alignment.yaml
      content_gap_from_paid_search.yaml
      channel_topic_overlap.yaml
    prompts/
      analyze_marketing_alignment.md
      summarize_weekly_growth_changes.md
    context/
      marketing_context_pack.yaml
      delta_marketing_context_pack.yaml
    dashboards/
      marketing_overview.yaml
      keyword_alignment.yaml
    reports/
      marketing_alignment_report.yaml
    monitors/
      paid_keyword_without_content.yaml
    examples/
      sample_keywords.csv
      sample_orders.jsonl
    README.md
```

## Module Manifest

Each module should have a manifest.

Example:

```yaml
id: marketing
name: Marketing Intelligence
version: 0.1.0
description: Connects search, ads, ecommerce, content, and semantic coverage.
requires_core: ">=0.1.0"
license: AGPL-3.0
capabilities:
  - connectors
  - entity_schema
  - analysis_presets
  - dashboards
  - mcp_prompts
  - monitors
  - context_units
  - context_subscriptions
default_templates:
  dataset_kind: marketing
  context_pack: marketing_context_pack
  context_unit: campaign_alignment_window
  context_subscription: paid_keyword_content_gap
  dashboard: marketing_overview
permissions:
  required:
    - dataset:read
    - analysis:create
  optional:
    - source:configure
    - raw_source:read
    - export:data
```

## Module Registry

MeaningGrid should include a module registry.

Registry responsibilities:

- list installed modules
- validate module manifests
- install module migrations/config
- register entity schemas
- register connectors
- register analysis presets
- register prompts
- register context unit builders
- register context subscription templates
- register routing rules
- expose module resources through API/MCP
- manage module version upgrades
- disable modules safely

Tables:

```text
modules
module_versions
module_installations
module_resources
module_migrations
```

## Module Installation Lifecycle

1. Discover module.
2. Validate manifest.
3. Check core version compatibility.
4. Register schemas, metrics, relations.
5. Register connectors and mapping presets.
6. Register analyses, prompts, dashboards, reports.
7. Apply module migrations if needed.
8. Create module installation record.
9. Expose module through API/MCP/UI.

## Dataset Template Lifecycle

Modules usually provide dataset templates.

Example:

```text
Create Marketing Dataset
  -> install marketing schema
  -> configure streams/connectors
  -> import website content
  -> sync GSC/Ads/ecommerce metrics
  -> run alignment analysis
  -> create context pack
  -> expose MCP prompts
```

## Module Interfaces

### Connector Interface

Modules can contribute connector definitions or connector adapters.

Required functions:

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

### Schema Interface

Modules define:

- entity types
- relation types
- content unit kinds
- metric definitions
- dimension definitions
- default labels
- default text fields

Core stores these as normal MeaningGrid schema records.

### Analysis Interface

Modules can register analysis presets.

Analysis preset fields:

```yaml
id: keyword_page_alignment
name: Keyword to Page Alignment
input_entity_types:
  - keyword
  - page
required_metrics:
  - cost
  - conversions
outputs:
  - alignment_table
  - gap_insights
  - recommendations
runner: core.semantic_alignment
config:
  source_entity_type: keyword
  target_entity_type: page
  source_text_fields: [keyword_text]
  target_text_fields: [title, headings, body]
  priority_metrics: [cost, conversions, revenue]
```

Analysis runners can be:

- core generic runners
- module-specific Python functions
- external services
- SQL/ClickHouse query templates
- LLM-assisted explainers over deterministic outputs

### Context Interface

Modules define context-pack templates.

Example:

```yaml
id: marketing_context_pack
includes:
  - dataset_card
  - stream_status
  - entity_schema
  - metric_definitions
  - recent_keyword_changes
  - top_alignment_gaps
  - high_spend_low_content_match
  - evidence_pack
budget_defaults:
  small: 8000
  medium: 30000
  large: 100000
```

### MCP Interface

Modules can register prompts and tool presets.

Prompts:

```text
/analyze_marketing_alignment
/find_paid_keyword_content_gaps
/prepare_investment_context_pack
/compare_won_lost_calls
/find_kb_gaps
```

Modules should not bypass core MCP security. They register prompts and tool
workflows; core enforces permissions.

### Dashboard Interface

Dashboards should be declarative where possible.

Dashboard blocks:

```text
metric_card
table
semantic_map
cluster_view
cohort_comparison
time_series
heatmap
evidence_panel
report_section
monitor_list
```

The same module should work without dashboards in headless mode.

## Headless Module Usage

Modules must be useful through MCP/API alone.

Example:

```text
User asks agent:
"Which new paid keywords should we support with content?"

Agent calls:
list_datasets()
build_delta_context_pack(dataset_id, since, task)
semantic_search()
get_evidence()

Module contributes:
marketing schema
keyword alignment analysis
marketing-specific context template
marketing MCP prompt
```

## Module Permissions

Modules declare required and optional permissions, but core enforces them.

Examples:

Marketing module:

- read campaign metrics
- read page content
- create analysis runs
- optional raw ad data access
- optional export report

VC module:

- read startup profiles
- read pitch deck text
- read decision history
- optional raw memo access
- optional export investment memo

Legal module:

- read contracts
- read clauses
- restricted raw document access
- export disabled by default

## Module Versioning

Modules need versioning because schemas and analyses will evolve.

Versioned resources:

- schema definitions
- metric definitions
- mapping presets
- analysis presets
- prompt templates
- context-pack templates
- report templates

Rules:

- existing analysis runs remain tied to the module version used
- context packs record module version
- schema migrations should be explicit
- destructive migrations require confirmation
- module upgrades can trigger reprocessing recommendations

## Example Module: Marketing Intelligence

Detailed spec: [Marketing Intelligence](modules/marketing-intelligence.md)

### Use Case

Marketing teams want to understand whether search demand, paid campaigns,
website content, linkbuilding, ecommerce sales, and conversion outcomes are
semantically aligned.

### Connected Sources

- website crawler
- Google Search Console
- Google Ads
- Meta/Facebook Ads
- ecommerce platform
- CRM conversions
- linkbuilding sheets
- analytics exports

### Entity Types

```text
website
page
paragraph
keyword
search_query
campaign
ad_group
ad
creative
landing_page
product
order
customer_segment
channel
link_target
```

### Metrics

```text
impressions
clicks
ctr
cost
cpc
conversions
conversion_rate
revenue
roas
organic_position
organic_clicks
product_sales
margin
backlinks
referring_domains
```

### Core Analyses Used

- semantic alignment
- centroid comparison
- cluster detection
- gap detection
- outlier detection
- metric-weighted prioritization
- time-window delta analysis

### Module-Specific Analyses

- paid keyword to landing page alignment
- search query to content cluster coverage
- ad copy to page similarity
- product revenue to content coverage
- linkbuilding target relevance
- organic vs paid topic overlap
- new keyword drift monitoring

### Human Interface

Dashboards:

- marketing overview
- keyword/page alignment
- paid content gaps
- organic vs paid coverage
- product content coverage
- weekly changes

### Agent Interface

Prompts:

```text
/analyze_marketing_alignment
/find_paid_keyword_content_gaps
/compare_organic_and_paid_queries
/summarize_new_marketing_changes
/recommend_content_priorities
```

Example agent answer:

```text
This week, 14 new paid search terms have high cost and weak landing-page
alignment. The largest gap is around "enterprise invoice approval workflow".
The nearest page is generic accounts-payable content, but it lacks workflow,
approval routing, and compliance language. Create or update a landing page and
link it from the accounting automation cluster.
```

## Example Module: VC Fund Intelligence

Detailed spec: [VC Fund Intelligence](modules/vc-fund-intelligence.md)

### Use Case

VC funds want to compare new startups against invested companies, rejected
companies, market theses, founder profiles, pitch decks, and historical
investment outcomes.

### Connected Sources

- application forms
- pitch decks
- investor memos
- CRM/dealflow tools
- financial spreadsheets
- portfolio updates
- market research docs
- emails or notes

### Entity Types

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
```

### Metrics

```text
revenue
growth_rate
burn_rate
runway_months
valuation
team_size
investment_amount
decision
portfolio_status
follow_on_rate
return_multiple
```

### Core Analyses Used

- nearest-neighbor similarity
- cohort comparison
- success pattern mining
- outlier detection
- cluster assignment
- semantic drift

### Module-Specific Analyses

- new startup to invested analogs
- new startup to rejected analogs
- thesis fit
- founder-market fit signals
- risk-theme similarity
- market saturation clusters
- investment memo context pack

### Human Interface

Dashboards:

- dealflow map
- new startup similarity
- portfolio clusters
- rejected-company analogs
- thesis coverage
- risk themes

### Agent Interface

Prompts:

```text
/analyze_new_startup
/compare_to_portfolio
/compare_to_rejected_startups
/prepare_investment_context_pack
/find_portfolio_success_patterns
```

Example agent answer:

```text
The new startup is closest to three rejected SMB payroll compliance companies
by go-to-market language and problem framing, but its growth metrics resemble
two successful portfolio companies. The key diligence question is whether the
claimed distribution channel is real or only pitch language.
```

## Example Module: Sales Intelligence

Detailed spec: [Sales Intelligence](modules/sales-intelligence.md)

### Use Case

Sales teams want to understand why deals are won or lost across calls, emails,
CRM notes, objections, account profiles, and rep behavior.

### Connected Sources

- CRM
- call recording/transcript tools
- email sync
- sales engagement tools
- meeting notes
- proposal documents

### Entity Types

```text
deal
account
contact
sales_rep
call
email
meeting
objection
competitor
proposal
stage
```

### Metrics

```text
deal_value
stage
closed_won
sales_cycle_days
call_duration
reply_rate
meeting_count
discount
forecast_category
```

### Analyses

- won vs lost cohort comparison
- objection handling patterns
- rep coaching opportunities
- deal risk similarity
- best-example retrieval
- stage drift detection
- account similarity

### Agent Prompts

```text
/compare_won_lost_deals
/explain_lost_deal
/find_best_call_examples
/prepare_rep_coaching_plan
/identify_deal_risks
```

## Example Module: Customer Support Intelligence

Detailed spec: [Customer Support Intelligence](modules/customer-support-intelligence.md)

### Use Case

Support and product teams want to identify repeated issues, escalation causes,
knowledge-base gaps, churn risks, and customer sentiment patterns.

### Connected Sources

- Zendesk
- LiveAgent
- Intercom
- Freshdesk
- chat logs
- email tickets
- knowledge base
- product analytics

### Entity Types

```text
ticket
conversation
customer
agent
organization
message
product_area
knowledge_article
resolution
escalation
```

### Metrics

```text
priority
status
resolution_time
first_response_time
reopen_count
csat
escalated
churn_risk
ticket_volume
```

### Analyses

- ticket clusters
- growing issue detection
- escalation pattern analysis
- KB gap detection
- similar resolved ticket retrieval
- churn-risk themes
- agent response quality

### Agent Prompts

```text
/analyze_support_tickets
/find_kb_gaps
/explain_escalation_patterns
/summarize_new_support_issues
/recommend_kb_articles
```

## Example Module: Knowledge Base Intelligence

Detailed spec: [Knowledge Base Intelligence](modules/knowledge-base-intelligence.md)

### Use Case

Companies want internal docs to be clean, discoverable, fresh, and agent-ready.

### Connected Sources

- Google Drive
- SharePoint
- Notion
- Confluence
- Git repositories
- Markdown docs
- PDFs

### Entity Types

```text
document
section
paragraph
owner
team
product
topic
policy
runbook
```

### Metrics

```text
last_updated_at
view_count
search_hits
helpfulness_score
owner_status
staleness_days
retrieval_score
```

### Analyses

- duplicate docs
- fragmented topics
- stale important docs
- orphan docs
- missing docs
- agent context readiness
- document ownership gaps

### Agent Prompts

```text
/analyze_knowledge_base
/find_duplicate_docs
/find_missing_docs
/prepare_agent_context
/summarize_stale_critical_docs
```

## Example Module: Ecommerce Intelligence

Detailed spec: [Ecommerce Intelligence](modules/ecommerce-intelligence.md)

### Use Case

Ecommerce teams want to connect product descriptions, reviews, ads, search
queries, sales, returns, and support issues.

### Connected Sources

- Shopify/WooCommerce/Magento
- product catalog
- reviews
- ads
- search console
- orders
- returns
- support tickets

### Entity Types

```text
product
category
review
order
return
campaign
search_query
page
customer_segment
support_ticket
```

### Metrics

```text
sales
revenue
margin
conversion_rate
return_rate
review_rating
inventory
ad_cost
roas
support_volume
```

### Analyses

- product content vs search demand
- review themes vs product descriptions
- return reason clusters
- high-sales low-content products
- product similarity and cannibalization
- support issue impact on revenue

### Agent Prompts

```text
/analyze_product_content_gaps
/explain_return_patterns
/find_review_themes
/recommend_product_page_updates
```

## Example Module: Product Event Intelligence

Detailed spec: [Product Event Intelligence](modules/product-event-intelligence.md)

This module analyzes application and website event streams, account journeys,
feature adoption, trial conversion, churn risk, and expansion signals. It uses
source events, entity relations, metric values, sequence summaries, cohort
comparison, and monitors to score current users/accounts and recommend next
best actions.

Core chain:

```text
app/website events
-> user/account/session/event entities
-> event sequence summaries and metrics
-> converter/non-converter cohort analysis
-> upgrade/churn/activation insights
-> MCP context pack or dashboard
```

Agent prompts:

```text
/score_trial_accounts
/explain_account_upgrade_likelihood
/find_activation_milestones
/recommend_next_best_action
```

## Example Module: Legal Contract Intelligence

Detailed spec: [Legal Contract Intelligence](modules/legal-contract-intelligence.md)

### Use Case

Legal teams want to compare contracts, detect unusual clauses, map obligations,
and understand risk across vendors, customers, and deals.

### Connected Sources

- contract repositories
- CLM tools
- PDFs/DOCX files
- vendor systems
- CRM deal docs

### Entity Types

```text
contract
party
clause
obligation
risk
vendor
deal
jurisdiction
template
```

### Metrics

```text
risk_score
contract_value
renewal_date
notice_period_days
liability_cap
payment_terms_days
deviation_count
```

### Analyses

- clause similarity
- unusual clause detection
- template deviation
- obligation extraction
- vendor risk comparison
- renewal risk monitoring
- missing clause detection

### Agent Prompts

```text
/compare_contract_to_template
/find_unusual_clauses
/summarize_obligations
/prepare_contract_risk_brief
```

Security note:

This module should default to restricted raw-source access and conservative
export permissions.

## Example Module: HR And Talent Intelligence

Detailed spec: [HR/Talent Intelligence](modules/hr-talent-intelligence.md)

### Use Case

HR and recruiting teams want to compare candidates, interviews, employee
feedback, performance notes, exit interviews, and engagement surveys.

### Connected Sources

- ATS
- interview notes
- resumes/CVs
- HRIS
- engagement surveys
- performance reviews
- exit interviews

### Entity Types

```text
candidate
employee
role
team
interview
resume
feedback
survey_response
performance_review
exit_interview
```

### Metrics

```text
hire_decision
performance_rating
tenure_months
engagement_score
attrition_risk
time_to_hire
offer_acceptance
```

### Analyses

- candidate similarity to successful employees
- interview feedback themes
- attrition risk themes
- engagement cluster changes
- team culture patterns
- hiring rubric consistency

### Agent Prompts

```text
/compare_candidate_to_success_profiles
/summarize_interview_feedback
/find_engagement_themes
/explain_attrition_patterns
```

Security note:

This module needs strong PII handling, restricted access, and careful retention
policies.

## Example Module: Procurement And Vendor Intelligence

Detailed spec: [Procurement/Vendor Intelligence](modules/procurement-vendor-intelligence.md)

### Use Case

Procurement teams want to compare vendors, contracts, RFP responses, spend,
support quality, security reviews, and performance.

### Connected Sources

- procurement systems
- vendor contracts
- RFP/RFI responses
- security questionnaires
- spend systems
- support tickets
- vendor reviews

### Entity Types

```text
vendor
contract
proposal
rfp
security_review
spend_record
business_owner
service
issue
```

### Metrics

```text
spend
contract_value
risk_score
sla_score
renewal_date
ticket_volume
response_time
compliance_status
```

### Analyses

- vendor similarity
- proposal comparison
- contract/risk gap detection
- spend vs value alignment
- renewal risk monitoring
- security questionnaire clustering

### Agent Prompts

```text
/compare_vendors
/summarize_vendor_risk
/prepare_renewal_brief
/find_rfp_response_patterns
```

## Example Module: Compliance And Audit Intelligence

Detailed spec: [Compliance/Audit Intelligence](modules/compliance-audit-intelligence.md)

### Use Case

Compliance teams want to map policies, controls, evidence, incidents, and audit
findings.

### Connected Sources

- policy documents
- control systems
- ticketing systems
- audit evidence folders
- incident reports
- compliance platforms

### Entity Types

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
```

### Metrics

```text
control_status
evidence_age_days
risk_score
finding_severity
remediation_time
owner_response_time
```

### Analyses

- control-to-evidence coverage
- missing evidence
- duplicate controls
- stale evidence
- incident theme clustering
- audit readiness context packs

### Agent Prompts

```text
/prepare_audit_context_pack
/find_missing_evidence
/summarize_control_gaps
/explain_incident_themes
```

## How Modules Connect Features Together

Every module should connect the same core feature chain:

```text
connector -> source events/raw objects -> entity mapper -> content/metrics
-> embeddings -> analysis presets -> insights/evidence -> context packs
-> MCP/API/UI/report/monitor
```

Example for marketing:

```text
Google Ads connector
-> keyword and campaign entities
-> cost/conversion metrics
-> keyword embeddings
-> keyword-page alignment analysis
-> content-gap insights
-> marketing context pack
-> MCP prompt answers user question
```

Example for VC:

```text
new startup application
-> startup/founder/deck entities
-> growth and valuation metrics
-> deck/memo embeddings
-> similarity to invested/rejected cohorts
-> investment-context insight
-> VC context pack
-> agent prepares diligence brief
```

## Module Development Priorities

Recommended first modules:

1. Marketing Intelligence
2. VC Fund Intelligence
3. Product Event Intelligence
4. Sales Intelligence
5. Customer Support Intelligence
6. Knowledge Base Intelligence

Why:

- they prove different data shapes
- they use streaming and batch data
- they use semantic + metric comparison
- they are valuable in headless mode
- they share reusable core primitives

## Module Quality Requirements

Each module should include:

- manifest
- schemas
- sample data
- import instructions
- one headless MCP demo
- one dashboard/report demo where UI exists
- at least three analysis presets
- at least three prompts
- security notes
- reprocessing notes
- tests for schema and analysis config
