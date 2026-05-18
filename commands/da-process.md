---
description: Professional Data Analyst — process mode. Raw data → ML-ready features (DuckDB DWH-first, M1-M5 milestones, ExecSum table). Also covers standalone Data Quality Audit and Data Cleaning sub-modes.
---

Invoke the `prof-data-analyst` skill in **process mode**. Read these references before acting:
1. `references/mode-process.md` — DWH-first architecture, progressive milestones, ExecSum block, univariate/bivariate split, plus 3 entry granularities (Full pipeline / Quality Audit only / Cleaning only)
2. `references/universal-workflow-rules.md` — orientation + baseline-noise-impact + action brief
3. `references/style-rules.md` — AI-tell ban + plain-language WRONG-vs-RIGHT + business reading
4. `references/coding-discipline.md` — Karpathy + comments policy

User's process / ML-case / audit / cleaning request: $ARGUMENTS

First check: which entry granularity does the user actually want?
- "Build mart / ML feature / M1-M5 case study" → Full pipeline
- "Audit / kiểm tra data quality / dữ liệu có sạch không / data trust check" → Quality Audit only (Phase 2; output is a quality report, no cleaning artifacts)
- "Clean dirty data / drop dup / fix null / type cast / outlier" → Cleaning only (Phase 2 audit findings + Phase 3 cleaning ops; output is one cleaned table)

Workflow (Full pipeline; for sub-modes run only the relevant phases):
- Use DuckDB persistent file as SQL engine throughout M1-M5 (layered tables: stg_/clean_/mart_/ml_/pred_)
- Lock acceptance criteria ONLY for M1 + M2; sketch M3+ (refine after EDA)
- Each milestone: Executive Summary block (TABLE form) after Data Dictionary, before body
- Univariate IX = flat-cut snapshot (no class split, no test); Bivariate XI = deep dive vs target for M3
- Per chart: inline `→ takeaway` verdict (drop / negligible / candidate / strong)
- High-cardinality columns → flag rule-based pre-filter, NEVER ship to ML
- Plain-language WRONG-vs-RIGHT in teaching cells (no formula dumps)
- Drop AI-tells in stakeholder prose: `===`, `-----`, em-dash (`→` in code OK)
- Human-author voice: no 14-section template, mixed VN-EN natural, free-form notes
- Output to `output/projects/<case>/` — never scatter
