---
description: Professional Data Analyst — model mode. Data modeling pipeline. Pick 1 of 4 patterns (Kimball / dbt staging→marts / Medallion / DuckDB layered) + write Table Contracts + plan governance hooks.
---

Invoke the `prof-data-analyst` skill in **model mode**. Read these references before acting:
1. `references/mode-model.md` — 4 patterns + decision flow + schema documentation requirement
2. `references/governance.md` — 6-section governance framework to apply after modeling
3. `references/orchestration-patterns.md` — scheduler choice for the new pipeline
4. `references/universal-workflow-rules.md` — Rules 1-4 (Orientation / Baseline-Noise-Impact / 5W1H / Why-Explanation)

User's modeling request: $ARGUMENTS

Workflow:
- Confirm context from `da-frame` Gate 3 (TH2 path chose this mode) — read `PLANNING.md` if exists
- Pick pattern based on infrastructure:
  - Cloud DWH (BQ/Snowflake/Redshift) + dbt → dbt staging→marts
  - Cloud DWH without dbt → Kimball direct in DWH
  - Lakehouse (Databricks/Delta) → Medallion (Bronze/Silver/Gold)
  - Local files (CSV/Excel) → DuckDB layered (raw_/stg_/clean_/mart_/ml_)
- Design schema with explicit grain per table
- Write Table Contract (markdown) for each table: business def + grain + PK + partition + SLA + owner + downstream + metric coverage
- Define tests per layer (dbt schema tests OR equivalent assertions)
- Route to governance.md to pick 5 starter implementations (metric dict / naming convention / schema tests / freshness alert / certified dashboard)
- Route to orchestration-patterns.md for scheduler choice

Output: `<project>/schemas/<table>.md` per table + pipeline sketch + governance starter checklist.

Hard rules:
- Schema documentation MANDATORY per table
- Grain explicit (1 row = X × Y × Z)
- Naming convention enforced (stg_/int_/fct_/dim_/agg_)
- Tests defined alongside model
- Pattern matches infrastructure (don't over-model for one-off; don't under-model for scale)
- Governance hooks planned BEFORE shipping pipeline (5 starter checklist from governance.md)
