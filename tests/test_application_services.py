from uuid import uuid4

import pytest
from meaninggrid_application import ApplicationError, DatasetApplicationService
from meaninggrid_application.services import CreateDatasetCommand
from meaninggrid_db.database import session_scope
from meaninggrid_db.models import Job, Workspace
from meaninggrid_db.seed import ensure_local_seed
from sqlalchemy import select


def test_dataset_application_service_creates_dataset_and_event_job() -> None:
    with session_scope() as session:
        ensure_local_seed(session)
        workspace = session.scalar(select(Workspace).where(Workspace.slug == "default"))
        assert workspace is not None

        service = DatasetApplicationService(session)
        dataset = service.create_dataset(
            CreateDatasetCommand(
                workspace_id=workspace.id,
                name=f"DDD Service Dataset {uuid4().hex[:8]}",
                dataset_kind="site_audit",
                description="Created through the application layer.",
                labels={"module": "site_audit", "source": "application-test"},
                classification={"visibility": "internal", "sensitivity": "low"},
            )
        )

        assert dataset.workspace_id == workspace.id
        assert dataset.slug.startswith("ddd-service-dataset")
        assert dataset.labels_json["source"] == "application-test"
        assert dataset.classification_json["visibility"] == "internal"

        created_job = session.scalar(
            select(Job).where(
                Job.dataset_id == dataset.id,
                Job.job_type == "dataset_created",
            )
        )
        assert created_job is not None
        assert created_job.status == "finished"


def test_dataset_application_service_raises_application_error_for_missing_dataset() -> None:
    with session_scope() as session:
        service = DatasetApplicationService(session)

        with pytest.raises(ApplicationError) as error:
            service.get_dataset(uuid4())

    assert error.value.status_code == 404
    assert error.value.code == "dataset_not_found"
