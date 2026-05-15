# Validation & Evaluation Methods

When to load: user asks "is this result real?", "how do I confirm X?", "robustness check", "sensitivity analysis", "multiple testing", "post-hoc power", "should I trust this estimate?", "confirm a finding rigorously", or any check that goes beyond the headline number to ask whether it survives scrutiny.

## Overview — Why this toolkit exists

A single point estimate with a p-value is rarely enough to confirm a finding. Findings break under any of these stresses:
- The sample was unusual; a different sample would give a different answer
- The specification was lucky; different controls / different cutoffs flip the sign
- The result is one of many tests; multiple-testing correction wipes it out
- The test had too little power; the "null" is just "not enough data"
- The result was peeked-at and the metric chosen post-hoc

The methods below each address one specific failure mode. Stack the relevant ones before declaring a finding confirmed.

This file is the **decision table + 1-paragraph summary per method**. Full spec for each method lives in `references/methods/<name>.md` — load on demand.

## Decision Table — Which Validation When

| Concern | Method | Why this addresses the concern | Full spec |
|---------|--------|--------------------------------|-----------|
| Result depends on sample drawn | **Bootstrap CI** | Resamples with replacement → CI without parametric assumption | `methods/bootstrap_ci.md` |
| Result depends on specification | **Robustness checks** | Vary controls / functional form / sub-sample; sign should hold | `methods/robustness_checks.md` |
| Result depends on data window | **Sensitivity analysis** | Vary cutoffs / bandwidths / time window; magnitude should be stable | `methods/sensitivity_analysis.md` |
| You ran K tests | **Bonferroni or BH-FDR correction** | Adjusts α to control family-wise error or false discovery rate | `methods/multiple_testing.md` |
| Null result, but small sample | **Post-hoc power** | "Not significant" might mean "no effect" OR "no power" — disambiguate | `methods/post_hoc_power.md` |
| Your method "works" — try to break it | **Falsification test** | Run on data where effect should be zero; result should be zero | `methods/falsification_tests.md` |
| Cross-section result; want generalization | **Cross-validation** | K-fold split; result should hold across folds | `methods/cross_validation.md` |
| Researcher freedom drives the result | **Pre-registration** | Lock the hypothesis + analysis plan BEFORE seeing data | `methods/pre_registration.md` |

## 1. Bootstrap Confidence Intervals

Resample the sample WITH replacement B times (B ≥ 1000); compute the statistic on each resample; the 2.5th and 97.5th percentiles of the resulting distribution form a 95% CI without normality assumption.

Use when: n < 30 OR non-normal distribution OR custom statistic (median, ratio, custom KPI). Skip when: statistic depends on extremes (max, min, top-1%) or data is time-correlated (use block bootstrap instead). Bundled script: `scripts/stats/bootstrap_ci.py`.

→ Full spec: [methods/bootstrap_ci.md](methods/bootstrap_ci.md)

## 2. Robustness Checks

Re-run the headline analysis under 3-5+ alternative specifications: different functional forms, sub-samples (drop top 1%, drop pre-event, drop one region), control sets, outcome definitions, sample windows. If sign + magnitude survive across specs → robust. If one spec flips sign or changes magnitude > 50% → fragile.

Report a robustness TABLE with all specs, not just the headline.

→ Full spec: [methods/robustness_checks.md](methods/robustness_checks.md)

## 3. Sensitivity Analysis

Vary ONE parameter of the analysis (cutoff, bandwidth, window length, threshold) across a range; trace how the result moves. Plot: x = parameter, y = estimate with CI band. Stable line = parameter didn't drive result; sloping line = result depends on choice.

Distinct from robustness (which varies SPEC dimensions); sensitivity varies ONE parameter continuously. They complement each other.

### Special case — OLS anomaly window (time-series projection)

When OLS projection is used to derive an expected value or anomaly threshold (KVBD-style daily forecast, baseline-from-history), window choice dominates the result.

Rules:
- **Default window: last 3 months.** Longer windows pull in stale regimes; shorter windows are noisy.
- **Exclude structural breaks.** A regime shift (product launch, pricing change, COVID lockdown, fee restructure) inside the window biases the slope estimate. Drop the break window or split the analysis around it.
- **Document the window choice in the artifact.** "OLS fit on 2026-02-15 to 2026-05-14, excluding 2026-04-01 to 2026-04-07 (pricing reset)" lets the reader judge the choice.

Why these rules — anomaly detection that uses last-N-months blindly will flag a normal-but-post-regime-shift point as anomalous because the slope was learned from a different regime. Past incident: KVBD expected model + structural break = false anomalies; fix was exclude-break + last-3M window.

See `feedback_ols_anomaly_window.md`.

→ Full spec: [methods/sensitivity_analysis.md](methods/sensitivity_analysis.md)

## 4. Falsification Tests

Run the same method on data where the effect is KNOWN to be zero. If the method still finds an effect, the method is broken (or the original "effect" was spurious).

Examples: DiD on pre-pre vs pre periods (no treatment, should give zero); RDD at fake cutoffs above and below the real cutoff (should give zero); Synthetic Control in-space placebo (treated unit's effect should be extreme among donor placebos); IV reduced form on an outcome the instrument should not affect.

→ Full spec: [methods/falsification_tests.md](methods/falsification_tests.md)

## 5. Multiple Testing Correction

When you run K tests at α = 0.05, the probability of at least one false positive is `1 − (1 − 0.05)^K` — far above 0.05 for K ≥ 2. Two corrections:

**Bonferroni (FWER control)**: α / K per test. Conservative; controls "any false positive" probability. Use for confirmatory / regulatory / high-stakes work.

**Benjamini-Hochberg (FDR control)**: Order p-values, find largest k where `p_(k) ≤ (k / K) × α`. Less conservative; controls expected proportion of false positives among rejections. Use for exploratory / shortlist ranking.

Caveat: α (FPR) ≠ (1 − Precision) (FDR) — different denominators; class-imbalanced contexts diverge 4-10×. Cite the denominator explicitly when teaching. Bundled script: `scripts/stats/multiple_testing.py`.

→ Full spec: [methods/multiple_testing.md](methods/multiple_testing.md)

## 6. Post-Hoc Power Analysis

You ran a test, got p > 0.05, want to claim "no effect." Was that conclusion driven by truly-zero effect or by under-powered sample? Power at the MDE (minimum detectable effect — set BEFORE data, by business meaning) answers this:

- Power ≥ 0.80 at MDE → null is informative; "no effect at MDE" is credible
- Power < 0.80 at MDE → null is uninformative; sample was insufficient

Caveat: NEVER use observed-effect-size power (Hoenig & Heisey 2001). Always use MDE. Bundled script: `scripts/stats/mde_sample_size.py`.

→ Full spec: [methods/post_hoc_power.md](methods/post_hoc_power.md)

## 7. Cross-Validation

K-fold CV: split data into K equal folds; for each fold, train on K-1 folds and evaluate on the held-out fold; average across K folds. Tighter estimate of generalization performance than single train-test split.

Choose the right splitter for data type: STRATIFIED for imbalanced classification, TIME-SERIES for ordered data (no future-to-past leakage), LEAVE-ONE-GROUP-OUT for grouped data. K ≥ 5 standard; report mean ± std across folds.

For hyperparameter tuning, use NESTED CV (inner CV for tuning, outer for reporting) to avoid leakage.

→ Full spec: [methods/cross_validation.md](methods/cross_validation.md)

## 8. Pre-Registration

BEFORE seeing the data, write down: hypothesis (falsifiable, directional), outcome metric + aggregation, sample inclusion/exclusion, statistical method + identifying assumption, decision rule with threshold for "real." Commit the document (git, OSF, internal log) with timestamp.

Run the analysis. If you followed the plan → confirmatory finding. If you deviated → exploratory finding (label as such). Even a 5-line markdown cell at the top of a notebook counts.

The cheapest validation method (zero compute cost) and the strongest defense against researcher degrees of freedom.

→ Full spec: [methods/pre_registration.md](methods/pre_registration.md)

## How to Stack These (typical confirmatory analysis)

Before declaring a finding confirmed, run AT LEAST:

1. **Headline estimate + parametric CI** (baseline)
2. **Bootstrap CI** if n < 30 or distribution non-normal → `methods/bootstrap_ci.md`
3. **Robustness across 3+ specs** — sign holds → `methods/robustness_checks.md`
4. **Sensitivity across parameter ranges** — magnitude stable → `methods/sensitivity_analysis.md`
5. **Multiple-testing correction** if K > 1 tests → `methods/multiple_testing.md`
6. **Falsification test** appropriate to the method → `methods/falsification_tests.md`
7. **Pre-registration check** — does the result match what you planned to find? → `methods/pre_registration.md`

If 6 of 7 pass and 1 fails, the finding has a specific weakness — report it. If 3+ fail, the finding is fragile — re-collect data or change method.

## Why this stacking, not "one definitive test"

There is no single test that confirms a finding. Each method addresses one failure mode. Stacking them is the empirical way to triangulate. A finding that survives bootstrap + robustness + sensitivity + falsification is far more credible than one with a tiny p-value alone.

## Reporting Standard

Every confirmed finding ships with:
- The original estimate + parametric CI
- A robustness table (≥3 specs, sign + magnitude)
- A sensitivity plot OR table (parameter range)
- Multiple-testing-adjusted p-value if K > 1
- A line stating which falsification test was run and its result
- A line stating which methods you DID NOT run and why (honesty)

Per Rule 4: every method chosen needs a Why; every method skipped needs a Why too.

## Reading Order

1. THIS file — decision table + 1-paragraph summary + pointer to full spec
2. `references/methods/<chosen-method>.md` — full spec for the chosen method
3. `references/causal-inference-toolkit.md` — the underlying causal method (these validations validate THAT method's result)
4. `references/universal-workflow-rules.md` — Rule 2 (Baseline-Noise-Impact) is the headline number; this file is the confirmation
5. Bundled scripts: `bootstrap_ci.py`, `multiple_testing.py`, `mde_sample_size.py`, `parallel_trends_test.py`
