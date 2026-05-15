---
description: Professional Data Analyst — review/refine mode. 3 sub-modes: Delivery Refine (lightweight) / Full Project Refine (heavyweight) / Stakeholder Questioning.
---

Invoke the `prof-data-analyst` skill in **review/refine mode**. Read these references before acting:
1. `references/mode-review.md` — 3 sub-modes (A Delivery / B Full Project / C Stakeholder)
2. `references/universal-workflow-rules.md` — Rules 1-4 as critique lens
3. `references/style-rules.md` — AI-tell ban, polish standards
4. `references/self-check-protocol.md` — what to check for
5. For Sub-mode B only: `references/causal-inference-toolkit.md` + `references/validation-evaluation-methods.md` — method-maturity audit basis

User's review/refine target: $ARGUMENTS

## Step 1 — Disambiguate sub-mode + target (MANDATORY)

If $ARGUMENTS is empty or vague, ASK the user:

```
Bạn muốn review theo option nào?

  A — Delivery Refine (~15-30 min, 1 file)
      Polish 1 deliverable: presentation, wording, format, charts, layout, checklist.
      Pick this if report đã có đủ thông tin / approach OK; chỉ cần polish + verify checklist.

  B — Full Project Refine (~1-3 hours, multi-file)
      Audit toàn bộ project: workflow + cache + logic + approach + method + advanced/academic
      + fact-check + code-check. Returns rework plan, awaits approval, executes.
      Pick this if cần kiểm tra approach có đủ rigor, method có advance được không, có miss
      khía cạnh gì không.

  C — Stakeholder Questioning (~10-15 min)
      Chuẩn bị câu hỏi cho stakeholder meeting BEFORE analyse.

Target nào? (file path / project folder / mô tả ngắn — tôi sẽ tìm)
```

If target description ambiguous → glob/grep candidates, list 3 closest matches, ask which one.

If user gives only target → infer sub-mode (single file → A; folder/multi-file → B); confirm before proceeding.

## Step 2 — Execute the chosen sub-mode

### Sub-mode A — Delivery Refine
- Read artifact end to end
- Run `python scripts/validators/rubric_audit.py <file>` for mechanical compliance
- Human pass: numbers (Ladder), reasoning (5-stage chain), style polish, code discipline
- Deliver gap table with severity BLOCKER/HIGH/MEDIUM/LOW + fix per row + headline verdict (ship/fix-then-ship/rebuild)
- Ask user: Approve fixes? Or revise list?
- On approve: switch to fix-pipeline / report / insight mode as appropriate, execute fixes

### Sub-mode B — Full Project Refine
- Phase 1: Target disambiguation — confirm project root + headline + sources + method files
- Phase 2: Context-tracing read → produce Project Understanding Summary, get user confirm BEFORE auditing
- Phase 3: 6-pass audit:
  - Pass 1 Workflow integrity (pipeline reproducibility, cache discipline, output discipline, pre-commit/CI, auto-send safety)
  - Pass 2 Business logic + domain accuracy (cite-check external numbers, domain terms, cohort definitions, units, "obvious-by-definition" flags)
  - Pass 3 Method maturity (method-actually-used vs `causal-inference-toolkit.md` decision table; validation stacking per `validation-evaluation-methods.md`)
  - Pass 4 Advanced-method opportunities (heavy-tail switch, staggered DiD, time-series structural, survival, Double-ML)
  - Pass 5 Code & reproducibility (tests, env pinning, secrets, logging, idempotency, Karpathy 4)
  - Pass 6 Delivery surface (run rubric_audit.py across all narrative files in project)
- Phase 4: Deliver structured rework plan (BLOCKER → polish bucket; per-item effort + Why + which mode to switch into)
- Phase 5: User approve → execute plan top-to-bottom across modes

### Sub-mode C — Stakeholder Questioning
- Map stakeholder (role, level, decision authority, language)
- Frame question set with 5W1H + Goal
- Catch anti-patterns (approval-ask, vague scope, yes/no when need number, missing acceptance criteria)
- Suggest output form upfront (chat / chart / mini-report / deep dive)
- Compile brief with top 3 questions + criteria + form + timeline

## Universal discipline (all sub-modes)

- Push back if user's choice is weak. Do NOT bandwagon-agree.
- Every finding has `file:line` (Sub-mode A) or `path:section` (Sub-mode B) + concrete fix + Why
- Severity assigned, not "all equally bad"
- Sub-mode B: Project Understanding confirmed BEFORE audit; rework plan approved BEFORE execution
