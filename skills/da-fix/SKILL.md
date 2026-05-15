---
name: da-fix
description: Surgical pipeline / report debug workflow. Bug triage decision tree. NEVER edit generator for HTML patch (use update_report_vN.py overlay). Cache verify. Numerical debug. Silent data-layer bugs. Wire email-on-fail. Patch ceiling escalation after 3 patches. Triggers on "fix pipeline", "sửa pipeline", "debug pipeline", "report sai", "bug ở ...", or /da-fix.
---

# DA Fix Mode

Surgical debug for pipeline / report bugs. Triage by symptom; touch only what's broken.

## 4 Universal Rules
1. Orientation Block on patch summary (what broke, what fixed, how verified)
2. Baseline → Noise → Impact for any metric used to verify the fix
3. 8-field Action Brief if recommending follow-up changes
4. Why-Explanation on the fix choice + the rejected alternatives

Full: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/universal-workflow-rules.md`.

## Mode workflow

Bug triage decision tree routes symptom to repair pattern:
- HTML report visually wrong → update_report_vN.py overlay (NEVER edit generator)
- Data missing in cache → cache verify → BQ direct query → repull
- Pipeline failed silently → wire email-on-fail
- Wrong numbers → cross-card reconciliation + back-derive
- Model bias / surprising drift → silent data-layer bugs (state machine neighbor / two cache files / OLS window)
- ≥3 distinct bugs in same artifact → STOP, escalate to rebuild

Full workflow: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/mode-fix-pipeline.md`.

## Hard rules
- NEVER edit `generate_report.py` for HTML patch — use `update_report_vN.py` overlay
- After patch validated: PROPOSE equivalent change to generator, DO NOT commit until user confirms
- Validate fix end-to-end (NOT just unit test): run pipeline, compare output checksum / row count vs expected, cross-validate vs BQ direct query
- Patch ceiling: ≥3 patches in same artifact → handoff spec doc + escalate to rebuild
- Surgical Karpathy principle: every changed line traces to the bug

## Cross-references
- Full mode workflow: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/mode-fix-pipeline.md`
- Coding discipline: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/coding-discipline.md`
- Self-check: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/self-check-protocol.md`
