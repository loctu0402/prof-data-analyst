# Data Governance — Practical 6-Section Framework

> Generic framework portable across companies. Use this after `mode-model.md` ships a pipeline. Source: `data_governance_practical_approaches_interview_ready_examples.md`.

## Overview — Why this file exists

After building a pipeline, you ship → data starts flowing → 2 weeks later: someone disagrees on a metric definition, a dashboard shows wrong numbers, sensitive PII appears in a report, downstream tables silently drift.

Without governance, every ship → 1-2 weeks rework. WITH governance, the rework is caught BEFORE the bad data hits decisions.

**Why (Empirical):** governance is enabling, not gatekeeping. Reference framing: *"Good data governance makes the right thing the easy thing."* Track this with 6 sections; each section has practical implementation patterns + STAR examples for interviews.

## 6 Sections (decision-table summary)

| # | Section | Goal | Top-3 Implementations |
|---|---------|------|------------------------|
| 1 | **Metric & Definition** | Everyone speaks same data language | Metric Dictionary + Canonical Metrics + Versioning |
| 2 | **Data Modeling & Grain** | Prevent double-counting + misleading aggregations | Explicit Grain + Naming Convention (fct/dim/agg) + Fact-Dim Separation |
| 3 | **Data Quality & Validation** | Build trust so data is actually used | Schema tests + Business logic tests + Cross-table reconciliation |
| 4 | **Access Control & Privacy** | Enable use without violating regulation | Masking + RBAC + Row-Level Security + Audit trail |
| 5 | **Reporting & Consumption** | Decision-makers trust what they see | Certified Dashboards + Reuse-First + Embedded Metric Docs |
| 6 | **Mindset** | Governance = enablement at scale | Reframe from "control" to "trust at scale" |

---

## Section 1 — Metric & Definition Governance

### Common Problems
- Same metric, different definitions across teams
- Conflicting dashboards → loss of trust → stop using data

### Practical Implementation

| Component | What It Is |
|-----------|------------|
| **Metric Dictionary** | Per metric: name + formula + grain + owner + use case |
| **Canonical Metrics** | ONE official source per metric. Other dashboards reference it, not redefine. |
| **Ownership** | 2 owners per metric: Data Owner (table) + Business Owner (definition) |
| **Change Control** | Versioning + announcement when definition changes (mandatory) |

### Implementation pattern
```markdown
## Metric: MAU SOF
**Definition:** Users who completed ≥1 successful payment using SOF in the month
**Formula:** COUNT(DISTINCT user_id) WHERE sof_payment_success = TRUE GROUP BY month
**Grain:** 1 row = 1 user × 1 month
**Source:** mart_sof_monthly
**Data Owner:** @data-team
**Business Owner:** @product-payment
**Use Case:** Monthly product review dashboard
**Version:** v2.1 (2026-04-01: excluded test accounts)
**Anti-confusion:** Different from MAU (which includes all activity); SOF requires payment.
```

### Anti-pattern catch
- 2 dashboards show "MAU" with different numbers → STOP. Reconcile definition before either ships.
- New metric added without owner → returns to draft.

---

## Section 2 — Data Modeling & Grain Governance

### Common Problems
- Double counting due to grain mismatch
- Inconsistent joins between fact tables → wrong aggregations
- Schema drift between dev / staging / production

### Practical Implementation

| Rule | Concrete Form |
|------|---------------|
| **Explicit Grain** | Every table doc says: 1 row = X × Y × Z |
| **Enforced Grain** | No implicit aggregation downstream (e.g., no `SELECT user_id FROM events` without `DISTINCT` when needing user count) |
| **Fact–Dim Separation** | Events, users, sessions modeled separately; not flattened into a wide single table |
| **Naming Convention** | Prefixes: `fct_` for facts, `dim_` for dimensions, `agg_` for aggregates, `stg_` for staging, `int_` for intermediate |
| **Test Grain on Build** | Test asserts row count matches expected grain (e.g., `unique` on PK) |

### Grain check protocol (dbt test example)
```yaml
- name: fct_orders
  description: "1 row = 1 order"
  tests:
    - unique: [order_id]
    - not_null: [order_id, user_id, order_date]
```

If row count of fct_orders > unique(order_id) → grain broken → BLOCKER.

---

## Section 3 — Data Quality & Validation Governance (Most Critical)

### Core Validation Principles (AE mindset)

| Principle | Practical Meaning |
|-----------|-------------------|
| **Fail Fast** | Stop downstream models when data is invalid (don't pollute) |
| **Shift Left** | Validate as close to raw data as possible (cheaper to fix upstream) |
| **Automate by Default** | No manual QA for recurring pipelines |
| **Business-Aware** | Validation reflects business logic, not just schema |

### 5 Validation Layers

#### 3.1 Schema & Structural Validation
| Check | Example |
|-------|---------|
| Not Null | `user_id`, `event_time` not null |
| Uniqueness | Primary key uniqueness per grain |
| Accepted Values | `event_name` ∈ predefined enum |
| Data Type | Timestamp, numeric ranges |

#### 3.2 Freshness & Completeness
| Check | Example |
|-------|---------|
| Freshness SLA | Data delay < 2 hours |
| Volume Completeness | Daily events ≥ historical P25 |
| Partition Coverage | No missing date partitions |

#### 3.3 Business Logic Validation
| Rule | Example |
|------|---------|
| Funnel Consistency | `checkout_complete` ≤ `checkout_start` |
| Temporal Order | `session_end_time` ≥ `session_start_time` |
| Threshold Rules | Conversion rate within expected bounds |

#### 3.4 Distribution & Anomaly Detection
| Method | Example |
|--------|---------|
| Statistical Bounds | Z-score, IQR-based checks |
| Percentile Drift | P50 duration shifts > X% |
| Ratio Monitoring | Paid vs organic traffic ratio |

#### 3.5 Cross-Table Reconciliation
| Type | Example |
|------|---------|
| Raw vs Modeled | Fact count ≈ raw events |
| Aggregate vs Detail | Sum(detail) = aggregate |
| Source Parity | BI dashboard = certified mart |

### Automation Pattern

| Stage | Action |
|-------|--------|
| **Pre-Transform** | Validate raw ingestion |
| **Transform** | Apply schema & logic tests |
| **Post-Transform** | Reconcile aggregates |
| **Alerting** | Slack / Email on failure |

Validation failures BLOCK downstream dependencies. Don't ship broken data.

### dbt test integration
If using dbt, validation = `tests/` folder with both schema tests (yml) + singular tests (sql). Run `dbt test` after every `dbt build`. Failures block production deploy.

---

## Section 4 — Access Control & Privacy Governance

### Common Problems
- PII exposure in dashboards
- Uncontrolled sharing of sensitive reports
- No audit trail of who accessed what

### Practical Implementation

| Level | Controls |
|-------|----------|
| **Dataset** | Masking / hashing sensitive fields (email, phone, SSN) |
| **Role-Based Access** | Viewer, editor, admin roles |
| **Row-Level Security** | Access scoped by team, region, function |
| **Audit Trail** | Track who accessed what + when |

### Interview framing
*"Good governance protects privacy without slowing down teams."*

Practical: don't put raw PII in the analyst layer. Mask/hash at staging. Only ops/security teams see raw.

---

## Section 5 — Reporting & Consumption Governance

### Common Problems
- Duplicate dashboards (3 versions of "Revenue Dashboard")
- No clarity on which report is the source of truth
- Stakeholders trust the wrong one

### Practical Implementation

| Rule | Implementation |
|------|----------------|
| **Certified Dashboards** | Labeled "trusted" — owner + last review date visible |
| **Report Lifecycle** | States: Active, Deprecated, Retired |
| **Reuse-First Policy** | Encourage reuse over duplication ("does an existing dashboard answer this?") |
| **Embedded Documentation** | Metric definitions visible inside BI tool (tooltip / sidebar) |

### Anti-pattern catch
- New dashboard request → check existing first; require justification for new one
- Old dashboard not reviewed in 6 months → mark Deprecated; require active maintenance

---

## Section 6 — Governance Mindset (Critical for Senior Roles)

### Incorrect Mindset
- Governance = control + approval gates + slow-down
- Result: teams bypass governance; data quality drops

### Correct Mindset
- Governance = enablement with trust at scale
- Result: teams pull governance into their workflow because it makes their life easier

### Strong One-Liners
- *"Good data governance makes the right thing the easy thing."*
- *"Governance is not about restriction, it's about reliability."*
- *"Dashboards are not sources of truth; governed datasets are."*

---

## STAR Example (Ready for Interview)

| Field | Content |
|-------|---------|
| **Situation** | Metric discrepancies across teams caused conflicting decisions |
| **Task** | Establish trusted reporting foundation |
| **Action** | Defined canonical metrics + enforced grain + automated quality tests + certified dashboards |
| **Result** | Reduced rework ~50% + increased adoption + faster decisions at senior levels |

---

## Implementation Checklist (Pick 5 to start)

When governance setup is new, don't try all 30 implementations at once. Start with:

- [ ] **Metric Dictionary** for top 5 most-used metrics (Section 1)
- [ ] **Naming Convention** enforced on all new tables (`stg_`, `int_`, `fct_`, `dim_`, `agg_`) (Section 2)
- [ ] **Schema tests** on all `fct_*` and `dim_*` tables (unique PK + not null FK) (Section 3.1)
- [ ] **Freshness alert** on top 3 dashboards' source tables (Section 3.2)
- [ ] **Certified Dashboard** labels for top 5 trusted dashboards (Section 5)

After these 5 ship, add 5 more per quarter. Don't boil the ocean.

## Cross-references
- Modeling that prevents grain issues: `mode-model.md`
- Tests that catch quality issues: `mode-model.md` Pattern 2 (dbt tests) + `quality-pipeline.md`
- Metric definitions per project: `metric-framework.md` + `planning-protocol.md` Gate 2
- Reporting standards: `style-rules.md` + `mode-report.md`

— part of prof-data-analyst · Loc Tu, 2026
