# Universal Workflow Rules

These 4 rules are MANDATORY for every deliverable, regardless of mode. They sit ABOVE every mode-specific workflow. Rule 4 is a meta-rule that applies to Rules 1-3 themselves and to every choice within them.

## Rule 1 — Orientation Block (FIRST in every deliverable)

Every deliverable opens with an Orientation Block. Form depends on artifact type.

### For written reports / docs
SCQR pattern:
- **S — Situation**: 1-2 sentences setting baseline state
- **C — Complication**: what changed / what triggered the analysis
- **Q — Question**: the specific question this report answers
- **R — Resolution**: 1-sentence headline answer (with caveats if needed)

### For dashboards / HTML reports
3-line intro:
- Line 1: What data + time range covered (e.g., "product daily snapshots, 2026-04-01 → 2026-05-08")
- Line 2: Primary question this dashboard answers
- Line 3: Reading order / how-to-use note (which tab first, what to skip)

### For code modules
Module docstring containing:
- Purpose (1 sentence)
- Inputs / dependencies (external + internal)
- Outputs / side effects (incl. files written, services called, emails sent)
- Owner + last-updated date

### For notebooks (M1-M5 case study, EDA)
Executive Summary block right after Data Dictionary, BEFORE body. Table-based format:
- Terminology + assumption + Q&A descriptive + diagnostic per feature
- Multi-feature combo findings
- Final belief / verdict
- Rule-based filter (high-cardinality ban, identifier flag)
- Traps + next action

### Terminology Block — add when
- Complex / first-time / niche / multi-meaning terms appear
- Org-specific acronyms (product codes, channel names, mart tables, account types)
- Bank / fintech jargon a non-DA reader would miss
- Format: 1-line definition per term, alphabetical, right after Orientation

### "How to read" guide — add when
- Non-text artifact (chart-heavy report, multi-tab dashboard, JSON output, HTML SPA)
- Each section needs a triage rule: "skip tab 4 if you only need headline", "read Card A → Chart 1 → Recommendations in that order"

### Why this rule exists
Stakeholders land on the deliverable cold — no prior conversation context. The Orientation Block lets them decide in 30 seconds whether to read further and where to start. Without it, the reader either bounces or pings Loc for context.

## Rule 2 — Baseline → Noise → Impact Ladder

Every numeric statement MUST pass 3 rungs BEFORE you claim a finding.

### Rung 1 — Baseline
What is the reference value? Options:
- Previous period (DoD / WoW / MoM / YoY)
- Same period last year
- Pre-event baseline (before policy / shock)
- Industry canonical (e.g., bank CASA rates: Techcom 5.5%, LPBank 4.5%, MSB 4.2%, Cake 3.6% — Q1 2026)
- Plan / forecast / KVBD expected (per-metric 3-anchor weights)

State which baseline you chose explicitly. Bare "X = 1.2M" without baseline = REJECTED.

### Rung 2 — Real or Noise
Is the delta beyond noise? Provide ONE of:
- **95% CI**: when n ≥ 30
- **p-value**: from appropriate test (t-test, chi-square, Pearson r threshold |r| ≥ 0.22 for p<0.05 at n=83)
- **Effect size**: Cohen's d (continuous), Cramer's V (categorical — but flag inflation on high-cardinality columns)
- **z-score**: vs historical baseline distribution
- **KVBD expected gap**: actual − expected, with σ from cov-aware residual

For step-function variables (e.g., bank rate flat 19 days then jumps): do NOT use Pearson — use Event Study (pre/post comparison).

For n < 30: ASK user to extend date range. Don't force a conclusion.

Bare "X giảm 5%" without noise check = REJECTED.

### Rung 3 — Impact or Worth
Verdict from {negligible, small, medium, large} based on:
- Business threshold (e.g., 1% AUM gap on a flagship product = "medium")
- Cohort size affected (one tier = 71% of drain → "large")
- Reversibility / persistence
- Stakeholder priority (revenue / cost / risk / compliance)

Quantify the impact in business terms, NOT statistical terms. "p<0.001" is not an impact; "6.5B VND AUM gap sustained 3 days post-payday" is.

### Example
WRONG: "Day-5 AUM coefficient = −1.3% (significant)"

RIGHT: "Day-5 AUM coefficient = −1.3% vs MoM baseline +0.2% (Rung 1: baseline). 95% CI [−1.8%, −0.8%], p<0.001 (Rung 2: noise). Translates to ~6.5B VND AUM gap on payday, sustained 3 days before recovery — medium impact on T1 cohort (Rung 3: worth)."

## Rule 3 — Question → Goal → 5W1H Action Brief

Every proposed action (recommendation, fix, follow-up) MUST come with an 8-field brief BEFORE it ships.

### The 8 fields
1. **Question** — what specifically is this action solving? Frame as a question.
2. **Goal** — measurable outcome. Numbers + deadline.
3. **Why** — motivation linking to evidence in the report
4. **What** — scope: what's in / out
5. **Who** — owner (team / role / individual)
6. **When** — deadline (absolute date, not "next sprint")
7. **Where** — which system / team / region / cohort
8. **How** — concrete first step (not "investigate further")

### Why all 8 fields
- Missing Question → unclear if action solves the stated problem
- Missing Goal → no acceptance criteria
- Missing Why → stakeholder distrusts gut-feel proposals
- Missing What → scope creep on day 1
- Missing Who → no owner → doesn't happen
- Missing When → stays in backlog
- Missing Where → wrong team picks it up
- Missing How → action stays abstract

### Anti-pattern
"Recommend deeper investigation into the heavy-withdrawal tier" — ZERO of 8 fields filled. Reject.

### Right pattern
- **Question**: Why did the heavy-withdrawal tier drain 1,649B over 24 days while the lighter tier stayed positive?
- **Goal**: Identify top-2 mechanism by 2026-05-20; reduce that tier's drain rate by 30% by 2026-06-30
- **Why**: Report section 4.2 finds the heavy-withdrawal tier = 71% of total drain, but mechanism not isolated
- **What**: Behavioral cohort analysis on the heavy-withdrawal tier cashout patterns; OUT-of-scope: redesign of the other tiers
- **Who**: DA + product owner
- **When**: Hypothesis matrix 2026-05-15; validation analysis 2026-05-20; intervention proposal 2026-05-25
- **Where**: focal product, all regions, all balance ranges
- **How**: Start with the daily user-level mart filtered to the heavy-withdrawal tier, run the drain-anatomy SQL pattern from your domain templates

### Tone for C-level / CEO audience
Frame as "Next steps" timeline DIRECTIVE, not "Cần phê duyệt" checkbox. Same content, different frame — approval-ask suggests the team isn't taking ownership.

## Rule 4 — Why-Explanation for Every Choice (META-RULE)

Every action, method, framework, rule, workflow, process, tool choice, or threshold value MUST ship with a `Why` explanation. No bare prescription. No "do X" without "because Y, evidence Z".

This rule is META — it applies to:
- The 3 rules above (each rule has its own "Why this rule exists" section)
- Every step inside every mode reference (Query / Process / Insight / Automation / Report / Review / Fix)
- Every recommendation in stakeholder reports (already enforced by Rule 3 field 3: `Why`)
- Every threshold, cutoff, n-of-K, p-value bar, sample-size target chosen
- Every tool / framework / library / engine selected (DuckDB over CSV, BH-FDR over Bonferroni, Event Study over Pearson)

### The Why must answer ONE of these

| Why-type | Question it answers | Example |
|----------|---------------------|---------|
| **Causal** | What pain does this prevent? | "Orientation Block exists because cold readers bounce in 30s without it." |
| **Empirical** | What evidence justifies this? | "Use last-3M OLS window because structural break in 2026-02; older data biases slope." |
| **Comparative** | Why this over alternative X? | "DuckDB over CSV-only because type preservation prevents date-as-string downstream bugs." |
| **Theoretical** | What principle / framework backs this? | "Bonferroni FWER bound is conservative under independence; we use BH-FDR because tests are positively correlated." |
| **Operational** | What workflow downstream needs this? | "Save to `output/` not `personal-workspace/` because pipeline grep-discovers from `output/` only." |

A Why that just restates the action is NOT a Why. "Use Bonferroni because we need Bonferroni" — REJECTED.

### Where Why appears in artifacts

| Artifact | Where Why goes |
|----------|----------------|
| Reference doc | Each section ends with **Why this matters** line or paragraph |
| SQL / Python script | Module docstring + inline `# Why: ...` for non-obvious choices |
| Notebook | Markdown cell above the code cell, NOT a comment buried in code |
| Stakeholder report | Inline alongside recommendation (Rule 3 field 3) + "Reading in business terms" column for methods/numbers |
| Method-comparison table | A `Why this method` column alongside the method name |
| Slide deck | Speaker note OR caption underneath the slide |
| Choice in chat reply | First sentence after the action: "I picked X because..." |

### Anti-patterns

```
WRONG (bare action):
"Use DuckDB."

WRONG (circular Why):
"Use DuckDB because DuckDB is good for this."

WRONG (Why hidden in another doc):
"Use DuckDB. (See appendix C for rationale.)"

RIGHT (Why inline, evidence-anchored):
"Use DuckDB for M2 mart layer.
Why — CSV-only loses type info (date columns serialize as string, ints widen to float on NULL).
DuckDB persistent file preserves DATE/INT64 native, enables cross-table SQL JOIN
without pandas merge gymnastics, and downstream HTML builder reads 1 SQL line per
table from `information_schema`. Compared to Parquet: same type preservation, but
DuckDB adds atomic CREATE OR REPLACE so partial-failure mid-write doesn't corrupt
the table."
```

### Why this rule exists (meta-Why)

- **Audit trail**: 6 months later, you (or a teammate) reading the deliverable cannot reverse-engineer why threshold = 0.05 vs 0.01. Why-line preserves the decision context.
- **Stakeholder trust**: bare prescriptions read as gut-feel. Why-line transforms "I think we should do X" into "X follows from evidence Y, principle Z".
- **Skill-as-teaching**: this skill is read by other DAs, not just executed. A method without Why teaches "what to do" but not "when to deviate".
- **Self-correction**: writing the Why often reveals the choice is wrong. The act of articulating "because evidence Y" surfaces missing evidence.

### Quick checklist (apply before declaring any artifact done)

- [ ] Every `## Rule N` section has a "Why this rule exists" paragraph
- [ ] Every method / framework introduced has a Why-column or Why-line
- [ ] Every threshold / cutoff / sample-size has a Why anchored to evidence or principle
- [ ] Every tool / library / engine choice has a 1-sentence Why (or pointer to comparison table)
- [ ] Every recommendation in a stakeholder report fills Rule 3 field 3 (`Why`)
- [ ] No "see appendix for rationale" — Why is inline OR the choice is too important to defer

## Connect-the-Dots Reasoning (cross-cutting)

When stating any finding, the reasoning chain MUST link:

```
Fact → Mechanism → Behavioral Change → Product Impact → Evidence
```

NOT "state-the-fact" alone. Example:

WRONG: "Oil correlation r = −0.751"

RIGHT: "Oil price +31% in March (FACT) → transport + food prices ↑ (MECHANISM) → households reallocate cash toward expenses (BEHAVIORAL CHANGE) → withdrawal from a savings product for daily payments (PRODUCT IMPACT) → Payment Cashout +13.2% same period, evidence in daily mart section 4.1 (EVIDENCE)"

If you cannot fill all 5 stages, the finding is incomplete.

## Self-Check Numerical Consistency (pre-ship)

Before declaring any deliverable done:

1. **Cross-card reconciliation** — find every metric appearing in 2+ places (cards, tables, charts). Verify they match.
2. **Implied parameter check** — if Card A says "−2.5% drop" and Card B says "from 12.96T to 12.65T", does 12.65 / 12.96 actually = 0.975? Verify by hand.
3. **Back-derive** — take each headline figure, recompute from raw source. If divergence > rounding error, find the bug.
4. **Structural self-checks miss this** — grep / keyword scans WON'T catch cross-card numerical contradictions. Manual reconciliation required.

When stuck on conflicting numbers between sections, call `advisor` — keyword checks alone won't surface it.

See `references/self-check-protocol.md` for the full pre-ship checklist.

## Show Numbers → Business Reading (presentation layer)

Stakeholder slides / tables containing numbers, methods, formulas MUST have a "Reading in business terms" column with quoted business-language interpretation per row.

WRONG: "76% sessions tốt"  
RIGHT: "100 / 176 sessions (56.8%) không lỗi — đủ ngưỡng pilot, còn 43.2% có ít nhất 1 lỗi cần fix"

Showing số mà không có business reading = academic theatre. Apply to method-comparison tables, cross-period tables, Bayesian breakdowns, formula derivations.

This is the presentation layer of Connect-the-Dots Reasoning. Analytical layer = reasoning chain; presentation layer = "Reading in business terms" column.

## Define Winning Metric FIRST

For any task involving evaluation, scoring, comparison:
1. Define the **unit of success** (session? task? feature?)
2. Define the **measurement** (how do we score one unit?)
3. Define the **aggregation** (mean? p50? % passing threshold?)
4. THEN pick the data, judge, rubric

Anti-pattern: pick metric while looking at data; conflate granularities (session vs task). Field-research first if unsure.
