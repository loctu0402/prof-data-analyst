---
description: Professional Data Analyst — report mode. Build stakeholder deliverable from a template catalog, with style polish and pre-ship validators.
---

Invoke the `prof-data-analyst` skill in **report mode**. Read these references before acting:
1. `references/mode-report.md` — template catalog, build workflow, HTML patterns
2. `references/universal-workflow-rules.md` — SCQR orientation, baseline-noise-impact, action brief
3. `references/style-rules.md` — AI-tell ban, numbers, charts, language conventions
4. `references/self-check-protocol.md` — pre-ship checklist

User's report request: $ARGUMENTS

Workflow:
- Confirm audience + format + language + length BEFORE forking template
- Fork template into `output/projects/<name>/` or `output/reports/`
- Apply Orientation Block (SCQR or 3-line intro) at top
- Every chart: organization brand theme + inline `→ takeaway` verdict
- Every number: run `scripts/stats/baseline_noise_impact.py` — quote the verdict
- Every recommendation: 8-field Action Brief (validate with `scripts/validators/action_brief.py`)
- Run `scripts/validators/self_check.py <file>` before declaring done — DO NOT auto-send

