# Causal Inference Toolkit

When to load: user asks for "why X caused Y", "did the policy work", "DiD", "Event Study", "RDD", "synthetic control", "PSM", "instrumental variable", "causal effect", "treatment effect", or any analysis that goes beyond correlation to claim a cause.

## Overview — Why this toolkit exists

Most DA work answers `what changed?` and `does X correlate with Y?`. Neither is causal. When a stakeholder asks "did our intervention work?" — bare correlation is the most common wrong answer, because:

- A pre/post comparison ignores secular trends (the metric would have moved anyway)
- A treated-vs-control comparison ignores selection bias (the groups differ for reasons besides treatment)
- A regression with controls ignores omitted confounders (you cannot control for what you don't measure)

The methods below each address one specific identification gap. **Wrong method → wrong causal claim → stakeholder distrust.** Each method has a specific assumption it requires; that assumption is the price you pay for the causal claim.

This file is the **decision table + 1-paragraph summary per method**. Full spec for each method lives in `references/methods/<name>.md` — load on demand.

## Decision Table — Which Method When

| Question / Data Setup | Method | Key assumption | Falsification test | Full spec |
|------------------------|--------|----------------|--------------------|-----------|
| Treated group + control group + pre/post timestamps | **Diff-in-Diff (DiD)** | Parallel trends pre-treatment | Event-study leads ≈ 0 | `methods/did.md` |
| Same as DiD + multi-period sharp event + dynamic effects | **Event Study** | Same as DiD + dynamic effects | Pre-event coefficients ≈ 0 | `methods/event_study.md` |
| Treatment assigned by a sharp cutoff on a running variable | **Regression Discontinuity (RDD)** | Continuity of potential outcomes at cutoff | McCrary density test + covariate balance | `methods/rdd.md` |
| One treated unit, no good control, long pre-treatment series | **Synthetic Control** | Weighted control reproduces pre-treatment outcomes | In-space placebo permutation | `methods/synthetic_control.md` |
| Observational, known confounders, want ATT | **Propensity Score Matching (PSM)** | Conditional independence given covariates | Covariate balance post-match + Rosenbaum bounds | `methods/psm.md` |
| Endogenous treatment, valid instrument exists | **Instrumental Variable (IV)** | Relevance + exclusion + monotonicity | First-stage F ≥ 10 + overidentification J-test | `methods/iv.md` |

If none fit → state honestly: "Cannot identify causal effect with this data; reporting correlation only."

Why this matters — the methods are not interchangeable. Picking DiD where RDD fits, or PSM where IV is required, produces a wrong-but-plausible number. The decision table is the first step; the method spec is the second.

## 1. Difference-in-Differences (DiD)

Compare the BEFORE-AFTER change in the treated group to the BEFORE-AFTER change in an untreated control group. The DiD estimator subtracts both time-invariant group differences AND common time shocks, isolating the treatment-specific change.

Identifies ATT (Average Treatment effect on the Treated) under the parallel-trends assumption. Bundled script: `scripts/causal/did_event_study.py did`.

→ Full spec: [methods/did.md](methods/did.md)

## 2. Event Study

Extension of DiD with multiple pre and post periods. Each event-time coefficient β_τ shows the treatment effect τ periods relative to the event. Pre-event coefficients (τ < 0) double as the parallel-trends test.

Reveals dynamics that DiD's single post coefficient hides. Bundled script: `scripts/causal/did_event_study.py event-study`.

For STAGGERED treatment timing (different units treated at different times), the naïve TWFE Event Study is biased (Goodman-Bacon 2021); use Callaway-Sant'Anna (2021) or Sun-Abraham (2021) estimators instead.

→ Full spec: [methods/event_study.md](methods/event_study.md)

## 3. Regression Discontinuity (RDD)

When treatment is assigned by a sharp cutoff on a continuous running variable (credit score ≥ 700, age ≥ 18, score ≥ threshold), compare units just above to units just below — they are quasi-randomly assigned.

Identifies LATE at the cutoff under the continuity assumption. Critical falsification: McCrary density test (running variable should not be manipulated at the cutoff).

No bundled script — use the `rdrobust` package for proper standard errors and optimal bandwidth selection (Calonico-Cattaneo-Titiunik 2014).

→ Full spec: [methods/rdd.md](methods/rdd.md)

## 4. Synthetic Control

When there's ONE treated unit (a city, market, product line) and many candidate donor units, construct a "synthetic control" as a weighted combination of donors that matches the treated unit pre-treatment. Treatment effect = treated outcome − synthetic outcome post-treatment.

Inference via in-space placebo: pretend each donor was treated; the real treated unit's effect should be extreme among the placebo distribution.

No bundled script — use `pysyncon` or `SyntheticControlMethods` package. The optimization requires constrained quadratic programming.

→ Full spec: [methods/synthetic_control.md](methods/synthetic_control.md)

## 5. Propensity Score Matching (PSM)

Estimate each unit's probability of being treated (propensity score) via logistic regression on observed covariates. Match each treated unit to a control unit with similar score. Compare outcomes within matched pairs.

Identifies ATT under selection-on-observables (strong assumption — cannot handle unobserved confounders). Rosenbaum bounds quantify sensitivity to that violation.

No bundled script — use `psmpy` or `causalinference`. Always run + report covariate balance post-match (SDM < 0.1) and Rosenbaum Γ sensitivity.

→ Full spec: [methods/psm.md](methods/psm.md)

## 6. Instrumental Variable (IV / 2SLS)

When treatment is endogenous (correlated with the error term) and you have a valid instrument Z (relevant + excluded + monotone), use 2SLS to recover the causal effect on COMPLIERS (LATE — Local Average Treatment Effect).

The hardest method to use credibly — exclusion restriction is untestable, weak instruments bias estimates MORE than OLS. Require first-stage F ≥ 10 (some demand F ≥ 23 for ≤10% bias).

No bundled script — use `linearmodels.IV2SLS` (correct standard errors built in).

→ Full spec: [methods/iv.md](methods/iv.md)

## Reporting Standard (every causal claim)

Whenever you ship a causal estimate, the deliverable MUST include:

1. **Method name + why** — "Used DiD because we have treated + control groups with pre/post timestamps. Considered Synthetic Control but our control group has a credible parallel-trend match."
2. **Identification assumption stated** — "Assumes parallel trends in absence of treatment."
3. **Falsification test result** — "Event-study leads −3, −2, −1 are statistically zero (p = 0.32, 0.48, 0.18); parallel trends not rejected."
4. **Point estimate + 95% CI** — "ATT = 12.4M VND per user-month, 95% CI [4.1, 20.7]."
5. **Sensitivity / robustness** — "Result robust to: bandwidth choice (10d vs 20d window), alternative outcome definition (log Y vs Y), exclusion of top-1% outliers." See `methods/robustness_checks.md` and `methods/sensitivity_analysis.md`.
6. **Limitations** — "Cannot rule out unobserved confounders that vary differently between groups over time. Recommend RCT for tier-1 confirmation."

Without these six fields, a causal claim is not falsifiable and stakeholders should treat it as correlational. Per Rule 4 (Why-Explanation), each field answers a Why that the method itself raises.

## Why "I just ran a regression with controls" is not enough

A reader of a regression with controls cannot tell:
- Whether the controls cover all confounders
- Whether the treatment was as-good-as-randomly assigned given controls
- Whether the SE accounts for clustering / matching / design

The 6 methods above are not extra steps for rigor; they are the specific assumption-and-test pairs that turn "regression coefficient" into "causal effect". If your task answers "did X cause Y?", regression with controls is a step in the analysis — not the answer.

## Reading Order

1. THIS file — decision table + 1-paragraph summary + pointer to full spec
2. `references/methods/<chosen-method>.md` — full spec for the chosen method
3. `references/validation-evaluation-methods.md` — robustness, sensitivity, multiple testing, falsification (post-estimation validation)
4. `references/universal-workflow-rules.md` — especially Rule 4 (Why-Explanation): every method choice needs a Why
5. Bundled scripts: `scripts/causal/did_event_study.py`, `scripts/causal/parallel_trends_test.py`
