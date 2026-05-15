---
description: Professional Data Analyst — automation mode. Set up scheduled pipeline with email-on-fail and cache discipline.
---

Invoke the `prof-data-analyst` skill in **automation mode**. Read these references before acting:
1. `references/mode-automation.md` — pipeline anatomy, fail-email wiring, market-data fetch
2. `references/coding-discipline.md` — Karpathy + cache patterns + market-data rules
3. `references/universal-workflow-rules.md` — orientation in README, action brief for deploy plan
4. `references/self-check-protocol.md` — section L (pipeline checks)

User's automation request: $ARGUMENTS

Workflow:
- Pick scheduling layer (MoMo cron / Claude `/loop` / Claude `/schedule`)
- Wire `shared.notifications.email_on_fail.send_failure_email` — natural Vietnamese reason, NO stacktrace in body
- Market data: auto-fetch + 50d staleness gate — NEVER hardcode in config.py
- Cache files: preserve history on incremental update; document scope if multi-cache
- BQ backfill > 1 month: dry-run FIRST, report GB + $ to user
- README in Vietnamese-with-diacritics for ops team
- NEVER auto-send report to stakeholders (only pipeline-fail email to loc.tu)
