# Changelog

All notable changes to `prof-data-analyst` plugin.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [3.3.0] — 2026-05-18

Minor release: schema-discovery hierarchy + portable semantic-layer recipe + visualization discipline + optional org-specific extensions.

### Added
- **`references/schema-source-hierarchy.md`** — 5-tier ladder: T0 owner-curated LLM tag → T1 catalog tool direct API → T2 access-aware metadata MCPs (per-user-access-filtered) → T3 INFORMATION_SCHEMA + brainstorm with user → T4 sampling. Decision tree, per-tier rationale, audit-vs-trust matrix. T2 placement rationale: T1 catalog API and T3 INFORMATION_SCHEMA both show what the org has, not what the current user can use; access-aware MCPs bridge that gap and bundle multiple metadata sources (catalog + semantic cube + documentation) in one user-scoped interface.
- **`references/semantic-layer-setup.md`** — Portable 6-phase recipe (Discovery → Architecture → Foundation cube template → Layered modeling → Pre-aggregation → Delivery+Governance → Operate). Engine-agnostic (Cube.js / dbt-metrics / LookML / MetricFlow).
- **`references/storytelling-with-data.md`** — Visualization discipline: 6 lessons (Context / Visual / Clutter / Focus / Designer / Story) + 5-rule cheatsheet (action title, grey + 1 accent, no pie / no 3D, clutter checklist, horizontal logic) + preattentive attribute cookbook + Z-pattern + Gestalt application + 10 anti-patterns + per-chart and per-deck pre-ship checklists.
- **`references/momo-extensions.md`** — Optional org-specific extension file: Semantic Cube (Synmetrix + Cube.js), MoMo unified data MCP gateway (semantic / data-portal / journey / apollo tool groups), Mimir NL→SQL MCP + tag namespace, OpenMetadata API+PAT curation playbook. Non-MoMo users ignore.
- **`mcp/example-momo-mcp.json`** — Drop-in MCP server config snippet for `~/.claude.json` user scope (momo-data + mimir-da-sql). CLI install commands included.

### Changed
- **`references/mode-query.md` Step 0 — Request Intake** (NEW) — Pre-flight phase BEFORE schema discovery. Restate question + surface implicit choices (grain / cohort / aggregation / dedup / window / comparison / breakdown) + propose calculation logic in plain language + suggest 1-2 extensions + user-confirm gate. Documents skip conditions (explicit SQL provided, repeat query, pipeline-internal, fully-atomic ask). Encodes the senior-DA pattern of "structure the question before structuring the answer".
- **`references/mode-query.md` Step 2** — Discovery refactored to 5-tier schema-source hierarchy with cross-reference to new references.
- **`references/mode-report.md` Step 5** — Hooked SWD discipline into body-population: every chart follows action title + grey + 1 accent + clutter checklist + horizontal logic.
- **`references/style-rules.md`** — Added "Visualization discipline (Storytelling with Data)" callout above Chart Anatomy section. 5-rule cheatsheet inline + pointer to full reference.
- **`references/mode-process.md`** — Documented 3 entry granularities: Full pipeline / Quality Audit only / Cleaning only. Trigger phrases expanded to cover "data audit", "data quality", "quality check", "kiểm tra data", "clean data", "data cleaning". Process mode is now the standard discoverable entry for standalone data quality work.
- **`references/mode-frame.md`** — Added "Mid-stream Gate 2 standalone" sub-mode. Allows running Gate 2 (Metric Define) alone when project context already exists and only the metric question needs resolving, without forcing a full 4-gate Frame run.
- **`references/mode-model.md`** — Added "Schema Evolution" section. 9-row safe-migration recipe (add column / rename / drop / split / merge / type change / grain change / partition-key change) with 7 discipline rules + 4 anti-patterns.
- **`references/mode-automation.md`** — Added "Backfill Workflow" section. Decision tree (why → cost → idempotency → lower-bound preservation → cross-validation), 4 execution patterns (`--backfill-from` / chunked / shadow / full rebuild) + 5 anti-patterns.
- **`SKILL.md` "Where to Read Next" + mode router** — Added pointers to schema-source-hierarchy, semantic-layer-setup, momo-extensions, storytelling-with-data. Process mode router row updated with data quality trigger phrases.
- **`commands/da-process.md`** — Updated to surface 3 entry granularities at command-invocation time.
- **`README.md`** — Bumped to v3.3; added Visualization discipline section + Schema discovery + semantic layer section + Optional org-specific extensions section.

## [3.2.2] — 2026-05-15

Patch release: storyline pattern refinement (question-based framing pre-step).

### Added
- **Question-based framing pre-step in `mode-report.md` Step 5 storyline section** — agent drafts `[Q] [A] [Why]` triplet per section BEFORE writing slide title. [Q] = stakeholder question the section answers; [A] = the storyline title that answers it; [Why] = 1-line rationale per Rule 4 (Causal/Empirical/Comparative/Theoretical/Operational). Only [A] appears on slide; [Q] and [Why] stay in working notes. Updated storyline checklist to require Section Question drafted + Why-Explanation logged per section.

### Why
Storyline titles without explicit question framing risk being decoration rather than communication. Question-based pre-step makes (a) why-the-slide-exists legible, (b) predicted result visible before chart-building, (c) action implied because the question is decision-shaped. Aligns with consulting practice (draft question first, then answer, then chart).

## [3.2.1] — 2026-05-15

Patch release: 2 foundational additions. No new modes / agents / breaking changes.

### Added — Section 0 in `metric-framework.md` (KPI Framework foundation)
- `0.1 Definition + Formula`: KPI = Metric × Goal
- `0.2 5-criterion "must"` checklist (tied to business goal / influences decisions / drives action / clear owner / tracked consistently)
- `0.3 From Data to KPI` 4-step protocol
- `0.4 Good vs Bad KPIs` (Vanity vs Actionable)
- `0.5 Think Like a Data Analyst` (4 design principles)
- `0.6 KPI Stress Test` — 3 archetype questions for self-audit (Product Thinking / KPI Judgment / Problem Solving 5-step diagnostic descent)
- `0.7 Workflow plug-in points` (`da-frame` Gate 2, `da-review` Sub-mode B Pass 2, pre-ship stress test)

### Added — Multi-domain dbt project layout in `orchestration-patterns.md` Pattern 2
Portable multi-domain pattern. No proprietary code or credentials.

- 4-layer per domain: `sources → staging (stg_*) → warehouse (fct_*/dim_*) → datamart (agg_*/metric_*)`
- Project-level `vars:` for execute_date (T, T-1, T-3) + partition_date + multi-day sliding-window lists + alert hooks (prod / staging separated)
- Default test ownership via `+meta: PIC: <owner>`
- Phased `dbt run` (build_staging → build_warehouse → build_datamart → run_tests) in DAG config, NOT in dbt itself
- Incremental mart pattern: `insert_overwrite + partition_by + cluster_by + on_schema_change="append_new_columns"` + sliding window via `overwrite_days` set var
- DAG sensor pattern for cross-pipeline dependency
- 6 anti-patterns added (manual dbt run vs build / no source freshness / full-refresh daily / flat models folder / tests without owner / hardcoded dates)

### Changed
- `metric-framework.md` "Overview" updated to mention 4 sections (KPI Framework foundation / decision table / per-framework deep dive / design protocol)
- Plugin v3.2.0 → v3.2.1

## [3.2.0] — 2026-05-15

Additive release: proactive capability discovery — plugin suggests extensions at mode exit instead of waiting for the user to read overview docs.

### Added
- **`references/suggestion-protocol.md`** — 3-step Suggestion Loop: detect context (mode + data source + output format + available MCPs + stakeholder hints) → map to 8 extension categories (data source / automation / quality validation / method upgrade / audience / format / downstream / MCP tooling) → propose with opt-in phrasing. Includes 3 worked examples + per-mode default top-3 fallback.
- **`orchestration-patterns.md` Pattern 5 — Google Apps Script** — Sheet-driven HTML dashboard with auto-refresh. Starter `Code.gs` + `Dashboard.html` template. GCP project + API setup guide + step-by-step manual deploy. Pros / cons / anti-patterns / graduation-path documented.
- **`SKILL.md` new Core Operating Principle: "Proactive Suggestion at Mode Exit"** — codified alongside Script-over-Agent-Compute / Progressive Disclosure / Portable First.
- **`agents/da-orchestrator.md` Exit Suggestion gate** — after final-review verdict (SHIP / FIX / REBUILD), orchestrator runs Suggestion Loop with hard rules (MAX 3 / cite trigger / 1-line Why per Rule 4 / effort estimate / explicit OUT path).

### Changed
- Plugin description: "5 orchestration patterns" (was 4) + "proactive capability discovery" added
- Marketplace description updated to highlight suggestion protocol
- `orchestration-patterns.md` decision table now lists 5 patterns + hybrid note about Apps Script for stakeholder dashboards
- SKILL.md "Where to Read Next" adds "Proactive capability discovery" subsection
- New keywords: `apps-script`, `google-sheets`, `proactive-suggestion`, `capability-discovery`

### Why
Users cannot discover full plugin capability by passively reading overview docs. Proactive suggestion at mode exit (vs. dumping all features upfront) lets the user see relevant options when they have working context to evaluate them. Pattern adapted from consulting: after deliverable, propose "what's next" rather than handing over and walking away.

## [3.1.0] — 2026-05-15

Additive release: front-of-workflow planning + data engineering hooks + brief-tier review.

### Added
- **2 new modes:** `da-frame` (Business Understanding → Metric Define → Data Plan TH1/TH2 → Lock & Hand-off) + `da-model` (4 data modeling patterns: Kimball / dbt staging→marts / Medallion / DuckDB layered)
- **6 new reference files:**
  - `references/mode-frame.md` — Frame mode (4-gate workflow)
  - `references/mode-model.md` — Model mode (4 patterns + Table Contract template + governance hooks)
  - `references/planning-protocol.md` — Gate-by-gate protocol: Business Understanding / Metric Define / Data Plan TH1 (schema-exists) vs TH2 (brainstorm + modeling) / Lock & Hand-off
  - `references/metric-framework.md` — 8 frameworks (NSM / OMTM / Growth Loop / HEART / Diagnostic / Counter-metric / AARRR / Unit Economics) + 10-step KPI design protocol
  - `references/governance.md` — 6-section practical framework (Metric & Definition / Modeling & Grain / Quality & Validation / Access & Privacy / Reporting & Consumption / Mindset) + STAR example + 5-implementation starter checklist
  - `references/orchestration-patterns.md` — 4 patterns (Airflow with TaskGroup + DagSensor + alerts / dbt + Cloud or GitHub Actions / Cron / GitHub Actions) + hybrid pattern + decision table
- **Sub-mode A0 (Brief tier)** in `/da-review`: 5-min snapshot — rubric_audit + outline check + 1-paragraph Ship / Fix / Rebuild verdict. Solves review overbloat (previously every review defaulted to A or B; A0 gives quick verdict for low-stakes / non-academic case).
- **Storytelling pattern** added to `mode-report.md` Step 5: storyline > dashboard; complete-sentence slide titles; conclusion-led headlines.
- **Orchestration pointer** added to `mode-automation.md` Schedule Layers: decision table + cross-ref to `orchestration-patterns.md`.
- **2 new commands:** `/prof-data-analyst:da-frame` + `/prof-data-analyst:da-model`.

### Changed
- Plugin description updated to "Professional Data Analyst + Analytics Engineer plugin — 9 routable modes"
- Mode router in `SKILL.md` updated: 7 → 9 modes (added Frame + Model); review mode now lists 4 tiers (A0 Brief / A Polish / B Full / C Stakeholder Q)
- Where to Read Next section organized: Core / Quality / Narrative / Methods / Front-of-workflow planning / Data engineering hooks / Sub-agent / Mode-specific

### Fixed
- `scripts/validators/method_maturity_audit.py` CLI error message: distinguished "path doesn't exist" vs "file passed instead of directory" with friendly hints.

### Architecture decisions
- **LEAN agents unchanged** (3 max): orchestrator + context-tracer + method-auditor. No new agents for new modes — modes are SKILLS, not agents.
- **Tier-based review** solves overbloat without removing capability — user picks detail level per task.
- **Frame + Model as 1 continuum** (planning → modeling), not 2 isolated modes.
- **References > separate files for thin topics**: storytelling stays inside `mode-report.md`; schema-doc stays inside `mode-model.md`; no fragmentation.

## [3.0.0] — 2026-05-14

First plugin-format release.

### Added
- Plugin manifest at `.claude-plugin/plugin.json` + marketplace entry at `.claude-plugin/marketplace.json`
- ROOT skill `prof-data-analyst` with 4 universal rules (Orientation / Baseline-Noise-Impact / 5W1H / Why-Explanation META) + 14 stdlib scripts
- 7 mode skills: `da-query` / `da-process` / `da-insight` / `da-automate` / `da-report` / `da-review` / `da-fix`
- 3 sub-agents: `da-orchestrator` (Sonnet, session-start + final-review gate) + `da-context-tracer` (Haiku, multi-file reads for Sub-mode B Phase 2) + `da-method-auditor` (Sonnet, Sub-mode B Pass 3 causal-method judgment)
- 8 slash commands: `/prof-data-analyst:da` + 7 mode-specific commands
- 5 new reference files: `subagent-prompt-discipline.md`, `quality-criteria.md` (5 Quality Criteria framework), `quality-pipeline.md` (5-Gate Quality Pipeline), `narrative-template.md` (SCQR + Key Terms + Impact Cards), `domain-discovery-protocol.md` (L1/L2/L3 hub generation)
- 14 method spec files under `references/methods/`: causal family (DiD, Event Study, RDD, Synthetic Control, PSM, IV) + validation family (Bootstrap CI, Robustness Checks, Sensitivity Analysis, Falsification Tests, Multiple Testing, Post-Hoc Power, Cross-Validation, Pre-Registration). Each follows canonical `_template.md` structure with primary source citations.
- `methods/_template.md` canonical W/H/W/W/W/W structure + `methods/_index.md` router
- LICENSE (MIT) + README + CHANGELOG

### Changed
- Refactored `causal-inference-toolkit.md` to decision table + 1-paragraph per method + pointer to `methods/<name>.md`
- Refactored `validation-evaluation-methods.md` to decision table + summary + pointer
- `/da-review` split into 3 sub-modes (Sub-mode A Delivery Refine, Sub-mode B Full Project Refine, Sub-mode C Stakeholder Questioning) with explicit option choice at invocation
- Added Outline / Story Flow Check to self-check-protocol Section A2 + mode-review Phase 3.5 + Sub-mode B Pass 6
- Added BQ Safety Protocol (5-gate) + Query Logic Card audit trail to `mode-query`
- Added 6-Step EDA Sequence + Source-pending discipline to `mode-process`
- Added Hypothesis 3 traps (n_T verification, multi-outcome DiD, wrong-sign reframe) to `mode-insight`
- Added Dual-Comparison Mandate + Chart Anatomy 7-element + Sentiment Color context override to `style-rules`
- Added Code Output ≠ Professional Deliverable rule to `coding-discipline`
- Added OLS anomaly window special case to `validation-evaluation-methods`
- Added HTML SPA structural inspection (Step 7.5) to `mode-report`
- Added Max 3 iteration ceiling + Fresh-session review discipline to `mode-review`

### Architecture decisions
- LEAN agent architecture (3 agents max). Workflow lives in SKILLS, not agents. Sub-agents spawned only when value > cost.
- Skills do the workflow; agents support specific gates (orchestration / context-tracing / method-auditing).
- Engine-agnostic SQL workflow (BQ / Postgres / Snowflake / Redshift / DuckDB).
- Progressive disclosure: SKILL.md lean; mode references load on demand; method specs load on demand.
