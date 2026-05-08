# Use Case Templates

## Purpose

Use-case templates let MeaningGrid feel specific while keeping the platform
generic.

Each template should define:

- entity types
- relations
- content units
- metrics
- recommended analyses
- context-pack defaults
- dashboard layout
- report sections
- MCP prompts

## Template Structure

```json
{
  "id": "website_geo",
  "name": "Website and GEO Audit",
  "entity_types": [],
  "relations": [],
  "content_units": [],
  "metrics": [],
  "analyses": [],
  "dashboards": [],
  "prompts": []
}
```

## Website And GEO Template

### Entity Types

```text
domain
page
paragraph
heading
link
query
section
```

### Relations

```text
domain owns page
page contains paragraph
page contains heading
page links_to page
page targets query
paragraph belongs_to page
heading belongs_to page
```

### Content Units

```text
page_body
paragraph
heading
anchor_text
meta_title
meta_description
```

### Metrics

```text
word_count
internal_link_count
external_link_count
in_degree
out_degree
page_rank
answerability_score
indexability
traffic
impressions
clicks
conversions
```

### Analyses

- domain focus and radius
- page clusters
- paragraph clusters
- heading drift
- duplicate pages
- outlier pages
- section coherence
- internal link graph
- wrong-home paragraphs
- query coverage
- GEO answerability
- content gaps

### Report Sections

- executive action plan
- semantic map
- cluster overview
- outliers
- duplicates
- section coherence
- paragraph opportunities
- internal link recommendations
- GEO readiness
- evidence table

### MCP Prompts

```text
/audit_website_geo
/find_page_outliers
/find_duplicate_pages
/recommend_internal_links
/prepare_geo_report
```

## Company Benchmark Template

### Entity Types

```text
company
branch
department
person
product
review
document
market
```

### Relations

```text
company owns branch
branch employs person
company offers product
review describes branch
document describes company
company competes_with company
```

### Content Units

```text
company_description
branch_description
review_text
employee_note
product_description
market_note
```

### Metrics

```text
revenue
growth_rate
profit_margin
customer_satisfaction
review_rating
retention_rate
conversion_rate
response_time
```

### Analyses

- top vs weak branch cohort comparison
- successful company profile
- branch outliers
- semantic gaps in weak companies
- metric-semantic mismatch
- competitor similarity
- best-practice pattern mining

### Questions

- Which weak branches look closest to successful branches?
- What themes are missing in weak companies?
- Which strong companies are semantically unique?
- What patterns correlate with revenue growth?

### MCP Prompts

```text
/compare_companies
/find_branch_success_patterns
/explain_underperforming_branch
/prepare_benchmark_report
```

## Call Center And Sales Template

### Entity Types

```text
call
agent
customer
campaign
transcript_turn
call_phase
objection
outcome
```

### Relations

```text
call handled_by agent
call involves customer
call belongs_to campaign
transcript_turn belongs_to call
objection detected_in call
call has outcome
```

### Content Units

```text
full_transcript
transcript_turn
call_phase_summary
objection_segment
agent_response
customer_response
```

### Metrics

```text
sale_closed
deal_value
duration_seconds
sentiment_score
talk_ratio
agent_talk_time
customer_talk_time
interruption_count
objection_count
csat
```

### Analyses

- won vs lost calls
- objection handling clusters
- agent pattern comparison
- transcript phase drift
- nearest winning call examples
- failed-call remediation suggestions
- sentiment and semantic divergence

### Questions

- Where do lost calls diverge from won calls?
- Which agent responses correlate with success?
- Which objections are handled poorly?
- Which failed calls are closest to successful calls?

### MCP Prompts

```text
/analyze_sales_calls
/compare_won_lost_calls
/find_best_call_examples
/explain_failed_call
/create_call_coaching_plan
```

## Support Ticket Template

### Entity Types

```text
ticket
customer
agent
organization
message
product_area
knowledge_article
resolution
```

### Relations

```text
ticket opened_by customer
ticket handled_by agent
ticket belongs_to organization
message belongs_to ticket
ticket relates_to product_area
ticket resolved_by resolution
ticket answered_by knowledge_article
```

### Content Units

```text
ticket_subject
ticket_message
agent_reply
customer_reply
resolution_summary
knowledge_article_section
```

### Metrics

```text
status
priority
resolution_time
first_response_time
reopen_count
escalated
csat
churn_risk
```

### Analyses

- ticket clusters
- unresolved cluster detection
- knowledge-base gap detection
- escalation patterns
- churn-risk semantic patterns
- duplicate ticket themes
- support article coverage

### MCP Prompts

```text
/analyze_support_tickets
/find_kb_gaps
/explain_escalation_patterns
/prepare_support_report
```

## Knowledge Base Template

### Entity Types

```text
document
section
paragraph
owner
team
product
topic
```

### Relations

```text
document owned_by team
document contains section
section contains paragraph
document describes product
document covers topic
```

### Content Units

```text
document_body
section
paragraph
heading
code_block
table_text
```

### Metrics

```text
last_updated_at
view_count
search_hits
helpfulness_score
owner_status
staleness_days
```

### Analyses

- duplicate docs
- fragmented topics
- stale important docs
- orphan docs
- missing topics
- retrieval readiness
- agent context quality

### MCP Prompts

```text
/analyze_knowledge_base
/find_duplicate_docs
/find_missing_docs
/prepare_agent_context
```

## Custom Entity Template

Custom template should let users define:

- entity type names
- label fields
- text fields
- metric fields
- relation fields
- success metric
- comparison cohorts
- analysis goals

Initial UI can be simple:

1. Upload CSV/JSONL.
2. Select primary entity.
3. Select text columns.
4. Select metric columns.
5. Select success metric.
6. Run analysis.

## Template Registry

Templates should be stored as versioned JSON/YAML.

Fields:

```text
template_id
version
display_name
description
entity_types
relations
content_units
metrics
analysis_defaults
dashboard_defaults
prompt_defaults
```

Templates can become a future marketplace:

- community templates
- enterprise templates
- vertical templates
- customer-private templates

## Marketing Performance Template

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
product
order
customer_segment
channel
```

### Streams

```text
Google Search Console query/page metrics
Google Ads campaign/ad group/keyword/search term metrics
Meta Ads campaign/adset/ad/creative metrics
Ecommerce orders and product sales
Website crawl snapshots
Linkbuilding targets
```

### Relations

```text
campaign contains ad_group
ad_group targets keyword
search_query lands_on page
ad links_to page
order contains product
page describes product
keyword semantically_matches page
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
```

### Analyses

- paid keyword to landing page semantic alignment
- organic query to content cluster coverage
- campaign spend to content gap analysis
- ad copy to page content similarity
- product sales to content coverage
- new keyword drift monitoring
- linkbuilding target relevance

### MCP Prompts

```text
/analyze_marketing_alignment
/find_paid_keyword_content_gaps
/compare_organic_and_paid_queries
/summarize_new_marketing_changes
```

## Investor Portfolio Template

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
```

### Streams

```text
new startup applications
new pitch decks
updated financials
new investor memos
portfolio performance updates
market notes
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
portfolio_status
decision
```

### Analyses

- new startup similarity to portfolio companies
- new startup similarity to rejected companies
- nearest success/failure analogs
- market cluster assignment
- risk theme comparison
- performance analog discovery

### MCP Prompts

```text
/analyze_new_startup
/compare_to_portfolio
/compare_to_rejected_startups
/prepare_investment_context_pack
```
