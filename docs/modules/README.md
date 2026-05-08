# MeaningGrid Module Specs

Modules add domain-specific schemas, connectors, analyses, prompts, dashboards,
reports, monitors, and context templates on top of the generic MeaningGrid
core.

Each module spec describes:

- target users
- jobs to be done
- connected sources
- entities and relations
- metrics and dimensions
- content and embeddings
- core analyses used
- module-specific analyses
- dashboards and reports
- headless agent workflows
- MCP prompts and tools
- security and governance notes
- MVP and later phases

## Module Specs

- [Module Feature Mapping To MeaningGrid Core](module-feature-mapping.md)
- [Site Audit And GEO Intelligence](site-audit-intelligence.md)
- [Marketing Intelligence](marketing-intelligence.md)
- [VC Fund Intelligence](vc-fund-intelligence.md)
- [Sales Intelligence](sales-intelligence.md)
- [Customer Support Intelligence](customer-support-intelligence.md)
- [Knowledge Base Intelligence](knowledge-base-intelligence.md)
- [Ecommerce Intelligence](ecommerce-intelligence.md)
- [Product Event Intelligence](product-event-intelligence.md)
- [Legal Contract Intelligence](legal-contract-intelligence.md)
- [HR/Talent Intelligence](hr-talent-intelligence.md)
- [Procurement/Vendor Intelligence](procurement-vendor-intelligence.md)
- [Compliance/Audit Intelligence](compliance-audit-intelligence.md)

## Shared Module Pattern

Every module should connect the same feature chain:

```text
connectors -> source events/raw objects -> entity mapper -> content/metrics
-> embeddings -> analysis presets -> insights/evidence -> context packs
-> MCP/API/UI/report/monitor
```

The strongest module pattern is:

```text
compare successful entities vs unsuccessful entities
find semantic differences
connect differences to metrics
show evidence
recommend action
```
