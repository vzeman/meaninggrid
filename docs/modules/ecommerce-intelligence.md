# Ecommerce Intelligence Module

## Purpose

Ecommerce Intelligence connects product catalog data, product pages, reviews,
search queries, ads, orders, returns, support tickets, and revenue.

The module answers:

```text
Which products need better content, positioning, or operational fixes?
```

## Target Users

- ecommerce managers
- merchandising teams
- product marketers
- performance marketers
- support/product teams
- agencies

## Jobs To Be Done

- Find high-revenue products with weak content.
- Compare review themes to product descriptions.
- Identify return reason clusters.
- Detect product cannibalization.
- Match search demand to product pages.
- Find support issues affecting revenue.
- Prioritize product page updates.
- Monitor new review themes.

## Connected Sources

Initial:

- product catalog CSV
- orders CSV/JSONL
- reviews CSV/JSONL
- website/product page crawl
- ads/search exports

Later:

- Shopify
- WooCommerce
- Magento
- BigCommerce
- review platforms
- Google Merchant Center
- ads APIs
- support tools

## Entity Types

```text
product
variant
category
collection
review
order
return
customer_segment
campaign
search_query
product_page
support_ticket
competitor_product
```

## Relations

```text
product belongs_to category
variant belongs_to product
review describes product
order contains product
return relates_to product
product_page describes product
search_query lands_on product_page
campaign promotes product
support_ticket concerns product
competitor_product competes_with product
```

## Metrics

```text
sales
revenue
margin
conversion_rate
return_rate
review_rating
inventory
ad_cost
roas
support_volume
refund_amount
stockout_days
```

## Content And Embeddings

Embed:

- product titles
- product descriptions
- product page body
- reviews
- return reasons
- search queries
- ad copy
- support tickets
- competitor product descriptions

## Core Analyses Used

- semantic alignment
- cluster detection
- gap detection
- cohort comparison
- outlier detection
- duplicate/cannibalization detection
- metric-weighted prioritization

## Module-Specific Analyses

### Product Content Coverage

Compares product page content to search demand, reviews, and support issues.

### Review Theme Mining

Finds positive and negative themes in reviews.

### Return Reason Clustering

Clusters return reasons and links them to product content gaps.

### High Revenue Weak Content

Finds products with strong sales but weak descriptions or support content.

### Product Cannibalization

Finds semantically similar products competing for the same queries.

### Support Impact On Revenue

Connects support ticket clusters to product revenue and return rates.

## Dashboards

- Ecommerce overview
- Product content gaps
- Review themes
- Return reason clusters
- Product cannibalization
- Search demand coverage
- Support impact

## Reports

- Product page priority report
- Review insights report
- Return reduction report
- Search/product content gap report

## Headless Agent Workflows

User asks:

```text
Which product pages should we improve first?
```

Agent:

1. Compares revenue, margin, search demand, reviews, and content quality.
2. Finds semantic gaps.
3. Retrieves review/support evidence.
4. Produces prioritized page updates.

## AI Agent Decision Support And Automation

AI agents should help ecommerce teams decide which products, pages, reviews,
and operational issues deserve attention first.

Decision support:

- prioritize product page updates by revenue, margin, search demand, and content gap
- recommend changes to product descriptions based on reviews and return reasons
- identify products likely to cannibalize each other
- explain why a product has high returns or poor reviews
- recommend which products need comparison guides, FAQs, or support content
- identify review themes that should influence merchandising
- recommend which ad/search terms should map to which product pages

Automation tasks:

- draft product page improvement briefs
- draft FAQ sections from support and review themes
- classify return reasons into actionable clusters
- generate weekly product-content priority reports
- monitor new negative review themes
- route product issues to merchandising, support, or operations
- draft comparison tables for similar products
- create content tasks for high-revenue weak-content products

Agent guardrails:

- agent should not change prices, inventory, or live product pages without approval
- revenue and margin visibility should be permission-controlled
- customer PII from orders/reviews should be redacted
- generated product claims should be checked against source evidence

## MCP Prompts

```text
/analyze_product_content_gaps
/explain_return_patterns
/find_review_themes
/recommend_product_page_updates
/detect_product_cannibalization
```

## Security Notes

- Order data can include PII.
- Customer-level data should be aggregated or redacted by default.
- Revenue/margin metrics need role-based access.

## MVP Scope

- product/orders/reviews CSV import
- product page crawl
- review theme clustering
- product content gap analysis
- ecommerce MCP prompts

## Later Phases

- Shopify/WooCommerce connectors
- return analytics
- inventory-aware recommendations
- competitor product monitoring
- automated content briefs
