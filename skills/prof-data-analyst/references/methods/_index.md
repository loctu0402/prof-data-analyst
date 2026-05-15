# Methods Index — Router

## Overview

This file routes any analytical-method question to the right spec file under `references/methods/`. Parent reference files (`causal-inference-toolkit.md`, `validation-evaluation-methods.md`) carry the DECISION TABLE — this file lists the specs in order with 1-line summaries + cross-references.

## How to use this index

1. User mentions a method by name (DiD, bootstrap, Bonferroni, etc.) → look up here → load the spec.
2. User describes a problem ("treated vs control with pre/post panel") → load the parent decision table first → it points to the right method → load that spec.
3. Agent reviewing rigor (Sub-mode B Pass 3 of `/da-review`) → loads the index to check for missing methods, then loads relevant specs.

## Reading order for a new analyst

1. `references/universal-workflow-rules.md` (rules) → 2. parent decision table (causal-inference-toolkit or validation-evaluation-methods) → 3. THIS file → 4. specific method spec.

## Causal Inference Family (6 methods)

Decision table parent: `references/causal-inference-toolkit.md`

| # | Method | When | Spec |
|---|--------|------|------|
| 1 | **Difference-in-Differences** | Treated + control + pre + post; parallel-trends holds | [methods/did.md](did.md) |
| 2 | **Event Study** | DiD + multi-period dynamics; want lead/lag coefficients | [methods/event_study.md](event_study.md) |
| 3 | **Regression Discontinuity** | Sharp cutoff on a running variable assigns treatment | [methods/rdd.md](rdd.md) |
| 4 | **Synthetic Control** | One treated unit, no good control, long pre-series | [methods/synthetic_control.md](synthetic_control.md) |
| 5 | **Propensity Score Matching** | Observational, known confounders, want ATT | [methods/psm.md](psm.md) |
| 6 | **Instrumental Variable** | Endogenous treatment, valid instrument exists | [methods/iv.md](iv.md) |

## Validation & Evaluation Family (8 methods)

Decision table parent: `references/validation-evaluation-methods.md`

| # | Method | When | Spec |
|---|--------|------|------|
| 7 | **Bootstrap CI** | n < 30 OR non-normal distribution OR custom statistic | [methods/bootstrap_ci.md](bootstrap_ci.md) |
| 8 | **Robustness checks** | Confirmatory finding; want sign-stable across specs | [methods/robustness_checks.md](robustness_checks.md) |
| 9 | **Sensitivity analysis** | Result depends on bandwidth / window / cutoff parameter | [methods/sensitivity_analysis.md](sensitivity_analysis.md) |
| 10 | **Falsification tests** | Method should give zero where effect should be zero | [methods/falsification_tests.md](falsification_tests.md) |
| 11 | **Multiple testing correction** | K > 1 tests; need Bonferroni (FWER) or BH-FDR | [methods/multiple_testing.md](multiple_testing.md) |
| 12 | **Post-hoc power** | p > 0.05 finding; disambiguate null vs under-powered | [methods/post_hoc_power.md](post_hoc_power.md) |
| 13 | **Cross-validation** | Want generalization estimate beyond one sample | [methods/cross_validation.md](cross_validation.md) |
| 14 | **Pre-registration** | Confirmatory analysis; lock plan before seeing data | [methods/pre_registration.md](pre_registration.md) |

## Method selection cheat sheet (collapsed view)

```
Question: identify causal effect?
  ├─ Treated + control + pre + post → DiD (or Event Study for multi-period)
  ├─ Sharp cutoff → RDD
  ├─ Single treated unit + long pre → Synthetic Control
  ├─ Observational + known confounders → PSM
  └─ Endogenous + instrument exists → IV

Question: is the result real?
  ├─ Small n or non-normal → Bootstrap CI
  ├─ Stable across specs? → Robustness checks
  ├─ Stable across parameter? → Sensitivity analysis
  ├─ Method gives zero on null data? → Falsification tests
  ├─ Multiple hypotheses tested? → Multiple testing correction
  ├─ Null result with small n? → Post-hoc power
  ├─ Generalizes beyond sample? → Cross-validation
  └─ Locked plan before EDA? → Pre-registration
```

## What's NOT in this index

Methods deliberately excluded (out of scope for v3):

- **Bayesian methods** (Bayesian regression, MCMC, hierarchical models) — heavyweight; defer to v4 unless workspace adopts PyMC
- **Time-series-specific** (ARIMA, Prophet, state-space, BSTS) — defer to a dedicated `methods/time_series_*.md` family in v4
- **Survival analysis** (Cox, Kaplan-Meier) — niche for DA work; load on-demand only
- **Tree-based interpretability** (SHAP, LIME) — model-explanation domain, not DA-rigor domain
- **Double-ML / LASSO + IV** — high-dim confounders rare in DA workflows; advanced

If a future v4 needs these, add the family + decision-table parent + per-method specs following `methods/_template.md`.

## Per-method status

| Spec | Written? | Validated against `_template.md`? | Reviewed by user? |
|------|----------|-----------------------------------|--------------------|
| did.md | ☑ | ☑ | ☐ |
| event_study.md | ☑ | ☑ | ☐ |
| rdd.md | ☑ | ☑ | ☐ |
| synthetic_control.md | ☑ | ☑ | ☐ |
| psm.md | ☑ | ☑ | ☐ |
| iv.md | ☑ | ☑ | ☐ |
| bootstrap_ci.md | ☑ | ☑ | ☐ |
| robustness_checks.md | ☑ | ☑ | ☐ |
| sensitivity_analysis.md | ☑ | ☑ | ☐ |
| falsification_tests.md | ☑ | ☑ | ☐ |
| multiple_testing.md | ☑ | ☑ | ☐ |
| post_hoc_power.md | ☑ | ☑ | ☐ |
| cross_validation.md | ☑ | ☑ | ☐ |
| pre_registration.md | ☑ | ☑ | ☐ |

All 14 specs written and template-validated 2026-05-14. User review pending.

## Why this index exists (Rule 4 meta)

A 14-method library without an index is unsearchable — analysts grep filenames or scroll. The index turns method choice into a 30-second lookup: read parent decision table → pick method → load spec. The cost is one extra file; the benefit is consistent method choice across the team.
