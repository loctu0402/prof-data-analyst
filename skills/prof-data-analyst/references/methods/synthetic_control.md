# Method — Synthetic Control

> When there's only ONE treated unit and many candidate control units, build a WEIGHTED COMBINATION of controls ("synthetic control") that matches the treated unit pre-treatment. Treatment effect = treated outcome − synthetic outcome post-treatment.

## Overview — Quick reference card

| Attribute | Value |
|-----------|-------|
| Type | Causal inference |
| Cost (compute) | Medium (constrained optimization for donor weights; in-space placebo loop) |
| Prerequisite data shape | Long pre-period for 1 treated unit + N donor units (N ≥ 10); plus a post-period |
| Output | Treatment effect over time + permutation p-value via in-space placebo |
| Bundled script | None bundled; use `pysyncon` or `SyntheticControlMethods` package |
| Reading time | 12 minutes |
| Primary source | Abadie & Gardeazabal (2003); Abadie, Diamond & Hainmueller (2010) |

## What — definition

The synthetic control is a weighted average of "donor" control units, with weights chosen to match the treated unit's PRE-treatment characteristics (outcome trajectory + covariates). Post-treatment, the synthetic provides the counterfactual — what the treated unit would look like without treatment. The gap between actual treated outcome and synthetic outcome is the treatment effect.

Inference is by PERMUTATION: re-run the procedure pretending each donor unit was treated; the treated unit's effect should be extreme among the placebo distribution.

## How — step-by-step protocol

1. **Define pre-period and post-period.** Need long pre-period (e.g., 30+ periods).
2. **Pick donor pool.** Untreated units similar enough to plausibly weight, but not so few that the optimization degenerates.
3. **Optimize weights** to minimize pre-period gap between treated and synthetic on outcome + chosen covariates. Constraints: weights non-negative, sum to 1.
4. **Compute post-treatment gap** = treated outcome − synthetic outcome for each post-period.
5. **In-space placebo**: re-run the procedure pretending each donor was treated. Get a distribution of placebo effects.
6. **Permutation p-value** = fraction of donor placebos with effect ≥ treated effect (in magnitude).

```python
# Using pysyncon
from pysyncon import Synth, Dataprep

dataprep = Dataprep(
    foo=panel,
    predictors=["covariate_1", "covariate_2"],
    predictors_op="mean",
    time_predictors_prior=range(2020, 2026),
    dependent="outcome",
    unit_variable="unit",
    time_variable="period",
    treatment_identifier=TREATED_UNIT,
    controls_identifier=[u for u in panel.unit.unique() if u != TREATED_UNIT],
    time_optimize_ssr=range(2020, 2026),
)
synth = Synth()
synth.fit(dataprep=dataprep)
```

## Why — Comparative

Synthetic Control exists because the standard DiD breaks down when there's only ONE treated unit: a single treated unit cannot have parallel-trends "tested" in the usual sense, and the SE of a 1-treated-unit DiD is ill-defined. Synthetic Control replaces "treated vs control" with "treated vs synthetic-built-from-controls" and replaces parametric SE with permutation inference.

This is a comparative-rationale Why: when DiD's identifying setup fails, Synthetic Control provides an alternative that uses the same panel-data information differently. It does NOT subsume DiD — it solves the specific single-treated-unit case better.

## When — trigger conditions

**Use Synthetic Control when:**
- Exactly ONE treated unit (or a small handful)
- LONG pre-period (≥ 20 periods recommended; more is better for fit)
- Many candidate donor units (≥ 10 untreated units)
- DiD doesn't work because you cannot define a "control group" cleanly

**Skip Synthetic Control when:**
- Multiple treated units → use DiD or Event Study
- Pre-period is short (<10 periods) — bad pre-fit; synthetic cannot match the trajectory
- Treated unit's pre-trajectory cannot be matched well by any weighted combination of donors (large pre-period RMSE) — synthetic is unreliable; consider alternative
- Donor pool contains units that experienced their own shocks during pre-period

## Where — workflow stage / artifact type

- Mode: `mode-insight` Phase 3 (Diagnostic, when DiD's setup fails)
- Phase: After verifying single-treated-unit setup and donor availability
- Artifact type: Synthetic vs treated trajectory plot + permutation distribution plot + treatment gap table

## Who — target roles

- **Runs the method**: DA senior or DS — requires optimization familiarity + permutation logic
- **Reads the output**: PM / Strategy / C-level reviewing a single-market or single-product intervention
- **Reviews the rigor**: Senior DA / DS in `mode-review` Sub-mode B Pass 3 — checks pre-fit quality and donor pool composition

## Acceptance gate — declare Synthetic Control "credible" only if

1. **Pre-period RMSE small** relative to outcome scale (rule of thumb: pre-RMSE < 5% of treated unit's average outcome)
2. **At least 10 donor units** in the pool
3. **In-space placebo distribution** computed → permutation p-value reported
4. **Donor weights inspected**: not concentrated on 1 donor (means weak match) and not uniform (means optimization barely active)
5. **Post-treatment gap is OUTSIDE the placebo distribution** at the chosen confidence level
6. **Sensitivity check**: removing the top-weighted donor doesn't flip the conclusion (`methods/robustness_checks.md`)

## Template — copy-paste starter

```python
"""Synthetic Control template.

Source: Abadie-Gardeazabal (2003); Abadie-Diamond-Hainmueller (2010).
Acceptance: pre-RMSE < 5% of outcome, ≥10 donors, permutation p reported, robust to top-donor drop.
"""

import pandas as pd
from pysyncon import Synth, Dataprep

panel = pd.read_csv("data/long_panel.csv")
TREATED = "city_X"
TREATMENT_PERIOD = 2026

dataprep = Dataprep(
    foo=panel,
    predictors=["pop", "gdp_per_capita"],
    predictors_op="mean",
    time_predictors_prior=range(2010, TREATMENT_PERIOD),
    dependent="outcome",
    unit_variable="unit",
    time_variable="period",
    treatment_identifier=TREATED,
    controls_identifier=[u for u in panel.unit.unique() if u != TREATED],
    time_optimize_ssr=range(2010, TREATMENT_PERIOD),
)
synth = Synth()
synth.fit(dataprep=dataprep)

# Pre-RMSE check
synth.summary()   # Inspect pre_rmspe

# Permutation: loop pretend-each-donor-treated → distribution of effects
# (pysyncon has placebo helpers)
```

## Worked example — single city promo launch

Setup: MoMo launched an AUM-boosting feature exclusively in Hà Nội in 2026-03. Question: did it increase AUM per user?

Setup:
- Treated: Hà Nội
- Donors: 20 other cities, similar GDP / population / banking penetration
- Pre-period: 2024-01 to 2026-02 (26 months)
- Outcome: AUM per user

Result (illustrative):
- Pre-period RMSE: 0.8% of treated mean ✓
- Synthetic = 0.32 · Đà Nẵng + 0.18 · TP.HCM + 0.15 · Hải Phòng + 0.10 · Cần Thơ + 0.25 · weighted-others ✓ (diverse)
- Post-treatment gap: +4.2% AUM per user in Hà Nội (M+1), +6.8% (M+2), +5.1% (M+3)
- In-space placebo: Hà Nội effect is the 1st largest among 21 units → permutation p = 1/21 ≈ 0.048 ✓
- Sensitivity: removing top donor (Đà Nẵng) gives +3.6% / +5.9% / +4.8% — same conclusion ✓

Verdict: feature launch caused ~5% AUM-per-user boost in Hà Nội over 3 months post-launch.

## Anti-patterns

- **No donor pool diversity.** If synthetic is 95%-one-donor, the method is essentially "compare to that one donor" — not a synthetic. Inspect weights.
- **Forcing a fit with too many predictors.** Over-fitting the pre-period RMSE produces a synthetic that matches by accident, not by genuine similarity.
- **Skipping the placebo permutation.** Without it, there's no inference — just a point estimate.
- **Reporting effect after a placebo unit produced an even larger effect.** If 5 of 21 placebos exceed the treated unit, the treated unit isn't unusual; permutation p > 0.20.
- **Choosing donor pool AFTER seeing post-period outcomes.** This is data-snooping. Donor pool is locked before looking at post-treatment data.

## Cross-references

- **Required prereq method**: long pre-period + donor pool selection (no formal method needed; judgement call)
- **Complementary methods**: `methods/robustness_checks.md` (top-donor drop), permutation-based inference
- **Alternative methods**: `methods/did.md` (multiple treated units), `methods/rdd.md` (sharp cutoff)
- **Bundled scripts**: None; install `pysyncon` or `SyntheticControlMethods`
- **Decision-table parent**: `references/causal-inference-toolkit.md`

## Reading order

1. THIS file
2. `methods/did.md` — for contrast (when DiD applies vs when Synthetic Control applies)
3. Primary sources: Abadie-Diamond-Hainmueller (2010) the canonical paper; Abadie (2021) JEP review
