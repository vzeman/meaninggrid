# Sales Intelligence Module

## Purpose

Sales Intelligence compares deals, accounts, calls, emails, objections,
proposals, competitors, and CRM outcomes to explain why sales are won or lost.

The module answers:

```text
What patterns separate winning sales motions from losing ones?
```

## Target Users

- sales leaders
- sales operations
- account executives
- sales enablement teams
- revenue operations
- founders doing sales
- AI agents coaching sales teams

## Jobs To Be Done

- Compare won and lost deals.
- Find objection handling patterns.
- Retrieve best call examples.
- Detect deal risks based on similarity to lost deals.
- Identify rep coaching opportunities.
- Summarize account-specific context before a meeting.
- Compare email and call messaging against successful examples.
- Prepare win/loss reports.

## Connected Sources

Initial:

- CRM export
- call transcripts JSONL/CSV
- sales email export
- meeting notes

Later:

- Salesforce
- HubSpot
- Pipedrive
- Gong
- Chorus
- Aircall
- Outreach/Salesloft
- Google Calendar
- Gmail/Outlook

## Entity Types

```text
deal
account
contact
sales_rep
call
email
meeting
objection
competitor
proposal
stage
product
use_case
```

## Relations

```text
deal belongs_to account
deal owned_by sales_rep
deal involves contact
call belongs_to deal
email belongs_to deal
meeting belongs_to deal
objection detected_in call
proposal sent_for deal
competitor mentioned_in deal
deal uses product
```

## Metrics

```text
deal_value
stage
closed_won
sales_cycle_days
call_duration
reply_rate
meeting_count
discount
forecast_category
next_step_age
close_probability
```

## Content And Embeddings

Embed:

- call transcripts
- speaker turns
- objection segments
- emails
- CRM notes
- proposal text
- account descriptions
- competitor mentions
- next-step notes

## Core Analyses Used

- cohort comparison
- semantic search
- nearest-neighbor retrieval
- success pattern mining
- outlier detection
- temporal drift
- cluster detection

## Module-Specific Analyses

### Won Vs Lost Deal Comparison

Compares deal content and activity across outcomes.

### Objection Handling Analysis

Clusters objections and identifies successful responses.

### Deal Risk Similarity

Finds active deals similar to historically lost deals.

### Best Example Retrieval

Finds best calls/emails for a given objection, segment, or deal stage.

### Rep Coaching Analysis

Compares rep behavior to team success patterns.

### Stage Drift Detection

Detects deals whose recent communication no longer matches their CRM stage.

## Dashboards

- Sales overview
- Won/lost semantic differences
- Objection clusters
- Deal risk board
- Rep coaching view
- Best examples library
- Active deal context

## Reports

- Win/loss analysis
- Objection handling playbook
- Rep coaching report
- Pipeline risk report
- Account context brief

## Headless Agent Workflows

User asks:

```text
Which active deals look like deals we usually lose?
```

Agent:

1. Builds active pipeline context.
2. Finds similarity to lost-deal cohort.
3. Retrieves evidence from calls/emails.
4. Explains risk reasons and next actions.

## AI Agent Decision Support And Automation

AI agents should help sales teams decide what to do next in active deals and
learn from historical outcomes.

Decision support:

- recommend next best action for risky active deals
- explain why a deal resembles past lost deals
- identify which objection should be addressed next
- recommend the best proof point or case study for an account
- summarize account context before a meeting
- suggest questions for discovery calls
- identify whether a deal is in the wrong CRM stage
- recommend coaching focus areas for reps
- compare a rep's messaging to winning examples

Automation tasks:

- draft meeting prep briefs
- draft follow-up emails grounded in call evidence
- create deal risk summaries for pipeline reviews
- generate objection-handling playbook snippets
- classify call segments into discovery, demo, pricing, legal, or next steps
- monitor active deals for risk signals
- route coaching moments to managers
- populate CRM notes from transcripts with citations

Agent guardrails:

- agent should not send customer emails without approval
- agent should not update forecast or stage automatically unless configured
- coaching insights should be role-restricted
- agent should cite exact calls/emails behind recommendations

## MCP Prompts

```text
/compare_won_lost_deals
/explain_lost_deal
/find_best_call_examples
/prepare_rep_coaching_plan
/identify_deal_risks
/prepare_account_context
```

## Security Notes

- Sales emails and calls can contain customer confidential data.
- Raw transcripts should be permission controlled.
- Agent coaching outputs should avoid exposing sensitive HR conclusions unless authorized.

## MVP Scope

- CRM CSV import
- call transcript JSONL import
- won/lost cohort analysis
- objection clustering
- best-example retrieval
- sales MCP prompts

## Later Phases

- CRM API connectors
- call platform connectors
- real-time deal risk monitors
- rep coaching dashboards
- sequence/email analysis
