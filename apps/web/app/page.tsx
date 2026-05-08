const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const mcpUrl = process.env.NEXT_PUBLIC_MCP_URL ?? "http://localhost:8010";

const firstSteps = [
  "Create a Site Audit dataset",
  "Crawl a fixture or real website",
  "Extract pages, paragraphs, headings, and links",
  "Embed chunks and run Site Audit v0 analysis",
  "Inspect issues, clusters, outliers, duplicates, GEO readiness, and evidence"
];

export default function Home() {
  return (
    <main className="shell">
      <section className="masthead">
        <div>
          <p className="eyebrow">MeaningGrid v0.1 scaffold</p>
          <h1>Local Site Audit workspace</h1>
          <p className="lede">
            The first build turns a crawled website into entities, content,
            metrics, embeddings, analysis artifacts, insights, and MCP-ready
            context.
          </p>
        </div>
        <div className="statusPanel">
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

      <section className="grid">
        <div className="panel">
          <h2>First workflow</h2>
          <ol>
            {firstSteps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </div>
        <div className="panel">
          <h2>Bundled module</h2>
          <dl>
            <div>
              <dt>Key</dt>
              <dd>site_audit</dd>
            </div>
            <div>
              <dt>Focus</dt>
              <dd>Technical SEO, semantic quality, GEO readiness</dd>
            </div>
            <div>
              <dt>Runtime</dt>
              <dd>Docker, FastAPI, Celery, Next.js, Postgres, Redis, MinIO, Qdrant</dd>
            </div>
          </dl>
        </div>
      </section>
    </main>
  );
}
