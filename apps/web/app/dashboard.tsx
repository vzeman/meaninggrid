"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type Workspace = {
  id: string;
  name: string;
  slug: string;
};

type Module = {
  module_key: string;
  name: string;
  current_version: string;
  bundled: boolean;
  status: string;
};

type Dataset = {
  id: string;
  name: string;
  dataset_kind: string;
  status: string;
  freshness_at: string | null;
  entity_count: number;
  content_unit_count: number;
};

type Overview = {
  pages_crawled: number;
  technical_score_avg: number | null;
  geo_readiness_avg: number | null;
  open_insights: number;
  top_issue_types: Array<{ type: string; count: number }>;
};

type PageRow = {
  entity_id: string;
  label: string;
  canonical_uri: string | null;
  title: string | null;
  status_code: number | null;
  word_count: number | null;
  technical_score: number | null;
};

type SearchResult = {
  content_chunk_id: string;
  score: number;
  text: string;
  unit_kind: string | null;
  page_label: string | null;
  canonical_uri: string | null;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const mcpUrl = process.env.NEXT_PUBLIC_MCP_URL ?? "http://localhost:8010";

export function Dashboard() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [modules, setModules] = useState<Module[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>("");
  const [datasetName, setDatasetName] = useState("Example Site Audit");
  const [crawlUrl, setCrawlUrl] = useState("https://example.com");
  const [maxPages, setMaxPages] = useState(20);
  const [overview, setOverview] = useState<Overview | null>(null);
  const [pages, setPages] = useState<PageRow[]>([]);
  const [query, setQuery] = useState("pricing plans checkout automation");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const workspace = workspaces[0];
  const selectedDataset = datasets.find((dataset) => dataset.id === selectedDatasetId) ?? null;
  const siteAuditModule = modules.find((module) => module.module_key === "site_audit");
  const status = useMemo(() => (error ? "Needs attention" : loading ? "Loading" : "Ready"), [
    error,
    loading
  ]);

  async function request<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${apiUrl}${path}`, {
      cache: "no-store",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers ?? {})
      }
    });
    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }
    return (await response.json()) as T;
  }

  async function loadData(preferredDatasetId?: string) {
    setError(null);
    setLoading(true);
    try {
      const [workspaceData, moduleData] = await Promise.all([
        request<{ workspaces: Workspace[] }>("/workspaces"),
        request<{ modules: Module[] }>("/modules")
      ]);
      const nextWorkspaces = workspaceData.workspaces ?? [];
      setWorkspaces(nextWorkspaces);
      setModules(moduleData.modules ?? []);

      if (nextWorkspaces[0]) {
        const datasetData = await request<{ datasets: Dataset[] }>(
          `/workspaces/${nextWorkspaces[0].id}/datasets?kind=site_audit`
        );
        const nextDatasets = datasetData.datasets ?? [];
        setDatasets(nextDatasets);
        const readyDataset = nextDatasets.find((dataset) => dataset.content_unit_count > 0);
        const nextSelectedId =
          preferredDatasetId || selectedDatasetId || readyDataset?.id || nextDatasets[0]?.id || "";
        setSelectedDatasetId(nextSelectedId);
        await loadDatasetDetails(nextSelectedId);
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not load MeaningGrid API");
    } finally {
      setLoading(false);
    }
  }

  async function loadDatasetDetails(datasetId: string) {
    if (!datasetId) {
      setOverview(null);
      setPages([]);
      setSearchResults([]);
      return;
    }
    const [overviewData, pageData] = await Promise.all([
      request<Overview>(`/datasets/${datasetId}/site-audit/overview`),
      request<{ pages: PageRow[] }>(`/datasets/${datasetId}/site-audit/pages`)
    ]);
    setOverview(overviewData);
    setPages(pageData.pages ?? []);
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function createDataset(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!workspace || !datasetName.trim()) {
      return;
    }
    setWorking(true);
    setError(null);
    try {
      const dataset = await request<Dataset>(`/workspaces/${workspace.id}/datasets`, {
        method: "POST",
        body: JSON.stringify({
          name: datasetName.trim(),
          dataset_kind: "site_audit",
          labels: { module: "site_audit", source: "web" },
          classification: { visibility: "internal", sensitivity: "standard" }
        })
      });
      setDatasetName("");
      await loadData(dataset.id);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Dataset creation failed");
    } finally {
      setWorking(false);
    }
  }

  async function runCrawl(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedDataset || !crawlUrl.trim()) {
      return;
    }
    setWorking(true);
    setError(null);
    try {
      const queued = await request<{ job_id: string }>(
        `/datasets/${selectedDataset.id}/site-audit/crawls`,
        {
          method: "POST",
          body: JSON.stringify({
            base_url: crawlUrl.trim(),
            max_pages: maxPages,
            respect_robots: true,
            render_javascript: false
          })
        }
      );
      setActiveJobId(queued.job_id);
      await request(`/jobs/${queued.job_id}/run-now`, { method: "POST" });
      await loadData(selectedDataset.id);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Crawl failed");
    } finally {
      setWorking(false);
    }
  }

  async function search(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedDataset || !query.trim()) {
      return;
    }
    setWorking(true);
    setError(null);
    try {
      const response = await request<{ results: SearchResult[] }>(
        `/datasets/${selectedDataset.id}/site-audit/search`,
        {
          method: "POST",
          body: JSON.stringify({ query: query.trim(), limit: 8 })
        }
      );
      setSearchResults(response.results ?? []);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Semantic search failed");
    } finally {
      setWorking(false);
    }
  }

  return (
    <main className="shell">
      <section className="masthead">
        <div>
          <p className="eyebrow">MeaningGrid v0.1</p>
          <h1>Site Audit workspace</h1>
        </div>
        <div className="statusPanel" aria-label="Runtime status">
          <div>
            <span>Status</span>
            <strong>{status}</strong>
          </div>
          <div>
            <span>API</span>
            <strong>{apiUrl}</strong>
          </div>
          <div>
            <span>MCP</span>
            <strong>{mcpUrl}</strong>
          </div>
        </div>
      </section>

      {error ? <div className="notice">{error}</div> : null}

      <section className="toolbar">
        <div>
          <span>Workspace</span>
          <strong>{workspace ? workspace.name : "Waiting for seed"}</strong>
        </div>
        <div>
          <span>Module</span>
          <strong>{siteAuditModule ? siteAuditModule.name : "Site Audit"}</strong>
        </div>
        <button type="button" onClick={() => void loadData(selectedDatasetId)} disabled={loading}>
          Refresh
        </button>
      </section>

      <section className="grid">
        <form className="panel formPanel" onSubmit={createDataset}>
          <h2>Dataset</h2>
          <label htmlFor="datasetName">Name</label>
          <div className="inlineForm">
            <input
              id="datasetName"
              value={datasetName}
              onChange={(event) => setDatasetName(event.target.value)}
              placeholder="example.com audit"
            />
            <button type="submit" disabled={!workspace || working}>
              Create
            </button>
          </div>
          <label htmlFor="datasetSelect">Active dataset</label>
          <select
            id="datasetSelect"
            value={selectedDatasetId}
            onChange={(event) => {
              setSelectedDatasetId(event.target.value);
              void loadDatasetDetails(event.target.value);
            }}
          >
            {datasets.map((dataset) => (
              <option key={dataset.id} value={dataset.id}>
                {dataset.name}
              </option>
            ))}
          </select>
        </form>

        <form className="panel formPanel" onSubmit={runCrawl}>
          <h2>Crawl</h2>
          <label htmlFor="crawlUrl">URL</label>
          <input
            id="crawlUrl"
            value={crawlUrl}
            onChange={(event) => setCrawlUrl(event.target.value)}
            placeholder="https://example.com"
          />
          <label htmlFor="maxPages">Max pages</label>
          <div className="inlineForm compact">
            <input
              id="maxPages"
              type="number"
              min={1}
              max={10000}
              value={maxPages}
              onChange={(event) => setMaxPages(Number(event.target.value))}
            />
            <button type="submit" disabled={!selectedDataset || working}>
              Run
            </button>
          </div>
          {activeJobId ? <p className="smallText">Last job {activeJobId}</p> : null}
        </form>
      </section>

      <section className="metricGrid">
        <Metric label="Pages" value={overview?.pages_crawled ?? 0} />
        <Metric label="Technical score" value={formatScore(overview?.technical_score_avg)} />
        <Metric label="Entities" value={selectedDataset?.entity_count ?? 0} />
        <Metric label="Content units" value={selectedDataset?.content_unit_count ?? 0} />
      </section>

      <section className="grid">
        <section className="tablePanel">
          <div className="tableHeader">
            <h2>Pages</h2>
            <span>{pages.length}</span>
          </div>
          {pages.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>Page</th>
                  <th>Status</th>
                  <th>Words</th>
                  <th>Score</th>
                </tr>
              </thead>
              <tbody>
                {pages.map((page) => (
                  <tr key={page.entity_id}>
                    <td>
                      <strong>{page.title || page.label}</strong>
                      <small>{page.canonical_uri}</small>
                    </td>
                    <td>{page.status_code ?? "n/a"}</td>
                    <td>{page.word_count ?? "n/a"}</td>
                    <td>{formatScore(page.technical_score)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="emptyState">No crawled pages.</div>
          )}
        </section>

        <section className="panel searchPanel">
          <h2>Semantic Search</h2>
          <form className="searchForm" onSubmit={search}>
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Find content about pricing, setup, integrations..."
            />
            <button type="submit" disabled={!selectedDataset || working}>
              Search
            </button>
          </form>
          <div className="resultList">
            {searchResults.map((result) => (
              <article key={result.content_chunk_id} className="resultRow">
                <div>
                  <strong>{result.page_label ?? "Content chunk"}</strong>
                  <span>{formatScore(result.score)}</span>
                </div>
                <p>{result.text}</p>
                <small>{result.canonical_uri}</small>
              </article>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function formatScore(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "n/a";
  }
  return Math.round(value * 10) / 10;
}
