---
name: da-insight
description: Hypothesis → Diagnostic → Recommendation workflow with causal-method matching, 5-stage reasoning chain, anti-bias protocol, validation stacking. Triggers on "phân tích insight", "hypothesis validation", "diagnostic", "why X", "root cause", or /da-insight.
---

# DA Insight Mode

Hypothesis-driven analysis: from "what happened" descriptive to "why it happened" diagnostic with causal rigor.

## 4 Universal Rules
1. Orientation Block (SCQR for written, 3-line for dashboard)
2. Baseline → Noise → Impact ladder for every numeric finding
3. 8-field Action Brief for every recommendation
4. Why-Explanation on every method choice (DiD over Pearson? Why. Bootstrap vs parametric? Why.)

Full: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/universal-workflow-rules.md`.

## Mode workflow

9 phases:
1. Scope & Hypothesize (3-5 hypotheses + validation criteria)
2. Data Collection (internal + market + competitor)
3. Diagnostic Techniques (match to situation — DiD / Event Study / RDD / Synthetic Control / PSM / IV)
4. Statistical Methodology (Pearson, effect size, CV vs MDE, α vs FDR, 3 hypothesis traps)
5. Self-Evaluation (methodology / proxy / sample / confounding / direction / consistency audit)
6. Anti-Bias Protocol (counter-arguments, multi-dimensional, structural vs cyclical)
7. Reasoning Output (5-stage chain: Fact → Mechanism → Behavior → Impact → Evidence)
8. Hypothesis Verdicts (ĐÚNG / MỘT PHẦN / KHÔNG)
9. Recommendations (8-field brief, C-level tone)

Full workflow: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/mode-insight.md`.

## Method specs
Causal inference: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/causal-inference-toolkit.md` (decision table) + `methods/<name>.md` (full spec per method).
Validation: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/validation-evaluation-methods.md` + `methods/<name>.md`.

## Hard rules
- Wrong method → wrong causal claim. Match method to data setup before estimating.
- Heavy-tail outcomes (median≈0, SD/mean>3×) → Wilcoxon + winsorize + median Δ
- Multiple testing: K > 1 → Bonferroni or BH-FDR correction
- Never claim causal without falsification test
- Connect-the-Dots: never state-the-fact alone

## Cross-references
- Full mode workflow: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/mode-insight.md`
- Quality criteria: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/quality-criteria.md`
- Self-check: `${CLAUDE_PLUGIN_ROOT}/skills/prof-data-analyst/references/self-check-protocol.md`
