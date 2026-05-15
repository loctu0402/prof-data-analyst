# Mode — Process (Raw Data → Analysis / ML-Ready)

Invoke when user asks: "process data", "build mart", "feature engineering", "EDA notebook", "data pipeline", "raw → clean", "DWH layer", "/da-process".

This mode covers the **transformation engine** from raw input through staged → cleaned → mart → analysis/ML-ready output. Sits between `mode-query` (fetch) and `mode-insight` (hypothesis-driven analysis) or `mode-report` (stakeholder delivery).

## Overview — Why Process Mode Exists

Two failure modes that this mode prevents:

1. **Scattered-script anti-pattern** — analyst writes 12 ad-hoc Pandas cells reading 4 parquet files, no staging, no lineage. Cannot reproduce, cannot hand off, cannot audit.
2. **Skipping data quality gate** — analyst jumps from raw load straight to model / insight, never quantifies missingness / dupes / type drift. Downstream conclusion is built on silently bad data.

Process mode enforces a layered, phased, validated workflow. The framework is market-standard (CRISP-DM + Medallion + dbt-style staging), not personal convention.

## Market-Standard Frameworks (the WHY behind the workflow)

This mode synthesizes three established frameworks. Knowing the source lets you defend the choice to a stakeholder or new teammate.

### CRISP-DM (1996, IBM / SPSS — still the most widely cited)
6 phases: Business Understanding → Data Understanding → Data Preparation → Modeling → Evaluation → Deployment. **Why use it**: the iteration arrows (Eval → Business, Prep → Data) are baked in — discourages waterfall mindset.

### Medallion Architecture (Databricks, 2020+ — modern lakehouse standard)
3 layers: **Bronze** (raw ingested, append-only), **Silver** (cleaned, conformed, deduped), **Gold** (business-aggregated, KPI-ready). **Why use it**: layer naming forces explicit transformation intent — you cannot accidentally mix raw + cleaned + agg.

### dbt Staging Convention (dbt Labs — most-cloned SQL transformation pattern)
Prefix convention: `stg_<source>` → `int_<entity>` → `fct_<fact>` / `dim_<dimension>`. **Why use it**: prefix discoverability via `information_schema` — a new analyst SELECTs prefix and sees the whole pipeline.

This skill blends the three into one layered table prefix convention (see below). You can substitute any equivalent your team prefers — the rule is **prefixed layers with documented transformation intent**, not the specific prefix.

## Recommended Layered Table Convention

```
stg_<source>        — staged raw (typed, no business logic)   [Bronze]
clean_<table>       — deduped, null-handled, type-cast          [Silver]
mart_<entity>       — joined + aggregated, business keys        [Gold]
ml_<feature_set>    — ML feature table (optional, ML-only)      [Gold+]
pred_<model_v>      — model output (versioned)                  [Gold+]
```

Why per layer:

| Layer | Transformation allowed | Transformation BANNED | Why this boundary |
|-------|------------------------|------------------------|-------------------|
| `stg_*` | Type cast, column rename | Dedup, null handling, join, agg | Bronze must be append-only and reproducible from source — lineage anchor |
| `clean_*` | Dedup, null handling, outlier flag, unit conversion | Cross-table join, business agg | Silver = "data fixed but not yet interpreted" — reusable across all downstream marts |
| `mart_*` | Join, agg, business KPI, derived columns | ML-specific feature engineering | Gold = consumable by BI tools / dashboards / non-ML stakeholders |
| `ml_*` | Encoding, scaling, train-test split, feature interaction | Anything that leaks future info into past | Adds ML-specific transforms downstream of clean Gold |
| `pred_*` | Model predictions, calibrated scores, threshold-applied class labels | Mixing with ground truth labels post-hoc | Audit trail of model output by version |

## DuckDB Recommended Pattern (Why this engine for this mode)

When raw input is CSV / Parquet / mart-export-dump and the workflow needs SQL-style joins, aggregations, and HTML/dashboard downstream — use **DuckDB persistent file** (`.duckdb`) as the SQL engine, not scattered `pd.read_csv` / `pd.read_parquet`.

### Why DuckDB over CSV-only

| Concern | CSV-only | DuckDB persistent file | Why DuckDB wins |
|---------|----------|------------------------|-----------------|
| **Source of truth** | N files; analyst picks which to read; risk of drift | Single `.duckdb` file with all tables | Hand-off = one file. No "which CSV is canonical?" debate. |
| **Type preservation** | Dates serialize as string, ints widen to float on NULL | DATE / INT64 / VARCHAR preserved natively | Eliminates downstream "why is my date a string?" bugs. |
| **Cross-table operations** | `pd.merge` gymnastics, manual join keys | SQL `JOIN` directly | SQL JOIN is debuggable, version-able, readable. |
| **Append vs replace** | Append risks dup; replace overwrites silently | `CREATE OR REPLACE TABLE` is atomic | No partial-write corruption mid-pipeline. |
| **Aggregation speed** | Pandas single-thread, copies in RAM | Columnar vectorized, ~10× faster on agg queries | On 1M+ rows the speedup is felt in interactive EDA. |
| **Production-grade signal** | Looks like a hobby script | Looks like a staged DWH submission | Hiring / handoff signal: "this person thinks in layers". |
| **Discoverability** | Have to grep filenames | `SELECT * FROM information_schema.tables` | New reader sees the whole pipeline in one query. |
| **HTML / dashboard builder** | Read CSV → reshape → write template | 1 SQL line per table, embed in template | The downstream renderer reads from one engine, not N file paths. |

### When NOT to use DuckDB (be honest about the choice)

- Raw data is already in a production DWH (BQ, Snowflake) — query that directly via `mode-query`; do not duplicate to DuckDB.
- Data > 100 GB and a real cluster is available — use the cluster.
- Workflow is a single-cell exploration, no joins, no downstream — `pd.read_csv` is fine, no need for the file overhead.

### Anti-pattern (reject)

```python
df_a = pd.read_parquet("data/source_a.parquet")
df_b = pd.read_parquet("data/source_b.parquet")
df_c = pd.read_parquet("data/source_c.parquet")
df = df_a.merge(df_b, ...).merge(df_c, ...)
df["new_col"] = df["x"] / df["y"]   # mixed cleaning + business logic in one cell
df.to_csv("output.csv")             # no layer, no schema, no history
```

### Right pattern

```python
import duckdb
con = duckdb.connect("project.duckdb")

con.execute("""CREATE OR REPLACE TABLE stg_source_a AS SELECT * FROM 'data/source_a.parquet'""")
con.execute("""CREATE OR REPLACE TABLE stg_source_b AS SELECT * FROM 'data/source_b.parquet'""")

con.execute("""
CREATE OR REPLACE TABLE clean_source_a AS
SELECT DISTINCT * FROM stg_source_a WHERE id IS NOT NULL
""")

con.execute("""
CREATE OR REPLACE TABLE mart_entity AS
SELECT a.id, a.x, b.y, a.x / NULLIF(b.y, 0) AS ratio
FROM clean_source_a a JOIN clean_source_b b USING (id)
""")
```

Each layer = one named table. Each transformation = one named CREATE statement. Lineage = traceable via `information_schema.tables` and table-comment metadata.

## Phased Workflow (the actual steps)

Define phases by their **acceptance gate**, not by milestone label. Lock criteria only for phases whose acceptance is data-independent — sketch later phases until prior findings refine them.

### Phase 1 — Ingest & Data Dictionary
Acceptance gate: every source table has (a) a `stg_*` table, (b) row count + column type recorded, (c) a 1-line column description in the data dictionary.

Why lock upfront — independent of data content; missing this step = no audit trail.

Deliverable: `data_dictionary.md` or markdown cell with table { source name, row count, columns × types × description, primary key, refresh cadence }.

### Phase 2 — Data Quality Audit + 6-Step EDA Sequence
Acceptance gate: every column passes the 7-check audit AND the 6-step EDA sequence has been executed in order.

#### Part A — 7-check audit (run once per source)
1. **Missingness** — % null per column; flag > 5%
2. **Duplicates** — row count vs `COUNT(DISTINCT primary_key)`; flag any gap
3. **Type drift** — does declared type match actual? (Date stored as string, etc.)
4. **Range sanity** — min/max within expected business range (age 0-120, ratio 0-1, etc.)
5. **Categorical cardinality** — flag columns where `n_unique ≈ n_rows` as identifiers (NOT features — see High-Cardinality section below)
6. **Temporal coverage** — date range covered, gaps (missing days / weeks), time-zone alignment
7. **Referential integrity** — joined keys exist on both sides; orphan rate

#### Part B — 6-Step EDA Sequence (run in order; do not skip ahead)

| Step | What | Why this step exists | Skipping this step causes |
|------|------|----------------------|---------------------------|
| **S1 — Dtype audit** | Verify dtype per column matches business meaning (ID = str, date = date, money = float) | Wrong dtype propagates as silent miscompute downstream (e.g., ID as int loses leading zeros) | Mysterious join failures, leading-zero loss |
| **S2 — Univariate distribution** | Per column: distribution shape, central tendency, spread, missingness | Anchors expectation for what "normal" looks like before any cross-feature analysis | Reader cannot calibrate "weird" without baseline |
| **S3 — Anomaly + outlier scan** | Per column: outlier rule (IQR / z-score / domain rule), document each anomaly | Anomalies that survive into modeling = silent data-quality bugs at deploy time | Model bias traced 3 weeks later to a Phase-2 outlier nobody flagged |
| **S4 — Bivariate vs target** | Each feature × target relationship; effect size; test significance | The actual signal-discovery step; everything above sets the table | "Feature X correlates" claimed from univariate — Cohen's d at zero, no real signal |
| **S5 — Feature ranking** | Rank features by predictive contribution (mutual info, importance, effect size) | Phase 3 (Feature/Mart construction) needs a ranked shortlist to filter from | Build features for everything → wasted Phase 3 cycle |
| **S6 — Pattern + interaction** | Cross-feature patterns: clusters, interactions, correlated features | Most predictive signal lives in interactions; solo features rarely tell the full story | Model underperforms; missing feature interactions |

Order matters: S4 before S3 produces analysis on dirty data; S6 before S5 generates noise patterns from low-signal features.

Why this is a SEPARATE phase — most "model failed mysteriously" incidents trace to a Phase-2 gap that was skipped. The 7-check + 6-step combination is the structured catch.

Deliverable: a quality-audit table (Part A, run by code, not eyeballed) + EDA notebook with one section per S-step.

### Source-pending discipline — no premature lock

If a data source is PENDING (table not yet created, partner team not yet pulling, mart still building) — do NOT block downstream work. Stub the source with a clearly-named placeholder (`stg_<source>_PENDING` table with the expected schema + dummy 1-row sample) and continue downstream design.

When the real data lands:
1. Replace the PENDING table with the real `stg_*`
2. Re-run Phase 2 audit on the real data
3. Re-verify downstream tables that depend on it

Why — pipeline workflow rule: blocking the entire downstream waiting for one source delays N parallel workstreams. Stubbing lets the architecture / schema decisions proceed while data is pending. See `feedback_no_premature_lock_when_source_pending.md`.

### Phase 3 — Feature / Mart Construction
Acceptance gate: every mart / feature has a docstring stating { purpose, source tables, transformation, expected row count, leak check }.

Why sketch only (no upfront lock) — features depend on what Phase 2 surfaced; cannot pre-commit to features before knowing data quality.

### Phase 4 — Model / Analysis
Acceptance gate: defined per task (model AUC, hypothesis p-value, etc.). Driven by `Define Winning Metric FIRST` rule below.

### Phase 5 — Evaluation & Report
Acceptance gate: results match the gold metric from Phase 4, formatted for stakeholder per `mode-report` rules.

This is a generic skeleton — ML case studies, A/B analyses, dashboard builds, all pass through these 5 gates. Substitute domain-specific names (M1-M5, sprint goals, etc.) if your team uses different vocabulary; the gates do not change.

### Why phases instead of milestones

A "milestone" label can drift (M1, M2 may mean different things on different teams). A **gate** is binary: passed or not. The gate is the unit of progress, not the label.

## Executive Summary Block (per phase)

Each phase deliverable opens with a TABLE-form Executive Summary (after the Orientation Block, before the body).

Columns:
| Column | What it captures | Why this column |
|--------|------------------|-----------------|
| Terminology | niche / multi-meaning term + 1-line definition | Cold readers cannot guess MoMo / company / domain jargon |
| Assumption | "assumed X because input did not give Y" | Surfaces inference vs given-fact — protects against silent over-claim |
| Q&A descriptive | what does this feature / metric look like? | Shape of the data, not interpretation |
| Q&A diagnostic | what does this feature tell us about target / outcome? | Interpretation layer, separated from shape |
| Multi-feature combo | notable interactions / combinations | Most insight lives in interactions, not solo features |
| Final belief | what I conclude about this feature | Forces explicit conclusion, not "TBD" filler |
| Rule-based filter | rules excluding rows / values pre-ML | High-cardinality, business-illegal values |
| Traps | what to watch in next phase | Hands off explicit caveat to next phase reader |
| Next action | concrete first step for next phase | No vague "investigate further" |

Why TABLE not PROSE — reader scans the table in 60s and sees the per-feature reasoning side-by-side. Prose forces sequential reading and hides cross-feature contamination of reasoning.

Why per-phase not just at-end — late-phase reader of an end-of-notebook summary cannot re-run the upstream phases mentally. Per-phase ExecSum localizes the audit.

## Univariate vs Bivariate — Role Split

In EDA / case-study notebooks, separate two roles into two sections so each chart has ONE job:

### Univariate (snapshot section)
- Flat-cut view pre/post-preprocess
- No class split, no statistical test
- Each feature in isolation
- Goal: pre-processing audit (missing, outlier, distribution shape)

### Bivariate (deep-dive section)
- Each feature × target
- Goal: feature → target relationship discovery
- Stat test belongs HERE, not in univariate

### Why split

If both sections show a class-split t-test on the same feature, you have duplicated the test. The reader does not know which is canonical. Either the univariate section should drop the test (it is not a univariate operation) or the bivariate section should not duplicate it.

Concretely: univariate "this feature has 5% missingness, right-skewed" vs bivariate "this feature differs by class with d=0.34" — two different findings, each in its own section.

## Per-Chart Inline Takeaway

Every chart in a process notebook MUST end with a 1-line verdict beneath / beside it, classified into one of:

| Verdict | Meaning | Why this verdict |
|---------|---------|------------------|
| `drop` | exclude this feature, no signal | save downstream-phase reader time |
| `negligible` | weak signal, low priority | keeps feature alive but de-emphasized |
| `candidate` | worth investigating in next phase | explicit hand-off to next phase |
| `strong` | clear pattern, ready for action | unblocks immediate use |

Why required — reader expects a conclusion AT the chart, not scrolled-down. If the verdict cannot be filled, the chart is not finished — either get more data or remove the chart.

## High-Cardinality Rule-Based Ban

Columns where unique-count ≈ row-count are identifiers, NOT ML features.

Examples: `transaction_id`, `user_id`, `device_id`, `session_id`, `request_uuid`.

- DO NOT ship to ML feature set
- FLAG as rule-based pre-filter ("business bans rows fast on this dimension")
- Document in ExecSum "Rule-based filter" column

Why — Cramer's V on high-cardinality categorical is inflated artefact (chi-square statistic scales with degrees of freedom). High Cramer's V on `transaction_id` is not signal; it is df.

## Plain Language — WRONG vs RIGHT

Teaching / hand-off notebooks: explain in plain language, NOT formula dumps.

```
WRONG cell output:
"E[AUM] = 12.96T. z = −2.19. %gap = −6.5%"
(zero interpretation; reader does not know if this is good / bad / actionable)

RIGHT cell output:
"AUM thực tế thấp hơn dự kiến 6.5% (~840B VND), vượt ngưỡng cảnh báo (±5%)"
(then formula in small print or markdown: "z = −2.19 < −1.96 → significant")
```

Why — formulas are the audit trail; plain language is the message. A deliverable that shows only formulas is academic theatre. A deliverable that shows only plain language is unauditable.

## Metrics Need Denominator

Notebook output that surfaces a percentage MUST show absolute + % + total.

```
WRONG: "76% sessions tốt"            (% without denominator → reader cannot weight it)
RIGHT: "100 / 176 sessions (56.8%) không lỗi"   (actionable: reader can re-aggregate)
```

Why — a 76% bar on 17 sessions is noise; a 76% bar on 1,700 is signal. The denominator decides.

## Comment Discipline in Notebooks

- Zero-comment AND over-note are BOTH anti-patterns
- Each cell / code block MUST have a 1-line purpose comment OR a markdown cell above it stating intent
- Markdown reading blocks ≤ 2 lines (longer = move to a separate dedicated cell)
- `print()` MUST end with a takeaway verdict, not a bare number dump
- BAN AI-tell symbols in stakeholder prose cells: `===`, `-----`, em-dash, `≈`, `→` (in stakeholder prose only — `→` inside code blocks is fine)

Why — code-only cells force reader to reverse-engineer intent; over-noted cells bury the code. The middle (1-line purpose + clean code) reads fastest.

## Define Winning Metric FIRST

Before picking data / rubric / judge / model:
1. Define **unit of success** (session? task? user? feature?)
2. Define **measurement** (how do we score one unit?)
3. Define **aggregation** (mean? p50? % passing threshold?)
4. THEN pick the data, judge, rubric, model

Why — picking the metric while looking at the data invites motivated reasoning. The metric should be defendable before you see the answer. If unsure, do field research first (talk to the stakeholder, look at past similar tasks) — do not start aggregating until the metric is locked.

## No Fabricated Anything

In notebook narrative cells:
- NEVER invent academic credentials for the author
- NEVER invent data that does not exist in the source
- Mark inferences explicitly: "I assumed because input did not give X"
- NEVER glue calendar context as causation ("X = 0.98 on Day 5 (payday)" reads as causation — separate label from claim)

Why — stakeholder distrust scales fast. One fabricated detail caught in the deliverable poisons every other claim by association.

## ML Pipeline Anatomy (canonical reference, optional)

If the task is supervised ML specifically, also load the canonical 10-stage pipeline reference covering: business framing → target def → split design → leak audit → feature analysis → preprocessing → baseline model → tuning → calibration → threshold → deployment, plus 7 cross-cutting concerns (leakage taxonomy, feature analysis 4-task, split design, imbalance, calibration, threshold, reproducibility).

→ Substitute your local pointer: `<your-workspace>/<your-templates-dir>/ml-pipeline-anatomy.md` (or your team's equivalent)

Process mode itself is engine-agnostic — pipeline anatomy is the ML-supervised-task specialization.

## Output File Discipline

Process artifacts land per type:

| Artifact | Destination |
|----------|-------------|
| `.duckdb` persistent file | project root (`<workspace>/<project>/`) — submission anchor |
| HTML EDA report (ydata-profiling, sweetviz, custom) | `<workspace>/output/projects/<case>/` |
| Trained model pickles | `<workspace>/output/projects/<case>/models/` |
| Feature export CSVs | `<workspace>/output/projects/<case>/features/` |
| Notebook itself | project root, version-stamped (`eda_v3_2026-05-14.ipynb`) |

Never scatter outputs into the notebook directory or workspace root.

Why — separate "code I am editing" from "artefacts I produced". Pre-commit hooks, gitignore, and clean handoff all rely on this split.

## Universal Rules Reminder

Process notebook applies all 4 universal rules:
- **Rule 1** — Orientation Block at top (purpose + inputs + outputs + owner + dataset version + data freshness)
- **Rule 2** — Baseline-Noise-Impact ladder for every numeric statement in cells
- **Rule 3** — 5W1H action brief on any recommendation surfaced from EDA
- **Rule 4** — Why-explanation on every framework / threshold / encoding / split choice (e.g., "test set = last 20% by time because temporal validation matters here")

Plus mode-specific reminders:
- Executive Summary table per phase (NOT just at end)
- Per-chart inline `→ takeaway`
- "Reading in business terms" for any formula
- Plain-language WRONG-vs-RIGHT framing
- Drop AI-tells in stakeholder prose cells
- Save outputs to `<your-workspace>/output/projects/<case>/`

## Reading Order Recap

Before starting process notebook:
1. THIS file — frameworks + DuckDB pattern + phases + ExecSum + chart/test split
2. `references/universal-workflow-rules.md` — Orientation + Ladder + Action Brief + **Why-Explanation**
3. `references/style-rules.md` — AI-tells, numbers, charts (Plain language + Show numbers + business reading)
4. `references/coding-discipline.md` — Karpathy + comments policy
5. `references/self-check-protocol.md` — pre-ship checks (especially Section E2 — Why-Explanation)
6. If ML-supervised task: also load your local `ml-pipeline-anatomy.md`
