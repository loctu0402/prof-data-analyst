# Mode — Frame (Business Understanding → Metric → Data Plan → Data Model)

Invoke when user asks: "tôi có 1 yêu cầu mới", "stakeholder muốn", "tôi cần plan", "frame project mới", "metric define", "không biết bắt đầu từ đâu", "scope project", "kickoff", "/da-frame".

## Overview — Why this mode exists

The 7 original modes (query / process / insight / automate / report / review / fix) assume someone already framed the problem. But fresher DAs (and busy senior DAs starting a new project) often DON'T have a framed problem — they have a vague ask + maybe-data + a deadline.

**This mode is the front of the workflow.** Output is a `PLANNING.md` doc that locks: business question + metrics + data plan + chosen modeling pattern. The next mode (query / process / model / etc.) consumes that doc and executes.

**Why (Causal):** skipping framing → analyst computes wrong metric → 1-2 weeks rework. Industry-standard remedy: CRISP-DM Phase 1 (Business Understanding) + Kimball's Conformed Dimensions design step. Both put framing BEFORE data work. This mode packages them as 4 gates.

## When to invoke

- **New project kickoff** (no prior planning doc exists)
- **Stakeholder ask is vague** ("phân tích segment X", "build dashboard cho team")
- **Scope is ambiguous** (one-off vs recurring? exploratory vs hypothesis-driven?)
- **No prior data plan** (need to verify schema / discover domain / design new model)
- **Pivot mid-project** (original frame broke; need re-plan)

Skip Frame mode when: planning doc already exists + stakeholder has clear ask + data plan is set → jump to `da-query` or `da-process`.

## Mid-stream Gate 2 standalone (metric question only, no full project frame)

Common case: analysis already in flight, but mid-stream the user (or stakeholder) asks "which metric / dimension / framework fits here?". A full 4-gate Frame run is overkill.

Run **Gate 2 only** in this case:

1. Read existing project context if any (`PLANNING.md`, prior session notes, current deliverable draft). Do NOT re-frame the business question — assume it's already set.
2. Run Gate 2 (Metric Define) as a standalone protocol:
   - Identify the decision the metric must inform (1 sentence)
   - Pick framework from `metric-framework.md` decision table (NSM / OMTM / Growth Loop / HEART / AARRR / Diagnostic / Counter-metric / Unit Economics) — match framework to question type
   - Fill the 10-field metric contract (name / formula / grain / unit / cohort / window / baseline / threshold / owner / refresh)
   - Apply Section 0 KPI Stress Test: 5-criterion must-pass (tied to business goal / influences decisions / drives action / clear owner / tracked consistently)
3. Output: append the metric contract to the existing PLANNING.md (or write a `METRIC.md` if no planning doc exists). Skip Gates 1 / 3 / 4.

Total time: 15-25 min vs 1.5-3 hrs for the full frame.

Trigger phrases for this sub-mode: "metric nào phù hợp", "dimension nào nên dùng", "đo cái gì cho đúng", "stress test metric này", "mid-stream metric question".

## Four Gates (workflow)

This mode runs the 4-gate Planning Protocol (full detail: `planning-protocol.md`):

| Gate | Output | Effort |
|------|--------|--------|
| **Gate 1 — Business Understanding** | 5W1H table + stake/audience/reversibility | 15-30 min |
| **Gate 2 — Metric Define** | Metric contract(s) with framework chosen | 20-45 min |
| **Gate 3 — Data Plan** | TH1 schema verified OR TH2 modeling pattern chosen | 30 min - 2 hrs |
| **Gate 4 — Lock & Hand-off** | `PLANNING.md` written + route to next mode | 15 min |

Total: 1.5-3 hrs for a new project. Worth it: saves 5-10× downstream.

## Hard rules

1. **Each gate has user-confirm checkpoint.** Don't proceed to next gate without explicit OK. Cost of asking < cost of wrong direction.
2. **Cost ceilings respected at Gate 3.** TH2 schema discovery: $0.01 schema scan / $0.10 sample / $1.00 validation. Hit ceiling → STOP + surface.
3. **Metric contract MUST include all 10 fields.** Half-defined metrics cause downstream conflict. Use template from `metric-framework.md` Step 10.
4. **TH1 vs TH2 explicit choice.** Don't pretend data exists when it doesn't. Don't over-model when it does.
5. **Output is a doc**, not chat. `PLANNING.md` lives in project folder. Future sessions read it, don't re-frame.

## Phase routing (after Gate 4)

Based on `Next Mode` field in `PLANNING.md`:

| Next mode | When |
|-----------|------|
| `/da-query` | Schema known, SQL needed |
| `/da-process` | Data wrangling / EDA needed |
| `/da-model` | New data modeling pipeline needed (TH2 path) |
| `/da-insight` | Hypothesis framed, ready for diagnostic |
| `/da-automate` | Pipeline needs scheduling |
| `/da-report` | Stakeholder deliverable needs structure |

Orchestrator gate (if invoked via `/da-frame` after `/da`): confirm Next Mode before hand-off.

## Frame mode anti-patterns

| Anti-pattern | Symptom | Fix |
|--------------|---------|-----|
| **Skip to data immediately** | "Let me just check the data" | Stop. Run Gate 1 first. 30 min planning > 3 days wandering. |
| **Frame without stakeholder input** | Analyst-internal frame; stakeholder later disagrees | Gate 1.1 captures from stakeholder, not assumed |
| **Pick framework without question** | "Let's use OMTM" before knowing what's being decided | Gate 2.1 matches framework to question |
| **TH1 → TH2 silently** | Assumed data exists; actually doesn't | Gate 3 schema verification is mandatory |
| **Over-model for one-off** | Build 5-stage pipeline for 1 question | Gate 3.3 reuse over rebuild |
| **No PLANNING.md** | Plan lives in chat history; lost on session restart | Gate 4 mandatory output |

## Cross-references
- Workflow detail: `planning-protocol.md`
- Metric design deep dive: `metric-framework.md`
- Data modeling patterns: `mode-model.md`
- Schema discovery cost ceilings: `domain-discovery-protocol.md`
- Why a separate mode: universal-workflow-rules.md Rule 3 (5W1H Action Brief)

— part of prof-data-analyst · Loc Tu, 2026
