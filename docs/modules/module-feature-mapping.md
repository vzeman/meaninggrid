# Module Feature Mapping To MeaningGrid Core

## Purpose

This document explains what each MeaningGrid module does, why customers need
it, what tasks it supports, and how its features map to the generic
MeaningGrid core.

The point of the modular architecture is that every domain module feels
specialized to the customer, but still runs on the same core primitives:

```text
connectors
source events
raw objects
entity model
relations
content units
chunks
embeddings
metric values
analysis runs
artifacts
insights
evidence
context packs
MCP/API/CLI
dashboards
reports
monitors
security policies
```

## Shared Core Mapping

Every module should map its domain features into the same platform layers.

| Module Feature | MeaningGrid Core Subsystem |
|---|---|
| Import data from tools | Connectors, sources, data streams |
| Track new/changed data | Source events, entity change events |
| Preserve original data | Raw objects, object storage, retention policies |
| Model domain objects | Entity types, entities, properties |
| Model relationships | Entity relations |
| Store text | Content units |
| Prepare text for vectors | Content chunks |
| Compare meaning | Embeddings, vector stores, semantic search |
| Store business outcomes | Metric definitions, metric values, dimensions |
| Analyze patterns | Analysis engine, analysis runs, artifacts |
| Explain findings | Insight engine, insights, evidence |
| Give agents context | Context packs, MCP resources, MCP tools, prompts |
| Show humans results | Dashboards, reports, exports |
| Watch changes | Monitors, alerts, delta context packs |
| Protect data | RBAC/ABAC, PII redaction, audit logs, policies |

## Shared AI Agent Patterns Beyond Similarity

Similarity is only one primitive. The real value comes when agents combine
similarity with metrics, history, policies, and workflow context.

Common AI-agent decision support patterns:

| Agent Pattern | What It Does | Core Subsystems |
|---|---|---|
| Prioritization | Ranks what to fix, review, write, renew, or escalate | Metrics, analysis artifacts, insights |
| Triage | Routes entities to the right owner/team/workflow | Entity relations, schemas, rules, MCP tools |
| Context briefing | Prepares concise evidence-backed summaries | Context packs, evidence packs, reports |
| Gap explanation | Explains missing content, evidence, clauses, or coverage | Gap analysis, semantic alignment, evidence |
| Risk explanation | Explains why something is risky or unusual | Outliers, cohorts, metrics, evidence |
| Drafting | Drafts briefs, reports, tasks, emails, KB outlines, checklists | Prompts, context packs, report templates |
| Monitoring | Watches new data and alerts on meaningful changes | Streams, source events, monitors, delta packs |
| QA/review | Checks whether output/content/process meets standards | Module rules, metrics, semantic checks |
| Workflow creation | Creates tasks, reports, labels, or review packets | Action tools, permissions, audit logs |
| Decision memory | Saves accepted/rejected insights and human decisions | Agent notes, feedback, analysis history |

Common automations:

- create a weekly report
- draft a project-management task
- route an issue to an owner
- create a review packet
- monitor a threshold or semantic gap
- generate a content brief
- summarize a long conversation/document
- classify new incoming data
- detect missing information
- prepare questions for a human decision maker

Guardrail pattern:

```text
agent may recommend -> agent may draft -> human approves -> system acts
```

For sensitive modules such as HR, Legal, Compliance, and VC, the agent should
support decisions but not make final decisions automatically.

## Site Audit And GEO Intelligence

Detailed spec: [Site Audit And GEO Intelligence](site-audit-intelligence.md)

### What The Module Does

Site Audit And GEO Intelligence crawls domains and turns pages, paragraphs,
headings, links, and technical crawl facts into a semantic and metric model.

It analyzes:

- technical SEO issues
- semantic clusters
- page and paragraph similarity
- outlier pages
- duplicate content
- internal linking gaps
- topic coverage
- GEO readiness
- domain comparisons

### Why Customers Need It

SEO and GEO teams usually have fragmented crawl reports, keyword data, content
briefs, and competitor notes. They can see technical issues, but they often
cannot see how meaning is distributed across the site.

Customers need this module to answer:

- Which pages dilute topical authority?
- Which pages are too similar and should be merged?
- Which pages are far from the domain centroid?
- Which paragraphs are duplicated across different pages?
- Which internal links should exist because pages are semantically close?
- Which topics are weak compared with competitors?
- Which pages are not clear or evidence-rich enough for AI answer engines?

### Tasks The Module Supports

- Crawl a domain.
- Run technical SEO checks.
- Build page and paragraph semantic maps.
- Find duplicates and cannibalization.
- Find outlier pages and weak clusters.
- Compare domains by topic coverage.
- Score GEO readiness.
- Generate content briefs and internal link plans.
- Prepare evidence-backed reports through UI or MCP.

### Feature Mapping To Core

| Site Audit Feature | Core Mapping |
|---|---|
| Website crawl | Connector runtime, source events, raw objects |
| Sitemap/robots parsing | Source metadata, raw objects, crawl metrics |
| Pages and paragraphs | Entities, content units, content chunks |
| Links | Entity relations, graph analysis |
| Technical SEO checks | Metric definitions, metric values, insights |
| Page similarity | Embeddings, vector search, similarity edges |
| Topic clusters | Clustering, analysis artifacts |
| Outlier pages | Centroid metrics, insight evidence |
| Domain comparison | Cohort comparison, semantic gap analysis |
| GEO scoring | Metric extractors, analysis presets |
| Reports | Report templates, exports |
| Agent access | MCP prompts, context packs, evidence |

## Marketing Intelligence

Detailed spec: [Marketing Intelligence](marketing-intelligence.md)

### What The Module Does

Marketing Intelligence connects website content, search demand, ad campaigns,
ecommerce sales, conversions, and linkbuilding into one semantic and metric
model.

It helps customers understand whether the words they pay for, rank for, sell
through, and publish on their website are aligned.

The module transforms marketing data into entities like:

- pages
- paragraphs
- search queries
- paid keywords
- campaigns
- ads
- products
- orders
- link targets

Then it compares those entities semantically and weights the results by
business metrics such as cost, conversions, revenue, ROAS, clicks, and organic
impressions.

### Why Customers Need It

Marketing teams usually have fragmented tools:

- Search Console knows what people search organically.
- Google Ads knows what the company pays for.
- Ecommerce knows what sells.
- The website contains the content.
- SEO tools know links and competitors.
- Analytics tools know conversion behavior.

The customer problem is that these tools do not explain whether the whole
system is semantically coherent.

Customers need this module to answer:

- Are we paying for keywords that our website does not actually explain well?
- Are high-converting paid terms missing strong organic content?
- Are important product pages semantically weak?
- Are we building links to pages that support valuable topics?
- Are new search terms drifting away from our content strategy?

### Tasks The Module Supports

- Match paid keywords to landing pages.
- Match organic queries to pages and content clusters.
- Find paid keyword content gaps.
- Find high-revenue products with weak content coverage.
- Compare ad copy to landing page content.
- Prioritize content briefs by cost, revenue, and semantic gap.
- Monitor new search terms and content mismatches.
- Prepare weekly growth/GEO reports.
- Give an AI agent enough context to recommend content priorities.

### Feature Mapping To Core

| Marketing Feature | Core Mapping |
|---|---|
| Website crawl | Connector, raw objects, page/paragraph entities |
| Google Search Console sync | Data stream, source events, query/page metric values |
| Google Ads sync | Data stream, campaign/ad/keyword entities, cost/conversion metrics |
| Ecommerce sales import | Data stream, product/order entities, revenue metrics |
| Keyword-page matching | Embeddings, semantic alignment analysis |
| Paid content gap | Metric-weighted gap analysis |
| Organic vs paid comparison | Cohort comparison, cluster overlap |
| Weekly marketing changes | Delta context packs, monitors |
| Report for marketing team | Report templates, insights, evidence |
| Agent asks about gaps | MCP prompt, context pack, semantic search, evidence |

### Core System Flow

```text
GSC/Ads/Ecommerce/Website
-> source events + raw objects
-> marketing entities and metric values
-> content chunks and embeddings
-> semantic alignment and gap analysis
-> insights with evidence
-> dashboard/report/MCP context pack
```

## VC Fund Intelligence

Detailed spec: [VC Fund Intelligence](vc-fund-intelligence.md)

### What The Module Does

VC Fund Intelligence maps dealflow, startups, founders, pitch decks, investor
memos, financial metrics, investment decisions, portfolio companies, rejected
companies, and fund theses.

It helps investors compare a new opportunity to everything the fund has already
seen.

The module can answer whether a new startup resembles:

- successful portfolio companies
- failed or weak portfolio companies
- companies the fund rejected
- a specific investment thesis
- a crowded market cluster
- a semantically novel opportunity

### Why Customers Need It

Investment teams accumulate knowledge in scattered places:

- pitch decks
- memos
- partner notes
- CRM records
- spreadsheets
- emails
- portfolio updates
- rejection reasons

Much of the most valuable knowledge is textual and historical. Humans remember
some of it, but not all. New analysts do not know every prior deal. Partners
may have seen similar companies years ago.

Customers need this module to avoid repeating old mistakes, find hidden
analogs, and make deal review more evidence-based.

### Tasks The Module Supports

- Compare a new startup to invested companies.
- Compare a new startup to rejected companies.
- Find nearest success/failure analogs.
- Detect thesis fit.
- Surface risk themes from prior memos.
- Discover market clusters in dealflow.
- Prepare investment committee context packs.
- Summarize how a deal differs from prior opportunities.
- Monitor new incoming startups and route them by similarity.

### Feature Mapping To Core

| VC Feature | Core Mapping |
|---|---|
| New startup intake | Connector/stream, source event, startup entity |
| Pitch deck import | Raw object, content units, chunks, embeddings |
| Investor memo import | Content units, evidence, restricted raw source |
| Portfolio/rejected cohorts | Entity properties, metric values, cohort definitions |
| Similar startup search | Vector search, nearest-neighbor analysis |
| Thesis fit | Semantic alignment to thesis entities |
| Risk theme comparison | Cluster analysis, cohort comparison |
| Investment context brief | Context pack, report template, MCP prompt |
| Dealflow monitoring | Stream status, monitors, alerts |

### Core System Flow

```text
Startup/deck/memo/metrics
-> source event + raw document
-> startup/founder/market/memo entities
-> embeddings and metrics
-> similarity to invested/rejected cohorts
-> risk and success pattern insights
-> investment context pack for agent or analyst
```

## Sales Intelligence

Detailed spec: [Sales Intelligence](sales-intelligence.md)

### What The Module Does

Sales Intelligence analyzes deals, accounts, calls, emails, meetings,
objections, proposals, competitors, and CRM outcomes.

It connects what sellers and buyers say to what happens commercially.

The module identifies the semantic patterns that separate:

- won deals from lost deals
- healthy opportunities from risky opportunities
- strong rep behavior from weak rep behavior
- successful objection handling from failed handling

### Why Customers Need It

Sales organizations have data, but it is hard to learn from it:

- CRM fields are often shallow.
- Calls and emails contain the real signal.
- Win/loss reasons are inconsistent.
- Sales managers cannot manually review all conversations.
- Reps need examples, not abstract advice.

Customers need this module to turn sales conversations into coaching, risk
signals, and repeatable winning patterns.

### Tasks The Module Supports

- Compare won and lost deals.
- Find risky active deals similar to past losses.
- Retrieve best calls for a specific objection.
- Explain why a deal was lost.
- Prepare rep coaching plans.
- Detect competitor mention patterns.
- Summarize account context before a meeting.
- Monitor pipeline drift.

### Feature Mapping To Core

| Sales Feature | Core Mapping |
|---|---|
| CRM import | Connector, deal/account/contact entities, metric values |
| Call transcript import | Raw object, content units, chunks, embeddings |
| Email import | Content units, relation to deal/account |
| Won/lost analysis | Cohort comparison, metric-aware semantic analysis |
| Objection clusters | Cluster detection over transcript segments |
| Best example retrieval | Semantic search and evidence packs |
| Active deal risk | Similarity to lost cohort, monitors |
| Rep coaching | Insights, reports, context packs |
| Agent sales assistant | MCP prompts, entity profiles, evidence retrieval |

### Core System Flow

```text
CRM + calls + emails
-> deals/accounts/reps/calls/entities
-> transcripts and notes embedded
-> won/lost cohort comparison
-> objection and risk insights
-> coaching report or agent context pack
```

## Customer Support Intelligence

Detailed spec: [Customer Support Intelligence](customer-support-intelligence.md)

### What The Module Does

Customer Support Intelligence analyzes support tickets, chats, emails, agent
replies, knowledge-base articles, product areas, escalations, CSAT, and churn
risk.

It turns customer conversations into product, support, and knowledge-base
insights.

### Why Customers Need It

Support data is one of the richest sources of product truth, but it is noisy:

- tags are inconsistent
- tickets repeat in different words
- new issues emerge gradually
- escalations are hard to explain
- knowledge-base gaps are invisible until volume grows
- product teams often receive anecdotes instead of evidence

Customers need this module to discover recurring problems, prioritize fixes,
and improve self-service content.

### Tasks The Module Supports

- Cluster recurring support issues.
- Detect growing ticket themes.
- Find knowledge-base gaps.
- Compare escalated vs resolved tickets.
- Retrieve similar resolved tickets.
- Summarize customer pain by product area.
- Identify churn-risk themes.
- Recommend KB article updates.
- Prepare product feedback reports.

### Feature Mapping To Core

| Support Feature | Core Mapping |
|---|---|
| Ticket connector | Source, source events, ticket/message entities |
| Chat/email messages | Content units, chunks, embeddings |
| Ticket metadata | Metric values and entity properties |
| Ticket clusters | Cluster analysis |
| KB gap detection | Semantic alignment between tickets and articles |
| Escalation analysis | Cohort comparison |
| Similar resolved tickets | Vector search, evidence |
| Product feedback report | Insights, report templates |
| New issue alert | Delta analysis, monitors |

### Core System Flow

```text
Tickets/chats/KB
-> ticket/message/article entities
-> message and article embeddings
-> clusters, gaps, escalation comparison
-> insights with ticket evidence
-> support dashboard, report, or MCP context pack
```

## Knowledge Base Intelligence

Detailed spec: [Knowledge Base Intelligence](knowledge-base-intelligence.md)

### What The Module Does

Knowledge Base Intelligence analyzes internal and external documentation:
documents, sections, paragraphs, owners, teams, products, policies, runbooks,
and topics.

It evaluates whether the knowledge base is complete, fresh, non-duplicative,
and ready for humans or AI agents.

### Why Customers Need It

Internal knowledge tends to decay:

- duplicate docs accumulate
- owners leave
- content becomes stale
- topics fragment across many docs
- important docs are hard to find
- AI agents retrieve outdated or incomplete context

Customers need this module before trusting agents with internal knowledge.

### Tasks The Module Supports

- Find duplicate or overlapping docs.
- Find stale important docs.
- Find missing docs based on tickets or queries.
- Detect fragmented topics.
- Identify orphan docs without owners.
- Score agent context readiness.
- Prepare cleaned context packs for AI agents.
- Recommend doc merges and updates.

### Feature Mapping To Core

| Knowledge Base Feature | Core Mapping |
|---|---|
| Docs import | Connectors, raw objects, document entities |
| Section parsing | Content units and chunks |
| Owner/team mapping | Entity relations |
| Duplicate docs | Near-duplicate analysis |
| Fragmented topics | Cluster analysis |
| Stale docs | Metric values, time-aware analysis |
| Missing docs | Gap analysis against tickets/queries |
| Agent readiness | Context pack quality checks |
| Internal agent context | MCP resources, context packs |

### Core System Flow

```text
Docs/wiki/repo
-> document/section/topic/owner entities
-> embeddings and freshness metrics
-> duplicate/stale/gap/readiness analysis
-> cleanup insights
-> agent-ready context packs
```

## Ecommerce Intelligence

Detailed spec: [Ecommerce Intelligence](ecommerce-intelligence.md)

### What The Module Does

Ecommerce Intelligence connects product catalog data, product pages, reviews,
orders, returns, search queries, ads, support tickets, and revenue.

It helps customers understand which products need better content, positioning,
support, or operational fixes.

### Why Customers Need It

Ecommerce businesses often optimize ads and product pages separately from
customer feedback and return reasons.

That creates blind spots:

- product descriptions do not address review concerns
- high-revenue products have weak content
- return reasons repeat but are not reflected on the page
- similar products cannibalize each other
- support issues reduce conversion or increase returns

Customers need this module to connect language, demand, and revenue.

### Tasks The Module Supports

- Find product pages with weak semantic coverage.
- Mine positive and negative review themes.
- Cluster return reasons.
- Detect product cannibalization.
- Match search demand to product pages.
- Prioritize product page improvements by revenue and margin.
- Connect support tickets to product issues.
- Monitor new review/return themes.

### Feature Mapping To Core

| Ecommerce Feature | Core Mapping |
|---|---|
| Product catalog import | Product/category entities |
| Orders import | Order entities, revenue metrics |
| Reviews import | Review content units, sentiment metrics |
| Returns import | Return entities, reason text |
| Product page crawl | Page/product relations, embeddings |
| Review theme mining | Cluster analysis |
| Return reason analysis | Cluster and cohort analysis |
| Product page gaps | Semantic alignment and gap analysis |
| Cannibalization | Similarity/duplicate analysis |
| Agent recommendations | MCP prompts, context packs, evidence |

### Core System Flow

```text
Products/orders/reviews/returns/pages
-> product/review/order entities and metrics
-> review/page/query embeddings
-> content gap, review, return, cannibalization analysis
-> prioritized product recommendations
```

## Product Event Intelligence

Detailed spec: [Product Event Intelligence](product-event-intelligence.md)

### What The Module Does

Product Event Intelligence analyzes application and website events, user
journeys, account behavior, sessions, feature adoption, trial conversion,
subscription outcomes, and lifecycle touchpoints.

It helps customers score current users or accounts based on how similar their
behavior is to historical converters, non-converters, churned customers, or
expanded customers.

Unlike pure web analytics, this module connects behavioral sequences to
entities, metrics, content, cohorts, explanations, and AI-agent workflows.

### Why Customers Need It

SaaS and product-led companies collect many events, but raw event dashboards
rarely explain what to do next.

Customers need this module because:

- trial users behave differently before they convert or abandon
- activation milestones are often unknown or assumed
- sales and customer success teams need prioritized accounts
- product teams need to understand drop-off patterns
- lifecycle marketers need event-based next best actions
- leaders need explainable conversion and churn signals

### Tasks The Module Supports

- Score trial accounts for upgrade likelihood.
- Explain why an account is likely or unlikely to upgrade.
- Compare current account behavior to converters and non-converters.
- Find activation milestones.
- Detect onboarding friction.
- Identify churn-risk behavior.
- Recommend next best actions.
- Create daily sales/CS priority lists.
- Monitor new behavioral patterns.
- Summarize account journeys before sales calls.

### Feature Mapping To Core

| Product Event Feature | Core Mapping |
|---|---|
| App/website event stream | Source events, data streams |
| User/account/session modeling | Entity types, relations |
| Event properties | Entity properties, metric dimensions |
| Event sequence summaries | Content units, derived artifacts, embeddings |
| Trial conversion outcome | Metric values, cohort definitions |
| Upgrade scoring | Cohort comparison, similarity, metric weighting |
| Activation discovery | Sequence pattern mining, analysis artifacts |
| Next best action | Insights, prompts, action tools |
| Account explanation | Context packs, evidence packs |
| Real-time monitoring | Monitors, delta context packs |

### Core System Flow

```text
App/website events + account data + subscription outcomes
-> source events and event entities
-> user/account/session/event relations
-> event sequence summaries and metrics
-> converter/non-converter cohort comparison
-> upgrade/churn/activation insights
-> dashboard, monitor, report, or MCP context pack
```

## Legal Contract Intelligence

Detailed spec: [Legal Contract Intelligence](legal-contract-intelligence.md)

### What The Module Does

Legal Contract Intelligence analyzes contracts, clauses, templates,
obligations, parties, vendors, customers, deals, jurisdictions, renewals, and
risk notes.

It compares legal language across a contract corpus and highlights unusual,
missing, risky, or important terms.

### Why Customers Need It

Legal and business teams often have many contracts but limited visibility into:

- non-standard clauses
- missing protections
- obligations hidden in text
- renewal and notice risks
- vendor/customer term differences
- template deviations

Customers need this module to review contracts faster and manage risk with
evidence.

### Tasks The Module Supports

- Compare a contract to a template.
- Find unusual clauses.
- Detect missing clauses.
- Summarize obligations.
- Find similar prior contracts.
- Compare terms across vendors/customers.
- Monitor renewals and notice periods.
- Prepare contract risk briefs.

### Feature Mapping To Core

| Legal Feature | Core Mapping |
|---|---|
| Contract import | Raw objects, contract entities |
| Clause extraction | Content units, chunks |
| Template library | Template/clause entities |
| Clause comparison | Embeddings, semantic similarity |
| Missing clauses | Gap analysis |
| Unusual clauses | Outlier detection |
| Obligation summaries | Structured extraction, insights |
| Renewal monitoring | Time-aware metrics, monitors |
| Restricted evidence | Security policies, audit logs |

### Core System Flow

```text
Contracts/templates/metadata
-> contract/clause/party/obligation entities
-> clause embeddings and risk metrics
-> deviation/missing/unusual clause analysis
-> contract risk insights with evidence
```

## HR And Talent Intelligence

Detailed spec: [HR/Talent Intelligence](hr-talent-intelligence.md)

### What The Module Does

HR and Talent Intelligence analyzes candidates, resumes, roles, interview
notes, employee feedback, performance reviews, engagement surveys, exit
interviews, teams, and outcomes.

It compares talent-related text to outcomes such as hiring decisions,
performance, engagement, tenure, and attrition.

### Why Customers Need It

People data is sensitive and fragmented:

- interview feedback is unstructured
- hiring rubrics are inconsistently applied
- engagement survey themes are hard to compare
- attrition signals are buried in text
- successful employee profiles are not reusable

Customers need this module to understand patterns while maintaining strict
governance and human oversight.

### Tasks The Module Supports

- Compare candidates to successful employee profiles.
- Summarize interview feedback.
- Detect inconsistent hiring feedback.
- Analyze engagement themes.
- Explain attrition patterns.
- Compare teams over time.
- Prepare candidate or role context packs.
- Identify onboarding and documentation gaps.

### Feature Mapping To Core

| HR Feature | Core Mapping |
|---|---|
| Candidate/resume import | Candidate/resume entities, raw objects |
| Interview notes | Content units, embeddings |
| Employee outcomes | Metric values, cohorts |
| Candidate similarity | Vector search and cohort comparison |
| Feedback themes | Cluster analysis |
| Attrition analysis | Cohort comparison and success/risk patterns |
| Engagement trends | Time-aware metrics, delta context |
| Sensitive access | RBAC, PII redaction, audit logs |

### Core System Flow

```text
Candidates/resumes/interviews/surveys/reviews
-> candidate/employee/team/role entities
-> text embeddings + outcome metrics
-> similarity, feedback, engagement, attrition analysis
-> governed context packs and reports
```

## Procurement And Vendor Intelligence

Detailed spec: [Procurement/Vendor Intelligence](procurement-vendor-intelligence.md)

### What The Module Does

Procurement and Vendor Intelligence analyzes vendors, contracts, proposals,
RFP/RFI responses, security reviews, spend records, services, issues, renewals,
and business owners.

It helps customers compare vendors, manage renewals, understand risk, and
connect spend to performance.

### Why Customers Need It

Procurement data is scattered across contracts, spreadsheets, questionnaires,
emails, support issues, and spend systems.

Customers need this module because:

- vendors overlap in capability
- renewals happen without full context
- security and contract risks are hard to compare
- spend is not connected to quality or issues
- RFP responses are difficult to evaluate consistently

### Tasks The Module Supports

- Compare vendors and proposals.
- Find duplicate vendor capabilities.
- Summarize vendor risk.
- Prepare renewal briefs.
- Connect spend to value and issues.
- Compare security questionnaire responses.
- Cluster vendor issue themes.
- Prioritize vendor reviews.

### Feature Mapping To Core

| Procurement Feature | Core Mapping |
|---|---|
| Vendor import | Vendor/service entities |
| Spend records | Metric values, dimensions |
| Proposal/RFP import | Raw objects, content units, embeddings |
| Security reviews | Content units, risk metrics |
| Vendor similarity | Vector search and clustering |
| Renewal risk | Time-aware metrics, monitors |
| Proposal comparison | Semantic comparison and reports |
| Vendor risk brief | Context packs, insights, evidence |

### Core System Flow

```text
Vendors/contracts/proposals/spend/issues
-> vendor/service/proposal entities and metrics
-> document embeddings
-> vendor similarity, risk, renewal, spend analysis
-> renewal briefs and agent context
```

## Compliance And Audit Intelligence

Detailed spec: [Compliance/Audit Intelligence](compliance-audit-intelligence.md)

### What The Module Does

Compliance and Audit Intelligence maps policies, controls, requirements,
evidence, incidents, findings, owners, systems, audits, and remediation work.

It checks whether the organization has the right evidence for the right
controls and whether audit readiness is improving or weakening.

### Why Customers Need It

Compliance work often involves matching large amounts of text:

- framework requirements
- internal policies
- controls
- screenshots or documents as evidence
- audit findings
- incident reports
- remediation notes

Manual mapping is slow and error-prone. Customers need this module to find
missing evidence, stale evidence, control gaps, and repeated incident themes.

### Tasks The Module Supports

- Map controls to evidence.
- Find missing evidence.
- Find stale evidence.
- Compare policies to requirements.
- Detect duplicate controls.
- Cluster incidents and findings.
- Prepare audit context packs.
- Summarize remediation status.

### Feature Mapping To Core

| Compliance Feature | Core Mapping |
|---|---|
| Control import | Control/requirement entities |
| Evidence import | Raw objects, evidence entities |
| Policy import | Content units and embeddings |
| Control-evidence mapping | Semantic alignment analysis |
| Missing evidence | Gap analysis |
| Stale evidence | Time-aware metrics |
| Incident clustering | Cluster analysis |
| Audit context pack | Context layer, MCP resources, evidence |
| Restricted exports | Security policies, audit logs |

### Core System Flow

```text
Policies/controls/evidence/incidents/findings
-> control/evidence/requirement entities
-> embeddings + status/freshness metrics
-> coverage, stale evidence, gap, incident analysis
-> audit-ready context packs and reports
```

## Cross-Module Feature Matrix

| Module | Main Core Strength Used | Most Important Business Output |
|---|---|---|
| Marketing | semantic alignment + metric weighting | content and campaign priorities |
| VC Fund | similarity + cohort comparison | investment context and analogs |
| Sales | outcome cohort comparison | win/loss patterns and deal risk |
| Support | clustering + gap detection | issue themes and KB gaps |
| Knowledge Base | duplicate/gap/staleness analysis | agent-ready knowledge cleanup |
| Ecommerce | review/search/product alignment | product page and revenue improvements |
| Product Events | event sequences + cohort scoring | trial upgrade and churn decisions |
| Legal | clause similarity + outlier detection | contract risk and obligation briefs |
| HR/Talent | sensitive cohort comparison | hiring/engagement/attrition insights |
| Procurement | vendor similarity + renewal monitoring | vendor risk and renewal decisions |
| Compliance | control-evidence alignment | audit readiness and evidence gaps |
