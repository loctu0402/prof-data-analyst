---
description: Professional Data Analyst — query mode. Engine-agnostic NL→SQL workflow (BQ / Postgres / Snowflake / Redshift / DuckDB) with semantic-first discovery, self-correction loop, cost discipline.
---

Invoke the `prof-data-analyst` skill in **query mode**. Read these references before acting:
1. `references/mode-query.md` — RECALL→EXPLORE→LEARN, engine-agnostic patterns, self-correction loop
2. `references/universal-workflow-rules.md` — orientation, baseline-noise-impact, action brief
3. `references/coding-discipline.md` — Karpathy + cost discipline (for SQL writing)

User's query request: $ARGUMENTS

Workflow:
- Ask which SQL engine + access layer at session start (if not obvious)
- Try semantic / metric layer FIRST (Cube.js / dbt-metrics / Mimir / LookML) before raw SQL
- For billed engines (BQ / Snowflake / Redshift): dry-run if backfill > 1 month, report bytes + $ before running
- Verify cache files have needed columns; missing → query the source, NEVER fallback to placeholder
- Self-correction loop on errors (parse → re-prompt → retry, capped at N=3)
- After producing data: apply Orientation Block + Baseline-Noise-Impact for any "finding"
- For statistical work on the result: call `scripts/stats/` — never compute inline

