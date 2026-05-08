# Marketing Intelligence Module

## Purpose

Marketing Intelligence connects search demand, ads, website content,
linkbuilding, ecommerce sales, conversion data, and semantic content coverage.

The module answers:

```text
Are the things we pay for, rank for, sell, and write about semantically aligned?
```

## Target Users

- growth marketers
- SEO/GEO specialists
- PPC managers
- content strategists
- ecommerce managers
- agencies managing multiple clients
- AI agents preparing marketing reports

## Jobs To Be Done

- Find paid keywords that do not match landing page content.
- Find organic search queries that deserve dedicated content.
- Compare paid and organic topic coverage.
- Identify high-revenue products with weak content.
- Prioritize content based on spend, revenue, and semantic gaps.
- Monitor new search terms and alert when content coverage is weak.
- Connect linkbuilding targets to revenue and topic authority.
- Prepare weekly marketing insight reports with evidence.

## Connected Sources

Initial:

- website crawler
- CSV/XLSX imports for keywords, campaigns, products, orders
- Google Search Console export
- Google Ads export
- ecommerce orders JSONL/CSV

Later:

- Google Search Console API
- Google Ads API
- Meta/Facebook Ads API
- Shopify
- WooCommerce
- GA4
- Ahrefs/Semrush exports
- CRM conversion events
- linkbuilding sheets

## Entity Types

```text
website
page
paragraph
heading
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
backlink
competitor_domain
```

## Relations

```text
website owns page
page contains paragraph
page contains heading
campaign contains ad_group
ad_group targets keyword
ad links_to landing_page
search_query lands_on page
search_query semantically_matches page
keyword semantically_matches page
page describes product
order contains product
link_target points_to page
backlink points_to page
competitor_domain competes_with website
```

## Metrics

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
organic_impressions
product_sales
margin
return_rate
backlinks
referring_domains
domain_rating
content_word_count
answerability_score
```

Metric dimensions:

```text
date
country
device
campaign
ad_group
keyword
query
page
product
channel
source
medium
```

## Content And Embeddings

Embed:

- page body
- paragraphs
- headings
- meta title and description
- keyword text
- search query text
- ad copy
- product title and description
- link anchor text
- competitor page snippets

Useful vector spaces:

- content chunks
- page-level centroids
- keyword/query vectors
- ad creative vectors
- product vectors

## Core Analyses Used

- semantic search
- semantic alignment
- centroid and radius
- cluster detection
- outlier detection
- gap detection
- cohort comparison
- metric-weighted prioritization
- time-window delta analysis
- duplicate/cannibalization detection

## Module-Specific Analyses

### Keyword To Page Alignment

Compares paid keywords and organic queries to landing pages and page clusters.

Outputs:

- best matching page
- alignment score
- mismatch reason
- spend/revenue priority
- recommended action

### Paid Content Gap

Finds high-spend or high-converting paid terms that lack strong content.

### Organic Opportunity Gap

Finds organic queries with impressions or clicks but weak dedicated content.

### Ad Copy To Landing Page Similarity

Detects when ad promise and landing page content diverge.

### Product Revenue To Content Coverage

Finds high-revenue products with weak descriptions, weak content clusters, or
missing supporting pages.

### Linkbuilding Target Relevance

Scores whether linkbuilding targets support high-value commercial clusters.

### Weekly Change Monitor

Tracks new queries, new paid search terms, changed page content, and content
coverage movement.

## Dashboards

- Marketing overview
- Paid keyword alignment
- Organic query coverage
- Paid vs organic topic overlap
- Product content coverage
- Linkbuilding relevance
- New weekly changes
- Content priorities

## Reports

- Weekly marketing alignment report
- GEO content opportunity report
- Paid search content gap report
- Ecommerce content priority report
- Linkbuilding relevance report

## Headless Agent Workflows

### Weekly Alignment Review

User asks:

```text
What changed in paid keyword/content alignment this week?
```

Agent:

1. Lists marketing dataset streams.
2. Builds delta context pack since last week.
3. Retrieves high-cost weak-alignment keywords.
4. Gets evidence for top gaps.
5. Produces recommendations.

### Content Planning

User asks:

```text
What content should we create next based on paid spend and organic demand?
```

Agent compares:

- paid cost
- conversions
- organic impressions
- page similarity
- product revenue
- existing content clusters

## AI Agent Decision Support And Automation

AI agents should help marketers move from analysis to decisions.

Decision support:

- prioritize content briefs by spend, conversion potential, and semantic gap
- recommend whether to create a new page, update an existing page, or change ad targeting
- explain why a landing page is a poor match for a paid keyword
- identify which campaigns should be paused, expanded, or reviewed
- recommend internal links for pages supporting high-value topics
- choose which product/category pages deserve content investment first
- summarize weekly changes for executives, PPC teams, and content teams
- compare proposed content plans against actual search demand

Automation tasks:

- generate content brief drafts from keyword/query clusters
- create weekly marketing reports with evidence
- open tasks in project management tools for content updates
- monitor new paid search terms and alert on weak content match
- draft landing page improvement recommendations
- draft ad group restructuring suggestions
- classify new queries into topic clusters
- route content gaps to SEO, PPC, or ecommerce owners
- prepare competitor content comparison packs

Agent guardrails:

- agent should recommend campaign changes but not push ad-budget changes without approval
- agent should cite spend/conversion evidence for priorities
- agent should separate factual findings from suggested strategy
- agent should preserve client/workspace isolation in agency mode

## MCP Prompts

```text
/analyze_marketing_alignment
/find_paid_keyword_content_gaps
/compare_organic_and_paid_queries
/summarize_new_marketing_changes
/recommend_content_priorities
/prepare_geo_growth_report
```

## Security Notes

- Ad spend and revenue can be sensitive.
- Agency mode needs strict client/workspace separation.
- Raw ad account data should require explicit permission.
- Reports should avoid exposing customer-level ecommerce data unless permitted.

## MVP Scope

- Website crawler
- CSV imports for GSC, Google Ads, products/orders
- Keyword to page alignment
- Paid content gap table
- Marketing context pack
- MCP prompts
- Basic report

## Later Phases

- API connectors
- Meta Ads
- GA4
- competitor imports
- automated monitors
- ecommerce platform connectors
- agency multi-client rollups
