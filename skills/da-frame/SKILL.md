---
name: da-frame
description: Front-of-workflow planning mode — Business Understanding → Metric Define → Data Plan (TH1 schema-exists / TH2 brainstorm-modeling) → Lock & Hand-off. Outputs a PLANNING.md doc that downstream modes consume. Triggers on "frame project", "kickoff", "stakeholder muốn X", "metric define", "không biết bắt đầu từ đâu", "scope project", or /da-frame. Run BEFORE da-query/da-process when project is new or scope is ambiguous.
---

# DA Frame Mode

The front of the DA workflow. Translate a vague stakeholder ask into a locked plan with metrics + data strategy + next-mode routing.

## 4 Universal Rules (apply to all output)

1. **Orientation Block** — PLANNING.md opens with SCQR.
2. **Baseline → Noise → Impact Ladder** — metric contract MUST specify comparability baseline.
3. **Question → Goal → 5W1H Action Brief** — Gate 1 outputs the 5W1H table.
4. **Why-Explanation (META)** — every metric choice + framework choice has 1-line Why.

Full rules: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/universal-workflow-rules.md`.

## Mode workflow — 4 Gates

Full workflow: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/mode-frame.md` + `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/planning-protocol.md`.

| Gate | Output | Effort |
|------|--------|--------|
| **Gate 1 — Business Understanding** | 5W1H + stake + audience + reversibility | 15-30 min |
| **Gate 2 — Metric Define** | Metric contract(s) per chosen framework | 20-45 min |
| **Gate 3 — Data Plan** | TH1 schema-verified OR TH2 modeling-pattern-chosen | 30 min - 2 hr |
| **Gate 4 — Lock & Hand-off** | `PLANNING.md` written + route to next mode | 15 min |

## Hard rules

- **Each gate has user-confirm checkpoint** — don't proceed without explicit OK
- **TH1 vs TH2 explicit choice** at Gate 3 — don't pretend data exists when it doesn't
- **Metric contract MUST include 10 fields** (see `metric-framework.md` Step 10)
- **Output is a doc (`PLANNING.md`), not chat** — future sessions read it
- **Cost ceilings respected at Gate 3** ($0.01 schema scan / $0.10 sample / $1.00 validation)

## Phase routing (after Gate 4)

Based on `Next Mode` field in `PLANNING.md`:

| Next mode | When |
|-----------|------|
| `/da-query` | Schema known, SQL needed |
| `/da-process` | Data wrangling / EDA needed |
| `/da-model` | New pipeline modeling needed (TH2 path) |
| `/da-insight` | Hypothesis framed, ready for diagnostic |
| `/da-automate` | Pipeline needs scheduling |
| `/da-report` | Stakeholder deliverable needs structure |

## Cross-references
- Full mode workflow: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/mode-frame.md`
- Planning protocol (gates detailed): `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/planning-protocol.md`
- Metric framework selection: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/metric-framework.md`
- Domain discovery (TH2 path): `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/domain-discovery-protocol.md`
- Self-check: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/self-check-protocol.md`
