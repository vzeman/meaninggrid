# Product Event Intelligence Module

## Purpose

Product Event Intelligence analyzes behavioral events from applications,
websites, SaaS products, mobile apps, and product analytics tools.

The module helps teams understand user journeys, detect behavioral patterns,
score trial accounts, predict upgrades, identify churn risk, and explain which
actions are associated with successful conversion.

The module answers:

```text
Based on what this user or account is doing now, are they likely to convert,
expand, churn, or need intervention?
```

## Target Users

- SaaS founders
- growth teams
- product managers
- customer success teams
- product-led sales teams
- revenue operations
- lifecycle marketers
- AI agents monitoring trial accounts

## Jobs To Be Done

- Score trial accounts for upgrade likelihood.
- Compare current users to historical converters and non-converters.
- Identify product behaviors that predict paid conversion.
- Detect users who are stuck in onboarding.
- Find activation milestones.
- Explain why an account is likely or unlikely to upgrade.
- Recommend next best actions for lifecycle emails, sales outreach, or in-app prompts.
- Monitor behavioral changes across cohorts.
- Find event sequences that correlate with churn or expansion.
- Segment users by behavior, not only firmographics.

## Connected Sources

Initial:

- JSONL event stream
- Segment/RudderStack export
- product analytics CSV
- website analytics export
- SaaS account/user CSV
- subscription/payment CSV

Later:

- Segment
- RudderStack
- PostHog
- Mixpanel
- Amplitude
- Heap
- GA4
- Stripe
- Paddle
- Chargebee
- HubSpot/Salesforce
- Intercom/customer success tools
- application database CDC
- Kafka/Kinesis/PubSub event streams

## Entity Types

```text
account
user
session
event
event_sequence
feature
page
screen
trial
subscription
plan
workspace
organization
campaign
email
in_app_message
support_ticket
conversion_goal
```

## Relations

```text
user belongs_to account
session belongs_to user
event belongs_to session
event performed_by user
event occurs_in account
event uses feature
event views page
trial belongs_to account
subscription belongs_to account
account has_plan plan
email sent_to user
support_ticket opened_by user
conversion_goal achieved_by account
```

## Metrics

```text
trial_started
trial_age_days
activated
converted_to_paid
upgrade_probability
churn_probability
expansion_probability
feature_adoption_count
active_days
sessions_count
events_count
time_to_value_minutes
onboarding_completion
invited_users_count
integration_connected
payment_added
support_tickets_count
email_opens
email_clicks
revenue
mrr
plan_value
```

Metric dimensions:

```text
date
account
user
plan
source
campaign
channel
feature
event_name
country
device
industry
company_size
```

## Content And Embeddings

This module uses both structured events and text.

Embed:

- event names and descriptions
- feature descriptions
- page/screen names and metadata
- event sequence summaries
- session summaries
- support tickets linked to trial accounts
- onboarding emails and in-app messages
- account notes
- user feedback

For raw behavior, the system should create textual summaries of sequences, for
example:

```text
User created workspace, invited two teammates, connected HubSpot integration,
viewed pricing page twice, exported report, then opened support ticket about API limits.
```

These sequence summaries can be embedded and compared semantically.

## Event Push Format

Simple event JSONL:

```json
{
  "type": "event.track",
  "event_name": "integration_connected",
  "external_id": "evt_123",
  "user_id": "usr_1",
  "account_id": "acct_1",
  "occurred_at": "2026-05-08T10:15:00Z",
  "properties": {
    "integration": "hubspot",
    "source": "onboarding"
  },
  "labels": {
    "module": "product_event",
    "environment": "production"
  }
}
```

Account update:

```json
{
  "type": "entity.upsert",
  "entity_type": "account",
  "external_id": "acct_1",
  "label": "ACME Trial Account",
  "properties": {
    "plan": "trial",
    "industry": "fintech",
    "company_size": "51-200",
    "source": "google_ads"
  },
  "labels": {
    "module": "product_event",
    "lifecycle_stage": "trial"
  }
}
```

Conversion metric:

```json
{
  "type": "metric.observe",
  "entity_ref": {
    "entity_type": "account",
    "external_id": "acct_1"
  },
  "metric": "converted_to_paid",
  "value": true,
  "value_type": "boolean",
  "observed_at": "2026-05-15T00:00:00Z"
}
```

## Core Analyses Used

- cohort comparison
- nearest-neighbor similarity
- metric-weighted pattern mining
- temporal/windowed analysis
- sequence clustering
- outlier detection
- semantic search
- time-aware monitors
- delta context packs

## Module-Specific Analyses

### Trial Upgrade Scoring

Scores a trial account based on similarity to previous upgraded and
non-upgraded accounts.

Signals:

- event sequence similarity
- activation milestone completion
- feature adoption
- account firmographics
- support interactions
- pricing page visits
- team invitations
- integration setup
- time-to-value
- lifecycle email engagement

Output:

- upgrade probability
- confidence
- nearest upgraded analogs
- nearest non-upgraded analogs
- positive signals
- negative signals
- recommended next action

### Activation Milestone Discovery

Finds event patterns that often happen before conversion.

Examples:

- created project + invited teammate + exported report
- connected integration + created automation + returned next day
- uploaded data + viewed dashboard + shared report

### Non-Converter Pattern Analysis

Finds common behaviors of users who never paid.

Examples:

- created account but never imported data
- viewed docs repeatedly but never connected integration
- used feature once and never returned
- hit usage limit without contacting support

### Next Best Action

Recommends actions based on current journey state.

Examples:

- send onboarding email
- trigger in-app prompt
- assign sales outreach
- offer setup call
- recommend documentation
- escalate to customer success

### Journey Cluster Analysis

Clusters accounts by behavior sequences, not only attributes.

### Churn And Expansion Pattern Analysis

For paid accounts, compares behavior to churned, retained, and expanded
accounts.

### Feature Adoption Impact

Finds which features or event sequences correlate with conversion, retention,
or expansion.

## Dashboards

- Trial account scoring
- Account journey timeline
- Activation milestones
- Converter vs non-converter behavior
- At-risk accounts
- Feature adoption impact
- Journey clusters
- Next best actions
- Recent behavioral changes

## Reports

- Trial conversion report
- Activation milestone report
- Non-converter analysis
- Product-led sales priority report
- Churn-risk behavior report
- Feature adoption report

## Headless Agent Workflows

### Trial Account Scoring

User asks:

```text
Which trial accounts are most likely to upgrade this week, and why?
```

Agent:

1. Lists active trial accounts.
2. Builds a context pack for current trial behavior.
3. Scores accounts against upgraded and non-upgraded cohorts.
4. Retrieves nearest analogs and key events.
5. Recommends next actions for sales or lifecycle marketing.

### Account Explanation

User asks:

```text
Is ACME likely to upgrade? What should we do next?
```

Agent:

1. Gets ACME account profile.
2. Reads event sequence summary.
3. Compares to converters/non-converters.
4. Explains positive and negative signals.
5. Recommends next best action.

### Activation Discovery

User asks:

```text
What behaviors are most predictive of paid conversion?
```

Agent:

1. Compares converted vs non-converted cohorts.
2. Finds enriched event sequences.
3. Summarizes activation milestones.
4. Suggests product onboarding improvements.

## AI Agent Decision Support And Automation

AI agents should help product-led teams decide who needs attention, what action
to take, and which product behaviors matter.

Decision support:

- prioritize trial accounts for sales outreach
- explain why an account is likely or unlikely to convert
- recommend the next best lifecycle action
- identify users stuck in onboarding
- suggest product changes that improve activation
- recommend which events should become activation milestones
- identify accounts at risk of churn
- explain expansion opportunities based on feature adoption
- compare current product behavior to historical successful journeys

Automation tasks:

- generate daily trial-priority lists
- create sales/CS tasks for high-potential accounts
- draft personalized outreach based on product behavior
- trigger lifecycle email or in-app message recommendations
- summarize account journey before a sales call
- monitor trial accounts for conversion signals
- classify new accounts into journey clusters
- create product backlog items from drop-off patterns
- produce weekly product-led growth reports
- notify teams when a high-value account becomes stuck

Agent guardrails:

- agent should not contact customers automatically without approval unless policy allows it
- scoring should include evidence and nearest analogs, not only a number
- users should know whether score is heuristic, model-based, or rule-based
- sensitive account/customer data should follow workspace permissions
- automated recommendations should avoid discriminatory or protected attributes

## MCP Prompts

```text
/score_trial_accounts
/explain_account_upgrade_likelihood
/find_activation_milestones
/compare_converters_and_non_converters
/recommend_next_best_action
/summarize_account_journey
/find_churn_risk_patterns
/prepare_product_led_growth_report
```

## Feature Mapping To Core

| Product Event Feature | Core Mapping |
|---|---|
| Event ingestion | Source events, data streams, raw objects |
| User/account modeling | Entity types and relations |
| Event sequence summaries | Content units, derived artifacts |
| Trial conversion labels | Metric values and cohorts |
| Upgrade scoring | Cohort comparison, similarity, metric weighting |
| Activation discovery | Sequence pattern mining, analysis artifacts |
| Next best action | Insights, prompts, action tools |
| Account journey explanation | Context packs, evidence packs |
| Real-time monitoring | Streams, monitors, delta context packs |
| Agent workflow | MCP prompts, semantic search, filtered retrieval |

## Core System Flow

```text
App/website events + account data + subscription outcomes
-> source events and event entities
-> user/account/session/event relations
-> event sequence summaries and metrics
-> converter/non-converter cohort comparison
-> upgrade/churn/activation insights
-> dashboard, monitor, report, or MCP context pack
```

## Security Notes

- Behavioral data can be sensitive.
- Customer/account identifiers should be protected.
- Do not use protected personal attributes for scoring.
- Scores should be explainable and auditable.
- Agent-created tasks or outreach should be permission controlled.
- Customers may need data retention controls for event logs.

## MVP Scope

- JSONL event push
- account/user/session/event schema
- trial conversion metric
- converted vs non-converted cohort analysis
- event sequence summaries
- trial upgrade scoring heuristic
- account journey context pack
- MCP prompts for scoring and explanation

## Later Phases

- Segment/RudderStack/PostHog/Mixpanel connectors
- real-time event stream adapters
- sequence models
- causal analysis experiments
- lifecycle automation integrations
- product analytics dashboards
- churn and expansion scoring
- A/B experiment context integration

