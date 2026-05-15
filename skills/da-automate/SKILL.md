---
name: da-automate
description: Engine-agnostic pipeline + scheduling + fail-alert workflow. Works with Airflow / Dagster / Prefect / crontab / GitHub Actions. Triggers on "automation", "pipeline tự động", "schedule job", "set up cron", or /da-automate.
---

# DA Automate Mode

Pipeline automation with fail-alert + cache discipline + no auto-send safety.

## 4 Universal Rules
1. Orientation Block (docstring for pipeline modules)
2. Baseline → Noise → Impact for any monitoring metric
3. 8-field Action Brief for scheduling change
4. Why-Explanation on scheduler choice + alert channel + cache strategy

Full: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/universal-workflow-rules.md`.

## Mode workflow

1. Decision tree pick scheduling layer (cron / Airflow / Dagster / Prefect / GitHub Actions)
2. Wire pipeline.py with try/except + send_failure_email
3. Cache discipline: incremental MUST NOT clip lower bound; preserve history on update
4. Fail-alert config: channel + recipient + natural-language reason in team's primary language
5. No auto-send to stakeholder (only oncall on fail)

Full workflow: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/mode-automation.md`.

## Hard rules
- Pipeline FAIL alert wired to configured oncall recipient (auto-send by design)
- Stakeholder reports NEVER auto-sent (default: save to output/, show preview link, wait for "send" command)
- Reason in natural Vietnamese ("Pipeline daily lỗi khi đọc mart — chưa có data ngày YYYY-MM-DD"), NOT stacktrace
- Backfill > 1 month on billed engine → dry-run + $ report to user first

## Cross-references
- Full mode workflow: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/mode-automation.md`
- Coding discipline: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/coding-discipline.md`
- Self-check: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/self-check-protocol.md`
