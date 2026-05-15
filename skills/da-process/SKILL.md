---
name: da-process
description: Raw → staged → cleaned → mart → ML-ready pipeline. Layered tables (stg_/clean_/mart_/ml_/pred_) per Medallion + dbt-style. DuckDB-first for case studies. 7-check + 6-step EDA + Executive Summary per phase. Triggers on "process data", "ML case study", "EDA notebook", "feature engineering", "DWH", or /da-process.
---

# DA Process Mode

Transformation engine from raw input through staged → cleaned → mart → analysis/ML-ready output.

## 4 Universal Rules
1. Orientation Block at top of every deliverable
2. Baseline → Noise → Impact ladder for every numeric statement
3. 5W1H Action Brief for every recommendation
4. Why-Explanation on every framework / threshold / encoding / split choice

Full: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/universal-workflow-rules.md`.

## Mode workflow

5 phases with acceptance gates:
- Phase 1 — Ingest & Data Dictionary
- Phase 2 — Data Quality Audit (7-check + 6-step EDA sequence S1 dtype → S2 univariate → S3 anomaly → S4 bivariate → S5 ranking → S6 patterns)
- Phase 3 — Feature / Mart Construction
- Phase 4 — Model / Analysis
- Phase 5 — Evaluation & Report

Per-phase Executive Summary table (Terminology / Assumption / Q&A descriptive / Q&A diagnostic / Multi-feature combo / Final belief / Rule-based filter / Traps / Next action).

DuckDB-first when raw input is CSV / Parquet / mart-export for case studies. Bronze→Silver→Gold layered tables per Medallion architecture; prefix convention matches dbt staging.

Full workflow: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/mode-process.md`.

## Hard rules
- Layered prefix convention enforced: stg_/clean_/mart_/ml_/pred_
- High-cardinality columns flagged as rule-based pre-filter, NEVER ship to ML
- Source-pending: stub `stg_<source>_PENDING`, continue downstream design
- Univariate vs Bivariate role split (no duplicate t-test)
- Per-chart inline takeaway (drop / negligible / candidate / strong)

## Cross-references
- Full mode workflow: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/mode-process.md`
- Coding discipline: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/coding-discipline.md`
- Style + AI-tells: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/style-rules.md`
- Self-check: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/self-check-protocol.md`
