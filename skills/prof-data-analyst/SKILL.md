---
name: prof-data-analyst
description: Portable Data Analyst workflow with 7 modes (Query/Process/Insight/Automation/Report/Review/Fix-pipeline). Engine-agnostic SQL (BQ/Postgres/Snowflake/Redshift/DuckDB). Bundles 14 stdlib scripts: stats (effect size, MDE, bootstrap CI, multi-testing), causal inference (DiD, Event Study, parallel-trends), formatting, validators (orientation, action brief, AI-tell scan, rubric audit, method maturity audit, self-check). Script-over-agent-compute is a hard rule. Review mode has 3 sub-modes: Delivery Refine (lightweight polish), Full Project Refine (heavyweight audit + method maturity + rework plan), Stakeholder Questioning. Triggers on 'làm DA', 'viết SQL', 'EDA', 'build báo cáo', 'review report', 'refine delivery', 'refine project', 'audit project', 'phân tích insight', 'causal inference', 'fix pipeline', or /da-query /da-process /da-insight /da-automate /da-report /da-review /da-fix. Enforces 4 rules (Orientation, Baseline-Noise-Impact, 5W1H, Why-Explanation meta), Karpathy discipline, AI-tell ban.
metadata:
  author: Loc Tu
  handle: loctu
  origin: 2026
  curation: distilled from a personal practice of data analysis; ~50 feedback memories consolidated into a portable workflow
---

# Professional Data Analyst — Portable Workflow Skill

## What This Skill Does

Encodes a complete DA discipline (workflow rules + style polish + coding rigor) into 7 routable modes plus bundled scripts. Designed to be portable across companies — no hard dependency on any specific data warehouse, BI tool, notification channel, or chart theme. BigQuery, MoMo-style semantic layer, and shared chart themes are referenced as concrete examples but treated as replaceable.

## Core Operating Principles

### Script > Agent Compute (HARD RULE)
Never compute statistical results, sample sizes, p-values, effect sizes, or formatted numbers inline in chat. Always call a script. Scripts live in `scripts/` and produce deterministic, auditable output.

- Statistical inference: `scripts/stats/`
- Number formatting: `scripts/format/`
- Deliverable validators: `scripts/validators/`

Reason: AI inline arithmetic is unreliable and unauditable. Scripts are reproducible by the human reading the work.

### Progressive Disclosure
SKILL.md is lean. Mode-specific details live in `references/mode-*.md`, loaded only when the matching mode triggers. Scripts are NEVER loaded into context — they're executed.

### Portable First, Niche Optional
Mode-specific references treat any company-specific tooling, mart, or benchmark as **example**, not requirement. The same workflow runs against any SQL engine, any BI stack, any notification channel.

### Proactive Suggestion at Mode Exit (v3.2)
At every mode exit, agent MUST run the 3-step Suggestion Loop: (1) detect context (mode + data + output + available MCPs + stakeholder hints), (2) map to 1-3 of the 8 extension categories (data source expansion / automation upgrade / quality validation stack / method upgrade / audience expansion / format expansion / downstream connection / MCP-tooling expansion), (3) propose with opt-in phrasing (specific + cite trigger + Why + effort estimate + explicit skip path).

Reason: users can't discover full plugin capability by reading overview ("you don't know what you don't know"). Proactive suggestion at exit recovers most of the missed capability — users see relevant options when they have working context to evaluate them.

Full protocol + 3 worked examples: `references/suggestion-protocol.md`. Orchestrator (`agents/da-orchestrator.md`) runs this gate when `/da` was the entry; direct-mode invocations run the gate inline per mode reference.

MAX 3 suggestions per exit. Each suggestion: specific + cited trigger + 1-line Why + effort estimate + explicit "skip OK". Anti-pattern: 8-suggestion dump = paralysis.

## Mode Router

Pick the mode matching the current task, then read the matching reference file. If task spans multiple modes, read all relevant references before starting. If unsure, default to **insight** (covers reasoning + analysis).

Modes follow the standard DA flow: **Frame → Model → Query → Process → Insight → Automation → Report**, plus orthogonal helpers (review + fix-pipeline). Frame + Model are the new front-of-workflow planning modes (v3.1).

| Mode | Trigger phrases | Reference file |
|------|-----------------|----------------|
| **frame** | "frame project", "kickoff", "metric define", "scope project", "không biết bắt đầu", "/da-frame" | `references/mode-frame.md` |
| **model** | "data modeling", "build pipeline mới", "design DWH", "setup mart", "dbt project", "/da-model" | `references/mode-model.md` |
| **query** | "viết SQL", "query data", "lấy data", "NL→SQL", "/da-query" | `references/mode-query.md` |
| **process** | "process data", "ML case study", "M1 / M2 / M3", "feature engineering", "EDA notebook", "DWH", "/da-process" | `references/mode-process.md` |
| **insight** | "phân tích insight", "hypothesis validation", "diagnostic", "why X", "/da-insight" | `references/mode-insight.md` |
| **automation** | "automation", "pipeline tự động", "schedule job", "/da-automate" | `references/mode-automation.md` |
| **report** | "build báo cáo", "làm report", "stakeholder report", "/da-report" | `references/mode-report.md` |
| **review** | "review code", "audit project", "OK chưa", "snapshot review", "/da-review" (4 tiers: A0 Brief / A Polish / B Full / C Stakeholder Q) | `references/mode-review.md` |
| **fix-pipeline** | "fix pipeline", "debug pipeline", "sửa pipeline", "/da-fix" | `references/mode-fix-pipeline.md` |

## Four Universal Rules (apply to EVERY mode, every deliverable)

Full detail in `references/universal-workflow-rules.md`. Summary:

### 1. Orientation Block (FIRST in every deliverable)
- Reports → SCQR (Situation, Complication, Question, Resolution)
- Dashboards / HTML → 3-line intro (data + time range, primary question, reading order)
- Code modules → docstring (purpose, inputs, outputs, side effects, owner)
- Complex/niche terms → Terminology Block right after Orientation
- Non-text artifacts → "How to read" guide + per-section triage rule

**Validator**: `scripts/validators/orientation_block.py <file>` checks SCQR / docstring presence.

### 2. Baseline → Noise → Impact Ladder (every numeric statement)
Every number passes 3 rungs BEFORE claiming a finding:
1. **Baseline** — reference period / canonical value to compare against
2. **Real or Noise** — CI / p-value / effect size / z-score (NOT bare delta)
3. **Impact or Worth** — verdict {negligible, small, medium, large} quantified in business terms

**Helper script**: `scripts/stats/baseline_noise_impact.py` accepts current value + baseline + sample, outputs 3-rung verdict.

Bare "X giảm 5%" without these 3 rungs = REJECTED.

### 3. Question → Goal → 5W1H Action Brief (every proposed action)
8-field brief before any recommendation: Question, Goal, Why, What, Who, When, Where, How. Missing fields = action does not ship.

**Validator**: `scripts/validators/action_brief.py <text>` checks all 8 fields present.

### 4. Why-Explanation for Every Choice (META-RULE)
Every action, method, framework, threshold, tool / engine choice MUST ship with a `Why` line. The Why must answer one of: **Causal / Empirical / Comparative / Theoretical / Operational**. A Why that restates the action ("use X because we need X") is REJECTED.

- Reference docs → each section has a "Why this matters" line
- Method-comparison tables → add a `Why this method` column
- Threshold / cutoff / α / MDE → anchored to evidence or principle
- Tool / library / engine choice → 1-sentence comparative Why
- Stakeholder recommendation → fills Rule 3 field 3 (`Why`)
- Skill itself → every Rule has a "Why this rule exists" paragraph (this rule applies meta-to-itself: see Rule 4 "Why this rule exists" in `universal-workflow-rules.md`)

**Validator**: `scripts/validators/rubric_audit.py <file>` flags any method/threshold/tool choice missing inline Why.

## Bundled Scripts (run, don't reimplement)

```
scripts/
├── stats/
│   ├── effect_size.py            # Cohen's d, Cramer's V (with high-cardinality warning)
│   ├── significance.py           # t-test, chi-square, Pearson r with caveats
│   ├── mde_sample_size.py        # MDE + required sample size
│   ├── baseline_noise_impact.py  # 3-rung ladder runner
│   ├── bootstrap_ci.py           # non-parametric CI via resampling
│   └── multiple_testing.py       # Bonferroni FWER + BH-FDR correction
├── causal/
│   ├── did_event_study.py        # 2×2 DiD + Event Study (manual OLS, stdlib)
│   └── parallel_trends_test.py   # falsification test for DiD/Event Study
├── format/
│   └── number_format.py          # K/M/B/T units, sentiment colors
└── validators/
    ├── orientation_block.py      # checks SCQR / docstring / 3-line intro present
    ├── action_brief.py           # checks 8-field brief
    ├── ai_tell_scan.py           # scans for ===, em-dash, ≈, → in stakeholder text
    ├── rubric_audit.py           # mechanical ~30-check compliance audit (Rules 1-4 + style + code); --project flag walks a folder
    ├── method_maturity_audit.py  # heuristic: method-vs-claim mismatch + falsification gap + validation stacking + advanced-method opportunities (Sub-mode B Pass 3)
    └── self_check.py             # full pre-ship checklist runner
```

Run pattern:
```bash
python scripts/stats/effect_size.py --metric mean --group-a a.csv --group-b b.csv
python scripts/validators/orientation_block.py output/report.md
python scripts/format/number_format.py 1234567890   # → "1.23 B"
python scripts/stats/multiple_testing.py --p-values 0.01,0.04,0.001 --alpha 0.05 --method bh-fdr
python scripts/causal/did_event_study.py did --csv data.csv --treated-col t --time-col p --outcome y --pre 1 --post 2
python scripts/validators/rubric_audit.py output/report.md   # mechanical compliance check
```

See `references/scripts-guide.md` for full CLI reference.

## Mandatory Style Checks (ALL output)

Full list in `references/style-rules.md`. Top blockers:

- ✗ AI-tell symbols in stakeholder text: `===`, `-----`, em-dash (`—`), `≈`, `→`
  - **Scanner**: `scripts/validators/ai_tell_scan.py <file>`
- ✗ Bare metric without denominator ("76% sessions tốt" — needs absolute + total)
- ✗ Mermaid in .md (use ASCII art for editor portability)
- ✗ Auto-sending email / Slack to stakeholders without explicit user confirm
- ✗ Hardcoded market data (rates, prices, FX) — auto-fetch + staleness gate
- ✗ Em-dash glue implying causation ("X = 0.98 · Day 5 payday")
- ✓ Per-chart inline `→ takeaway` verdict (drop / negligible / candidate / strong)
- ✓ Local-language with proper diacritics for stakeholder-facing output (e.g., Vietnamese with full marks)
- ✓ Chart theme = your organization's brand (any consistent theme; MoMo theme is one example)

## Coding Discipline (when writing or editing code)

Full Karpathy + delegation playbook in `references/coding-discipline.md`. Top checks:

1. **Think before coding** — state assumptions, surface tradeoffs, push back on premature complexity
2. **Simplicity first** — minimum code, no speculative features / config / error handling for impossible scenarios
3. **Surgical changes** — touch only what's needed; don't fix adjacent code, don't refactor what isn't broken
4. **Goal-driven** — define verifiable success criteria before writing
5. **Script > agent-compute** — never do statistical / numerical work inline
6. **No comments by default** — code self-documents via names; only comment non-obvious WHY
7. **Edit over Write** — never rewrite a whole file when an Edit suffices
8. **No emojis in code / files** unless user explicitly asks

## External Analytical Resources (pointer convention)

The skill bundles SCRIPTS for stats / formatting / validators, but does NOT bundle textbooks or full analytical frameworks. Instead it documents the **kind** of reference you should keep accessible — and points to your local copy via convention paths.

Categories the skill expects (substitute YOUR local paths):
- Statistical inference cheat sheet (distribution → SD → SE → CI → effect size → MDE)
- A/B testing playbook
- Analytic frameworks (AARRR, North Star, Logic Tree, Growth Loop, OMTM)
- Segmentation framework
- Chart design standards
- Math / Stats / Probability foundational textbooks

If your workspace doesn't have any of these yet, the skill still works — just call scripts in `scripts/`. Add references over time as you encounter topics worth studying.

Index + usage with `<your-workspace>` placeholder convention: `references/analytical-resources.md`.

## Mode Quick Start

Once mode is selected:
1. Read the relevant `references/mode-*.md` file
2. Read `references/universal-workflow-rules.md` (always)
3. Read `references/style-rules.md` (if producing stakeholder deliverable)
4. Read `references/coding-discipline.md` (if writing / editing code)
5. Execute task following the mode workflow — call scripts for any statistical or numerical work
6. Run `scripts/validators/self_check.py <deliverable>` before declaring done
7. If session was substantive → trigger session-end hooks per the user's environment

## Where to Read Next

**Core workflow + rules:**
- Universal workflow rules → `references/universal-workflow-rules.md` (Rules 1-4)
- Coding discipline → `references/coding-discipline.md`
- Style + AI-tells + numbers + charts → `references/style-rules.md`
- Self-check protocol (pre-ship) → `references/self-check-protocol.md`

**Quality framework (whole-artifact checks):**
- 5 Quality Criteria (Interconnect / Compact / Insightful / Sufficient / Logical Reason) → `references/quality-criteria.md`
- 5-Gate Quality Pipeline (Scope → Data → Analysis → Viz+Story → Review) → `references/quality-pipeline.md`

**Narrative + structure:**
- SCQR + Key Terms + Impact Cards template → `references/narrative-template.md`
- Visualization discipline (action title, grey + 1 accent, no pie / no 3D, clutter checklist, horizontal logic, 10 anti-patterns) → `references/storytelling-with-data.md`

**Method specs:**
- Methods index — router for all 14 method specs → `references/methods/_index.md`
- Methods template — canonical W/H/W/W/W/W structure → `references/methods/_template.md`
- Causal inference toolkit (DiD, Event Study, RDD, Synthetic Control, PSM, IV) → `references/causal-inference-toolkit.md` (decision table) + `references/methods/<name>.md` (full spec per method)
- Validation & evaluation methods (bootstrap, robustness, sensitivity, falsification, multi-testing, post-hoc power, cross-validation, pre-registration) → `references/validation-evaluation-methods.md` (decision table) + `references/methods/<name>.md` (full spec per method)
- Scripts CLI reference → `references/scripts-guide.md`
- External analytical resources index → `references/analytical-resources.md`

**Front-of-workflow planning (v3.1 — new):**
- Planning protocol (Business Understanding → Metric Define → Data Plan TH1/TH2 → Lock & Hand-off) → `references/planning-protocol.md`
- Metric framework selection (NSM / OMTM / Growth Loop / HEART / AARRR / Diagnostic / Counter-metric / Unit Economics) → `references/metric-framework.md`
- Data modeling patterns (Kimball / dbt / Medallion / DuckDB layered) → `references/mode-model.md`

**Data engineering hooks (v3.1 — new):**
- Data governance (6-section practical framework) → `references/governance.md`
- Orchestration patterns (Airflow / dbt+GHA / cron / GitHub Actions / Apps Script) → `references/orchestration-patterns.md`

**Proactive capability discovery (v3.2 — new):**
- Suggestion protocol (8 extension categories + opt-in phrasing) → `references/suggestion-protocol.md`

**Sub-agent + domain protocols:**
- Sub-agent prompt discipline (anti-shortcut + handoff drift + fresh-session + context-packet) → `references/subagent-prompt-discipline.md`
- Domain discovery protocol (new-domain L1/L2/L3 generation) → `references/domain-discovery-protocol.md`

**Schema discovery + semantic layer (v3.3 — new):**
- Schema source hierarchy (T0 owner-tag → T1 catalog → T2 cube → T3 INFORMATION_SCHEMA → T4 sampling) → `references/schema-source-hierarchy.md`
- Semantic layer setup (portable 6-phase recipe, engine-agnostic) → `references/semantic-layer-setup.md`

**MoMo stakeholder extensions (v3.3 — new, opt-in):**
- MoMo Semantic Cube + momo-data MCP + Mimir tag + OpenMetadata workflow → `references/momo-extensions.md`
- Example MCP config (mimir + momo-data + powerbi-modeling) → `<plugin_root>/mcp/example-momo-mcp.json`

**Mode-specific:**
- `references/mode-{frame,model,query,process,insight,automation,report,review,fix-pipeline}.md`

---

<sub>*Colophon* — method by **Loc Tu** (`loctu`) · 2026. Distilled from a personal practice. Adopt freely; attribution welcome, not required.</sub>
