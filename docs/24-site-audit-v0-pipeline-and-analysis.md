# Site Audit V0 Pipeline And Analysis

## Purpose

This document specifies the first real analysis pipeline for MeaningGrid:
Site Audit v0.

The pipeline should prove that MeaningGrid can:

- ingest a website
- preserve raw evidence
- model pages and paragraphs as entities/content
- embed text
- compute semantic similarity
- find clusters, duplicates, and outliers
- score technical and GEO quality
- explain findings with evidence

## Pipeline Overview

```text
create dataset
-> start crawl job
-> discover URLs
-> fetch pages
-> store raw HTML
-> extract page metadata/content/links
-> create entities/content/relations/metrics
-> chunk content
-> embed chunks and page summaries
-> run technical analysis
-> run semantic analysis
-> run GEO analysis
-> create insights and evidence
-> render UI artifacts and context pack
```

## Job Sequence

For v0, use separate jobs but allow the UI to present them as one workflow.

```text
crawl_site
extract_site_content
embed_dataset
analyze_site_technical
analyze_site_semantic
analyze_site_geo
build_site_report
```

The orchestration job can create child jobs in sequence:

```text
run_site_audit_v0
```

## Inputs

Required:

```text
dataset_id
base_url
max_pages
```

Optional:

```text
include_patterns
exclude_patterns
respect_robots
render_javascript
max_depth
language_hint
```

V0 defaults:

```text
max_pages: 100
respect_robots: true
render_javascript: false
max_depth: 4
same_host_only: true
```

## URL Discovery

Discovery sources:

1. Base URL.
2. Sitemap URLs from `/sitemap.xml`.
3. Sitemap URLs referenced from `robots.txt`.
4. Internal links found during crawl.

Normalize URLs:

- lowercase host
- remove fragments
- normalize trailing slash policy
- resolve relative URLs
- keep query string by default, but de-duplicate obvious tracking params

Ignore by default:

```text
utm_*
fbclid
gclid
msclkid
```

Do not crawl:

- external hosts
- mailto/tel/javascript links
- binary files unless explicitly supported
- URLs blocked by robots if `respect_robots=true`

## Fetching

Fetcher should record:

- requested_url
- final_url
- status_code
- content_type
- headers
- redirect_chain
- fetched_at
- duration_ms
- error if failed

Store:

- raw HTML in object storage
- response metadata in `raw_objects.metadata_json`
- `source_event` for page fetched or failed

V0 does not need JavaScript rendering by default. Add Playwright support behind
a flag later.

## Extraction

From every HTML page extract:

- title
- meta description
- canonical URL
- robots meta
- language
- headings H1-H3
- main text
- paragraphs
- links
- image alt text count
- JSON-LD/schema types

Recommended libraries:

```text
selectolax or lxml for DOM
trafilatura/readability for main text fallback
```

Extraction must produce deterministic content hashes so reprocessing can skip
unchanged units.

## Entity Mapping

### domain

One entity per host.

External ID:

```text
host
```

### crawl_run

One entity per crawl execution.

External ID:

```text
crawl:{job_id}
```

### page

One entity per final canonical URL, where possible.

External ID:

```text
normalized_final_url
```

Properties:

```text
requested_url
final_url
canonical_url
title
meta_description
language
status_code
content_type
robots_meta
is_indexable
redirect_chain
```

### paragraph

V0 can store paragraphs as content units only. If paragraph-level entity
analysis becomes useful, paragraph entities can be added later.

### heading

V0 can store headings as content units. Heading entities are optional.

### link

V0 should store internal page-to-page links as `entity_relations`.

External links can be stored in relation properties or as `to_external_ref`.

## Content Units

Create content units:

```text
page_title
meta_description
h1
h2
h3
main_content
paragraph
anchor_text_group
schema_jsonld
```

V0 required:

```text
page_title
meta_description
h1
h2
main_content
paragraph
```

## V0 Embedding Implementation

The first implementation embeds every `content_chunk` after crawl extraction.
The default local provider is deterministic and offline-safe so Docker tests do
not depend on downloading a model. It writes:

- embedding model identity to `embedding_models`
- run status to `embedding_runs`
- vector lineage to `embeddings`
- vectors to Qdrant collection
  `mg_local_sentence_transformers_all_minilm_l6_v2_content_chunks`

Every Qdrant point payload must include tenant, workspace, dataset, entity,
content unit, content chunk, module, classification, language, and content hash
fields so later semantic search and MCP tools can always filter safely.

## V0 Semantic Search

The first user-facing semantic search surface is:

```text
POST /datasets/{dataset_id}/site-audit/search
```

Input:

```json
{
  "query": "pricing plans checkout automation",
  "limit": 10
}
```

The API embeds the query with the same local embedding provider, searches the
default Qdrant content collection with a mandatory `dataset_id` filter, and
hydrates results from Postgres so every match includes chunk text, content unit,
page label, canonical URL, score, and Qdrant payload evidence.

## Chunking

Chunking strategy:

```text
site_audit_v0
```

Rules:

- paragraph units usually become one chunk
- main content can be chunked into 300-500 token chunks
- preserve page/entity reference
- include heading path in chunk metadata where possible
- skip chunks below 20 meaningful tokens unless they are titles/headings

Chunk metadata:

```json
{
  "url": "https://example.com/pricing",
  "unit_kind": "paragraph",
  "heading_path": ["Pricing", "Enterprise plans"],
  "order_index": 12
}
```

## Embedding Targets

Embed:

- paragraph chunks
- main content chunks
- generated page summary content unit
- headings

Do not embed:

- empty metadata
- navigation-only text
- footer boilerplate if detected
- repeated cookie banners

Default local model can be small. The exact model can change, but embedding
model identity must be stored.

## Technical Analysis

### Technical Issue Rules

Create insights for:

```text
page_failed
broken_internal_link
missing_title
title_too_short
title_too_long
missing_meta_description
meta_description_too_short
meta_description_too_long
missing_h1
multiple_h1
non_indexable_page
canonical_missing
canonical_mismatch
redirect_chain
thin_content
images_missing_alt
```

Initial thresholds:

```text
title_too_short: title_length < 20
title_too_long: title_length > 65
meta_description_too_short: meta_description_length < 70
meta_description_too_long: meta_description_length > 170
thin_content: word_count < 250
redirect_chain: redirect_hop_count > 1
```

### Technical Score

Start with simple penalty score:

```text
technical_score = 100 - penalties
```

Penalties:

```text
page failed: 100
non-indexable: 40
missing title: 15
missing meta description: 10
missing h1: 10
multiple h1: 5
canonical mismatch: 20
broken internal link: 10 each, max 30
thin content: 15
images missing alt: min(10, missing_alt_count * 2)
```

Clamp:

```text
0 <= technical_score <= 100
```

## Semantic Analysis

### Page Summary Text

For each page, build an analysis text:

```text
title
meta description
h1
h2 headings
main content extract
```

This becomes the page-level semantic representation.

### Similarity

Compute:

- nearest pages for each page
- nearest paragraphs for each paragraph
- duplicate candidates
- internal link opportunities

Duplicate page candidate:

```text
cosine_similarity(page_a, page_b) >= 0.92
```

Near-duplicate / cannibalization candidate:

```text
0.84 <= cosine_similarity < 0.92
```

Internal link opportunity:

```text
cosine_similarity(page_a, page_b) >= 0.72
and no existing internal link from page_a to page_b
and page_a != page_b
```

Thresholds should be configurable in analysis preset.

### Clustering

V0 clustering approach:

```text
if page_count < 20: agglomerative clustering or skip cluster labels
if page_count >= 20: HDBSCAN or k-means with heuristic k
```

Simpler first implementation:

```text
use k-means with k = sqrt(page_count / 2), min 2, max 12
```

Store:

- cluster ID
- representative pages
- centroid
- top terms
- average technical score
- average GEO score
- page count

Cluster label v0:

- use top terms from page titles/headings/content via TF-IDF
- no LLM required

### Outliers

Compute domain centroid from page embeddings.

For each page:

```text
centroid_distance = 1 - cosine_similarity(page_embedding, domain_centroid)
```

Outlier if:

```text
centroid_distance > percentile_90
and centroid_distance > 0.35
```

For small sites:

```text
mark top 3 farthest pages as candidates, but lower confidence
```

### Topical Focus Score

```text
topical_focus_score = 100 * cosine_similarity(page_embedding, cluster_centroid)
```

Clamp to 0-100.

Low focus:

```text
topical_focus_score < 65
```

## GEO Analysis

GEO v0 should be explainable, not magical.

Compute component scores:

### Answerability Score

Signals:

- page has clear H1
- page has question/answer sections
- page has descriptive headings
- page has enough body content
- page covers topic with specific nouns/entities

Simple v0 formula:

```text
answerability_score =
  20 if h1_count == 1
  + 20 if word_count >= 600
  + 20 if h2_count >= 2
  + 20 if page contains question-like headings or FAQ patterns
  + 20 if semantic_depth_score >= 70
```

### Entity Coverage Score

Approximate in v0 without full NER:

```text
entity_coverage_score =
  min(100, unique_capitalized_terms_count * 4 + schema_type_count * 10)
```

Later replace with NER/entity extraction.

### Evidence Score

Signals:

- outbound links to authoritative sources
- internal links to supporting pages
- numbers/statistics present
- schema markup present

V0:

```text
source_evidence_score =
  min(100,
    external_outlinks * 8
    + internal_outlinks * 3
    + numeric_claim_count * 5
    + schema_type_count * 10
  )
```

### Structured Data Score

```text
structured_data_coverage_score =
  100 if schema_type_count >= 2
  60 if schema_type_count == 1
  0 if schema_type_count == 0
```

### GEO Readiness Score

```text
geo_readiness_score =
  0.35 * answerability_score
  + 0.25 * entity_coverage_score
  + 0.20 * source_evidence_score
  + 0.10 * structured_data_coverage_score
  + 0.10 * topical_focus_score
```

Severity:

```text
good: >= 80
needs_work: 60-79
weak: 40-59
poor: < 40
```

## Priority Score

Use a simple priority score for ordering recommendations:

```text
priority_score =
  issue_severity_weight
  + traffic_proxy_weight
  + semantic_importance_weight
  + fix_confidence_weight
```

V0 without traffic data:

```text
priority_score =
  severity_points
  + max(0, 30 - centroid_distance_rank)
  + internal_inlinks_weight
  + confidence_points
```

If no traffic source exists, do not pretend to know business impact. Say
"priority by structural/semantic importance."

## Artifacts

Analysis should write these artifacts:

```text
site_overview
technical_issue_table
semantic_cluster_table
outlier_table
duplicate_pair_table
internal_link_opportunity_table
geo_readiness_table
projection_2d
```

Each artifact should include:

- artifact_type
- artifact_json
- source analysis_run_id
- created_at
- content_hash

Large artifacts can later move to object storage.

## Insights

V0 insight types:

```text
technical_issue
semantic_outlier
duplicate_content
internal_link_opportunity
geo_weakness
thin_content
cluster_gap
```

Every insight must include evidence:

- page entity
- metric value
- content unit or chunk
- raw object when useful
- quote when text-based

## Report

V0 report sections:

```text
summary
top_issues
technical_findings
semantic_findings
geo_readiness
page_priorities
evidence_links
recommended_next_steps
```

Report can be HTML first. PDF export can come later.

## MCP Context Pack

Site Audit context pack should include:

- dataset card
- crawl summary
- metric definitions
- top technical issues
- clusters
- outliers
- duplicates
- GEO weak pages
- representative evidence
- next resource links

## Reprocessing Rules

When raw HTML changes:

```text
invalidate content units
invalidate chunks
invalidate embeddings
invalidate affected analysis artifacts
```

When analysis thresholds change:

```text
rerun analysis only; keep crawl/extraction/embeddings
```

When embedding model changes:

```text
rerun embeddings and semantic analysis
```

## Acceptance Tests

Test with fixture website:

- detects missing title
- detects missing meta
- detects broken internal link
- detects duplicate page
- detects outlier page
- creates clusters
- creates GEO score
- creates at least 5 insights
- evidence links resolve
- report renders
