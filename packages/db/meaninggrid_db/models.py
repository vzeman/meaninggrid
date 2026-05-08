from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from meaninggrid_db.database import Base


def uuid_pk() -> Column:
    return Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))


def uuid_fk(table_name: str, nullable: bool = False) -> Column:
    return Column(
        UUID(as_uuid=True),
        ForeignKey(f"{table_name}.id", ondelete="CASCADE"),
        nullable=nullable,
    )


def json_object() -> Column:
    return Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))


def json_array() -> Column:
    return Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True))


class Tenant(TimestampMixin, Base):
    __tablename__ = "tenants"

    id = uuid_pk()
    name = Column(Text, nullable=False)
    slug = Column(Text, nullable=False, unique=True)
    plan = Column(Text, nullable=False, server_default="local")


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),)

    id = uuid_pk()
    tenant_id = uuid_fk("tenants")
    email = Column(Text, nullable=False)
    display_name = Column(Text)
    role = Column(Text, nullable=False, server_default="admin")
    password_hash = Column(Text)
    is_local_admin = Column(Boolean, nullable=False, server_default=text("false"))


class Workspace(TimestampMixin, Base):
    __tablename__ = "workspaces"
    __table_args__ = (UniqueConstraint("tenant_id", "slug", name="uq_workspaces_tenant_slug"),)

    id = uuid_pk()
    tenant_id = uuid_fk("tenants")
    name = Column(Text, nullable=False)
    slug = Column(Text, nullable=False)
    description = Column(Text)
    default_language = Column(Text)
    labels_json = json_object()
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_members_pair"),
    )

    id = uuid_pk()
    tenant_id = uuid_fk("tenants")
    workspace_id = uuid_fk("workspaces")
    user_id = uuid_fk("users")
    role = Column(Text, nullable=False, server_default="owner")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Module(TimestampMixin, Base):
    __tablename__ = "modules"

    id = uuid_pk()
    module_key = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    current_version = Column(Text, nullable=False)
    bundled = Column(Boolean, nullable=False, server_default=text("false"))
    status = Column(Text, nullable=False, server_default="active")


class ModuleInstallation(Base):
    __tablename__ = "module_installations"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "workspace_id",
            "module_id",
            name="uq_module_installations_scope",
        ),
    )

    id = uuid_pk()
    tenant_id = uuid_fk("tenants")
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"))
    module_id = uuid_fk("modules")
    module_version = Column(Text, nullable=False)
    enabled = Column(Boolean, nullable=False, server_default=text("true"))
    config_json = json_object()
    installed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    installed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class ModuleResource(Base):
    __tablename__ = "module_resources"
    __table_args__ = (
        UniqueConstraint(
            "module_installation_id",
            "resource_type",
            "resource_key",
            name="uq_module_resources_installation_key",
        ),
    )

    id = uuid_pk()
    module_installation_id = uuid_fk("module_installations")
    resource_type = Column(Text, nullable=False)
    resource_key = Column(Text, nullable=False)
    resource_version = Column(Text, nullable=False, server_default="1")
    config_json = json_object()
    status = Column(Text, nullable=False, server_default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class LabelDefinition(TimestampMixin, Base):
    __tablename__ = "label_definitions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "workspace_id", "key", name="uq_label_definitions_scope_key"),
    )

    id = uuid_pk()
    tenant_id = uuid_fk("tenants")
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"))
    key = Column(Text, nullable=False)
    display_name = Column(Text)
    description = Column(Text)
    value_type = Column(Text, nullable=False, server_default="string")
    allowed_values_json = Column(JSONB)
    protected = Column(Boolean, nullable=False, server_default=text("false"))


class Dataset(TimestampMixin, Base):
    __tablename__ = "datasets"

    id = uuid_pk()
    tenant_id = uuid_fk("tenants")
    workspace_id = uuid_fk("workspaces")
    name = Column(Text, nullable=False)
    slug = Column(Text)
    description = Column(Text)
    dataset_kind = Column(Text, nullable=False)
    status = Column(Text, nullable=False, server_default="draft")
    source_count = Column(Integer, nullable=False, server_default=text("0"))
    entity_count = Column(Integer, nullable=False, server_default=text("0"))
    content_unit_count = Column(Integer, nullable=False, server_default=text("0"))
    freshness_at = Column(DateTime(timezone=True))
    labels_json = json_object()
    classification_json = json_object()
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))


class Source(TimestampMixin, Base):
    __tablename__ = "sources"

    id = uuid_pk()
    tenant_id = uuid_fk("tenants")
    workspace_id = uuid_fk("workspaces")
    dataset_id = uuid_fk("datasets")
    connector_type = Column(Text, nullable=False)
    connector_version = Column(Text)
    display_name = Column(Text, nullable=False)
    labels_json = json_object()
    classification_json = json_object()
    config_json = json_object()
    sync_state_json = json_object()
    last_sync_at = Column(DateTime(timezone=True))


class DataStream(TimestampMixin, Base):
    __tablename__ = "data_streams"

    id = uuid_pk()
    tenant_id = uuid_fk("tenants")
    workspace_id = uuid_fk("workspaces")
    dataset_id = uuid_fk("datasets")
    source_id = uuid_fk("sources")
    name = Column(Text, nullable=False)
    stream_type = Column(Text, nullable=False)
    sync_mode = Column(Text, nullable=False)
    status = Column(Text, nullable=False, server_default="active")
    cursor_json = json_object()
    watermark_at = Column(DateTime(timezone=True))
    labels_json = json_object()
    classification_json = json_object()
    schedule_cron = Column(Text)


class EntityType(TimestampMixin, Base):
    __tablename__ = "entity_types"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "workspace_id",
            "dataset_id",
            "name",
            name="uq_entity_types_scope_name",
        ),
    )

    id = uuid_pk()
    tenant_id = uuid_fk("tenants")
    workspace_id = uuid_fk("workspaces")
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"))
    module_key = Column(Text)
    name = Column(Text, nullable=False)
    display_name = Column(Text, nullable=False)
    description = Column(Text)
    schema_json = json_object()
    primary_label_field = Column(Text)
    default_text_fields = json_array()


class RelationDefinition(Base):
    __tablename__ = "relation_definitions"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "workspace_id",
            "dataset_id",
            "name",
            name="uq_relation_definitions_scope_name",
        ),
    )

    id = uuid_pk()
    tenant_id = uuid_fk("tenants")
    workspace_id = uuid_fk("workspaces")
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"))
    module_key = Column(Text)
    name = Column(Text, nullable=False)
    display_name = Column(Text, nullable=False)
    description = Column(Text)
    from_entity_type = Column(Text)
    to_entity_type = Column(Text)
    properties_json = json_object()
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class MetricDefinition(TimestampMixin, Base):
    __tablename__ = "metric_definitions"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "workspace_id",
            "dataset_id",
            "name",
            name="uq_metric_definitions_scope_name",
        ),
    )

    id = uuid_pk()
    tenant_id = uuid_fk("tenants")
    workspace_id = uuid_fk("workspaces")
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"))
    module_key = Column(Text)
    name = Column(Text, nullable=False)
    display_name = Column(Text, nullable=False)
    description = Column(Text)
    value_type = Column(Text, nullable=False)
    unit = Column(Text)
    direction = Column(Text, nullable=False, server_default="neutral")
    aggregation = Column(Text)
    properties_json = json_object()
    labels_json = json_object()


class Job(TimestampMixin, Base):
    __tablename__ = "jobs"

    id = uuid_pk()
    tenant_id = uuid_fk("tenants")
    workspace_id = uuid_fk("workspaces")
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"))
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="SET NULL"))
    job_type = Column(Text, nullable=False)
    status = Column(Text, nullable=False, server_default="queued")
    progress_current = Column(Integer, nullable=False, server_default=text("0"))
    progress_total = Column(Integer)
    progress_message = Column(Text)
    payload_json = json_object()
    result_json = json_object()
    error_json = Column(JSONB)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    queued_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))


class JobEvent(Base):
    __tablename__ = "job_events"

    id = uuid_pk()
    job_id = uuid_fk("jobs")
    event_type = Column(Text, nullable=False)
    message = Column(Text)
    progress_current = Column(Integer)
    progress_total = Column(Integer)
    payload_json = json_object()
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
