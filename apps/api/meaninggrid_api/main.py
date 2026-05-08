from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from meaninggrid_core.config import get_settings
from meaninggrid_core.health import build_health_status

settings = get_settings()

app = FastAPI(
    title="MeaningGrid API",
    description="Semantic intelligence and context management API.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        settings.public_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return build_health_status()


@app.get("/version", tags=["system"])
def version() -> dict[str, str | None]:
    return {
        "version": "0.1.0",
        "commit": None,
        "build_time": None,
    }


@app.get("/workspaces", tags=["workspaces"])
def list_workspaces() -> dict[str, list[dict[str, str]]]:
    return {
        "workspaces": [
            {
                "id": "local-workspace",
                "name": "Default Workspace",
                "slug": "default",
            }
        ]
    }


@app.get("/modules", tags=["modules"])
def list_modules() -> dict[str, list[dict[str, str | bool]]]:
    return {
        "modules": [
            {
                "module_key": "site_audit",
                "name": "Site Audit And GEO Intelligence",
                "current_version": "0.1.0",
                "bundled": True,
                "status": "active",
            }
        ]
    }
