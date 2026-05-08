# UI Information Architecture V0

## Purpose

This document defines the first web UI shape for MeaningGrid v0.1.

The UI should make the local Site Audit workflow usable without requiring the
CLI or MCP. It should feel like a real analysis tool, not a landing page.

## UI Principles

- Start with the working product, not marketing.
- Keep navigation predictable.
- Make job progress visible.
- Let users move from overview to evidence quickly.
- Show source evidence for findings.
- Keep dashboards dense but readable.
- Avoid building generic module UI too early.

## Top-Level Navigation

```text
Workspaces
Datasets
Site Audit
Reports
MCP
Settings
```

For v0 local mode, workspace switching can be simple because seed creates one
default workspace.

## Routes

```text
/
/datasets
/datasets/new/site-audit
/datasets/{dataset_id}
/datasets/{dataset_id}/crawl
/datasets/{dataset_id}/overview
/datasets/{dataset_id}/pages
/datasets/{dataset_id}/pages/{entity_id}
/datasets/{dataset_id}/issues
/datasets/{dataset_id}/clusters
/datasets/{dataset_id}/outliers
/datasets/{dataset_id}/duplicates
/datasets/{dataset_id}/internal-links
/datasets/{dataset_id}/geo
/datasets/{dataset_id}/insights
/datasets/{dataset_id}/reports
/datasets/{dataset_id}/mcp
/jobs/{job_id}
/settings
```

## First Screen

If no dataset exists:

```text
New Site Audit wizard
```

If datasets exist:

```text
Dataset list with primary action: New Site Audit
```

Do not make a marketing homepage inside the app.

## New Site Audit Wizard

Fields:

- dataset name
- website URL
- max pages
- respect robots toggle
- render JavaScript toggle disabled/advanced
- include patterns advanced
- exclude patterns advanced

Primary action:

```text
Start crawl
```

After submit:

```text
navigate to crawl/job status
```

## Crawl Status Screen

Shows:

- current job phase
- progress bar
- pages discovered
- pages fetched
- pages failed
- current URL
- warnings
- errors
- next expected phase

Actions:

- cancel job
- view partial pages if available
- retry failed job

## Dataset Overview

Cards/sections:

- pages crawled
- indexable pages
- technical issue count
- average technical score
- average GEO readiness
- semantic clusters
- outlier pages
- duplicate pairs
- internal link opportunities

Tables:

- top issues
- highest priority pages
- weakest GEO pages

Charts:

- issue type distribution
- GEO readiness distribution
- semantic projection preview

## Pages Table

Columns:

- URL/title
- status code
- indexable
- word count
- technical score
- GEO score
- cluster
- centroid distance
- duplicate risk
- internal inlinks
- issues count

Filters:

- status code
- issue type
- cluster
- indexable
- GEO score range
- duplicate risk
- outlier only

Actions:

- open page detail
- open raw source metadata
- find similar pages

## Page Detail

Sections:

- page header with URL, title, status, canonical
- score summary
- technical metrics
- GEO score breakdown
- semantic nearest neighbors
- duplicate/cannibalization candidates
- internal links in/out
- suggested internal links
- extracted headings
- paragraphs/evidence
- related insights

Important behavior:

Users should be able to click an insight and see the exact paragraph, metric,
or link that supports it.

## Technical Issues

Table grouped by issue type.

Columns:

- severity
- issue type
- page
- explanation
- evidence
- recommendation

Filters:

- severity
- issue type
- page cluster
- indexable only

## Semantic Clusters

Shows:

- cluster label
- page count
- average technical score
- average GEO score
- representative pages
- top terms
- internal link density

Cluster detail:

- pages in cluster
- nearest neighboring clusters
- outliers inside cluster
- suggested improvements

## Outliers

Shows pages far from their cluster or domain centroid.

Columns:

- page
- centroid distance
- nearest cluster
- possible reason
- evidence
- recommendation

Possible reasons v0:

- off-topic content
- thin content
- wrong language
- duplicate but misplaced
- boilerplate/noise extraction

## Duplicates

Shows:

- page A
- page B
- similarity score
- shared headings/paragraphs
- canonical status
- recommendation

Recommendations:

- merge
- canonicalize
- differentiate
- no action

## Internal Link Opportunities

Shows:

- source page
- target page
- semantic similarity
- existing link status
- suggested anchor topic
- priority

V0 does not need to edit the site. It only recommends.

## GEO Readiness

Shows:

- GEO score by page
- answerability score
- entity coverage score
- source evidence score
- structured data score
- topical focus score

Page-level recommendations:

- add clear definitions
- add FAQ/question sections
- add evidence or sources
- add schema markup
- clarify product/company/entity facts
- improve topic focus

## Insights

Insight list:

- title
- severity
- confidence
- insight type
- affected pages
- recommendation

Insight detail:

- summary
- why it matters
- evidence
- affected entities
- metrics
- recommended action

## Reports

V0 reports:

- Site Audit Summary
- GEO Readiness Report
- Internal Link Plan
- Content Brief

Actions:

- generate report
- view HTML report
- export later

PDF can wait.

## MCP Setup

Shows:

- local MCP server URL/command
- available resources
- available tools
- example questions

Example questions:

```text
What are the biggest GEO weaknesses?
Which pages are outliers?
Which duplicate pages should we merge?
Which internal links should we add?
Build a content brief for the biggest topic gap.
```

## Loading And Empty States

Empty dataset:

```text
Start a crawl to create the first Site Audit.
```

No analysis yet:

```text
Run analysis after crawl completes.
```

No duplicates:

```text
No duplicate pages were detected with the current threshold.
```

No outliers:

```text
No strong outliers were detected. Try lowering the threshold or crawling more pages.
```

## Error States

Show clear messages for:

- API unavailable
- crawl failed
- no pages fetched
- embedding provider failed
- analysis failed
- vector store unavailable

Each error should offer a next action:

- retry
- view job events
- adjust crawl settings
- open logs link later

## Components V0

Reusable components:

- AppShell
- DatasetSwitcher
- JobProgress
- MetricCard
- ScoreBadge
- SeverityBadge
- EntityLink
- EvidenceSnippet
- DataTable
- FilterBar
- InsightList
- InsightDetail
- SemanticMap2D
- PageScoreBreakdown
- ReportViewer

## Design Constraints

- Tables should handle 1k pages comfortably.
- Semantic map can sample points if needed.
- Text should not overflow table cells/cards.
- Use compact dashboard typography, not landing-page hero typography.
- Prefer direct data views over decorative cards.
- Every recommendation should have evidence access.

## Acceptance Tests

Playwright smoke test:

1. Open app.
2. Create Site Audit dataset.
3. Start fixture crawl.
4. Wait for job succeeded or use seeded fixture.
5. Open overview.
6. Open pages table.
7. Open page detail.
8. Open insights/evidence.
9. Open GEO readiness.
10. Open MCP setup.

## Deferred UI

Do not build in v0:

- custom dashboard builder
- module marketplace UI
- advanced auth screens
- billing
- multi-tenant admin
- drag-and-drop report builder
- real-time streaming notification center
- custom schema designer
