# 5-Gate Quality Pipeline

> Every DA project passes through 5 gates. Each gate has an entry condition, an exit criterion, and a fail-mode. Maximum 3 retries per gate before escalating to the user.

## Overview — Why this file exists

Modes (query / process / insight / report) describe WHAT to do at each stage. The pipeline describes WHEN you are allowed to advance. Without explicit gates, projects skip ahead — analysis starts before data is verified, report ships before analysis is challenged — and rework dominates the timeline.

## Outline (story-flow check)

1. The 5 gates, in order (Scope → Data → Analysis → Viz+Story → Review)
2. Gate entry conditions + exit criteria
3. Fail-modes per gate
4. Retry budget and escalation
5. How the gates map to the 7 modes

A reader scanning headings should be able to predict the gate logic.

---

## Gate 1: Scope

**Entry:** User has asked for something analytical (data question, report, pipeline).
**Exit:** A written 8-field Action Brief (Rule 3) is locked. The Question, Goal, Why, What, Who, When, Where, How are all filled.
**Fail-mode:** Brief has placeholder fields ("TBD," "depends," "unclear"). The gate does not pass.
**Why (Operational):** Vague scope is the single most expensive bug in DA work — every downstream gate amplifies the cost of an unclear question. Lock scope or stop.

## Gate 2: Data

**Entry:** Scope is locked.
**Exit:** All required tables identified, sampled (partition-safe), schema documented in a Data Dictionary, freshness verified (data_date derived from `df.iloc[-1]`, not assumed). A 6-Step EDA pass is complete (S1 dtype → S2 univariate → S3 anomaly → S4 bivariate → S5 ranking → S6 patterns).
**Fail-mode:** Mart lag undetected, schema assumed, anomaly missed.
**Why (Empirical):** Past incidents — mart T-2 lag, duplicate rows on backfill, legacy-vs-current schema union mismatch — happen at this gate. The 6-step EDA pass is the structured catch.

## Gate 3: Analysis

**Entry:** Data is locked.
**Exit:** Every claim passes Rule 2's Baseline-Noise-Impact ladder. Method choice has a Why per Rule 4. If causal claim, falsification test attached. Multiple comparisons → Bonferroni or BH-FDR adjustment ran. Heavy-tail metrics → switched to Wilcoxon + winsorize + median Δ.
**Fail-mode:** Bare delta with no test. Causal verb on correlational evidence. Multi-p-value report without correction.
**Why (Causal):** Method mismatch is silent — the analysis looks rigorous until a peer asks "what would have falsified this?" Gate forces the answer to exist before the report ships.

## Gate 4: Viz + Story

**Entry:** Analysis is locked.
**Exit:** Every chart has all 7 anatomical elements (Figure N + title + axes + legend + total cards + insight line + notes + Download PNG). Every KPI shows dual comparison (DoD + 7d avg). Sentiment colors match the context (cashout↑ = red for AUM, may flip elsewhere — explicit override mapping documented). Narrative follows SCQR + Key Terms + Impact Cards (`narrative-template.md`). Outline / Story Flow Check passes.
**Fail-mode:** Chart with no insight line. Single-delta KPI. Color used by default ("red = bad") in a context where the default is wrong.
**Why (Empirical):** Stakeholder confusion at this gate looks like "this is great work, but I do not know what to do with it." Visualization and story layer determine action, not data layer.

## Gate 5: Review

**Entry:** Viz + Story is locked.
**Exit:** 5 Quality Criteria (`quality-criteria.md`) pass — Interconnect, Compact, Insightful, Sufficient, Logical Reason. Rubric audit clean (`scripts/validators/rubric_audit.py`). For high-stakes deliverables, fresh-session review agent run (`subagent-prompt-discipline.md` §3).
**Fail-mode:** Self-review only, no fresh-session pass. Or: rubric findings dismissed without explanation.
**Why (Empirical):** Self-review is anchored. Fresh-session review or rubric_audit are cheap insurance.

---

## Retry budget

Each gate allows up to **3 retries** before escalating to the user:

- Retry 1: Fix the obvious gap (missing field, missing test, missing chart element).
- Retry 2: Re-examine assumptions (was the scope wrong? Is the method right for the data shape?).
- Retry 3: Surface to user — "Gate K failed for reason X after 2 fixes; recommend Y or Z option."

After 3 retries, do NOT keep iterating in-place. Escalate. Continued iteration is a Patch Ceiling signal — see `feedback_patch_ceiling_escalate_rebuild.md`.

**Why (Operational):** Without a retry budget, agents loop indefinitely on the same gate, burning context and time. Explicit budget forces escalation.

---

## Mapping pipeline → 7 modes

| Gate | Owning mode |
|------|-------------|
| 1. Scope | All modes — every mode starts with brief lock |
| 2. Data | `mode-query` (lock data) + `mode-process` (lock shape) |
| 3. Analysis | `mode-insight` (hypothesis → diagnostic → recommendation) |
| 4. Viz + Story | `mode-report` (assemble deliverable) |
| 5. Review | `mode-review` (Sub-mode A delivery refine / Sub-mode B full project) |

Orthogonal modes:
- `mode-automation` — wraps Gate 2 + 4 into a scheduled job.
- `mode-fix-pipeline` — re-enters Gate 2 / 4 surgically for a broken pipeline.

---

## Anti-patterns

- **Skipping Gate 2 because "the data is familiar."** Familiarity is exactly when stale mart lag bites.
- **Compressing Gate 3 into "we ran a t-test."** Method choice + falsification + multi-testing correction is the gate, not a single test.
- **Treating Gate 5 as a formality.** Self-review at Gate 5 = no review. Either rubric_audit + fresh-session, or do not call it reviewed.
- **Retrying the same fix 5 times.** Budget exists for a reason — escalate at 3.

## Cross-references

- 5 Quality Criteria (Gate 5 entry test) → `quality-criteria.md`.
- 6-Step EDA (Gate 2 exit test) → `mode-process.md`.
- BQ Safety Protocol (Gate 2 cost discipline) → `mode-query.md`.
- Outline / Story Flow Check (Gate 4 narrative test) → `self-check-protocol.md` Section A2.
- Patch Ceiling escalation (after 3 retries) → `feedback_patch_ceiling_escalate_rebuild.md`.

## Why this rule exists (Rule 4 meta)

Modes are a vocabulary; gates are a grammar. Without gates, modes compose in any order — and any order means rework. Gates encode "you are not allowed to advance until X" so the workflow converges instead of looping.
