# Analysis Engine

## Purpose

The analysis engine turns vectors, metrics, and relationships into explainable
patterns.

It should be use-case agnostic. Website analysis, call analysis, company
benchmarking, and support-ticket analysis should all use the same primitives.

## Inputs

The analysis engine consumes:

- entities
- entity relations
- content units
- content chunks
- embeddings
- metric values
- filters
- cohorts
- analysis specification

## Outputs

The analysis engine produces:

- centroid metrics
- clusters
- labels
- outliers
- duplicate pairs
- similarity tables
- 2D/3D projections
- cohort differences
- success patterns
- gap tables
- drift scores
- insight candidates
- analysis artifacts

## Core Metrics

### Centroid

For a selected population:

```text
centroid = normalized mean embedding
```

Use cases:

- domain centroid
- company centroid
- successful-call centroid
- failed-call centroid
- branch centroid
- cluster centroid

### Similarity To Centroid

```text
similarity = cosine(entity_embedding, centroid)
distance = 1 - similarity
```

Use cases:

- focus
- outlier detection
- drift from parent entity
- comparison to successful cohort

### Radius

Measures spread around the centroid.

```text
radius = stddev(1 - cosine(entity_embedding, centroid))
```

Interpretation:

- low radius: focused population
- high radius: broad or fragmented population

### Pairwise Similarity Distribution

Sample pairwise similarities to understand corpus shape.

Outputs:

- mean
- p10
- p50
- p90
- sample size

This helps calibrate focus scores because modern embedding models often have a
similarity floor.

### Effective Topic Dimension

Estimate how many independent semantic directions exist in a population.

Method:

- mean-center embeddings
- compute singular values
- convert eigenvalue distribution to entropy
- return exp(entropy)

Use cases:

- detect broad vs focused corpora
- compare domains or companies
- find unfocused datasets

## Clustering

Initial algorithm:

- k-means over normalized embeddings
- configurable k
- automatic k heuristic for MVP
- cluster labels via c-TF-IDF or LLM labeler

Later algorithms:

- HDBSCAN
- Leiden over nearest-neighbor graph
- hierarchical clustering
- topic modeling alternatives

Cluster outputs:

- cluster_id
- centroid
- size
- cohesion
- top entities
- top chunks
- keywords
- label
- metric summaries
- related clusters

## Outlier Detection

Initial methods:

- distance from dataset centroid
- distance from parent centroid
- distance from nearest cluster centroid
- low nearest-neighbor similarity

Outlier types:

```text
global_outlier
parent_drift
cluster_outlier
metric_semantic_mismatch
orphan_entity
```

Examples:

- a page far from the domain centroid
- a branch semantically unlike other branches
- a successful call that looks like failed calls
- a ticket with no nearby knowledge-base article

## Duplicate And Near-Duplicate Detection

Use nearest-neighbor search within a population.

Outputs:

- entity A
- entity B
- similarity
- duplicate type
- shared phrases or evidence chunks

Applications:

- duplicate web pages
- duplicate knowledge-base articles
- repeated support issues
- repeated sales-call scripts

## Semantic Drift

Drift compares a child entity/content unit to a parent centroid.

Examples:

- paragraph vs page centroid
- page vs domain centroid
- branch vs company centroid
- support ticket vs product-area centroid
- transcript segment vs successful-call centroid

Outputs:

- drift score
- nearest better home
- explanation
- evidence

## Wrong-Home Detection

Detects content that fits another parent better than its current parent.

Examples:

- paragraph belongs on another web page
- ticket belongs to another product area
- review is attached to wrong branch/product
- document section should be moved

Method:

1. Compute child embedding.
2. Compare to current parent centroid.
3. Compare to candidate parent centroids.
4. Flag if another parent is significantly closer.

## Cohort Comparison

Cohorts are groups of entities defined by filters or metrics.

Examples:

```text
successful calls vs failed calls
top branches vs weak branches
high-converting pages vs low-converting pages
resolved tickets vs escalated tickets
```

Outputs:

- centroid distance between cohorts
- clusters enriched in cohort A
- clusters enriched in cohort B
- metric differences
- representative examples
- nearest successful analogs for weak entities
- missing topics in weak cohort

## Success Pattern Mining

Goal:

Find semantic patterns associated with positive metrics.

Approaches:

- compare top and bottom metric cohorts
- train simple interpretable classifier over cluster membership
- compute cluster enrichment
- identify phrases/topics that occur in success cohort
- find successful nearest neighbors for failed entities

Output format:

```text
Pattern:
  title
  positive cohort prevalence
  negative cohort prevalence
  metric lift
  confidence
  representative evidence
  recommendation
```

## Gap Detection

Gap detection compares actual semantic coverage to target coverage.

Target sources:

- successful cohort
- competitor dataset
- query set
- ideal profile
- user-provided taxonomy
- product requirements

Examples:

- website lacks content for important GEO queries
- weak branches lack topics common in top branches
- support knowledge base lacks articles for frequent ticket clusters
- sales calls lack proof examples used by successful calls

## Projection

Use 2D and 3D projections for human exploration.

Initial:

- UMAP for 2D
- sampled projection for large datasets

Later:

- PaCMAP
- TriMap
- incremental projections
- WebGL rendering

Important:

- projection coordinates are for visualization, not exact distance claims
- combined comparisons must use one shared projection, not separate maps

## Incremental And Streaming Analysis

For changing datasets, the engine should support more than full refreshes.

Analysis modes:

```text
incremental
windowed
full_refresh
backfill
comparison
```

Invalidation rules:

- content changed: re-chunk, re-embed, update nearest neighbors
- metric changed: recompute metric summaries and affected cohorts
- relation changed: recompute graph metrics and relation-group coherence
- new entity: assign nearest cluster and update approximate centroids
- many changes: schedule full refresh

Window examples:

- last 24 hours
- last 7 days
- last 30 days
- current campaign period
- investment cohort
- since last context pack

Streaming insights should always include freshness and window information.

## Semantic Alignment Analysis

Semantic alignment compares one class of entities to another.

Examples:

- paid keyword to landing page
- organic query to website page
- ad copy to page content
- product sales to content coverage
- new startup to invested/rejected startups
- support ticket to knowledge-base article

Outputs:

- nearest matching entities
- alignment score
- metric-weighted priority
- missing-content gaps
- representative evidence
- recommended action

Marketing example:

```text
High-cost paid keywords have weak semantic alignment with their landing pages.
Create or update pages near the paid-query centroid and link them from the
closest existing content cluster.
```

## Insight Generation

The analysis engine should generate structured insight candidates. The LLM
layer can then turn them into readable explanations.

Insight candidate fields:

- type
- title
- affected entities
- metric impact
- evidence chunks
- confidence
- recommended action
- explanation inputs

Do not ask the LLM to discover everything from raw data. Use deterministic
analysis to create strong candidates first.

## LLM Responsibilities

Good LLM tasks:

- label clusters
- summarize evidence
- explain a cohort difference
- write recommendations
- prepare reports
- normalize messy schema descriptions

Bad LLM tasks:

- compute exact nearest neighbors
- enforce security
- decide permissions
- act without evidence
- inspect huge raw datasets directly

## Reusable Analyses From Site-Audit

Ideas to generalize from the previous website project:

- page centroid -> entity centroid
- site focus -> dataset focus
- section coherence -> relation-group coherence
- page clusters -> entity clusters
- paragraph clusters -> chunk clusters
- wrong-home paragraphs -> misplaced content units
- cross-domain comparison -> cross-cohort comparison
- GEO action plan -> domain template report
- combined UMAP -> shared semantic map
