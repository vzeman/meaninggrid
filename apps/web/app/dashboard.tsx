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

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const mcpUrl = process.env.NEXT_PUBLIC_MCP_URL ?? "http://localhost:8010";

export function Dashboard() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [modules, setModules] = useState<Module[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [datasetName, setDatasetName] = useState("Example Site Audit");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const workspace = workspaces[0];
  const status = useMemo(() => (error ? "Needs attention" : loading ? "Loading" : "Ready"), [
    error,
    loading
  ]);

  async function loadData() {
    setError(null);
    setLoading(true);
    try {
      const workspaceResponse = await fetch(`${apiUrl}/workspaces`, { cache: "no-store" });
      const moduleResponse = await fetch(`${apiUrl}/modules`, { cache: "no-store" });
      if (!workspaceResponse.ok || !moduleResponse.ok) {
        throw new Error("API returned an error");
      }
      const workspaceData = await workspaceResponse.json();
      const moduleData = await moduleResponse.json();
      const nextWorkspaces: Workspace[] = workspaceData.workspaces ?? [];
      setWorkspaces(nextWorkspaces);
      setModules(moduleData.modules ?? []);

      if (nextWorkspaces[0]) {
        const datasetResponse = await fetch(
          `${apiUrl}/workspaces/${nextWorkspaces[0].id}/datasets`,
          { cache: "no-store" }
        );
        if (!datasetResponse.ok) {
          throw new Error("Dataset API returned an error");
        }
        const datasetData = await datasetResponse.json();
        setDatasets(datasetData.datasets ?? []);
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not load MeaningGrid API");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function createDataset(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!workspace || !datasetName.trim()) {
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/workspaces/${workspace.id}/datasets`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: datasetName.trim(),
          dataset_kind: "site_audit",
          labels: { module: "site_audit" }
        })
      });
      if (!response.ok) {
        throw new Error("Dataset creation failed");
      }
      setDatasetName("");
      await loadData();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Dataset creation failed");
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="shell">
      <section className="masthead">
        <div>
          <p className="eyebrow">MeaningGrid v0.1</p>
          <h1>Local Site Audit workspace</h1>
          <p className="lede">
            Create a dataset, enqueue crawl and analysis jobs through the API,
            and expose the same core records to MCP.
          </p>
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
        <button type="button" onClick={() => void loadData()} disabled={loading}>
          Refresh
        </button>
      </section>

      <section className="grid">
        <form className="panel formPanel" onSubmit={createDataset}>
          <h2>New Site Audit</h2>
          <label htmlFor="datasetName">Dataset name</label>
          <div className="inlineForm">
            <input
              id="datasetName"
              value={datasetName}
              onChange={(event) => setDatasetName(event.target.value)}
              placeholder="example.com audit"
            />
            <button type="submit" disabled={!workspace || saving}>
              {saving ? "Creating" : "Create"}
            </button>
          </div>
        </form>

        <div className="panel">
          <h2>Bundled Modules</h2>
          <div className="moduleList">
            {modules.map((module) => (
              <div key={module.module_key} className="moduleRow">
                <span>{module.name}</span>
                <strong>{module.current_version}</strong>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="tablePanel">
        <div className="tableHeader">
          <h2>Datasets</h2>
          <span>{datasets.length}</span>
        </div>
        {datasets.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Kind</th>
                <th>Status</th>
                <th>Entities</th>
                <th>Content units</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((dataset) => (
                <tr key={dataset.id}>
                  <td>{dataset.name}</td>
                  <td>{dataset.dataset_kind}</td>
                  <td>{dataset.status}</td>
                  <td>{dataset.entity_count}</td>
                  <td>{dataset.content_unit_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="emptyState">No datasets yet.</div>
        )}
      </section>
    </main>
  );
}
