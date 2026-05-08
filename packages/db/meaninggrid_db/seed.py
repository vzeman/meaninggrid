from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from meaninggrid_db.database import session_scope
from meaninggrid_db.models import (
    EntityType,
    LabelDefinition,
    MetricDefinition,
    Module,
    ModuleInstallation,
    ModuleResource,
    RelationDefinition,
    Tenant,
    User,
    Workspace,
    WorkspaceMember,
)

SITE_AUDIT_ENTITY_TYPES = [
    ("domain", "Domain", ["label", "canonical_uri"]),
    ("crawl_run", "Crawl Run", ["label"]),
    ("page", "Page", ["label", "canonical_uri", "title", "meta_description"]),
    ("paragraph", "Paragraph", ["text"]),
    ("heading", "Heading", ["text"]),
    ("link", "Link", ["label", "href"]),
    ("topic_cluster", "Topic Cluster", ["label", "description"]),
]

SITE_AUDIT_RELATIONS = [
    ("belongs_to_domain", "Belongs To Domain", "page", "domain"),
    ("discovered_in_crawl", "Discovered In Crawl", "page", "crawl_run"),
    ("links_to", "Links To", "page", "page"),
    ("has_paragraph", "Has Paragraph", "page", "paragraph"),
    ("has_heading", "Has Heading", "page", "heading"),
]

SITE_AUDIT_METRICS = [
    ("status_code", "HTTP Status Code", "integer", "higher_is_not_always_better"),
    ("word_count", "Word Count", "integer", "higher_is_not_always_better"),
    ("title_length", "Title Length", "integer", "higher_is_not_always_better"),
    (
        "meta_description_length",
        "Meta Description Length",
        "integer",
        "higher_is_not_always_better",
    ),
    ("technical_score", "Technical Score", "number", "higher_is_better"),
    ("geo_readiness_score", "GEO Readiness Score", "number", "higher_is_better"),
    ("duplicate_similarity", "Duplicate Similarity", "number", "lower_is_better"),
    ("internal_link_count", "Internal Link Count", "integer", "higher_is_better"),
    ("external_link_count", "External Link Count", "integer", "neutral"),
]

LABEL_DEFINITIONS = [
    ("module", "Module", "string", ["site_audit"]),
    ("source", "Source", "string", ["website_crawler", "api", "manual"]),
    ("environment", "Environment", "string", ["local", "staging", "production"]),
    ("project", "Project", "string", None),
]


def ensure_local_seed(session: Session) -> dict[str, Any]:
    tenant = session.scalar(select(Tenant).where(Tenant.slug == "local"))
    if tenant is None:
        tenant = Tenant(name="Local Tenant", slug="local", plan="local")
        session.add(tenant)
        session.flush()

    user = session.scalar(
        select(User).where(User.tenant_id == tenant.id, User.email == "admin@meaninggrid.local")
    )
    if user is None:
        user = User(
            tenant_id=tenant.id,
            email="admin@meaninggrid.local",
            display_name="Local Admin",
            role="admin",
            is_local_admin=True,
        )
        session.add(user)
        session.flush()

    workspace = session.scalar(
        select(Workspace).where(Workspace.tenant_id == tenant.id, Workspace.slug == "default")
    )
    if workspace is None:
        workspace = Workspace(
            tenant_id=tenant.id,
            name="Default Workspace",
            slug="default",
            description="Local MeaningGrid workspace.",
            default_language="en",
            created_by_user_id=user.id,
        )
        session.add(workspace)
        session.flush()

    membership = session.scalar(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace.id,
            WorkspaceMember.user_id == user.id,
        )
    )
    if membership is None:
        session.add(
            WorkspaceMember(
                tenant_id=tenant.id,
                workspace_id=workspace.id,
                user_id=user.id,
                role="owner",
            )
        )

    module = session.scalar(select(Module).where(Module.module_key == "site_audit"))
    if module is None:
        module = Module(
            module_key="site_audit",
            name="Site Audit And GEO Intelligence",
            description="Website semantic, technical SEO, and GEO readiness analysis.",
            current_version="0.1.0",
            bundled=True,
            status="active",
        )
        session.add(module)
        session.flush()

    installation = session.scalar(
        select(ModuleInstallation).where(
            ModuleInstallation.tenant_id == tenant.id,
            ModuleInstallation.workspace_id == workspace.id,
            ModuleInstallation.module_id == module.id,
        )
    )
    if installation is None:
        installation = ModuleInstallation(
            tenant_id=tenant.id,
            workspace_id=workspace.id,
            module_id=module.id,
            module_version=module.current_version,
            enabled=True,
            installed_by_user_id=user.id,
        )
        session.add(installation)
        session.flush()

    for resource_type, resource_key, config in _site_audit_resources():
        resource = session.scalar(
            select(ModuleResource).where(
                ModuleResource.module_installation_id == installation.id,
                ModuleResource.resource_type == resource_type,
                ModuleResource.resource_key == resource_key,
            )
        )
        if resource is None:
            session.add(
                ModuleResource(
                    module_installation_id=installation.id,
                    resource_type=resource_type,
                    resource_key=resource_key,
                    resource_version="1",
                    config_json=config,
                    status="active",
                )
            )

    for name, display_name, fields in SITE_AUDIT_ENTITY_TYPES:
        entity_type = session.scalar(
            select(EntityType).where(
                EntityType.tenant_id == tenant.id,
                EntityType.workspace_id == workspace.id,
                EntityType.dataset_id.is_(None),
                EntityType.name == name,
            )
        )
        if entity_type is None:
            session.add(
                EntityType(
                    tenant_id=tenant.id,
                    workspace_id=workspace.id,
                    module_key="site_audit",
                    name=name,
                    display_name=display_name,
                    default_text_fields=fields,
                )
            )

    for name, display_name, from_entity_type, to_entity_type in SITE_AUDIT_RELATIONS:
        relation = session.scalar(
            select(RelationDefinition).where(
                RelationDefinition.tenant_id == tenant.id,
                RelationDefinition.workspace_id == workspace.id,
                RelationDefinition.dataset_id.is_(None),
                RelationDefinition.name == name,
            )
        )
        if relation is None:
            session.add(
                RelationDefinition(
                    tenant_id=tenant.id,
                    workspace_id=workspace.id,
                    module_key="site_audit",
                    name=name,
                    display_name=display_name,
                    from_entity_type=from_entity_type,
                    to_entity_type=to_entity_type,
                )
            )

    for name, display_name, value_type, direction in SITE_AUDIT_METRICS:
        metric = session.scalar(
            select(MetricDefinition).where(
                MetricDefinition.tenant_id == tenant.id,
                MetricDefinition.workspace_id == workspace.id,
                MetricDefinition.dataset_id.is_(None),
                MetricDefinition.name == name,
            )
        )
        if metric is None:
            session.add(
                MetricDefinition(
                    tenant_id=tenant.id,
                    workspace_id=workspace.id,
                    module_key="site_audit",
                    name=name,
                    display_name=display_name,
                    value_type=value_type,
                    direction=direction,
                )
            )

    for key, display_name, value_type, allowed_values in LABEL_DEFINITIONS:
        label = session.scalar(
            select(LabelDefinition).where(
                LabelDefinition.tenant_id == tenant.id,
                LabelDefinition.workspace_id == workspace.id,
                LabelDefinition.key == key,
            )
        )
        if label is None:
            session.add(
                LabelDefinition(
                    tenant_id=tenant.id,
                    workspace_id=workspace.id,
                    key=key,
                    display_name=display_name,
                    value_type=value_type,
                    allowed_values_json=allowed_values,
                    protected=True,
                )
            )

    session.flush()
    return {
        "tenant_id": str(tenant.id),
        "workspace_id": str(workspace.id),
        "user_id": str(user.id),
        "site_audit_module_id": str(module.id),
    }


def _site_audit_resources() -> list[tuple[str, str, dict[str, Any]]]:
    resources: list[tuple[str, str, dict[str, Any]]] = []
    for name, display_name, fields in SITE_AUDIT_ENTITY_TYPES:
        resources.append(
            (
                "entity_type",
                name,
                {
                    "display_name": display_name,
                    "default_text_fields": fields,
                },
            )
        )
    for name, display_name, from_type, to_type in SITE_AUDIT_RELATIONS:
        resources.append(
            (
                "relation_definition",
                name,
                {
                    "display_name": display_name,
                    "from_entity_type": from_type,
                    "to_entity_type": to_type,
                },
            )
        )
    for name, display_name, value_type, direction in SITE_AUDIT_METRICS:
        resources.append(
            (
                "metric_definition",
                name,
                {
                    "display_name": display_name,
                    "value_type": value_type,
                    "direction": direction,
                },
            )
        )
    resources.extend(
        [
            ("analysis_preset", "site_audit_v0", {"pipeline": "crawl_extract_embed_analyze"}),
            ("dashboard", "site_audit_overview", {"view": "overview"}),
            ("context_template", "site_audit_context_pack", {"budget_tokens": 16000}),
            ("mcp_prompt", "audit_site_geo", {"prompt": "/audit_site_geo"}),
            ("mcp_prompt", "explain_page_outlier", {"prompt": "/explain_page_outlier"}),
            ("mcp_prompt", "find_content_gaps", {"prompt": "/find_content_gaps"}),
            (
                "mcp_prompt",
                "find_internal_link_opportunities",
                {"prompt": "/find_internal_link_opportunities"},
            ),
            ("mcp_prompt", "prepare_content_brief", {"prompt": "/prepare_content_brief"}),
        ]
    )
    return resources


def main() -> None:
    with session_scope() as session:
        result = ensure_local_seed(session)
    print(f"Seed complete: {result}")


if __name__ == "__main__":
    main()
