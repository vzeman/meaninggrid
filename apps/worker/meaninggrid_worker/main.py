from celery import Celery
from meaninggrid_core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "meaninggrid",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)


@celery_app.task(name="meaninggrid.ping")
def ping() -> dict[str, str]:
    return {"status": "ok"}
