# Site Audit Testing Readiness

## Purpose

This document describes how to test the first MeaningGrid module locally.

The Site Audit module is ready for tester feedback when a fresh checkout can:

- start the full Docker stack
- create a Site Audit dataset
- crawl the bundled fixture website
- extract pages, content units, metrics, and links
- embed content chunks into Qdrant
- search crawled content semantically
- compute semantic page clusters
- compute similar page pairs and outliers
- expose dataset context through MCP
- render the dashboard workflow

## Quick Verification

From the repository root:

```bash
cp .env.example .env
make ready
```

`make ready` runs:

- backend lint
- web typecheck
- backend integration tests
- Site Audit smoke test

The smoke test creates a fresh fixture dataset and verifies the full module path:

```text
dataset -> crawl -> extract -> embed -> Qdrant search -> clusters -> semantic map -> MCP search
```

Expected final line:

```text
MeaningGrid Site Audit smoke test passed
```

## Manual UI Test

Start the stack:

```bash
docker compose up --build
```

Open:

```text
http://localhost:3000
```

Test flow:

1. Confirm the status panel shows `Ready`.
2. Create a Site Audit dataset.
3. Use the bundled fixture URL if testing deterministic local behavior:

```text
file:///app/examples/site-audit/fixture-site/index.html
```

4. Run the crawl with `max_pages=5`.
5. Confirm the dashboard shows:
   - 5 pages
   - technical score
   - entities
   - content units
   - page table
   - semantic search results
   - similar pages
   - outliers

For a real external website, use an HTTP or HTTPS URL. The first implementation
does not render JavaScript and is intentionally conservative.

## API Smoke Flow

The core endpoints used by the UI are:

```text
GET  /workspaces
POST /workspaces/{workspace_id}/datasets
POST /datasets/{dataset_id}/site-audit/crawls
POST /jobs/{job_id}/run-now
GET  /datasets/{dataset_id}/site-audit/overview
GET  /datasets/{dataset_id}/site-audit/pages
POST /datasets/{dataset_id}/site-audit/search
GET  /datasets/{dataset_id}/site-audit/clusters
GET  /datasets/{dataset_id}/site-audit/semantic-map
```

## MCP Smoke Flow

The first headless agent surface is HTTP-shaped and intentionally thin:

```text
GET  /mcp/resources
GET  /mcp/resource/dataset/{dataset_id}/card
GET  /mcp/resource/dataset/{dataset_id}/site-audit/overview
GET  /mcp/resource/dataset/{dataset_id}/site-audit/clusters
POST /mcp/tools/site-audit/semantic-search
```

The MCP semantic search tool returns evidence chunks with page labels,
canonical URLs, scores, and payload metadata.

## Known V0 Limits

- Local embeddings are deterministic hash vectors, not a transformer model.
- JavaScript rendering is not enabled yet.
- Robots handling is represented in request shape but not a full crawler policy.
- Semantic clusters are computed on request and are not persisted as first-class
  artifacts yet.
- Similar pages and outliers are computed on request from content chunk vectors.
- Authentication is local-only.

These limits are acceptable for first tester feedback because the full module
loop is present and deterministic.
