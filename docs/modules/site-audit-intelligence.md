# Site Audit And GEO Intelligence

## Purpose

Site Audit And GEO Intelligence is the default bundled MeaningGrid module.

It lets users crawl one or more domains, deeply analyze technical SEO,
semantic structure, content quality, internal linking, topic coverage, and GEO
readiness, then expose the findings to humans and AI agents.

GEO means generative engine optimization: how well a site can be understood,
trusted, cited, summarized, and used by AI search systems and AI agents.

## Why This Module Should Be Bundled

The open-source distribution needs one complete, useful workflow. Site audit is
the best default because:

- it reuses previous site-audit work
- users understand the value quickly
- the data can be collected without enterprise credentials
- semantic similarity is visually obvious on pages and paragraphs
- it demonstrates clusters, outliers, duplicates, centroids, and evidence
- it is useful for SEO, GEO, content strategy, agencies, and founders
- it can compare multiple domains and show the platform's generality

Other modules can be paid or enterprise later, but this one should be valuable
in the community edition.

## Target Users

- SEO consultants
- GEO consultants
- content strategists
- agencies
- SaaS founders
- ecommerce teams
- technical SEO teams
- AI search optimization teams
- product marketers
- AI agents researching a website

## Jobs To Be Done

- Crawl my website and find technical SEO issues.
- Show which pages are semantically similar or duplicated.
- Find pages far away from the site's topical center.
- Find pages that belong to weak or confused clusters.
- Compare my domain against competitor domains.
- Identify missing content for important topic clusters.
- Find internal linking opportunities based on semantic proximity.
- Explain why a page is weak for AI search engines.
- Generate a prioritized content improvement plan.
- Give an AI agent enough evidence to write a report or content brief.

## Connected Sources

MVP sources:

- website crawler
- sitemap XML
- robots.txt
- HTML pages
- internal links
- external links

Later sources:

- Google Search Console
- Ahrefs/Semrush/Sistrix exports
- PageSpeed Insights
- Chrome UX Report
- analytics exports
- CMS exports
- competitor crawl snapshots
- linkbuilding spreadsheets
- LLM answer observations

## Dataset Types

```text
site_audit
domain_comparison
competitor_gap
geo_readiness
```

## Entity Types

MVP:

```text
domain
crawl_run
page
paragraph
heading
link
topic_cluster
```

Full module:

```text
domain
crawl_run
page
page_snapshot
paragraph
heading
image
link
external_url
schema_markup
topic_cluster
keyword
search_query
competitor_domain
ai_prompt
ai_answer_observation
content_brief
```

## Entity Details

### domain

Represents one crawled domain.

Properties:

- base_url
- host
- scheme
- crawl_scope
- default_language
- country
- brand_name

### crawl_run

Represents one crawl execution.

Properties:

- started_at
- finished_at
- status
- max_pages
- crawl_depth
- include_patterns
- exclude_patterns
- user_agent
- robots_policy

Metrics:

- pages_discovered
- pages_crawled
- pages_failed
- pages_indexable
- pages_non_indexable
- total_internal_links
- total_external_links

### page

Represents a URL as a logical page.

Properties:

- url
- final_url
- canonical_url
- title
- meta_description
- language
- content_type
- status_code
- robots_meta
- is_indexable

Metrics:

- word_count
- title_length
- meta_description_length
- h1_count
- internal_inlinks
- internal_outlinks
- external_outlinks
- load_time_ms
- semantic_depth_score
- geo_readiness_score
- centroid_distance

### paragraph

Represents a paragraph or meaningful section from a page.

Properties:

- text
- order_index
- css_selector
- language

Metrics:

- token_count
- duplicate_similarity_score
- paragraph_consistency_score
- semantic_specificity_score

### heading

Represents H1-H6 headings.

Properties:

- level
- text
- order_index

### link

Represents a discovered link.

Properties:

- source_url
- target_url
- anchor_text
- rel
- is_internal
- is_followed
- status_code

Metrics:

- anchor_relevance_score
- target_semantic_similarity

### topic_cluster

Represents semantic grouping of pages or paragraphs.

Properties:

- label
- description
- representative_terms
- centroid_vector_ref

Metrics:

- page_count
- average_depth_score
- average_geo_readiness_score
- internal_link_density
- content_gap_score

## Relations

```text
domain owns page
crawl_run discovered page
page has_snapshot page_snapshot
page contains paragraph
page contains heading
page contains image
page links_to page
page links_to external_url
page canonical_of page
page redirects_to page
page similar_to page
page duplicates page
page cannibalizes page
page belongs_to topic_cluster
paragraph belongs_to page
heading belongs_to page
link source_page page
link target_page page
page targets keyword
page ranks_for search_query
domain competes_with domain
topic_cluster missing_in domain
ai_answer_observation cites page
```

## Content Units

```text
page_title
meta_description
h1
h2
h3
main_content
paragraph
anchor_text
image_alt_text
schema_jsonld
faq_item
author_bio
organization_facts
```

Embedding strategy:

- embed page-level summary
- embed main content
- embed paragraphs
- embed headings
- embed anchor text groups
- optionally embed schema and FAQ items

Paragraph-level embeddings are important. They let the system detect similarity
inside pages, not only between whole pages.

## Metric Definitions

### Technical SEO Metrics

```text
http_status_code
is_indexable
robots_allowed
has_noindex
canonical_present
canonical_matches_final_url
redirect_hop_count
html_size_bytes
load_time_ms
title_missing
title_length
meta_description_missing
meta_description_length
h1_count
h2_count
images_without_alt_count
schema_type_count
```

### Link Metrics

```text
internal_inlinks
internal_outlinks
external_outlinks
broken_internal_links
broken_external_links
orphan_score
anchor_relevance_score
topic_link_coverage_score
semantic_link_opportunity_count
```

### Semantic Metrics

```text
embedding_centroid_distance
topic_cluster_id
topical_focus_score
semantic_depth_score
duplicate_similarity_score
canonical_topic_overlap_score
cannibalization_risk_score
content_gap_score
paragraph_consistency_score
topic_authority_score
```

### GEO Metrics

```text
answerability_score
entity_coverage_score
source_evidence_score
expertise_signal_score
freshness_signal_score
structured_data_coverage_score
comparison_readiness_score
definition_clarity_score
claim_evidence_density
brand_fact_consistency_score
ai_citation_readiness_score
```

## Analysis Presets

### site_audit_technical

Checks:

- crawl failures
- broken internal links
- redirect chains
- noindex/robots issues
- canonical issues
- missing or weak titles
- missing or weak descriptions
- heading structure
- thin pages
- duplicate titles/descriptions
- schema presence

Core systems used:

- crawler
- raw objects
- entities
- metric values
- relation graph
- insights and evidence

### site_audit_semantic

Checks:

- page clusters
- paragraph clusters
- outlier pages
- pages far from domain centroid
- near-duplicate pages
- duplicated paragraphs
- cannibalization risk
- weak topical clusters
- internal link gaps

Core systems used:

- content units
- chunks
- embeddings
- vector search
- clustering
- centroid metrics
- similarity edges
- analysis artifacts

### site_audit_geo

Checks:

- whether pages clearly answer important questions
- whether entities and facts are explicit
- whether claims have evidence
- whether author/company/product facts are consistent
- whether schema supports the content
- whether comparison and definition content exists
- whether content is useful to AI answer engines

Core systems used:

- semantic analysis
- content metrics
- entity extraction
- evidence scoring
- report templates
- MCP prompts

### domain_comparison

Compares two or more domains by:

- topic coverage
- semantic clusters
- content depth
- GEO readiness
- technical quality
- internal linking
- duplicate/cannibalization patterns
- unique topic ownership
- missing topic areas

Core systems used:

- multi-source dataset
- entity filters
- cohort comparison
- cluster overlap
- semantic gap analysis
- metric summaries

### internal_link_opportunities

Finds pages that are semantically close but weakly linked.

Outputs:

- source page
- target page
- suggested anchor topic
- relevance score
- priority
- evidence paragraphs

### content_brief_generation

Builds content briefs from detected gaps.

Brief includes:

- target topic
- nearest existing pages
- competitor evidence
- missing subtopics
- internal links to include
- facts/entities to mention
- schema recommendations
- questions to answer

## Dashboards

Default dashboards:

```text
site_overview
crawl_status
technical_issues
semantic_map
topic_clusters
outlier_pages
duplicate_content
internal_link_graph
geo_readiness
domain_comparison
page_detail
```

Useful visualizations:

- 2D semantic map of pages
- 2D semantic map of paragraphs
- topic cluster table
- centroid distance ranking
- page similarity table
- link graph
- issue severity table
- domain comparison matrix
- GEO score breakdown

## Reports

Report templates:

```text
technical_seo_report
semantic_site_audit_report
geo_readiness_report
domain_comparison_report
content_gap_report
content_brief
internal_link_plan
```

Reports must include evidence links for every important claim.

## MCP Prompts

```text
/audit_site_geo
/explain_page_outlier
/compare_domains
/find_content_gaps
/find_internal_link_opportunities
/prepare_content_brief
/summarize_crawl_changes
/explain_geo_readiness
/prioritize_site_fixes
```

## MCP Tools Used

```text
list_datasets
get_dataset_card
semantic_search
find_similar_entities
find_similar_chunks
find_outliers
explain_outlier
explain_cluster
build_context_pack
get_evidence
create_report
```

Later:

```text
subscribe_context
list_changed_context
read_context_unit
ack_context_notification
```

## Headless Agent Workflows

### GEO Audit Brief

Agent task:

```text
Prepare a GEO audit for this website and prioritize the 10 most important fixes.
```

MeaningGrid provides:

- dataset card
- crawl summary
- semantic clusters
- GEO metric table
- outlier pages
- duplicate pages
- evidence snippets
- recommended fixes

### Page Outlier Explanation

Agent task:

```text
Why is this page far away from the website centroid?
```

MeaningGrid provides:

- page profile
- nearest neighbors
- cluster summary
- paragraph evidence
- centroid distance
- likely reason
- fix suggestions

### Domain Comparison

Agent task:

```text
Compare our website with these competitor domains and show where we are weaker.
```

MeaningGrid provides:

- domain cohort summaries
- topic cluster overlap
- missing topic clusters
- content depth comparison
- GEO readiness comparison
- evidence pages

## UI Workflow

1. User creates a Site Audit dataset.
2. User enters a domain and crawl limits.
3. Crawler discovers sitemap and pages.
4. Worker stores raw HTML and extracted content.
5. System creates page, paragraph, heading, and link entities.
6. Embedding worker embeds content.
7. Analysis worker runs technical, semantic, and GEO presets.
8. UI shows overview, issues, clusters, outliers, duplicates, and reports.
9. User can ask an AI agent through MCP for explanations and briefs.

## Module Installation

The local Docker seed should install this module automatically:

```yaml
id: site_audit
name: Site Audit And GEO Intelligence
version: 0.1.0
bundled: true
default_enabled: true
license: AGPL-3.0
capabilities:
  - website_crawler
  - entity_schema
  - metric_definitions
  - analysis_presets
  - dashboards
  - reports
  - mcp_prompts
  - context_pack_templates
```

## MVP Scope

MVP should include:

- website crawler
- sitemap discovery
- robots/noindex/canonical parsing
- page and paragraph extraction
- link extraction
- core technical metrics
- local embeddings
- page clustering
- page outliers
- duplicate page detection
- paragraph similarity
- internal link opportunities
- basic GEO readiness score
- overview dashboard
- issue table
- semantic map
- page detail
- report export
- MCP prompts

## Later Phases

Later:

- competitor crawl comparison
- Google Search Console connector
- PageSpeed/CrUX connector
- schema validation
- AI answer observation tracking
- continuous recrawl monitoring
- linkbuilding alignment
- content brief workflow
- scheduled weekly GEO report
- streaming context subscriptions for important new crawl changes

## Security And Governance

Site crawls may include sensitive content for private staging sites.

Requirements:

- respect crawl scope and robots policy setting
- store raw HTML as raw objects with retention policy
- avoid sending content to external LLMs unless enabled
- redact secrets from HTML if detected
- keep source URLs and evidence links auditable
- support private/offline local mode

## Mapping To Core

| Site Audit Feature | MeaningGrid Core |
|---|---|
| Crawl domain | Connector runtime, source events, raw objects |
| Store pages | Entities, content units |
| Store paragraphs | Content units, content chunks |
| Store links | Entity relations |
| Technical checks | Metric definitions, metric values, insights |
| Semantic clusters | Embeddings, analysis runs, artifacts |
| Outlier pages | Centroid metrics, insight evidence |
| Duplicate content | Similarity edges, duplicate analysis |
| GEO scoring | Metric extractors, analysis artifacts |
| Domain comparison | Cohort comparison, semantic gaps |
| Reports | Report templates, exports |
| Agent access | MCP resources, context packs, evidence |
