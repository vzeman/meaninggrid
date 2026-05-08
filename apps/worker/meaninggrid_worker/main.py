from celery import Celery
from meaninggrid_analysis.site_audit import run_crawl_job
from meaninggrid_core.config import get_settings
from meaninggrid_db.database import session_scope

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


@celery_app.task(name="meaninggrid.site_audit.run_crawl_job")
def run_site_audit_crawl_job(job_id: str) -> dict[str, int]:
    with session_scope() as session:
        return run_crawl_job(session, job_id)
