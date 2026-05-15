# Changelog

All notable changes to `prof-data-analyst` plugin.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [3.2.2] — 2026-05-15

Patch release: storyline pattern improvement (question-based framing pre-step) surfaced from random-scenario demo walkthrough.

### Added
- **Question-based framing pre-step in `mode-report.md` Step 5 storyline section** — agent MUST draft `[Q] [A] [Why]` triplet per section BEFORE writing slide title. [Q] = stakeholder question this section answers; [A] = the storyline title that answers it; [Why] = 1-line Why per Rule 4 (Causal/Empirical/Comparative/Theoretical/Operational). Only [A] appears on slide; [Q] and [Why] stay in working notes. Worked example added (weekly sales report, 4 sections). Updated storyline checklist to require Section Question drafted + Why-Explanation logged per section.

### Why
Surfaced during random-scenario demo walkthrough (CSV → weekly dashboard for non-technical manager). Loc observed: storyline titles still risk being decoration without explicit question framing. Q-based pre-step makes (a) why-the-slide-exists legible, (b) predicted result visible before chart-building, (c) action implied because question is decision-shaped. Aligns with McKinsey/BCG/Bain consulting playbook: draft question first, then answer, then chart.

### Demo reference
Walkthrough captured as atom note at `notes/loctu-pkm/3-projects/prof-data-analyst-demo-csv-dashboard.md` (≤300 lines per llm-wiki contract). Linked from skill overview `prof-data-analyst.md` under new "Demo cases" section. Future demos: 1 per month, random scenario rotation, as stress test for unused/broken plugin paths.

## [3.2.1] — 2026-05-15

Patch release: codify 2 references that v3.2 initially skipped per advisor scope-prune. Both add foundational content with zero new modes / agents / breaking changes.

### Added — Section 0 in `metric-framework.md` (KPI Framework foundation)
Source: Data Analytics Series, @bitesbybytes. 5-slide framework packaged as the rule layer beneath framework selection (NSM / OMTM / etc. are ways to ORGANIZE KPIs; Section 0 is the rule for what makes a metric BE a KPI).

- `0.1 Definition + Formula`: KPI = Metric × Goal (most dashboards show numbers, few drive decisions — the Goal column is the difference)
- `0.2 5-criterion "must"` checklist (tied to business goal / influences decisions / drives action / clear owner / tracked consistently)
- `0.3 From Data to KPI` 4-step protocol (Define Objective → Choose Metric → Make it KPI → Drive Action; cycle)
- `0.4 Good vs Bad KPIs` (Vanity vs Actionable): Same-data-different-thinking example (Traffic ↑40% + Conversions ↓ → Vanity says "growing"; KPI says "funnel problem")
- `0.5 Think Like a Data Analyst` (4 design principles: Ask Right Question / Tie to Goal / Make it Clear / Predict + Report)
- `0.6 KPI Stress Test` — 3 archetype questions for self-audit (Product Thinking / KPI Judgment / Problem Solving 5-step diagnostic descent)
- `0.7 Workflow plug-in points` (`da-frame` Gate 2, `da-review` Sub-mode B Pass 2, pre-ship stress test)

### Added — Multi-domain dbt project layout in `orchestration-patterns.md` Pattern 2
Multi-domain pattern derived from production dbt project structure. Generic / portable / NO company-specific code or credentials.

- 4-layer per domain: `sources → staging (stg_*) → warehouse (fct_*/dim_*) → datamart (agg_*/metric_*)`
- Project-level `vars:` for execute_date (T, T-1, T-3) + partition_date + multi-day sliding-window lists + alert hooks (prod / staging separated)
- Default test ownership via `+meta: PIC: <owner>` (catches the "tests have no owner" anti-pattern)
- Phased `dbt run` (build_staging → build_warehouse → build_datamart → run_tests) in DAG config, NOT in dbt itself (cleaner failure inspection)
- Incremental mart pattern: `insert_overwrite + partition_by + cluster_by + on_schema_change="append_new_columns"` + sliding window via `overwrite_days` set var
- DAG sensor pattern for cross-pipeline dependency (wait for upstream DAG + task before downstream dbt build)
- 6 anti-patterns added (manual dbt run vs build / no source freshness / full-refresh daily / flat models folder / tests without owner / hardcoded dates)

### Why these added (vs v3.2 skip)
Loc's correction: "pattern extraction is learning, not data leak". Apollo gitlab pattern is portable knowledge (4-layer per domain, phased run, default PIC ownership) usable on ANY multi-domain dbt project — no proprietary code included. Same for metric-plan 5 jpg: framework is foundational rule for KPI design, not optional decoration.

### Changed
- `metric-framework.md` "Overview" updated to mention 4 sections (KPI Framework foundation / decision table / per-framework deep dive / design protocol)
- Plugin v3.2.0 → v3.2.1 (patch — no breaking change)

## [3.2.0] — 2026-05-15

Additive release: solves the "you don't know what you don't know" capability discovery problem. Plugin now proactively suggests extensions at mode exit instead of passively waiting for user to read overview docs.

### Added
- **`references/suggestion-protocol.md`** (~280 lines) — 3-step Suggestion Loop: detect context (4 signals: mode + data source + output format + available MCPs + stakeholder hints) → map to 8 extension categories (data source / automation / quality validation / method upgrade / audience / format / downstream / MCP tooling) → propose with opt-in phrasing. Includes 3 worked examples (TTT report, simple-correlation insight, DuckDB prototype) + per-mode default top-3 fallback.
- **`orchestration-patterns.md` Pattern 5 — Google Apps Script** (~150 lines): Sheet-driven HTML dashboard with auto-refresh. Starter `Code.gs` + `Dashboard.html` template. GCP project + API setup guide for Claude-automated workflows OR step-by-step manual deploy. Pros/cons/anti-patterns/graduation-path documented.
- **`SKILL.md` new Core Operating Principle: "Proactive Suggestion at Mode Exit"** — codifies the discovery rule alongside Script-over-Agent-Compute / Progressive Disclosure / Portable First.
- **`agents/da-orchestrator.md` Exit Suggestion gate** — after final-review verdict (SHIP / FIX / REBUILD), orchestrator now runs Suggestion Loop with hard rules (MAX 3 / cite trigger / 1-line Why per Rule 4 / effort estimate / explicit OUT path).

### Changed
- Plugin description: "5 orchestration patterns" (was 4) + "proactive capability discovery" added
- Marketplace description updated to highlight suggestion protocol
- `orchestration-patterns.md` decision table now lists 5 patterns + hybrid note about Apps Script for stakeholder dashboards
- SKILL.md "Where to Read Next" adds "Proactive capability discovery (v3.2 — new)" subsection
- New keywords: `apps-script`, `google-sheets`, `proactive-suggestion`, `capability-discovery`

### Why
- Field test 2026-05-15: Loc observed superpowers plugin has same issue — users can't discover full capability via passive overview reading. "You don't know what you don't know" is a real cost: shipped static reports without realizing event-tracking / auto-refresh / Apps Script / alert options existed.
- Proactive suggestion at exit (vs. dump 8 features upfront) lets user see relevant options when they have working context to evaluate them.
- Pattern adapted from consulting: after deliverable, propose "what's next" — never just hand over and walk away.

## [3.1.0] — 2026-05-15

Additive release: front-of-workflow planning + data engineering hooks + brief-tier review. Solves "review overbloat" feedback (Loc field-test 2026-05-15) + expands plugin to all-in-one DA + Analytics Engineer harness.

### Added
- **2 new modes:** `da-frame` (Business Understanding → Metric Define → Data Plan TH1/TH2 → Lock & Hand-off) + `da-model` (4 data modeling patterns: Kimball / dbt staging→marts / Medallion / DuckDB layered)
- **6 new reference files:**
  - `references/mode-frame.md` — Frame mode (~80 lines, 4-gate workflow)
  - `references/mode-model.md` — Model mode (~140 lines, 4 patterns + Table Contract template + governance hooks)
  - `references/planning-protocol.md` — Gate-by-gate protocol (~200 lines): Business Understanding / Metric Define / Data Plan TH1 (schema-exists) vs TH2 (brainstorm + modeling) / Lock & Hand-off
  - `references/metric-framework.md` — 8 frameworks (NSM / OMTM / Growth Loop / HEART / Diagnostic / Counter-metric / AARRR / Unit Economics) + 10-step KPI design protocol (~200 lines)
  - `references/governance.md` — 6-section practical framework (Metric & Definition / Modeling & Grain / Quality & Validation / Access & Privacy / Reporting & Consumption / Mindset) + STAR example + 5-implementation starter checklist (~200 lines)
  - `references/orchestration-patterns.md` — 4 patterns (Airflow with TaskGroup + DagSensor + alerts / dbt + Cloud or GitHub Actions / Cron / GitHub Actions) + hybrid pattern + decision table (~250 lines)
- **Sub-mode A0 (Brief tier)** in `/da-review`: 5-min snapshot — rubric_audit + outline check + 1-paragraph Ship/Fix/Rebuild verdict. Solves "review overbloat" (previously every review defaulted to A or B; A0 gives quick verdict for low-stakes / non-academic case)
- **Storytelling pattern** added to `mode-report.md` Step 5: storyline > dashboard (consulting pattern; complete-sentence slide titles; conclusion-led headlines)
- **Orchestration pointer** added to `mode-automation.md` Schedule Layers: decision table + cross-ref to `orchestration-patterns.md`
- **2 new commands:** `/prof-data-analyst:da-frame` + `/prof-data-analyst:da-model`

### Changed
- Plugin description updated to "Professional Data Analyst + Analytics Engineer plugin — 9 routable modes"
- Mode router in `SKILL.md` updated: 7 → 9 modes (added Frame + Model); review mode now lists 4 tiers (A0 Brief / A Polish / B Full / C Stakeholder Q)
- Where to Read Next section organized: Core / Quality / Narrative / Methods / **Front-of-workflow planning (new)** / **Data engineering hooks (new)** / Sub-agent / Mode-specific

### Fixed
- `scripts/validators/method_maturity_audit.py` CLI error message: distinguished "path doesn't exist" vs "file passed instead of directory" with friendly hints (per Loc handoff 2026-05-15)

### Architecture decisions
- **LEAN agents unchanged** (3 max): orchestrator + context-tracer + method-auditor. No new agents for new modes — modes are SKILLS, not agents.
- **Tier-based review** solves overbloat without removing capability — user picks detail level per task.
- **Frame + Model as 1 continuum** (planning → modeling), not 2 isolated modes — per advisor sanity check.
- **References > separate files for thin topics**: storytelling stays inside `mode-report.md`; schema-doc stays inside `mode-model.md`; no fragmentation.

## [3.0.0] — 2026-05-14

First plugin-format release. Consolidates ~50 personal DA feedback memories + lessons from `momo-agentic-platform` + TymeX case study + MoMo TTT pipeline into a portable, distributable Claude Code plugin.

### Added
- Plugin manifest at `.claude-plugin/plugin.json` + marketplace entry at `.claude-plugin/marketplace.json`
- ROOT skill `prof-data-analyst` with 4 universal rules (Orientation / Baseline-Noise-Impact / 5W1H / Why-Explanation META) + 14 stdlib scripts
- 7 mode skills: `da-query` / `da-process` / `da-insight` / `da-automate` / `da-report` / `da-review` / `da-fix`
- 3 sub-agents: `da-orchestrator` (Sonnet, session-start + final-review gate) + `da-context-tracer` (Haiku, multi-file reads for Sub-mode B Phase 2) + `da-method-auditor` (Sonnet, Sub-mode B Pass 3 causal-method judgment)
- 8 slash commands: `/prof-data-analyst:da` + 7 mode-specific commands
- 5 new reference files: `subagent-prompt-discipline.md`, `quality-criteria.md` (5 Quality Criteria framework), `quality-pipeline.md` (5-Gate Quality Pipeline), `narrative-template.md` (SCQR + Key Terms + Impact Cards), `domain-discovery-protocol.md` (L1/L2/L3 hub generation)
- 14 method spec files under `references/methods/`: causal family (DiD, Event Study, RDD, Synthetic Control, PSM, IV) + validation family (Bootstrap CI, Robustness Checks, Sensitivity Analysis, Falsification Tests, Multiple Testing, Post-Hoc Power, Cross-Validation, Pre-Registration), each ~150-200 lines following canonical `_template.md` structure with primary source citations
- `methods/_template.md` canonical W/H/W/W/W/W structure + `methods/_index.md` router
- LICENSE (MIT) + README + CHANGELOG

### Changed
- Refactored `causal-inference-toolkit.md` (247 → 135 lines) to decision table + 1-paragraph per method + pointer to `methods/<name>.md`
- Refactored `validation-evaluation-methods.md` (250 → 145 lines) to decision table + summary + pointer
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
- Pattern matches `superpowers` plugin: invoke agent when value clearly exceeds cost, not by default.
- Engine-agnostic SQL workflow (BQ / Postgres / Snowflake / Redshift / DuckDB).
- Progressive disclosure: SKILL.md lean; mode references load on demand; method specs load on demand.

### Prior history (pre-plugin format)
- v2 (2026-05-11): Refined `/da-review` into 3 sub-modes + added `rubric_audit.py --project` flag + added `method_maturity_audit.py`
- v1 (2026-05-09): Initial skill with 7 modes + 4 rules + ~10 scripts; consolidated MoMo DA workflow memories
