# Suggestion Protocol — Proactive Extension Proposals at Mode Exit

> Loaded from SKILL.md Core Operating Principle "Proactive Suggestion at Mode Exit". Solves the "you don't know what you don't know" gap: user can't discover full plugin capability by reading overview. Agent must detect context + propose 2-3 relevant extensions at exit.

## Overview — Why this file exists

Plugins (and skills) have a capability discovery problem. Users invoke 1-2 known commands repeatedly and never discover the other 80% of capability — because reading the overview doc isn't how humans work. They learn by doing, then ask "what else can this do?" only after they've gotten value.

**Example (the cost of passive discovery):**
- User runs `/da-report "weekly revenue + cashin flow"` → gets a report
- User doesn't know the plugin can ALSO: pull event-tracking from an org MCP + schedule daily refresh via Apps Script + alert when a KPI breaches threshold
- User ships the static report → loses most of the available value
- 2 weeks later: "Oh wait, the plugin can do that?" — too late, project archived

**Solution (this protocol):** at every mode exit, agent runs 3-step Suggestion Loop:
1. **Detect context** — what mode + what data + what output + what MCPs available
2. **Map to 8 extension categories** — pick 2-3 most relevant
3. **Propose with opt-in phrasing** — user picks yes/no/customize; agent only acts on yes

**Why (Operational):** the upstream cost of detecting + proposing is 30 seconds; the downstream value is user discovering capability they would have missed for weeks. Compounds across sessions.

---

## 3-Step Suggestion Loop

### Step 1 — Detect context (signals)

Agent at mode exit collects 4 signals (lightweight; no extra tool calls):

| Signal | Source | Example value |
|--------|--------|---------------|
| **Current mode** | The command invoked | `report`, `process`, `insight`, etc. |
| **Data source(s)** | Files / tables / MCPs referenced in this session | `<daily_user_mart>`, `events.csv`, `<org-data MCP>` |
| **Output format(s)** | Files produced | `notebook.ipynb`, `report.html`, `model.pkl`, `dashboard.json` |
| **Available MCPs / tools** | Listed in session context | `momo-data`, `mimir`, `google-drive`, `momo-data-portal` |
| **Stakeholder hints** | Explicit mentions in user prompt | "non-technical manager", "C-level", "team review" |

Agent does NOT proactively run new queries to gather these — just observes what's already in session memory.

### Step 2 — Map to 8 extension categories

Per signal, check which extension categories fit:

| # | Category | Trigger signal | Example proposal |
|---|----------|----------------|------------------|
| 1 | **Data source expansion** | User used 1 data source; another high-value source available via MCP / file / table | "Tôi thấy bạn dùng `mart_ttt_daily` cho business data. MCP momo-data có event tracking layer cho mini-app — muốn cover thêm góc event-based không?" |
| 2 | **Automation upgrade** | Output is static (one-off); recurring decision context | "Report này có cần update daily không? Tôi có thể wire cron job / Airflow / GHA / Apps Script auto-refresh" |
| 3 | **Quality validation stack** | Insight mode used; causal claim present; no validation visible | "Bạn vừa làm DiD. Muốn add robustness check (3 specs) + falsification (placebo period) + bootstrap CI để tăng rigor không?" |
| 4 | **Method upgrade** | Simple method used; advanced method better fits | "Hiện dùng Pearson correlation. Với causal claim này, DiD hoặc IV phù hợp hơn — muốn upgrade method không?" |
| 5 | **Audience expansion** | Output is technical; non-technical stakeholder context mentioned | "Notebook này technical. Muốn build thêm 1-pager non-academic version cho manager không?" |
| 6 | **Format expansion** | Output in 1 format; another format adds value | "Bạn có report HTML. Muốn convert sang PPTX cho present hoặc Apps Script dashboard auto-refresh không?" |
| 7 | **Downstream connection** | Output stands alone; could feed pipeline | "Output này có thể wire vào daily Slack alert nếu metric breach threshold — muốn setup không?" |
| 8 | **MCP / tooling expansion** | MCP available but not used; relevant to current task | "Session có MCP `mimir` (semantic layer) — có thể cross-check kết quả với canonical metric. Muốn run validation không?" |

### Step 3 — Phrase as opt-in

**Pattern:**
```
Bạn vừa hoàn thành <output>. Tôi có 2-3 gợi ý mở rộng:

1. <Category>: <specific proposal in 1 sentence>
   → Cost: <effort estimate>
   → Why: <1-line Why per Rule 4>

2. <Category>: <specific proposal>
   → Cost: <effort estimate>
   → Why: <1-line Why>

3. <Category>: <specific proposal>
   → Cost: <effort estimate>
   → Why: <1-line Why>

Muốn pursue 1+ option, hay đủ rồi? (skip cũng OK — đây là gợi ý không bắt buộc)
```

**Hard rules for phrasing:**
- MAX 3 suggestions per exit (don't dump 8)
- Each suggestion: specific (not "consider X"); cite the trigger ("tôi thấy bạn dùng Y")
- 1-line Why per Rule 4 (Causal / Empirical / Comparative / Theoretical / Operational)
- Effort estimate (5min / 30min / 1hr / 1day) — user budgets time decision
- Explicit OUT path: "skip cũng OK" — proactive ≠ pushy
- Vietnamese phrasing for Vietnamese sessions; English for English

**Anti-patterns:**
- 8 suggestions = paralysis. Pick top 3 ranked by value × user-context fit.
- Generic suggestions ("consider validation") — too vague to act on. Be specific.
- No effort estimate = user can't decide. Always include.
- Suggesting things outside plugin capability — only suggest what THIS plugin / current MCP set can do.

---

## Per-mode default extension priorities

When agent doesn't have enough signal, fall back to mode-specific top-3:

| Mode | Default top-3 to suggest at exit |
|------|----------------------------------|
| `frame` | (1) Once plan locked, route to next mode / (2) Add governance starter checklist for downstream / (3) Pre-register hypothesis if insight is next |
| `model` | (1) Pick orchestrator (Airflow/dbt/cron/GHA/Apps Script) / (2) Add 5-item governance starter / (3) Wire dbt tests if pattern is dbt |
| `query` | (1) Cache result for reuse / (2) Pre-aggregate for dashboard / (3) Add to project query log |
| `process` | (1) Validate mart via cross-table reconciliation / (2) Promote DuckDB prototype to dbt if recurring / (3) Build dashboard from mart |
| `insight` | (1) Validation stack (robustness + falsification + sensitivity) / (2) Multi-outcome DiD for mechanism / (3) Pre-registration for next round |
| `automate` | (1) Add fail-alert if not present / (2) Document SLA + freshness threshold / (3) Add cross-DAG sensor if dependency |
| `report` | (1) Schedule auto-refresh (cron/Apps Script/Airflow) / (2) Add non-technical 1-pager version / (3) Wire alert when KPI breach |
| `review` | (1) Run heavier tier (A → B) if HIGH count too high / (2) Spot-check method maturity / (3) Document outline check as template |
| `fix` | (1) Stabilize-to-template if recurring / (2) Backfill validation after fix / (3) Document anti-pattern in your long-term memory |

These are DEFAULTS. Context-detection (Step 1-2) overrides defaults when signals point elsewhere.

---

## Where the suggestion runs

Two natural exit points:

### Exit 1 — Mode workflow completion (per-mode reference)
After mode's final step (e.g., `mode-report.md` Step 8 "Save to output/"), the mode reference instructs:
```
After save: run suggestion-protocol.md Step 1-3.
```
Agent collects context + maps + proposes inline.

### Exit 2 — Orchestrator final-review gate (when `/da` was entry)
The `da-orchestrator` agent runs Suggestion Loop as part of final-review gate. After approving the deliverable, it adds:
```
Deliverable approved. Suggestion Loop:
[2-3 proposals per protocol]
```

Direct-mode invocations (`/da-report`, `/da-insight` etc.) hit Exit 1.
Orchestrator-routed sessions (`/da` → mode) hit Exit 2 (orchestrator handles both gate + suggestion).

---

## Examples (worked)

### Example 1 — Report mode with TTT revenue + cash-in flow

**Context detected:**
- Mode: `report`
- Data source: `mart_ttt_daily_user_record` (BQ business data)
- Output: HTML report static
- MCPs available: `momo-data` (with Apollo event tracking for mini-apps)
- Stakeholder hint: not specified

**Suggestion output:**
```
Bạn vừa hoàn thành TTT revenue + cash-in flow report (HTML static).

Có 3 gợi ý mở rộng:

1. Data source expansion: MCP momo-data có Apollo event tracking layer cho TTT mini-app.
   Tôi có thể thêm 1 tab event-based (entry point traffic, screen funnel, click-through cashin) — bổ sung góc product-tracking bên cạnh business data.
   → Cost: ~45 min (query Apollo + thêm 1 tab + verify)
   → Why (Empirical): event tracking + business data + together cho insight đầy đủ hơn — single-source view dễ miss user-journey friction

2. Automation upgrade: report hiện static. Có 3 path schedule:
   (a) Cron + DuckDB cache local — đơn giản, $0
   (b) Airflow DAG nếu org đã có — production-grade, dependency-aware
   (c) Apps Script auto-refresh từ Google Sheet — native Google ecosystem, real-time on Sheet change
   → Cost: ~30 min cho (a) / ~1 hr cho (b) / ~45 min cho (c)
   → Why (Operational): KPI drift mỗi ngày; static report stale sau 24 hr — schedule giúp stakeholder luôn nhìn data tươi

3. Alert wiring: nếu KPI (vd MAU SOF) breach threshold thì email/Slack alert tự động.
   → Cost: ~20 min
   → Why (Operational): proactive flag > stakeholder phát hiện sau khi đã trễ

Muốn pursue 1+, hay đủ rồi? (skip cũng OK)
```

### Example 2 — Insight mode with simple correlation

**Context detected:**
- Mode: `insight`
- Data source: `events.csv`
- Method used: Pearson correlation only
- Output: notebook
- Claim seen in output: "feature X drove retention drop"

**Suggestion output:**
```
Bạn vừa làm phân tích Tier 3 retention.

3 gợi ý:

1. Method upgrade: claim "feature X drove retention drop" là causal — nhưng method dùng là Pearson correlation (associative). Recommend upgrade sang DiD với treated (feature-X users) vs control (non-feature-X), parallel-trends test.
   → Cost: ~1 hr (build panel + DiD + parallel-trends check)
   → Why (Theoretical): correlation ≠ causation; causal claim cần causal method (Angrist-Pischke)

2. Validation stack: cause-effect cần multi-spec rigor — robustness (3 model specs), falsification (placebo period), sensitivity (window 30d/60d/90d).
   → Cost: ~45 min
   → Why (Comparative): mature DA reports stack validation; single-method causal claim không defendable trước skeptic

3. Pre-registration: lock hypothesis + method + decision rule TRƯỚC EDA round next time.
   → Cost: ~10 min (cell trong notebook)
   → Why (Empirical): pre-reg ngăn p-hacking + spec-fishing — chuẩn methodology 2017+

Muốn pursue?
```

### Example 3 — Process mode after DuckDB prototype

**Context detected:**
- Mode: `process`
- Output: `.duckdb` file with stg_/clean_/mart_ tables
- Frequency: one-off (no schedule)
- MCPs available: none specific
- Stakeholder hint: "team weekly review"

**Suggestion output:**
```
DuckDB prototype done với layered tables.

3 gợi ý:

1. Promote to dbt: nếu team weekly review = recurring → DuckDB prototype nên promote lên dbt (modular SQL + tests + lineage built-in).
   → Cost: ~2 hr (port stg/mart sang dbt models + yml tests)
   → Why (Operational): recurring task không nên rely on local file — production-grade cần version control + test automation

2. Build dashboard từ mart layer: Apps Script dashboard từ Google Sheet OR HTML report từ mart query.
   → Cost: ~30 min HTML / ~1 hr Apps Script
   → Why (Empirical): weekly review thường cần visual — table dump khó scan

3. Add quality assertions: row count check / not-null PK / cross-table reconciliation sum.
   → Cost: ~20 min
   → Why (Operational): silent data drift sau N tuần thường breaks downstream; assertion catch early

Muốn pursue?
```

---

## Cross-references
- Core principle: SKILL.md "Proactive Suggestion at Mode Exit"
- Per-mode default extensions: each `mode-*.md` references this protocol
- Orchestrator integration: `agents/da-orchestrator.md` final-review gate
- Apps Script pattern detail: `orchestration-patterns.md` Pattern 5
- Why pattern matters: `feedback_field_test_driven_expansion.md` (Loc's field test showed users miss capability)

— part of prof-data-analyst · Loc Tu, 2026
