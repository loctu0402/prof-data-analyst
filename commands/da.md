---
description: Professional Data Analyst — master entry. Lists 7 modes (Query→Process→Insight→Automation→Report + Review + Fix) and routes user to the right one.
---

Invoke the `prof-data-analyst` skill. The user typed `/da` without a mode — list the 7 available modes briefly:

Standard DA flow:
- `/da-query` — BQ semantic-first SQL workflow
- `/da-process` — Raw data → ML-ready features (DuckDB DWH, M1-M5, ExecSum)
- `/da-insight` — Hypothesis → diagnostic → recommendation
- `/da-automate` — Pipeline setup + email-on-fail
- `/da-report` — Build stakeholder report from template

Orthogonal helpers:
- `/da-review` — Code / output review or stakeholder questioning
- `/da-fix` — Debug existing pipeline / report bug

User's optional context for routing: $ARGUMENTS

If user's intent maps clearly to one mode, suggest it and invoke skill with that mode. Otherwise ask 1 question to disambiguate, then invoke.
