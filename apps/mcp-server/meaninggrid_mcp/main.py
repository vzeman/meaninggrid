from fastapi import FastAPI
from meaninggrid_core.health import build_health_status

app = FastAPI(
    title="MeaningGrid MCP Server",
    description="Placeholder HTTP surface for the v0 MCP server process.",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return build_health_status()


@app.get("/mcp/resources", tags=["mcp"])
def list_placeholder_resources() -> dict[str, list[str]]:
    return {
        "resources": [
            "meaninggrid://workspaces",
            "meaninggrid://dataset/{dataset_id}/card",
            "meaninggrid://context-pack/{context_pack_id}",
        ]
    }
