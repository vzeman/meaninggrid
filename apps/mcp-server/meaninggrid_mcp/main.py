from contextlib import asynccontextmanager
from typing import Any
from uuid import UUID

from fastapi import FastAPI
from meaninggrid_application import DatasetApplicationService, SiteAuditApplicationService
from meaninggrid_core.health import build_health_status
from meaninggrid_db.database import session_scope
from meaninggrid_db.models import Workspace
from meaninggrid_db.seed import ensure_local_seed
from pydantic import BaseModel, Field
from sqlalchemy import select


class SiteAuditSemanticSearchRequest(BaseModel):
    dataset_id: UUID
    query: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=8, ge=1, le=50)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    with session_scope() as session:
        ensure_local_seed(session)
    yield


app = FastAPI(
    title="MeaningGrid MCP Server",
    description="Headless context and tool surface for MeaningGrid agents.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return build_health_status()


@app.get("/mcp/resources", tags=["mcp"])
def list_resources() -> dict[str, list[dict[str, Any]]]:
    with session_scope() as session:
        resources = [
            {
                "uri": "meaninggrid://workspaces",
                "name": "Workspace index",
                "description": "Available MeaningGrid workspaces.",
            }
        ]
        workspace_rows = session.scalars(select(Workspace).order_by(Workspace.created_at.asc()))
        for workspace in workspace_rows:
            resources.append(
                {
                    "uri": f"meaninggrid://workspace/{workspace.id}/overview",
                    "name": f"Workspace: {workspace.name}",
                    "description": "Workspace overview and available datasets.",
                }
            )
            for dataset in DatasetApplicationService(session).list_workspace_datasets(workspace.id):
                resources.append(
                    {
                        "uri": f"meaninggrid://dataset/{dataset.id}/card",
                        "name": dataset.name,
                        "description": (
                            f"{dataset.dataset_kind} dataset with "
                            f"{dataset.entity_count} entities."
                        ),
                    }
                )
                if dataset.dataset_kind == "site_audit":
                    resources.extend(
                        [
                            {
                                "uri": f"meaninggrid://dataset/{dataset.id}/site-audit/overview",
                                "name": f"{dataset.name} overview",
                                "description": "Site Audit metrics and issue summary.",
                            },
                            {
                                "uri": f"meaninggrid://dataset/{dataset.id}/site-audit/pages",
                                "name": f"{dataset.name} pages",
                                "description": "Crawled page rows with metrics.",
                            },
                            {
                                "uri": f"meaninggrid://dataset/{dataset.id}/site-audit/clusters",
                                "name": f"{dataset.name} clusters",
                                "description": "Semantic page clusters and members.",
                            },
                            {
                                "uri": f"meaninggrid://dataset/{dataset.id}/site-audit/duplicates",
                                "name": f"{dataset.name} duplicates",
                                "description": "Duplicate and near-duplicate page pairs.",
                            },
                        ]
                    )
    return {"resources": resources}


@app.get("/mcp/resource/dataset/{dataset_id}/card", tags=["mcp"])
def get_dataset_card(dataset_id: UUID) -> dict[str, Any]:
    with session_scope() as session:
        card = DatasetApplicationService(session).build_dataset_card(dataset_id)
        dataset = card["dataset"]
        return {
            "id": str(dataset.id),
            "name": dataset.name,
            "dataset_kind": dataset.dataset_kind,
            "summary": card["summary"],
            "entity_types": card["entity_types"],
            "metrics": card["metrics"],
            "freshness_at": dataset.freshness_at.isoformat() if dataset.freshness_at else None,
            "next_resources": card["next_resources"],
        }


@app.get("/mcp/resource/dataset/{dataset_id}/site-audit/overview", tags=["mcp"])
def get_site_audit_overview(dataset_id: UUID) -> dict[str, Any]:
    with session_scope() as session:
        return SiteAuditApplicationService(session).overview(dataset_id)


@app.get("/mcp/resource/dataset/{dataset_id}/site-audit/clusters", tags=["mcp"])
def get_site_audit_clusters(dataset_id: UUID) -> dict[str, Any]:
    with session_scope() as session:
        clusters = SiteAuditApplicationService(session).clusters(dataset_id)
        return {
            **clusters,
            "clusters": [
                {
                    **cluster,
                    "members": [
                        {
                            **member,
                            "entity_id": str(member["entity_id"]),
                        }
                        for member in cluster["members"]
                    ],
                }
                for cluster in clusters["clusters"]
            ],
        }


@app.get("/mcp/resource/dataset/{dataset_id}/site-audit/duplicates", tags=["mcp"])
def get_site_audit_duplicates(dataset_id: UUID) -> dict[str, Any]:
    with session_scope() as session:
        duplicates = SiteAuditApplicationService(session).duplicates(dataset_id)
        return {
            **duplicates,
            "duplicates": [
                {
                    **duplicate,
                    "source_entity_id": str(duplicate["source_entity_id"]),
                    "target_entity_id": str(duplicate["target_entity_id"]),
                }
                for duplicate in duplicates["duplicates"]
            ],
        }


@app.post("/mcp/tools/site-audit/semantic-search", tags=["mcp"])
def site_audit_semantic_search(payload: SiteAuditSemanticSearchRequest) -> dict[str, Any]:
    with session_scope() as session:
        results = SiteAuditApplicationService(session).semantic_search(
            dataset_id=payload.dataset_id,
            query=payload.query,
            limit=payload.limit,
        )
        return {
            "results": [
                {
                    **result,
                    "content_chunk_id": str(result["content_chunk_id"]),
                    "content_unit_id": str(result["content_unit_id"]),
                    "entity_id": str(result["entity_id"]) if result["entity_id"] else None,
                }
                for result in results
            ]
        }
