from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urljoin, urlparse, urlunparse

import httpx
from meaninggrid_core.config import get_settings
from meaninggrid_db.models import (
    ContentChunk,
    ContentUnit,
    Dataset,
    Embedding,
    EmbeddingModel,
    EmbeddingRun,
    Entity,
    EntityRelation,
    EntityType,
    Job,
    JobEvent,
    MetricDefinition,
    MetricValue,
    RawObject,
    Source,
    SourceEvent,
)
from meaninggrid_embeddings import embed_text
from meaninggrid_vectorstores import (
    create_qdrant_client,
    ensure_default_content_collection,
    upsert_points,
)
from selectolax.parser import HTMLParser
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

TRACKING_QUERY_PREFIXES = ("utm_",)
TRACKING_QUERY_NAMES = {"fbclid", "gclid", "msclkid"}
TEXT_UNIT_KINDS = {"page_title", "meta_description", "h1", "h2", "main_content", "paragraph"}


@dataclass(frozen=True)
class FetchedPage:
    requested_url: str
    final_url: str
    status_code: int
    content_type: str
    body: str
    duration_ms: int


@dataclass(frozen=True)
class ExtractedPage:
    title: str | None
    meta_description: str | None
    canonical_url: str | None
    robots_meta: str | None
    language: str | None
    headings: list[tuple[str, str]]
    paragraphs: list[str]
    links: list[tuple[str, str]]
    main_text: str
    jsonld_types: list[str]
    image_count: int
    image_alt_count: int


def run_crawl_job(session: Session, job_id: str) -> dict[str, int]:
    job = session.get(Job, job_id)
    if job is None:
        raise ValueError(f"Job {job_id} was not found")
    if job.dataset_id is None or job.source_id is None:
        raise ValueError("Crawl job must have dataset_id and source_id")

    dataset = session.get(Dataset, job.dataset_id)
    source = session.get(Source, job.source_id)
    if dataset is None or source is None:
        raise ValueError("Crawl job references missing dataset or source")

    crawl = job.payload_json.get("crawl", {})
    base_url = normalize_url(crawl["base_url"], crawl["base_url"])
    max_pages = int(crawl.get("max_pages", 100))

    job.status = "running"
    job.started_at = datetime.now(UTC)
    job.progress_current = 0
    job.progress_total = max_pages
    job.progress_message = "Discovering pages"
    session.add(_job_event(job, "job_started", "Started website crawl."))
    session.flush()

    try:
        result = _crawl_dataset(session, job, dataset, source, base_url, max_pages)
        embedding_result = _embed_dataset_chunks(session, job, dataset)
        result.update(embedding_result)
        job.status = "succeeded"
        job.finished_at = datetime.now(UTC)
        job.progress_current = result["pages_fetched"]
        job.progress_message = "Crawl and extraction finished"
        job.result_json = result
        dataset.status = "active"
        dataset.freshness_at = datetime.now(UTC)
        dataset.entity_count = session.scalar(
            select(func.count()).select_from(Entity).where(Entity.dataset_id == dataset.id)
        )
        dataset.content_unit_count = session.scalar(
            select(func.count())
            .select_from(ContentUnit)
            .where(ContentUnit.dataset_id == dataset.id)
        )
        session.add(_job_event(job, "job_succeeded", "Crawl and extraction finished.", result))
        session.commit()
        return result
    except Exception as exc:
        job.status = "failed"
        job.finished_at = datetime.now(UTC)
        job.progress_message = "Crawl failed"
        job.error_json = {"error_code": "crawl_failed", "error_message": str(exc)}
        session.add(_job_event(job, "job_failed", str(exc)))
        session.commit()
        raise


def _crawl_dataset(
    session: Session,
    job: Job,
    dataset: Dataset,
    source: Source,
    base_url: str,
    max_pages: int,
) -> dict[str, int]:
    queued: list[str] = [base_url]
    seen: set[str] = set()
    fetched_count = 0
    failed_count = 0
    raw_object_ids: list[str] = []
    page_entities: dict[str, Entity] = {}
    pending_links: list[tuple[Entity, str, str]] = []

    domain_entity = _upsert_entity(
        session,
        dataset,
        "domain",
        _host_key(base_url),
        _host_key(base_url),
        canonical_uri=_origin_for(base_url),
        properties={"base_url": base_url},
    )
    crawl_run_entity = _upsert_entity(
        session,
        dataset,
        "crawl_run",
        f"crawl:{job.id}",
        f"Crawl {job.id}",
        properties={"job_id": str(job.id), "base_url": base_url, "max_pages": max_pages},
    )

    while queued and fetched_count < max_pages:
        requested_url = queued.pop(0)
        normalized_requested = normalize_url(requested_url, base_url)
        if normalized_requested in seen:
            continue
        seen.add(normalized_requested)
        _update_job_progress(job, fetched_count, max_pages, f"Fetching {normalized_requested}")

        try:
            fetched = fetch_url(normalized_requested)
        except Exception as exc:
            failed_count += 1
            session.add(
                _job_event(
                    job,
                    "page_failed",
                    f"Failed to fetch {normalized_requested}",
                    {"error": str(exc)},
                )
            )
            continue

        if "html" not in fetched.content_type:
            continue

        raw_object = _store_raw_object(session, dataset, source, fetched)
        raw_object_ids.append(str(raw_object.id))
        source_event = _store_source_event(session, dataset, source, raw_object, fetched)
        extracted = extract_html(fetched.body, fetched.final_url)
        page_entity = _store_extracted_page(
            session,
            dataset,
            source,
            source_event,
            raw_object,
            fetched,
            extracted,
            domain_entity,
            crawl_run_entity,
        )
        page_entities[page_entity.external_id or fetched.final_url] = page_entity
        fetched_count += 1

        for anchor, href in extracted.links:
            normalized_link = normalize_url(href, fetched.final_url)
            if not _is_crawlable_internal(normalized_link, base_url):
                pending_links.append((page_entity, normalized_link, anchor))
                continue
            pending_links.append((page_entity, normalized_link, anchor))
            if normalized_link not in seen and normalized_link not in queued:
                queued.append(normalized_link)

        session.add(
            _job_event(
                job,
                "page_extracted",
                f"Extracted {fetched.final_url}",
                {
                    "url": fetched.final_url,
                    "paragraphs": len(extracted.paragraphs),
                    "links": len(extracted.links),
                },
            )
        )
        session.flush()

    _store_links(session, dataset, pending_links, page_entities)
    session.flush()
    return {
        "pages_discovered": len(seen) + len(queued),
        "pages_fetched": fetched_count,
        "pages_failed": failed_count,
        "raw_objects": len(raw_object_ids),
    }


def _embed_dataset_chunks(session: Session, job: Job, dataset: Dataset) -> dict[str, Any]:
    settings = get_settings()
    if settings.vector_backend != "qdrant":
        return {"chunks_embedded": 0, "vector_backend": settings.vector_backend}

    chunks = session.scalars(
        select(ContentChunk).where(ContentChunk.dataset_id == dataset.id).order_by(ContentChunk.id)
    ).all()
    if not chunks:
        return {"chunks_embedded": 0, "vector_backend": "qdrant"}

    embedding_model = _get_embedding_model(session)
    embedding_run = EmbeddingRun(
        tenant_id=dataset.tenant_id,
        workspace_id=dataset.workspace_id,
        dataset_id=dataset.id,
        embedding_model_id=embedding_model.id,
        status="running",
        target_filter_json={"content_kind": "content_chunks", "module": "site_audit"},
        started_at=datetime.now(UTC),
    )
    session.add(embedding_run)
    session.flush()
    session.add(
        _job_event(
            job,
            "embedding_started",
            f"Embedding {len(chunks)} content chunks.",
            {"chunks": len(chunks)},
        )
    )

    client = create_qdrant_client()
    collection = ensure_default_content_collection(client)
    points = []
    for chunk in chunks:
        vector = embed_text(chunk.text, collection.dimension)
        payload = _chunk_vector_payload(dataset, chunk)
        points.append((str(chunk.id), vector, payload))
        _upsert_embedding_record(
            session,
            dataset,
            embedding_run,
            embedding_model,
            chunk,
            collection.name,
        )

    upsert_points(client, collection.name, points)
    embedding_run.status = "succeeded"
    embedding_run.finished_at = datetime.now(UTC)
    session.add(
        _job_event(
            job,
            "embedding_succeeded",
            "Embedded content chunks into Qdrant.",
            {
                "chunks_embedded": len(points),
                "vector_collection": collection.name,
                "embedding_model": embedding_model.model_name,
            },
        )
    )
    session.flush()
    return {
        "chunks_embedded": len(points),
        "vector_backend": "qdrant",
        "vector_collection": collection.name,
    }


def fetch_url(url: str) -> FetchedPage:
    parsed = urlparse(url)
    started = datetime.now(UTC)
    if parsed.scheme == "file":
        path = Path(parsed.path)
        body = path.read_text(encoding="utf-8")
        duration_ms = int((datetime.now(UTC) - started).total_seconds() * 1000)
        return FetchedPage(
            requested_url=url,
            final_url=url,
            status_code=200,
            content_type="text/html; charset=utf-8",
            body=body,
            duration_ms=duration_ms,
        )

    with httpx.Client(follow_redirects=True, timeout=20) as client:
        response = client.get(url)
    duration_ms = int((datetime.now(UTC) - started).total_seconds() * 1000)
    return FetchedPage(
        requested_url=url,
        final_url=str(response.url),
        status_code=response.status_code,
        content_type=response.headers.get("content-type", ""),
        body=response.text,
        duration_ms=duration_ms,
    )


def extract_html(html: str, final_url: str) -> ExtractedPage:
    tree = HTMLParser(html)
    title = _node_text(tree.css_first("title"))
    meta_description = _attr(tree.css_first("meta[name='description']"), "content")
    canonical_url = _attr(tree.css_first("link[rel='canonical']"), "href")
    if canonical_url:
        canonical_url = normalize_url(canonical_url, final_url)
    robots_meta = _attr(tree.css_first("meta[name='robots']"), "content")
    language = _attr(tree.css_first("html"), "lang")
    headings = [
        (node.tag.lower(), node.text(separator=" ", strip=True))
        for node in tree.css("h1, h2, h3")
        if node.text(separator=" ", strip=True)
    ]
    paragraphs = [
        node.text(separator=" ", strip=True)
        for node in tree.css("p")
        if _meaningful_text(node.text(separator=" ", strip=True))
    ]
    links = []
    for node in tree.css("a[href]"):
        href = node.attributes.get("href", "")
        if not href:
            continue
        links.append((node.text(separator=" ", strip=True), href))
    main_node = tree.css_first("main") or tree.css_first("body")
    main_text = main_node.text(separator=" ", strip=True) if main_node else ""
    jsonld_types = _jsonld_types(tree)
    image_nodes = tree.css("img")
    image_alt_count = len([node for node in image_nodes if node.attributes.get("alt")])
    return ExtractedPage(
        title=title,
        meta_description=meta_description,
        canonical_url=canonical_url,
        robots_meta=robots_meta,
        language=language,
        headings=headings,
        paragraphs=paragraphs,
        links=links,
        main_text=main_text,
        jsonld_types=jsonld_types,
        image_count=len(image_nodes),
        image_alt_count=image_alt_count,
    )


def normalize_url(url: str, base_url: str) -> str:
    base = urlparse(base_url)
    if base.scheme == "file" and url.startswith("/") and not url.startswith("//"):
        joined = (Path(base.path).parent / url.lstrip("/")).as_uri()
    else:
        joined = urljoin(base_url, url)
    joined, _fragment = urldefrag(joined)
    parsed = urlparse(joined)
    if parsed.scheme in {"mailto", "tel", "javascript"}:
        return joined
    query_parts = []
    for item in parsed.query.split("&"):
        if not item:
            continue
        name = item.split("=", 1)[0]
        if name in TRACKING_QUERY_NAMES or name.startswith(TRACKING_QUERY_PREFIXES):
            continue
        query_parts.append(item)
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    host = parsed.netloc.lower()
    return urlunparse((parsed.scheme, host, path, "", "&".join(query_parts), ""))


def _store_raw_object(
    session: Session,
    dataset: Dataset,
    source: Source,
    fetched: FetchedPage,
) -> RawObject:
    content_hash = _hash(fetched.body)
    existing = session.scalar(
        select(RawObject).where(
            RawObject.source_id == source.id,
            RawObject.external_id == fetched.final_url,
            RawObject.content_hash == content_hash,
        )
    )
    if existing is not None:
        return existing
    raw_object = RawObject(
        tenant_id=dataset.tenant_id,
        workspace_id=dataset.workspace_id,
        dataset_id=dataset.id,
        source_id=source.id,
        external_id=fetched.final_url,
        object_kind="html_page",
        object_uri=f"inline://sha256/{content_hash}",
        content_hash=content_hash,
        mime_type=fetched.content_type,
        size_bytes=len(fetched.body.encode("utf-8")),
        metadata_json={
            "requested_url": fetched.requested_url,
            "final_url": fetched.final_url,
            "status_code": fetched.status_code,
            "duration_ms": fetched.duration_ms,
        },
    )
    session.add(raw_object)
    session.flush()
    return raw_object


def _store_source_event(
    session: Session,
    dataset: Dataset,
    source: Source,
    raw_object: RawObject,
    fetched: FetchedPage,
) -> SourceEvent:
    idempotency_key = f"page_fetched:{source.id}:{raw_object.content_hash}:{fetched.final_url}"
    existing = session.scalar(
        select(SourceEvent).where(
            SourceEvent.tenant_id == dataset.tenant_id,
            SourceEvent.idempotency_key == idempotency_key,
        )
    )
    if existing is not None:
        return existing
    event = SourceEvent(
        tenant_id=dataset.tenant_id,
        workspace_id=dataset.workspace_id,
        dataset_id=dataset.id,
        source_id=source.id,
        event_type="page_fetched",
        raw_object_id=raw_object.id,
        idempotency_key=idempotency_key,
        payload_hash=raw_object.content_hash,
        processing_status="processed",
        partition_key=fetched.final_url,
        metadata_json=raw_object.metadata_json,
        labels_json={"module": "site_audit"},
    )
    session.add(event)
    session.flush()
    return event


def _store_extracted_page(
    session: Session,
    dataset: Dataset,
    source: Source,
    source_event: SourceEvent,
    raw_object: RawObject,
    fetched: FetchedPage,
    extracted: ExtractedPage,
    domain_entity: Entity,
    crawl_run_entity: Entity,
) -> Entity:
    canonical_url = extracted.canonical_url
    if urlparse(fetched.final_url).scheme == "file":
        canonical_url = normalize_url(fetched.final_url, fetched.final_url)
    canonical_url = canonical_url or normalize_url(fetched.final_url, fetched.final_url)
    page_entity = _upsert_entity(
        session,
        dataset,
        "page",
        canonical_url,
        extracted.title or canonical_url,
        canonical_uri=canonical_url,
        raw_object=raw_object,
        properties={
            "requested_url": fetched.requested_url,
            "final_url": fetched.final_url,
            "canonical_url": canonical_url,
            "title": extracted.title,
            "meta_description": extracted.meta_description,
            "language": extracted.language,
            "status_code": fetched.status_code,
            "content_type": fetched.content_type,
            "robots_meta": extracted.robots_meta,
            "is_indexable": "noindex" not in (extracted.robots_meta or "").lower(),
            "jsonld_types": extracted.jsonld_types,
            "image_count": extracted.image_count,
            "image_alt_count": extracted.image_alt_count,
        },
    )
    _replace_page_content(session, dataset, page_entity)
    _add_relation(session, dataset, page_entity, domain_entity, "belongs_to_domain")
    _add_relation(session, dataset, page_entity, crawl_run_entity, "discovered_in_crawl")

    order_index = 0
    if extracted.title:
        _add_content_unit(
            session,
            dataset,
            page_entity,
            raw_object,
            "page_title",
            extracted.title,
            order_index,
        )
        order_index += 1
    if extracted.meta_description:
        _add_content_unit(
            session,
            dataset,
            page_entity,
            raw_object,
            "meta_description",
            extracted.meta_description,
            order_index,
        )
        order_index += 1
    for level, text in extracted.headings:
        if level in {"h1", "h2"}:
            _add_content_unit(session, dataset, page_entity, raw_object, level, text, order_index)
            order_index += 1
    if extracted.main_text:
        _add_content_unit(
            session,
            dataset,
            page_entity,
            raw_object,
            "main_content",
            extracted.main_text,
            order_index,
        )
        order_index += 1
    for paragraph in extracted.paragraphs:
        _add_content_unit(
            session,
            dataset,
            page_entity,
            raw_object,
            "paragraph",
            paragraph,
            order_index,
        )
        order_index += 1

    _add_metric_values(session, dataset, source, source_event, page_entity, extracted, fetched)
    return page_entity


def _upsert_entity(
    session: Session,
    dataset: Dataset,
    entity_type_name: str,
    external_id: str,
    label: str,
    canonical_uri: str | None = None,
    raw_object: RawObject | None = None,
    properties: dict[str, Any] | None = None,
) -> Entity:
    entity_type = _get_entity_type(session, dataset, entity_type_name)
    entity = session.scalar(
        select(Entity).where(
            Entity.dataset_id == dataset.id,
            Entity.entity_type_id == entity_type.id,
            Entity.external_id == external_id,
        )
    )
    if entity is None:
        entity = Entity(
            tenant_id=dataset.tenant_id,
            workspace_id=dataset.workspace_id,
            dataset_id=dataset.id,
            entity_type_id=entity_type.id,
            external_id=external_id,
            label=label,
            canonical_uri=canonical_uri,
            raw_object_id=raw_object.id if raw_object else None,
            properties_json=properties or {},
            labels_json={"module": "site_audit", "entity_type": entity_type_name},
        )
    else:
        entity.label = label
        entity.canonical_uri = canonical_uri
        entity.raw_object_id = raw_object.id if raw_object else entity.raw_object_id
        entity.properties_json = properties or entity.properties_json
    session.add(entity)
    session.flush()
    return entity


def _replace_page_content(session: Session, dataset: Dataset, page_entity: Entity) -> None:
    unit_ids = session.scalars(
        select(ContentUnit.id).where(
            ContentUnit.dataset_id == dataset.id,
            ContentUnit.entity_id == page_entity.id,
        )
    ).all()
    if unit_ids:
        chunk_ids = session.scalars(
            select(ContentChunk.id).where(ContentChunk.content_unit_id.in_(unit_ids))
        ).all()
        if chunk_ids:
            session.execute(delete(Embedding).where(Embedding.content_chunk_id.in_(chunk_ids)))
        session.execute(delete(ContentChunk).where(ContentChunk.content_unit_id.in_(unit_ids)))
        session.execute(delete(ContentUnit).where(ContentUnit.id.in_(unit_ids)))
    session.execute(
        delete(MetricValue).where(
            MetricValue.dataset_id == dataset.id,
            MetricValue.entity_id == page_entity.id,
        )
    )
    session.execute(
        delete(EntityRelation).where(
            EntityRelation.dataset_id == dataset.id,
            EntityRelation.from_entity_id == page_entity.id,
        )
    )


def _add_content_unit(
    session: Session,
    dataset: Dataset,
    page_entity: Entity,
    raw_object: RawObject,
    unit_kind: str,
    text: str,
    order_index: int,
) -> ContentUnit:
    words = _words(text)
    content_unit = ContentUnit(
        tenant_id=dataset.tenant_id,
        workspace_id=dataset.workspace_id,
        dataset_id=dataset.id,
        entity_id=page_entity.id,
        raw_object_id=raw_object.id,
        unit_kind=unit_kind,
        title=unit_kind,
        text=text,
        language=page_entity.properties_json.get("language"),
        order_index=order_index,
        token_count=len(words),
        word_count=len(words),
        content_hash=_hash(text),
        metadata_json={"source": "site_audit_v0"},
        labels_json={"module": "site_audit", "unit_kind": unit_kind},
        classification_json=page_entity.classification_json,
    )
    session.add(content_unit)
    session.flush()
    if unit_kind in TEXT_UNIT_KINDS and len(words) >= 3:
        _add_chunk(session, dataset, page_entity, content_unit, text)
    return content_unit


def _add_chunk(
    session: Session,
    dataset: Dataset,
    page_entity: Entity,
    content_unit: ContentUnit,
    text: str,
) -> None:
    words = _words(text)
    chunk = ContentChunk(
        tenant_id=dataset.tenant_id,
        workspace_id=dataset.workspace_id,
        dataset_id=dataset.id,
        entity_id=page_entity.id,
        content_unit_id=content_unit.id,
        chunk_index=0,
        text=text,
        token_count=len(words),
        content_hash=_hash(text),
        chunking_strategy="site_audit_v0",
        chunking_version="1",
        start_offset=0,
        end_offset=len(text),
        metadata_json={
            "unit_kind": content_unit.unit_kind,
            "language": content_unit.language,
        },
        labels_json={
            "module": "site_audit",
            "unit_kind": content_unit.unit_kind,
            "entity_type": page_entity.labels_json.get("entity_type"),
        },
        classification_json=content_unit.classification_json,
    )
    session.add(chunk)


def _get_embedding_model(session: Session) -> EmbeddingModel:
    settings = get_settings()
    model = session.scalar(
        select(EmbeddingModel).where(
            EmbeddingModel.provider == settings.embedding_provider,
            EmbeddingModel.model_name == settings.embedding_model,
            EmbeddingModel.model_version == "default",
        )
    )
    if model is None:
        model = EmbeddingModel(
            provider=settings.embedding_provider,
            model_name=settings.embedding_model,
            model_version="default",
            dimension=settings.embedding_dimension,
            distance_metric="cosine",
            normalized=True,
            capabilities_json={
                "deterministic": settings.embedding_provider == "local",
                "content_kind": "content_chunks",
            },
        )
        session.add(model)
        session.flush()
    return model


def _upsert_embedding_record(
    session: Session,
    dataset: Dataset,
    embedding_run: EmbeddingRun,
    embedding_model: EmbeddingModel,
    chunk: ContentChunk,
    collection_name: str,
) -> Embedding:
    existing = session.scalar(
        select(Embedding).where(
            Embedding.embedding_model_id == embedding_model.id,
            Embedding.vector_store == "qdrant",
            Embedding.vector_collection == collection_name,
            Embedding.vector_point_id == str(chunk.id),
        )
    )
    if existing is None:
        existing = Embedding(
            tenant_id=dataset.tenant_id,
            workspace_id=dataset.workspace_id,
            dataset_id=dataset.id,
            embedding_model_id=embedding_model.id,
            vector_store="qdrant",
            vector_collection=collection_name,
            vector_point_id=str(chunk.id),
        )
    existing.embedding_run_id = embedding_run.id
    existing.entity_id = chunk.entity_id
    existing.content_unit_id = chunk.content_unit_id
    existing.content_chunk_id = chunk.id
    existing.content_hash = chunk.content_hash
    existing.embedding_status = "ready"
    session.add(existing)
    return existing


def _chunk_vector_payload(dataset: Dataset, chunk: ContentChunk) -> dict[str, Any]:
    labels = chunk.labels_json or {}
    classification = chunk.classification_json or {}
    return {
        "tenant_id": str(dataset.tenant_id),
        "workspace_id": str(dataset.workspace_id),
        "dataset_id": str(dataset.id),
        "entity_id": str(chunk.entity_id) if chunk.entity_id else None,
        "content_unit_id": str(chunk.content_unit_id),
        "content_chunk_id": str(chunk.id),
        "entity_type": labels.get("entity_type"),
        "unit_kind": labels.get("unit_kind"),
        "language": chunk.metadata_json.get("language"),
        "module": labels.get("module"),
        "visibility": classification.get("visibility", "internal"),
        "sensitivity": classification.get("sensitivity", "standard"),
        "content_hash": chunk.content_hash,
    }


def _add_metric_values(
    session: Session,
    dataset: Dataset,
    source: Source,
    source_event: SourceEvent,
    page_entity: Entity,
    extracted: ExtractedPage,
    fetched: FetchedPage,
) -> None:
    internal_link_count = len(
        [href for _anchor, href in extracted.links if _same_host(href, fetched.final_url)]
    )
    external_link_count = len(
        [href for _anchor, href in extracted.links if not _same_host(href, fetched.final_url)]
    )
    metrics = {
        "status_code": fetched.status_code,
        "word_count": len(_words(extracted.main_text)),
        "title_length": len(extracted.title or ""),
        "meta_description_length": len(extracted.meta_description or ""),
        "internal_link_count": internal_link_count,
        "external_link_count": external_link_count,
        "technical_score": _technical_score(extracted, fetched),
    }
    for name, value in metrics.items():
        metric_definition = _get_metric(session, dataset, name)
        session.add(
            MetricValue(
                tenant_id=dataset.tenant_id,
                workspace_id=dataset.workspace_id,
                dataset_id=dataset.id,
                metric_definition_id=metric_definition.id,
                entity_id=page_entity.id,
                value_number=float(value),
                source_id=source.id,
                source_event_id=source_event.id,
                labels_json={"module": "site_audit", "metric": name},
            )
        )


def _store_links(
    session: Session,
    dataset: Dataset,
    pending_links: list[tuple[Entity, str, str]],
    page_entities: dict[str, Entity],
) -> None:
    for from_entity, normalized_link, anchor in pending_links:
        to_entity = page_entities.get(normalized_link)
        _add_relation(
            session,
            dataset,
            from_entity,
            to_entity,
            "links_to",
            to_external_ref=None if to_entity else normalized_link,
            properties={"anchor_text": anchor, "href": normalized_link},
        )


def _add_relation(
    session: Session,
    dataset: Dataset,
    from_entity: Entity,
    to_entity: Entity | None,
    relation_type: str,
    to_external_ref: str | None = None,
    properties: dict[str, Any] | None = None,
) -> None:
    session.add(
        EntityRelation(
            tenant_id=dataset.tenant_id,
            workspace_id=dataset.workspace_id,
            dataset_id=dataset.id,
            from_entity_id=from_entity.id,
            to_entity_id=to_entity.id if to_entity else None,
            to_external_ref=to_external_ref,
            relation_type=relation_type,
            confidence=1.0,
            properties_json=properties or {},
            labels_json={"module": "site_audit", "relation_type": relation_type},
        )
    )


def _get_entity_type(session: Session, dataset: Dataset, name: str) -> EntityType:
    entity_type = session.scalar(
        select(EntityType).where(
            EntityType.workspace_id == dataset.workspace_id,
            EntityType.dataset_id.is_(None),
            EntityType.name == name,
        )
    )
    if entity_type is None:
        raise ValueError(f"Entity type {name} is not seeded")
    return entity_type


def _get_metric(session: Session, dataset: Dataset, name: str) -> MetricDefinition:
    metric = session.scalar(
        select(MetricDefinition).where(
            MetricDefinition.workspace_id == dataset.workspace_id,
            MetricDefinition.dataset_id.is_(None),
            MetricDefinition.name == name,
        )
    )
    if metric is None:
        raise ValueError(f"Metric {name} is not seeded")
    return metric


def _job_event(
    job: Job,
    event_type: str,
    message: str,
    payload: dict[str, Any] | None = None,
) -> JobEvent:
    return JobEvent(
        job_id=job.id,
        event_type=event_type,
        message=message,
        progress_current=job.progress_current,
        progress_total=job.progress_total,
        payload_json=payload or {},
    )


def _update_job_progress(job: Job, current: int, total: int, message: str) -> None:
    job.progress_current = current
    job.progress_total = total
    job.progress_message = message


def _jsonld_types(tree: HTMLParser) -> list[str]:
    types: list[str] = []
    for node in tree.css("script[type='application/ld+json']"):
        text = node.text(strip=True)
        for marker in ('"@type"', "'@type'"):
            if marker in text:
                types.append("jsonld")
                break
    return types


def _technical_score(extracted: ExtractedPage, fetched: FetchedPage) -> float:
    score = 100.0
    if fetched.status_code >= 400:
        score -= 40
    if not extracted.title:
        score -= 15
    if not extracted.meta_description:
        score -= 15
    if not any(level == "h1" for level, _text in extracted.headings):
        score -= 10
    if "noindex" in (extracted.robots_meta or "").lower():
        score -= 20
    return max(score, 0.0)


def _node_text(node: Any) -> str | None:
    if node is None:
        return None
    text = node.text(separator=" ", strip=True)
    return text or None


def _attr(node: Any, name: str) -> str | None:
    if node is None:
        return None
    value = node.attributes.get(name)
    return value.strip() if value else None


def _meaningful_text(text: str) -> bool:
    return bool(text and len(_words(text)) >= 3)


def _words(text: str) -> list[str]:
    return [word for word in text.split() if word.strip()]


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _host_key(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme == "file":
        return "local-fixture"
    return parsed.netloc.lower()


def _origin_for(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme == "file":
        return str(Path(parsed.path).parent.as_uri())
    return urlunparse((parsed.scheme, parsed.netloc.lower(), "/", "", "", ""))


def _is_crawlable_internal(url: str, base_url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme in {"mailto", "tel", "javascript"}:
        return False
    if parsed.path.lower().endswith((".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip")):
        return False
    return _same_host(url, base_url)


def _same_host(url: str, base_url: str) -> bool:
    parsed = urlparse(urljoin(base_url, url))
    base = urlparse(base_url)
    if parsed.scheme == "file" and base.scheme == "file":
        return Path(parsed.path).parent == Path(base.path).parent
    return parsed.netloc.lower() == base.netloc.lower()
