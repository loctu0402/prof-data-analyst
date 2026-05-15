# Planning Protocol — From Business Understanding to Data-Ready Plan

> Loaded from `da-frame` mode. Covers the FRONT of the DA workflow: business understanding → metric define → data planning (TH1 vs TH2 split). Before any SQL or EDA, finish this protocol.

## Overview — Why this file exists

A DA project that skips planning lands in 1 of 3 traps:
1. **Wrong metric** — analyst computes X, stakeholder wanted Y (waste 1-2 weeks)
2. **Missing data** — analyst assumes table exists, finds out 4 days in it doesn't (block + scope renegotiation)
3. **Over-scoped model** — analyst builds 5-stage pipeline when stakeholder just needed 1 query

This protocol forces 4 gates BEFORE data work: Business Understanding → Metric Define → Data Plan → Data Model (TH1 or TH2). Each gate has a user-confirm checkpoint. If you skip a gate, downstream rework cost is 5-10×.

**Why (Operational):** the upstream cost of planning is hours; the downstream cost of skipping is days. Industry-standard frameworks (CRISP-DM, Kimball, dbt) all anchor planning before data; this protocol packages them as a checklist.

---

## Gate 1 — Business Understanding (15-30 min)

### Goal
Translate "stakeholder wants X" into a structured problem statement with success criteria.

### Phase 1.1 — Capture the ask
Ask the user (or extract from brief):
- **What's the business question?** (1 sentence; no jargon)
- **Who's the decision-maker?** (PO / manager / C-level / external?)
- **What decision will be made from this?** ("Do we launch X?" / "Should we scale Y?" / "Why is Z happening?")
- **What's the deadline?** (now / EOW / EOM / quarterly)
- **What's the cost ceiling?** (free / dev tokens / $X cloud / production credits)

If user can't answer ≥3 of these → STOP. Surface as: "Tôi cần thêm context để frame đúng. Cho tôi 5 phút clarify."

### Phase 1.2 — Reformulate as 5W1H
| Field | Captured value |
|-------|---------------|
| **What** | The deliverable (report / dashboard / pipeline / model) |
| **Why** | The business outcome it informs |
| **Who** | Decision-maker + reader audience |
| **When** | Deadline + frequency (one-off / daily / monthly) |
| **Where** | Where the output lives (Slack / email / dashboard URL / notebook) |
| **How** | Initial guess at method (descriptive / diagnostic / predictive / prescriptive) |

### Phase 1.3 — Constraint mapping
- **Stake**: low (exploratory) / medium (recurring report) / high (executive decision)
- **Stakeholder technical level**: non-technical / data-literate / data-fluent → drives explanation depth
- **Reversibility**: one-shot decision (high stake) / iterative tweaks (low stake)

### Gate 1 exit criteria
- 5W1H table filled
- Stake + technical level + reversibility mapped
- User confirms: "Đúng, đây là gì tôi cần"

---

## Gate 2 — Metric Define (20-45 min)

### Goal
Translate business question → measurable metric(s). Single source of truth.

### Phase 2.1 — Pick metric framework
Match question type to framework (full detail: `metric-framework.md`):

| Question type | Framework |
|---------------|-----------|
| "Are we winning?" | North Star Metric (1 primary KPI for product) |
| "What's the most important thing now?" | OMTM (One Metric That Matters — phase-specific) |
| "Is our growth flywheel working?" | Growth Loop (input → action → output → reinvest) |
| "How is THIS feature performing?" | HEART (Happiness / Engagement / Adoption / Retention / Task Success) |
| "What broke?" | Diagnostic ladder (Funnel / Cohort / Driver decomposition) |

### Phase 2.2 — Define each metric

Per metric, fill the contract:

```markdown
**Metric Name:** <e.g., MAU SOF>
**Definition:** <1-sentence plain language>
**Formula:** <SQL-style pseudocode>
**Grain:** <1 row = ? × ? × ?>
**Filter logic:** <inclusion/exclusion rules>
**Source table(s):** <table_name @ grain>
**Owner (business):** <name / role>
**Owner (data):** <name / role>
**Use case:** <where this metric appears>
**Anti-confusion notes:** <e.g., MAU SOF ≠ MAU; SOF requires successful payment>
```

### Phase 2.3 — Sanity-check
- **Single source rule**: 1 metric = 1 definition. If team disagrees on definition, escalate now (cheaper than rework after dashboard ships).
- **Activity vs Value distinction**: distinguish "user did X" (activity) from "user generated Y value" (value). Don't conflate.
- **Comparability test**: is there a baseline to compare against? (7d avg / DoD / vs cohort / vs control)

### Gate 2 exit criteria
- Metric contract(s) drafted
- Single source confirmed (or escalated)
- User signs off on definition (verbal "OK" enough at low stake; written sign-off at high stake)

---

## Gate 3 — Data Plan (TH1 vs TH2 split)

After metrics are defined, plan the data needed. Two paths based on data availability:

### TH1 — Data exists & sufficient

Use when: schema is known, tables are reachable, data is fresh.

**Phase 3.1 — Field-by-field requirement**
For each metric, list:
```
Metric → Required fields → Source table → Grain → Refresh frequency → SLA
```

**Phase 3.2 — Schema verification**
- Run `INFORMATION_SCHEMA.COLUMNS` query (or equivalent) on each source table
- Confirm field names + types match expectation
- Check partition column + range (last 30d? last 90d? full history?)
- Verify SLA: when does this data refresh? T-1? T-2? T+0?

**Phase 3.3 — Sample query (smallest-cost validation)**
- Pull 7d of data with hard partition filter
- Verify row count makes sense
- Verify metric formula works on the sample
- Cost ceiling: $0.10 per validation query

**Phase 3.4 — Logic sketch**
List the calculation steps (NOT full SQL — just the logical flow):
```
1. Filter source by date range + segment
2. Compute per-user metric for each day
3. Aggregate to grain (daily / monthly / cohort)
4. Join to dim_user for demographic split
5. Output: dataset for analysis / mart for dashboard
```

### TH2 — Data missing / no source yet

Use when: stakeholder asks new question + no existing table covers it. Pre-modeling.

**Phase 3.1 — Brainstorm data resources**
Ask:
- What event triggers the data we'd need? (transaction / click / login / state change)
- Where could this event currently log? (existing event stream / new tracking / inferred from related event)
- Is this a one-off (build for this project) or recurring (build into platform)?

**Phase 3.2 — Discovery protocol** (full detail: `domain-discovery-protocol.md`)
1. Check registry: does `lt-memory/domains/<X>/` exist? → reuse
2. Schema scan: `INFORMATION_SCHEMA.TABLES` filter by likely keywords; cost < $0.01
3. Partition-safe sample: top 100 rows of 1 candidate table; cost < $0.10
4. User approval gate: "Found N candidate tables. Volume + cost estimate: $X. Proceed?"
5. Generate L1/L2/L3 hub if domain is new

**Phase 3.3 — Data modeling sketch**

If data needs to be MODELED (i.e., we need to design new tables), use one of these patterns:

| Pattern | When to use | Detail |
|---------|-------------|--------|
| **Kimball Star/Snowflake** | OLAP analysis; dim + fact tables; classic DWH | Industry standard; reusable dims |
| **dbt staging → marts** | dbt project; modular SQL transformations | `stg_/int_/fct_/dim_` convention |
| **Bronze/Silver/Gold** (Medallion) | Lakehouse; multi-stage ELT | Bronze=raw CDC, Silver=cleaned, Gold=mart |
| **DuckDB layered tables** | Local file-based; CSV/Excel input | `raw_/stg_/clean_/mart_/ml_` in 1 file |

**Choose ONE based on infrastructure:**
- Have cloud DWH (BQ / Snowflake / Redshift) → Kimball or dbt
- Have lakehouse (Databricks / Delta) → Medallion
- Local file input only → DuckDB layered
- Mixed → start DuckDB; promote to dbt when scaling

**Phase 3.4 — Pipeline sketch**
End-to-end flow per chosen pattern:
```
Source(s) → Ingest layer → Stage layer → Mart layer → Output (dashboard / report / API)
```
For each layer:
- Frequency (daily / hourly / on-demand)
- Idempotent? (re-run safe?)
- Backfill strategy
- Test/validation step

### Gate 3 exit criteria
- **TH1**: schema verified + sample query passes + logic sketch written
- **TH2**: data modeling pattern chosen + pipeline sketch + user approval on resource commitment
- Document goes into project folder (NOT scratched on paper)

---

## Gate 4 — Lock & Hand Off to Execution

### Phase 4.1 — Pre-flight checklist
- [ ] 5W1H from Gate 1 still accurate (no scope drift)
- [ ] Metric contracts from Gate 2 stable (no last-minute redefinition)
- [ ] Data plan from Gate 3 verified (schema confirmed OR modeling pattern chosen)
- [ ] Cost ceiling reaffirmed
- [ ] Deadline still met by current plan
- [ ] No blocking unknowns

### Phase 4.2 — Hand-off doc
Write a 1-page hand-off (`<project>/PLANNING.md`):
```markdown
# Planning — <Project Name>
**Date:** <YYYY-MM-DD>  
**Owner:** <name>  
**Status:** Locked / In-progress / Blocked

## Business Question
<1 sentence>

## 5W1H
<table>

## Metrics
<contracts>

## Data Plan
<TH1 schema verification OR TH2 modeling pattern + pipeline sketch>

## Next Mode
<da-query / da-process / da-model / da-automate>
```

### Phase 4.3 — Route to next mode
Per the next-mode field:
- Schema + SQL known → `/da-query`
- Need to wrangle/EDA → `/da-process`
- Need to build new pipeline → `/da-model` (modeling) → `/da-automate` (scheduling)
- Hypothesis already framed → `/da-insight`

---

## Anti-patterns to catch

| Anti-pattern | Symptom | Fix |
|--------------|---------|-----|
| **Skip Gate 1, jump to SQL** | "Let me just pull the data and we'll figure it out" | Stop. 30 min planning saves days. |
| **Compute metric without contract** | "MAU dropped 15%" with no agreement on MAU def | Lock Gate 2 contract before Gate 3 |
| **Assume data exists** | 3 days into project, "Oh, no table tracks that" | Gate 3 TH1 schema verification is mandatory |
| **Skip cost gate in TH2** | Run full table scan, $50 charged before checking | Cost ceiling enforced at every probe |
| **Over-model TH2** | Build 5-layer pipeline for 1-shot question | Start with smallest viable; promote only if recurring |
| **No hand-off doc** | Re-explain plan to next session / next teammate | `PLANNING.md` is mandatory output of Gate 4 |

---

## Cross-references
- Mode entry: `mode-frame.md` (Phase routing)
- Metric framework details: `metric-framework.md`
- Data modeling deep dive: `mode-model.md`
- Schema discovery cost ceilings: `domain-discovery-protocol.md`
- Why this protocol matters: `universal-workflow-rules.md` Rule 3 (5W1H Action Brief)

— part of prof-data-analyst · Loc Tu, 2026
