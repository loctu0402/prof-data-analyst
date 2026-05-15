---
name: da-review
description: 3 sub-modes for review work. Sub-mode A Delivery Refine (lightweight polish, 15-30 min). Sub-mode B Full Project Refine (heavyweight audit: workflow + method maturity + advanced + fact-check + rework plan + user approval gate). Sub-mode C Stakeholder Questioning (formulate questions before analysis). Triggers on "review report", "refine deliverable", "audit project", "kiểm tra bài", "stakeholder questions", or /da-review.
---

# DA Review Mode

3 sub-modes for review work. User picks ONE at invocation.

## 4 Universal Rules (applied to critique itself)
1. Orientation Block at top (verdict + summary)
2. Baseline → Noise → Impact when citing metrics in the critique
3. 8-field Action Brief for any "should fix" recommendation
4. Why-Explanation on every finding (why does this matter, why this fix, why this severity)

Full: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/universal-workflow-rules.md`.

## Sub-modes

### Sub-mode A — Delivery Refine (lightweight, single deliverable)
Phases: read end-to-end → rubric_audit.py → human pass → outline / story flow check → deliver gap table with severity → user approval → apply fixes.
Time: ~15-30 min.

### Sub-mode B — Full Project Refine (heavyweight, multi-file audit)
Phases: target disambiguation → context-tracing read → project understanding summary (user confirm) → 6-pass audit (workflow / business+domain / method maturity / advanced-method / code+repro / delivery surface) → deliver audit + rework plan → user approval → execute plan top-to-bottom.
Time: ~1-3 hours.

### Sub-mode C — Stakeholder Questioning
Phases: map stakeholder → frame Q set with 5W1H+Goal → catch anti-patterns (approval-ask, vague scope, yes/no when need number) → suggest output form → compile brief.
Time: ~10-15 min.

Full workflow: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/mode-review.md`.

## Hard rules
- Iteration ceiling: max 3 review rounds; after 4th, escalate (rebuild / handoff / accept-with-limitations)
- Fresh-session review discipline: sub-agent for context-tracing gets ZERO generator context (anti-bias)
- Outline / Story Flow Check mandatory at Phase 3.5 (Sub-mode A) and Pass 6 (Sub-mode B)
- Method maturity check (Sub-mode B Pass 3): compare method-used vs causal-inference-toolkit decision table
- Rework plan in Sub-mode B is awaited user approval BEFORE execution

## Sub-agent integration
- `da-context-tracer` (Haiku) — Sub-mode B Phase 2 when project ≥ 5 files
- `da-method-auditor` (Sonnet) — Sub-mode B Pass 3 when causal claims present

Sub-agent prompt discipline: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/subagent-prompt-discipline.md`.

## Cross-references
- Full mode workflow: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/mode-review.md`
- Self-check: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/self-check-protocol.md`
- Quality criteria: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/quality-criteria.md`
- Method specs: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/methods/_index.md`
