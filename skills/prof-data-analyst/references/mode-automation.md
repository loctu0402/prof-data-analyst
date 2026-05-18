# Mode — Automation Workflow

## Overview

Invoke when user asks: "automation", "pipeline tự động", "schedule job", "set up cron", "/da-automate".

This mode is engine-agnostic. Concrete cron / scheduling tools (Airflow, Dagster, Prefect, plain crontab, Claude `/loop`, Claude `/schedule`, MoMo internal cron, GitHub Actions) are treated as **replaceable schedulers** behind the same workflow contract.

## Decision Tree — Pick Scheduling Layer

```
What is being scheduled?
  │
  ├─ Daily report / data pipeline (production-flavored, owned by user)
  │   └─ Cron (Airflow / Dagster / Prefect / crontab / org-specific cron)
  │       + Python pipeline + fail-alert via SMTP/Slack/webhook
  │
  ├─ Recurring Claude task (status check, polling)
  │   └─ /loop <interval> /<command>
  │
  ├─ Long-running scheduled agent (cloud, multi-step)
  │   └─ /schedule (Claude Code routines)
  │
  ├─ One-time deferred task ("run X at 3pm")
  │   └─ /schedule once
  │
  └─ CI/CD-style trigger (on push / on schedule)
      └─ GitHub Actions / GitLab CI / Jenkins
```

## Standard Pipeline Anatomy (engine-agnostic)

```
projects/<pipeline-name>/
├── config.py / .env          # constants — NO market data hardcoded
├── pull_<source>.py          # cache update (incremental + backfill)
├── transform.py              # raw → clean → mart layered transforms
├── generate_output.py        # consume mart → render report / send notification
├── pipeline.py               # orchestrator (pull → transform → generate → notify)
├── cache/                    # CSV / Parquet / JSON staging (gitignored)
├── output/                   # generated reports / artifacts (gitignored)
└── README.md                 # ops handoff doc, audience = on-call engineer
```

The shape works for Python+crontab, Airflow DAG, Dagster asset graph, Prefect flow — only the orchestrator wrapper changes.

## Mandatory Setup Checklist

### Fail-Alert — MANDATORY (any channel)

Every scheduled job MUST wire a fail-alert. The channel depends on the org:

- **SMTP email**: `smtplib.SMTP` + app password / OAuth → user's preferred address
- **Slack webhook**: `requests.post(SLACK_WEBHOOK_URL, json={...})`
- **PagerDuty / Opsgenie**: API call
- **Custom internal notification**: org-specific module (e.g., `shared.notifications.email_on_fail`)

Generic pattern:
```python
try:
    pipeline.run()
except Exception as exc:
    notify_failure(
        channel=os.environ["ALERT_CHANNEL"],         # 'email' | 'slack' | ...
        reason="Daily pipeline failed reading source — source returned 0 rows",
        traceback=exc,
    )
    raise
```

Rules (any channel):
- Reason in plain natural language (1 sentence, business framing — what failed, why it matters)
- NEVER paste full stack trace in the notification body — log separately, reference log path
- Subject / title: `[FAIL] <pipeline name> <date>`
- Recipient: configured per environment, not hardcoded in the pipeline file
- Re-raise the exception so the scheduler sees a non-zero exit code

### Market Data — Auto-Fetch + Staleness Gate

Any field that changes daily (CPI, bank rates, gold, FX, oil prices):
- Versioned cache file (e.g., `cpi_history.json`)
- Source script (e.g., `cpi_source.py`) that fetches + appends
- Staleness gate: pick a window appropriate for the data (e.g., 50 days for monthly CPI)
- STALE warning → triggers refresh, NEVER ignored
- NEVER hardcode constants in `config.py` or fallback in templates

Source priority pattern (curated wins):
1. Realtime / news feed (most accurate)
2. Official source (slower update cadence)
3. Curated override JSON (when scrapers unreliable — override always wins)

### Cache File Discipline (universal)

- Cache files = CACHE, not source of truth
- Missing data → query the source, NEVER use placeholder
- Incremental mode MUST NOT clip lower bound of existing cache (silent history wipe)
- Test after incremental update: backfill range still intact?

### Two-Cache-Files Pitfall

When pipeline uses 2 caches with same prefix but different scope (e.g., `events_history.json` operational vs `events_timeline.json` cumulative):
- Document scope in each file's header / metadata
- Consumer picks source matching use case
- Wrong pick = silent miss (lookup doesn't error)
- Bug surfaces as model bias, not data-layer mismatch

### Date Robustness

- Derive `data_date` from the actual data (`df.iloc[-1]['date']`), NOT from `today − 1d`
- Mart lag varies (T-1 typical, T-2 on holidays / weekends, T-7 on quarterly close)
- Code must tolerate missing recent data — fail explicitly, don't silently use stale

### Cost Discipline (billed engines)

- Backfill > 1 month on a billed engine (BQ / Snowflake / Redshift) → dry-run FIRST
- Report bytes / cost estimate to user BEFORE running
- Prefer monthly-aggregate marts over daily marts when answer is monthly (often 10-30× cheaper)

## Backfill Workflow (recompute historical data safely)

A backfill recomputes past N days / months of cached data. Common triggers: bug fix in transformation logic, schema column added with default backfill, upstream mart got refreshed, expanding analysis window.

### Decision tree before any backfill

```
1. Why backfill?
   ├─ Bug fix in transform → backfill scope = affected date range only (not all-history)
   ├─ New column added → backfill scope = column NULL for historical rows? full table needed?
   ├─ Upstream refreshed → backfill scope = upstream date range only
   └─ Expanding window → backfill scope = newly-added date range only

2. Dry-run cost estimate
   ├─ < $1 → proceed
   ├─ $1-10 → surface estimate, user confirm
   ├─ $10-100 → user confirm + plan execution window (off-peak)
   └─ > $100 → STOP. Surface alternative (monthly mart? partition subset? sampling?)

3. Idempotency check
   ├─ Cache write is INSERT OVERWRITE / MERGE / upsert? → safe to re-run
   ├─ Cache write is plain INSERT? → MUST delete target range first
   └─ No idempotency guarantee? → STOP. Add idempotency before backfill.

4. Lower-bound preservation
   ├─ Incremental cache mode → MUST NOT clip the lower bound (silently wipes earlier history)
   ├─ Use --backfill-from <date> flag (or equivalent) explicitly
   └─ Validate after run: row count of historical range matches expected

5. Cross-validation post-backfill
   ├─ Spot-check 5 rows from middle of backfilled range vs source-of-truth (BQ direct)
   ├─ Check row count: GROUP BY date HAVING COUNT(*) > 1 → 0 dups expected
   └─ Compare aggregate (SUM / COUNT) of backfilled range vs canonical
```

### Backfill execution patterns

| Pattern | When | Risk |
|---------|------|------|
| **`--backfill-from <date>`** | Default; clean re-run of date range | Low if idempotent write |
| **Chunked backfill** (1 month at a time) | Backfill > 6 months on billed engine; want progress visibility + fail-recovery | Low; preferred for large ranges |
| **Shadow backfill** | Critical mart with active consumers; bug fix that changes historical numbers | Medium — write to `<table>_v2`, validate, atomic swap |
| **Full rebuild** | Schema change makes historical computation invalid; logic too different to patch | High — last-resort; requires explicit user OK + downtime window |

### Anti-patterns

| Anti-pattern | Symptom | Fix |
|--------------|---------|-----|
| Backfill without dry-run on billed engine | Cost surprise; quota exceeded mid-run | Always dry-run first; report bytes to user |
| Plain INSERT backfill on non-idempotent table | Duplicate rows everywhere | Switch to INSERT OVERWRITE / MERGE; delete target range first if needed |
| Backfill that silently clips lower bound | Historical history disappears | `--backfill-from <date>` flag; never let incremental mode auto-trim |
| Backfill without cross-validation | Bug fix introduced new bug; downstream reports wrong number | Spot-check 5 rows + compare aggregates post-run |
| Backfill during peak hours on shared cluster | Affects other team's pipelines | Schedule off-peak; coordinate with platform team if > $10 cost |

## Pipeline Versioning

Keep pipeline as `pipeline.py` (canonical). For experimental changes:
- Branch `pipeline_v2.py` for the new version
- Keep `pipeline.py` stable until v2 validated end-to-end
- Promote v2 → canonical after 1 week stable run

## Forecast / Expected-Value Engines (if pipeline computes expectations)

Generic pattern for time-series forecast components:
- **Flow variables**: 3-anchor weights (daily / weekly / monthly seasonality) — e.g., `T_blend × S_w × S_d × I`
- **Stock variables**: accounting identity (`stock(d) = stock(d-1) + E[flow(d)]`) — bypass season×interaction for stocks
- **Variance**: covariance-aware σ on residuals; do NOT just sum component variances
- **Online retraining**: walk-forward, always-recompute, upsert forecast log
- Avoid: EWMA on coefficients (mixes seasons); auto-retrain on drift (feedback loop rot)
- Floor weights at small ε (e.g., 0.05) to prevent corner solutions in optimization

## Schedule Layers (concrete tools)

For full per-pattern decision table + starter templates: see `orchestration-patterns.md`.

| Pattern | When to pick | Cost | Detail |
|---------|--------------|------|--------|
| **Airflow** | Production; multiple dependent DAGs; cross-DAG triggers + sensors | Infrastructure (or managed Composer / MWAA) | `orchestration-patterns.md` Pattern 1 |
| **dbt + Cloud / GHA** | Transformation-heavy; modular SQL; dbt-skilled team | dbt Cloud (paid) or self-host | `orchestration-patterns.md` Pattern 2 |
| **Cron** | 1 recurring job; no dependencies; small team / VPS | Free | `orchestration-patterns.md` Pattern 3 |
| **GitHub Actions** | CI/CD-native team; lightweight workflows; fits in 6 hr | Free for OSS / generous tier for private | `orchestration-patterns.md` Pattern 4 |
| **Claude `/schedule`** | One-time or recurring AI-agent tasks; not for production data pipelines | Token cost | (Claude Code feature) |
| **Claude `/loop`** | In-session polling; debugging cadence | Token cost | (Claude Code feature) |

**Hybrid common:** Cron / GHA triggers daily → Airflow DAG orchestrates phases (ingest with BQ operators / transform with dbt task / output / QC) → Trigger downstream DAG.

**Picking discipline:**
- Don't introduce a 2nd orchestrator if team already runs one (consolidate)
- Pipeline code stays portable; only the DAG / flow wrapper changes per scheduler
- Match scale: cron for 1 job, Airflow for 100+ dependent tasks

## Pipeline Handoff Doc (README.md)

When delivering pipeline to user / ops team, README.md must include:
1. Purpose + audience (1 paragraph)
2. Schedule (cron expression / scheduler name + ID)
3. Expected runtime + output location
4. Alert recipient list + channel
5. Rollback steps (revert to previous version)
6. Known limitations (mart lag, staleness gate, curated override file location)
7. Test-run log (date + bytes processed + output checksum)
8. Local-language version if team prefers (e.g., Vietnamese with full diacritics for VN ops teams)

## NEVER

- Auto-send report to stakeholders without explicit user confirm (exception: fail-alert to oncall, by design)
- Hardcode market data in `config.py` or template fallbacks
- Mix cron job with ad-hoc one-off — separate the orchestrator
- Skip fail-alert wiring
- Edit the generator file (`generate_output.py`) to "patch" today's output — use `update_output_vN.py` instead (see `mode-fix-pipeline.md`)
- Run pipeline before dry-run if backfill > 1 month on billed engine

## Universal Rules Reminder

Automation deliverable = pipeline code + README + schedule doc. Apply:
- Orientation Block in README (purpose, inputs, outputs, owner, last-updated)
- 5W1H Action Brief for any post-deploy follow-up
- Karpathy 4 principles when writing pipeline code (simplicity, surgical, goal-driven)
- Script > agent-compute (don't have the agent calculate sample sizes / costs — `scripts/stats/` does it)
- Self-check protocol section L (Pipeline) before declaring shipped

## Validation Scripts to Run Before Ship

```bash
python scripts/validators/orientation_block.py README.md
python scripts/validators/ai_tell_scan.py README.md
python scripts/validators/self_check.py pipeline.py --section L
```
