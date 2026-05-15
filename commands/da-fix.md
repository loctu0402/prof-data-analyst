---
description: Professional Data Analyst — fix-pipeline mode. Debug existing pipeline / report bug surgically.
---

Invoke the `prof-data-analyst` skill in **fix-pipeline mode**. Read these references before acting:
1. `references/mode-fix-pipeline.md` — bug triage tree, common silent bugs, patch-ceiling rule
2. `references/coding-discipline.md` — surgical changes, no drive-by refactor
3. `references/self-check-protocol.md` — section J (code) + L (pipeline)

User's bug report: $ARGUMENTS

Workflow:
- Triage symptom via decision tree (HTML / data missing / silent fail / wrong numbers / drift / recurring)
- HTML bug → CREATE `update_report_vN.py`, NEVER edit `generate_report.py`
- Cache schema drift → check 2026+ revenue tier split, Túi+ legacy union, Xu→VND ratio change
- Numerical bug → cross-card reconciliation + back-derive headlines (call advisor if stuck)
- Silent bugs → check state-machine neighbor inheritance, two-cache-files mismatch, OLS anomaly window
- Patch ceiling: ≥3 distinct bugs same artifact → STOP patching, surface rebuild option

Surgical Karpathy: every changed line traces to the bug. No adjacent cleanup.
After fix: verify pipeline end-to-end, NOT just unit test.
