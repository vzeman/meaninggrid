from dataclasses import asdict, dataclass

from meaninggrid_core.config import get_settings


@dataclass(frozen=True)
class HealthStatus:
    status: str
    version: str
    environment: str
    auth_mode: str
    vector_backend: str
    object_store_backend: str
    queue_backend: str


def build_health_status() -> dict[str, str]:
    settings = get_settings()
    return asdict(
        HealthStatus(
            status="ok",
            version="0.1.0",
            environment=settings.environment,
            auth_mode=settings.auth_mode,
            vector_backend=settings.vector_backend,
            object_store_backend=settings.object_store_backend,
            queue_backend=settings.queue_backend,
        )
    )
