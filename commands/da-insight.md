---
description: Professional Data Analyst — insight mode. Hypothesis → diagnostic → recommendation with anti-bias protocol.
---

Invoke the `prof-data-analyst` skill in **insight mode**. Read these references before acting:
1. `references/mode-insight.md` — hypothesis flow, diagnostic techniques, statistical methodology
2. `references/universal-workflow-rules.md` — 5-stage reasoning chain, baseline-noise-impact ladder
3. `references/style-rules.md` — connect-dots presentation, "Reading in business terms" column

User's WHY question: $ARGUMENTS

Workflow:
- Phase 1: Define WHY question + 3-5 hypotheses (internal / market / seasonal / behavioral)
- Phase 2: Data collection — verify cache columns, NEVER fallback placeholder
- Phase 3: Pick diagnostic technique (Pearson / DiD / Event Study / Anomaly / Turning Point / Sentiment Channel)
- Phase 4: Statistical methodology — Pearson n ≥ 83 for p<0.05 at |r| ≥ 0.22; step-function variables = Event Study NOT Pearson
- Phase 5: Self-eval (methodology, proxy, sample, confounding, direction, numerical consistency)
- Phase 6: Anti-bias — every negative finding gets counter-argument; structural vs cyclical distinction
- Phase 7: 5-stage chain (Fact → Mechanism → Behavior → Impact → Evidence) for every finding
- Phase 8: Hypothesis verdicts (ĐÚNG / MỘT PHẦN / KHÔNG)
- Phase 9: 8-field Action Brief for recommendations

If scope is large (multi-tab HTML, ≥4 market variables, C-level audience, ≥2-day budget): consider switching to `deep-dive-analysis` skill instead.
