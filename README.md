# prof-data-analyst v3.3

> Professional Data Analyst + Analytics Engineer workflow as a Claude Code plugin. **9 routable modes**, 14 stdlib scripts, 14 method specs (causal + validation), 4 mandatory rules + **Proactive Suggestion at Mode Exit**, planning protocol (TH1/TH2), 4 data modeling patterns, 6-section governance, **5 orchestration patterns** (Airflow/dbt+GHA/cron/GitHub Actions/Google Apps Script), 5-tier schema-source hierarchy, portable semantic-layer recipe, visualization discipline (SWD), 8-category suggestion protocol. 1-stop-shop end-to-end DA harness with **proactive capability discovery** — solves the "you don't know what you don't know" gap.

## Install

Claude Code marketplaces follow a **2-step pattern** (analogous to `apt-add-repository` then `apt install`):

```bash
# Step 1 — Register the marketplace (once per machine)
/plugin marketplace add loctu0402/prof-data-analyst

# Step 2 — Install the plugin from that marketplace
/plugin install prof-data-analyst@loctu-marketplace

# Verify
/plugin list
# → prof-data-analyst v3.3.0 should appear
```

**Both steps required.** If `/plugin install` returns `Marketplace "loctu-marketplace" not found`, Step 1 was skipped — re-run it first.

**Update to latest version** (after a new release):
```bash
/plugin update prof-data-analyst@loctu-marketplace
```

**Uninstall**:
```bash
/plugin uninstall prof-data-analyst
/plugin marketplace remove loctu-marketplace   # optional, if you want to drop the registry too
```

After install, the 10 slash commands are namespaced:

```bash
/prof-data-analyst:da             # entry — confirm intent, route to mode
/prof-data-analyst:da-frame       # NEW v3.1 — Business Understanding → Metric Define → Data Plan
/prof-data-analyst:da-model       # NEW v3.1 — Data modeling (Kimball/dbt/Medallion/DuckDB)
/prof-data-analyst:da-query       # NL→SQL workflow
/prof-data-analyst:da-process     # raw → staged → cleaned → mart → ML-ready
/prof-data-analyst:da-insight     # hypothesis → diagnostic → recommendation
/prof-data-analyst:da-automate    # pipeline + fail-alert (Airflow/dbt/cron/GHA)
/prof-data-analyst:da-report      # stakeholder deliverable + storyline pattern
/prof-data-analyst:da-review      # 4 tiers (A0 Brief / A Polish / B Full / C Stakeholder Q)
/prof-data-analyst:da-fix         # surgical pipeline / report debug
```

## 9-mode workflow tour

The standard end-to-end DA flow: **Frame → Model → Query → Process → Insight → Automate → Report**, plus orthogonal **Review** + **Fix-pipeline**.

| Mode | What it does | When to invoke |
|------|--------------|----------------|
| **frame** *(v3.1)* | Business Understanding → Metric Define → Data Plan (TH1 schema-exists / TH2 brainstorm-modeling) → Lock in PLANNING.md | "frame project", "metric define", "không biết bắt đầu", `/da-frame` |
| **model** *(v3.1)* | 4 data modeling patterns (Kimball / dbt staging→marts / Medallion / DuckDB layered) + Table Contracts + governance hooks | "data modeling", "build pipeline mới", "design DWH", `/da-model` |
| **query** | Engine-agnostic NL→SQL with BQ Safety Protocol + Query Logic Card | "viết SQL", "lấy data", `/da-query` |
| **process** | Raw → staged → cleaned → mart with 6-step EDA + Executive Summary per phase | "EDA notebook", "feature engineering", `/da-process` |
| **insight** | Causal-method matching + 5-stage reasoning chain + anti-bias | "phân tích insight", "why X", `/da-insight` |
| **automate** | Pipeline + fail-alert wiring + cache discipline + 4-orchestrator decision (Airflow/dbt+GHA/cron/GitHub Actions) | "automation", "schedule job", `/da-automate` |
| **report** | Stakeholder report from template + chart anatomy + dual-comparison KPIs + storyline pattern | "build báo cáo", "stakeholder report", `/da-report` |
| **review** | 4 tiers — A0 Brief (5min snapshot) / A Polish (15-30min) / B Full (1-3hrs audit) / C Stakeholder Q | "review report", "OK chưa", "audit project", `/da-review` |
| **fix** | Surgical pipeline / report debug with patch-ceiling escalation | "fix pipeline", "report sai", `/da-fix` |

### Front-of-workflow planning (v3.1 highlight)

```
[da-frame]
  Gate 1: Business Understanding (5W1H + stake + audience)
  Gate 2: Metric Define (pick framework: NSM/OMTM/Growth Loop/HEART... + 10-field contract)
  Gate 3: Data Plan
    TH1 (data exists)        → verify schema + sample query < $0.10
    TH2 (data missing)       → domain discovery + pick modeling pattern
  Gate 4: Lock PLANNING.md + route to next mode

[da-model]  (only if TH2 in Gate 3, or existing pipeline lacks structure)
  Pattern 1: Kimball Star/Snowflake     (cloud DWH, BI workload)
  Pattern 2: dbt staging → marts        (modular SQL, tests + lineage built-in)
  Pattern 3: Medallion Bronze/Silver/Gold (lakehouse, full audit trail)
  Pattern 4: DuckDB layered             (local files, rapid prototyping)
  → Schema documentation (Table Contracts) MANDATORY per table
  → Governance hooks planned (6-section practical framework)
```

## 4 mandatory universal rules

1. **Orientation Block** — every deliverable opens with SCQR / 3-line intro / module docstring
2. **Baseline → Noise → Impact Ladder** — every numeric statement passes 3 rungs (baseline + noise check + impact verdict)
3. **5W1H Action Brief** — every recommendation has 8 fields filled
4. **Why-Explanation (META)** — every action / method / threshold / tool choice has inline Why (Causal / Empirical / Comparative / Theoretical / Operational)

## 14 stdlib scripts

```
scripts/
├── stats/      effect_size, significance, mde_sample_size, baseline_noise_impact, bootstrap_ci, multiple_testing
├── causal/     did_event_study, parallel_trends_test
├── format/     number_format
└── validators/ orientation_block, action_brief, ai_tell_scan, rubric_audit, method_maturity_audit, self_check
```

Script-over-agent-compute is a hard rule: NEVER inline statistical work, always call a script.

## 14 method specs

```
references/methods/
├── _template.md           # canonical W/H/W/W/W/W structure
├── _index.md              # router
├── did.md                 # Difference-in-Differences
├── event_study.md         # Event Study
├── rdd.md                 # Regression Discontinuity
├── synthetic_control.md   # Synthetic Control
├── psm.md                 # Propensity Score Matching
├── iv.md                  # Instrumental Variable / 2SLS
├── bootstrap_ci.md        # Bootstrap CI
├── robustness_checks.md   # Robustness across specs
├── sensitivity_analysis.md # Sensitivity to parameter
├── falsification_tests.md # Placebo / zero-effect
├── multiple_testing.md    # Bonferroni / BH-FDR
├── post_hoc_power.md      # Power at MDE
├── cross_validation.md    # K-fold CV
└── pre_registration.md    # Lock plan before EDA
```

Each spec follows a 12-section template (Overview / What / How / Why-5-types / When / Where / Who / Acceptance gate / Template / Worked example / Anti-patterns / Cross-references / Reading order) and cites a primary source (Angrist-Pischke, Imbens-Rubin, Efron-Tibshirani, Benjamini-Hochberg, etc.).

## 3 sub-agents (LEAN architecture)

Sub-agents are spawned only when value > cost. Most work runs in the main agent + the loaded mode skill.

- **da-orchestrator** (Sonnet) — session-start intent confirmation + plan review + final-review gate
- **da-context-tracer** (Haiku) — multi-file reads for `/da-review` Sub-mode B Phase 2 (when project ≥ 5 files)
- **da-method-auditor** (Sonnet) — `/da-review` Sub-mode B Pass 3 causal-method judgment (when causal claims present)

## Quality framework

- **5 Quality Criteria** (Interconnect / Compact / Insightful / Sufficient / Logical Reason) at review gate
- **5-Gate Quality Pipeline** (Scope → Data → Analysis → Viz+Story → Review) with max 3 retries per gate
- **Outline / Story Flow Check** at every review pass (extract headings standalone, verify story is followable)
- **Sub-agent prompt discipline** (anti-shortcut + handoff drift + fresh-session + context-packet)

## Visualization discipline (v3.3)

Every chart / dashboard / slide goes through a 6-lesson visualization framework + 5-rule cheatsheet + 10 anti-pattern checklist:
1. **Action title** — chart title states a conclusion, not a topic
2. **Grey + 1 accent** — neutral grey default; one accent on focal entity
3. **No pie, no 3D** — horizontal bar > pie; 2D > 3D; slopegraph for 2-point trends
4. **Clutter checklist** — strip border / heavy gridlines / redundant legend / 3D / shadow / gradient
5. **Horizontal logic** — page titles read in order form a Setup → Conflict → Resolution story

Full reference: `references/storytelling-with-data.md` (preattentive attributes, Z/F reading patterns, Gestalt principles, pre-ship checklist).

## Schema discovery + semantic layer (v3.3)

5-tier hierarchy for table schema + access discovery: **T0** owner-curated LLM tag → **T1** catalog tool direct API → **T2** access-aware metadata MCPs (per-user access scope + semantic cube + documentation) → **T3** INFORMATION_SCHEMA + brainstorm with user → **T4** sampling. See `references/schema-source-hierarchy.md`.

Portable 6-phase recipe for building a semantic layer from scratch (engine-agnostic — Cube.js / dbt-metrics / LookML / MetricFlow): `references/semantic-layer-setup.md`.

## Engine-agnostic by design

The plugin treats specific engines as replaceable adapters:
- SQL engine: BQ / Postgres / Snowflake / Redshift / DuckDB
- Semantic layer: Cube.js / dbt-metrics / LookML / org-specific
- Notification channel: SMTP / Slack / Teams / PagerDuty / internal module
- Cron / scheduler: Airflow / Dagster / Prefect / crontab / GitHub Actions / Claude /loop / Claude /schedule

Workspace-specific configuration (project IDs, credentials, brand themes) lives OUTSIDE the plugin — in env vars, config files, or workspace docs.

## Optional org-specific extensions

For users at MoMo: a dedicated reference + example MCP config bundle access to Semantic Cube, momo-data MCP (Semantic Cube + Data Portal + Journey Data + Apollo), mimir MCP (NL→SQL + tag namespace), and OpenMetadata curation. See `references/momo-extensions.md` and `mcp/example-momo-mcp.json`. Non-MoMo users can ignore — the plugin works without them.

## License

MIT — see `LICENSE`.

## Author

Method by **Loc Tu** (loctu) · 2026. Distilled from personal practice.

Primary sources cited per method spec (see `references/methods/<name>.md` Reading order section).
