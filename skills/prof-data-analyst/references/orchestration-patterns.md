# Orchestration Patterns — Airflow / dbt / Cron / GitHub Actions

> Loaded from `mode-automate.md`. Picks scheduler + DAG shape based on infrastructure + scale. Generic; engine-agnostic.

## Overview — Why this file exists

After modeling (`mode-model.md`), pipelines need scheduling. Picking the wrong orchestrator wastes 1-2 weeks of setup and locks the team into the wrong stack. This file gives a decision table + per-pattern starter template.

**Why (Operational):** orchestrator choice is hard to reverse. Picking based on team skill + infrastructure + scale upfront beats migrating after.

## Decision table

| Constraint | Pick |
|------------|------|
| **Team owns Airflow, multiple dependent DAGs** | Pattern 1 (Airflow) |
| **dbt-first team, transformations dominate** | Pattern 2 (dbt + Cloud / GitHub Actions trigger) |
| **Single recurring job, no dependencies** | Pattern 3 (Cron) |
| **CI/CD-native team, lightweight workflows** | Pattern 4 (GitHub Actions) |
| **Google Sheet input → auto-refresh HTML dashboard** | Pattern 5 (Google Apps Script) |
| **Modern Python-first team, dynamic DAGs** | Alternative: Prefect / Dagster (mentioned, not detailed) |

Hybrid common: Airflow for ingest + dbt for transform + cron for tiny one-offs. Apps Script for stakeholder-facing dashboards bound to live Sheets.

---

## Pattern 1 — Airflow (Production-grade orchestration)

### When to pick
- Multiple dependent jobs (e.g., 6 DAGs with cross-dependencies)
- Need for retries / backfill / sensors / alerting first-class
- Team already runs Airflow (don't introduce a 2nd orchestrator)
- Production scale (daily 100+ tasks)

### Anatomy (plain DAG)

```python
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.task_group import TaskGroup
from airflow.models.baseoperator import chain
from functools import partial
import pendulum

GCP_CONN_ID = "<your-conn-id>"
PROJECT_ID = "<your-project-id>"

ARGS = {
    'owner': '<owner>',
    'depends_on_past': False,
    'start_date': pendulum.datetime(2026, 1, 1, tz="Asia/Ho_Chi_Minh"),
    'retries': 3,
    'email': ['oncall@yourcompany'],
    'email_on_failure': True,
    'on_failure_callback': partial(send_message_on_failure, http_conn_id="<slack-or-chat-webhook>"),
}

with DAG(
    dag_id="my_daily_pipeline",
    schedule_interval='00 6 * * *',
    catchup=False,
    default_args=ARGS,
) as dag:

    start = DummyOperator(task_id="start")
    end = DummyOperator(task_id="end")

    # Phase 1: Ingest raw
    with TaskGroup("ingest") as ingest:
        # ... raw table tasks
        pass

    # Phase 2: Transform to staging
    with TaskGroup("staging") as staging:
        # ... stg_ tasks
        pass

    # Phase 3: Build marts
    with TaskGroup("marts") as marts:
        # ... mart_ / fct_ / dim_ tasks
        pass

    # Phase 4: Aggregate for dashboards
    with TaskGroup("dashboards") as dashboards:
        # ... agg_ / dashboard tasks
        pass

    # Quality check between phases
    qc_check = BigQueryInsertJobOperator(
        task_id="qc_check",
        configuration={"query": {"query": "<assertion SQL>", "useLegacySql": False}},
    )

    # Trigger downstream DAG
    trigger_downstream = TriggerDagRunOperator(
        task_id='trigger_downstream',
        trigger_dag_id='downstream_dag_id',
        wait_for_completion=False,
        reset_dag_run=True,
    )

    # Overall dependency chain
    chain(start, ingest, qc_check, staging, marts, dashboards, end, trigger_downstream)
```

### Key features to use
- **TaskGroups** for visual grouping in UI
- **`chain()`** for clean sequential dependency
- **`DagSensor`** for cross-DAG wait (when downstream depends on upstream DAG completion)
- **Row-count check operators** for inline data validation (catches silent drops)
- **Trigger downstream** at end (TriggerDagRunOperator)
- **on_failure_callback** for Slack / Chat / Email alerting

### Cost discipline
- Idempotent tasks (re-run-safe)
- Sliding-window reprocess (e.g., last 3 days delete+insert) instead of full-rebuild
- Backfill via parameterized window (D-N → D)

### Anti-patterns
- 1 huge DAG with 200 tasks → split into smaller DAGs with `TriggerDagRunOperator`
- No retries / no callback → silent failures
- Catchup=True with long history → DAG storm

---

## Pattern 2 — dbt + Cloud (or GitHub Actions)

### When to pick
- Transformation-heavy workflow (most of the pipeline IS SQL transformations)
- Team already uses dbt or wants modular SQL
- Need built-in tests + lineage + docs

### Anatomy

**dbt project structure** (from `DBT-learn.md`):
```
my_dbt_project/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── staging/
│   │   ├── stg_<source>__<table>.sql
│   │   └── _<source>__sources.yml
│   ├── intermediate/
│   └── marts/
│       ├── finance/
│       └── marketing/
├── tests/
├── seeds/
└── snapshots/
```

**Daily run pattern:**
```bash
dbt deps           # install package deps
dbt seed           # load reference data
dbt source freshness   # check source data freshness
dbt build          # run + test all models in DAG order
dbt docs generate  # update docs
```

**Scheduling options:**
- **dbt Cloud** (paid, managed): set schedule in UI, runs jobs, alerts on failure
- **Airflow** (with `dbt-core`): one task = `dbt build`, schedule via Airflow
- **GitHub Actions** (free for OSS): `.github/workflows/dbt-daily.yml`

### GitHub Actions example
```yaml
name: dbt daily run
on:
  schedule:
    - cron: '0 6 * * *'   # 6 AM daily UTC
  workflow_dispatch:       # manual trigger

jobs:
  dbt-run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install dbt-bigquery
      - run: dbt deps
      - run: dbt build --target prod
        env:
          DBT_PROFILES_DIR: ./profiles
          GCP_SERVICE_ACCOUNT: ${{ secrets.GCP_SERVICE_ACCOUNT }}
      - name: Alert on failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          fields: workflow,message
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Built-in benefits
- Tests run automatically (`dbt build` = `dbt run + dbt test`)
- Lineage graph generated (`dbt docs generate`)
- Schema docs first-class (in `.yml` next to model)
- Materialization controlled (view / table / incremental)

### Multi-domain dbt project layout (production-grade pattern)

For projects covering multiple business domains (e.g., event tracking + product analytics + app performance), use the multi-domain layout:

```
my_dbt_project/
├── dbt_project.yml
├── pipeline_config/
│   ├── prod-config-v2.yml      # Production Airflow DAG + dbt run phases
│   └── stg-config-v2.yml       # Staging Airflow DAG
├── models/
│   ├── <domain_1>/             # e.g., "event_tracking"
│   │   ├── sources/            # source table registrations
│   │   ├── staging/            # stg_* models (1-to-1 with source)
│   │   ├── warehouse/          # fct_* / dim_* atomic facts + dimensions
│   │   ├── datamart/           # agg_* / metric_models (pre-aggregated)
│   │   └── pre_test/           # development sandbox (raw_data / view / dwh_data)
│   ├── <domain_2>/             # e.g., "app_performance"
│   │   ├── staging/
│   │   └── warehouse/
│   ├── <domain_3>/             # e.g., "segment_data"
│   │   ├── dwh/
│   │   └── dm/
│   └── <domain_N>/
├── macros/
│   ├── <purpose_1>/            # e.g., "doc_generator"
│   ├── <purpose_2>/            # e.g., "quality_data" (custom data quality)
│   ├── <purpose_3>/            # e.g., "segment"
│   └── <purpose_4>/            # e.g., "event_explorer"
├── tests/
│   ├── <test_group_1>/         # e.g., "detect_abnormal_detail"
│   └── <test_group_2>/         # e.g., "login_testcase"
├── seeds/
├── post_runs/                  # post-run automation (alerts, validation, etc.)
└── docs/
    └── models/                 # rendered docs (autogen)
```

**Per-domain 4-layer pattern:**
```
sources → staging (stg_*) → warehouse (fct_*/dim_*) → datamart (agg_*/metric_*)
```
- **sources**: register raw external tables via `sources:` in yml
- **staging**: light cleaning, 1-to-1 with source, typically materialized as view
- **warehouse**: business-ready atomic models (facts at transaction grain, dims as entities)
- **datamart**: pre-aggregated for dashboard / metric consumption

**Project-level variables (dbt_project.yml `vars:`):**
```yaml
vars:
  # Single-day vars (T-1 = yesterday)
  execute_date: "{{ var('execute_date') }}"           # passed from DAG
  execute_date_yymmdd: "{{ var('execute_date_yymmdd') }}"
  execute_date_yyyymmdd: "{{ var('execute_date_yyyymmdd') }}"
  partition_date: "{{ var('partition_date') }}"

  # Multi-day list (T-3 to T) for sliding-window reprocessing
  execute_date_list:
    - "{{ var('day_t_minus_3') }}"
    - "{{ var('day_t_minus_2') }}"
    - "{{ var('day_t_minus_1') }}"
    - "{{ var('day_t') }}"

  # Alert configuration per environment
  alert_prod:
    alert_hook: "<prod-webhook-url>"
    alert_filter: "singular"
  alert_staging:
    alert_hook: "<staging-webhook-url>"
    alert_filter: "singular"
```

**Default test ownership** (catches the "tests have no owner" problem):
```yaml
tests:
  <project_name>:
    +meta:
      PIC: <default-owner-email-or-handle>
```

**Phased dbt run** (in DAG config, NOT dbt itself):
```yaml
phases:
  - build_staging:
      command: dbt run
      select: "<project>.<domain>.staging.*"

  - build_warehouse:
      command: dbt run
      select: "<project>.<domain>.warehouse.*"

  - build_datamart:
      command: dbt run
      select: "<project>.<domain>.datamart.*"

  - run_tests:
      command: dbt test
      select: "<project>.<domain>.*"
```

Each phase runs in DAG order; failures block downstream phases. Cleaner than 1 monolithic `dbt build` because phase failures are inspectable.

**Incremental mart pattern with backfill window:**
```sql
{{ config(
  materialized = "incremental",
  incremental_strategy = "insert_overwrite",
  partition_by = {"field": "event_date", "data_type": "date"},
  cluster_by = ["dim_1", "dim_2"],
  on_schema_change = "append_new_columns"
) }}

{% set overwrite_days = 3 %}   -- sliding window reprocess
{% set max_window = 30 %}      -- rolling-window measure (e.g. MAU 30-day)

WITH base AS (
  SELECT ...
  FROM {{ ref('stg_xxx') }}
  WHERE event_date BETWEEN
    DATE_SUB(DATE('{{ var("execute_date") }}'), INTERVAL {{ overwrite_days }} DAY)
    AND DATE('{{ var("execute_date") }}')
)
SELECT ... FROM base
```

**DAG sensor pattern** (cross-pipeline dependency):
```yaml
phases:
  - wait_for_upstream:
      job: dag_sensor
      sensor_dag_id: <upstream-dag-id>
      sensor_task_ids:
        - <upstream-task-id>
      timeout: 21600        # 6 hours
      lookback_interval: 82800   # 23 hours

  - build_after_upstream:
      command: dbt run
      select: <models>
```

Apollo-style pattern verified in production at MoMo (multi-domain analytics platform). Pattern is portable to any dbt + Airflow combination.

### Anti-patterns
- Manual `dbt run` instead of `dbt build` → tests skipped
- No `source freshness` → stale source goes undetected
- `--full-refresh` daily on incremental models → cost explosion
- Single flat `models/` folder for multi-domain project → no clear ownership / no domain isolation
- Tests without `+meta: PIC` → broken tests with no one to fix them
- Hardcoded dates in dbt vars → not parameterized by DAG run → can't backfill

---

## Pattern 3 — Cron (Lightweight, Single Job)

### When to pick
- ONE recurring job, no dependencies
- No CI/CD infrastructure
- Small team, single machine / VPS
- Quick prototype before promoting to Airflow

### Anatomy

**Crontab on a server:**
```bash
# crontab -e
# Run my_pipeline.py daily at 6 AM
0 6 * * * cd /path/to/project && /path/to/.venv/bin/python pipeline.py >> logs/cron.log 2>&1

# Run weekly report Mondays at 8 AM
0 8 * * 1 cd /path/to/project && /path/to/.venv/bin/python weekly_report.py
```

**Pipeline script (`pipeline.py`):**
```python
#!/usr/bin/env python
"""Daily pipeline — runs ingest → transform → output → alert."""
import sys
import traceback
from pathlib import Path
from your_pipeline import ingest, transform, output
from your_notifications import send_failure_email

LOG_FILE = Path("logs") / "pipeline_runs.log"

def main():
    try:
        ingest()
        transform()
        output()
        # Append success to log
        with LOG_FILE.open("a") as f:
            f.write(f"SUCCESS: {datetime.now()}\n")
        return 0
    except Exception as e:
        # Send natural-language email
        reason = f"Pipeline failed at step {detect_step(e)}: {e}"
        send_failure_email(reason=reason, traceback=traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### Failure handling
- Catch exception → log + email natural Vietnamese/English reason
- NEVER spam stakeholder; only oncall on fail
- Return non-zero exit code so cron sees failure (for systemd integration)

### Anti-patterns
- No failure alert → silent breakage
- No logging → can't debug
- Run as root → privilege risk
- No idempotency → re-run doubles data

---

## Pattern 4 — GitHub Actions (CI/CD-native)

### When to pick
- Project already on GitHub
- Lightweight workflows (data fits in GitHub runners)
- Team familiar with YAML / GitHub Actions
- Want free orchestration for OSS / small projects

### Anatomy

**`.github/workflows/daily-data-pipeline.yml`:**
```yaml
name: Daily Data Pipeline
on:
  schedule:
    - cron: '0 6 * * *'
  workflow_dispatch:

jobs:
  pipeline:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python pipeline.py
        env:
          DB_USER: ${{ secrets.DB_USER }}
          DB_PASS: ${{ secrets.DB_PASS }}
          API_KEY: ${{ secrets.API_KEY }}
      - name: Upload output
        if: success()
        uses: actions/upload-artifact@v3
        with:
          name: pipeline-output
          path: output/
      - name: Slack alert on failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          channel-id: 'C0123456'
          slack-message: 'Pipeline failed. Check Actions logs.'
        env:
          SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
```

### Benefits
- Free for public repos / generous tier for private
- Secrets management built-in
- Artifact upload built-in
- Alerts via Slack/email integrations
- Version control of pipeline + workflow together

### Constraints
- 6-hour max per job (free tier)
- 2000 minutes / month (free tier private)
- No persistent storage between runs (use S3 / GCS for state)

### Anti-patterns
- Loading 10 GB into runner → fails timeout
- Hard-coded secrets in YAML → leaks on commit
- No `if: failure()` alert step → silent breakage

---

## Pattern 5 — Google Apps Script (Sheet-driven HTML dashboard)

### When to pick
- Input is a Google Sheet (manual upload / Forms response / 3rd-party export)
- Stakeholder-facing dashboard that should auto-refresh when Sheet changes
- Native Google ecosystem (Drive / Sheets / Docs already in use)
- No infrastructure available; need free + zero-ops
- Single-author scenario (analyst owns Sheet + dashboard)

Not for: high-volume data (Sheet ≤ 10M cells); production multi-team workflows; real-time streaming.

### Anatomy

**Input layer:** Google Sheet (any structure — analyst's working sheet, Forms output, or pasted CSV).

**Transform layer:** Apps Script (.gs files bound to the Sheet).

**Output layer:** HTML dashboard published as web app, or HTML email, or embedded iframe.

**Auto-refresh trigger:**
- `onEdit(e)` — fires when user edits Sheet
- `onChange(e)` — fires on structural changes (insert row, etc.)
- Time-driven trigger — `ScriptApp.newTrigger().timeBased().everyHours(1)`

### Starter template

**`Code.gs` (bound to the Sheet):**
```javascript
// Web app entry point
function doGet() {
  const template = HtmlService.createTemplateFromFile('Dashboard');
  template.data = fetchDashboardData();
  return template.evaluate()
    .setTitle('My Dashboard')
    .setSandboxMode(HtmlService.SandboxMode.IFRAME);
}

// Pull data from this Sheet
function fetchDashboardData() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Data');
  const data = sheet.getDataRange().getValues();
  // Transform: header row + rows → object array
  const headers = data.shift();
  return data.map(row => Object.fromEntries(headers.map((h, i) => [h, row[i]])));
}

// On Sheet edit, invalidate cache so next dashboard view recomputes
function onEdit(e) {
  CacheService.getScriptCache().remove('dashboard_data');
}

// Time-driven daily refresh (optional)
function setupDailyRefresh() {
  ScriptApp.newTrigger('refreshDashboard')
    .timeBased()
    .everyDays(1)
    .atHour(6)
    .create();
}

function refreshDashboard() {
  // Recompute any cached aggregates
  const data = fetchDashboardData();
  CacheService.getScriptCache().put('dashboard_data', JSON.stringify(data), 21600);
}
```

**`Dashboard.html` (the rendered template):**
```html
<!DOCTYPE html>
<html>
<head>
  <base target="_top">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
    .kpi-card { display: inline-block; padding: 16px; border-radius: 8px; background: #fdf6ee; margin: 8px; }
    .kpi-value { font-size: 32px; font-weight: bold; color: #d82d8b; }
  </style>
</head>
<body>
  <h1>Dashboard</h1>
  <div id="kpis"></div>
  <canvas id="chart"></canvas>

  <script>
    const data = <?= JSON.stringify(data) ?>;
    // Render KPIs + chart from data
    // ... (chart.js / vanilla JS rendering)
  </script>
</body>
</html>
```

### Deploy steps

1. Open the Google Sheet
2. Extensions → Apps Script (opens editor)
3. Paste `Code.gs` + create `Dashboard.html` file
4. Deploy → New deployment → Web app
5. Execute as: Me / Access: Anyone with link (or restrict to org)
6. Copy web app URL → share with stakeholder

Dashboard updates on every page load by re-querying the Sheet. To force refresh, user reloads the URL.

### GCP / API setup (for Claude-automated workflows)

If user wants Claude to AUTOMATE Apps Script project creation (not just provide code to paste):

**One-time GCP setup (user-driven, manual):**
1. Go to https://console.cloud.google.com/
2. Create new project (or use existing): `my-analytics-automation`
3. Enable APIs (APIs & Services → Library):
   - Google Sheets API
   - Google Drive API
   - Apps Script API (key one — enables programmatic .gs management)
4. Create OAuth 2.0 Client ID (APIs & Services → Credentials):
   - Application type: Desktop app
   - Download `credentials.json`
5. Save `credentials.json` to a known path in user's workspace

**Per-session OAuth flow (Claude runs):**
- Read `credentials.json`
- Run OAuth flow → user grants permissions in browser → token saved as `token.pickle`
- All future runs use cached token (refresh transparently)

**Reference Python helper** (if user has `shared/google/` infrastructure):
```python
from shared.google.auth_helper import build_drive, build_sheets, build_apps_script

drive = build_drive()
sheets = build_sheets()
apps_script = build_apps_script()  # Apps Script API client

# Programmatically create Apps Script project bound to a Sheet
script_project = apps_script.projects().create(body={
    'title': 'Dashboard Auto',
    'parentId': sheet_id  # ← binds to this Sheet
}).execute()

# Update script content
apps_script.projects().updateContent(
    scriptId=script_project['scriptId'],
    body={'files': [
        {'name': 'Code', 'type': 'SERVER_JS', 'source': code_gs_content},
        {'name': 'Dashboard', 'type': 'HTML', 'source': dashboard_html_content}
    ]}
).execute()
```

**If user does NOT want Claude automation:**
- Provide the `Code.gs` + `Dashboard.html` code as files
- Step-by-step manual paste instructions (Extensions → Apps Script → paste → deploy)
- ~5-10 min manual setup; Sheet owner keeps full control

### Pros
- Free (within Google Workspace quota)
- Native Google ecosystem (no auth indirection for end users)
- Real-time-ish (refreshes on page load = always current)
- No infrastructure / no server / no DevOps
- Sheet owner controls data + dashboard in 1 place
- Easy to share (just URL)

### Cons
- Execution limits: 6 min per script run (free) / 30 min (Workspace)
- 50 simultaneous users max per Web App
- Not for large data (Sheet capped at 10M cells)
- Apps Script editor limited (no proper IDE)
- No multi-environment (dev / staging / prod) — single Sheet = single env
- Hard to version-control (no git integration native)

### Anti-patterns
- Trying to pump 100M-row dataset through Apps Script → fails timeout
- Hard-coded Sheet IDs in script → breaks when Sheet copied
- No error handling on `fetchDashboardData()` → blank dashboard on bad data
- Long-running computation in `onEdit` → blocks user editing
- Public web app with sensitive data → IAM leak

### When to graduate beyond Apps Script
- Data volume exceeds Sheet capacity
- Need multiple concurrent users / production SLA
- Multi-team workflow (separate dev/staging/prod)
- Need version control + CI/CD

Migration path: Apps Script prototype → identify pipeline stages → port to dbt (transform) + Airflow (orchestration) + lightweight HTML/Streamlit (dashboard).

---

## Hybrid common pattern

Most production stacks are NOT pure one-pattern. Common:

```
[Cron / GitHub Actions]
  └── triggers daily
       │
       ↓
  [Airflow DAG]
    Phase 1: Ingest raw (Python tasks via BigQueryOperator)
    Phase 2: Transform (dbt task running `dbt build`)
    Phase 3: Output (Python task: build report, push to slack)
    Phase 4: QC (dbt test + custom assertions)
       │
       ↓ on success
  [Trigger downstream DAG] (for dashboard refresh, attribute export, etc.)
```

Or simpler for small teams:
```
[GitHub Actions cron]
  └── runs `dbt build` daily
  └── alerts on failure via Slack
```

## Cross-references
- Modeling that feeds orchestrator: `mode-model.md`
- Failure-alerting discipline: `mode-automate.md`
- Cost discipline (BQ-specific): `mode-query.md`
- dbt details: external — `DBT-learn.md` in user's reference folder

— part of prof-data-analyst · Loc Tu, 2026
