# Method — Propensity Score Matching (PSM)

> When treatment is observational and you have rich confounders, MATCH each treated unit to a similar control unit based on the estimated probability of being treated (propensity score). Then compare outcomes within matched pairs.

## Overview — Quick reference card

| Attribute | Value |
|-----------|-------|
| Type | Causal inference (selection-on-observables) |
| Cost (compute) | Medium (logistic regression for PS + nearest-neighbor matching) |
| Prerequisite data shape | Cross-sectional or panel; rich covariates assumed sufficient to capture confounding |
| Output | ATT (matched-pair averaged) + SE + covariate-balance table |
| Bundled script | None bundled; use `psmpy` or `causalinference` Python package |
| Reading time | 10 minutes |
| Primary source | Rosenbaum & Rubin (1983); Imbens & Rubin (2015) "Causal Inference for Statistics, Social, and Biomedical Sciences" |

## What — definition

PSM estimates each unit's probability of being treated as a function of observed covariates (propensity score, PS). Then for each treated unit, find a control unit with similar PS — these are "matched pairs". The treatment effect is the average outcome difference within matched pairs.

The intuition: if two units have the same propensity score, they had the same probability of being treated; their treatment status is "as-if random" conditional on the score. The catch: only TRUE if all relevant confounders are observed and included in the PS model.

## How — step-by-step protocol

1. **Estimate propensity score**: logistic regression of `treated ~ covariates`. Save PS per unit.
2. **Choose matching algorithm**: nearest-neighbor (1:1), k-nearest-neighbor, caliper matching, kernel matching. NN-1 with caliper is the safest default.
3. **Match treated → control**: for each treated unit, find the closest control unit by PS within the caliper.
4. **Check covariate balance** post-match: SDM (standardized mean difference) of each covariate; target |SDM| < 0.1.
5. **Compute ATT** as mean outcome difference across matched pairs.
6. **Sensitivity analysis** (Rosenbaum bounds): how much unobserved confounding would overturn the result?

```python
from psmpy import PsmPy

psm = PsmPy(df, treatment="treated", indx="user_id", exclude=["outcome"])
psm.logistic_ps(balance=True)
psm.knn_matched(matcher="propensity_logit", replacement=False, caliper=0.05)
psm.effect_size()  # ATT
```

## Why — Comparative

PSM exists because in observational data, treated and control groups differ on observed AND unobserved variables. Regression "controls" only partially — it imposes a functional form. Matching does NON-PARAMETRIC controlling: similar treated and control units are directly paired. Under the strong assumption that observed covariates capture all confounding (selection-on-observables), the matched-pair difference is the causal effect.

PSM is comparative-rationale: vs regression, PSM relies less on functional-form assumptions; vs DiD, PSM doesn't need parallel trends but DOES need observables-cover-confounding (a different assumption, often harder to defend).

## When — trigger conditions

**Use PSM when:**
- Cross-sectional / observational setup; no natural pre-treatment data
- Rich covariates plausibly capture confounding (selection-on-observables)
- Treated and control groups overlap on covariates (common support)
- You want ATT (matched estimate)

**Skip PSM when:**
- Selection-on-unobservables suspected (e.g., unobserved motivation, ability)
- Panel data available with pre/post → DiD or Event Study is preferred
- Valid instrument exists → IV identifies causal effect under weaker assumptions
- Sharp cutoff → RDD has cleaner identification
- Covariate overlap is poor (many treated have no nearby control or vice versa) — matching discards too many units

## Where — workflow stage / artifact type

- Mode: `mode-insight` Phase 3 (Diagnostic, observational setup)
- Phase: When neither DiD, RDD, nor Synthetic Control fits
- Artifact type: Balance table + ATT estimate + Rosenbaum bounds table

## Who — target roles

- **Runs the method**: DA mid-level + (familiar with logistic regression + matching libraries)
- **Reads the output**: PM / Strategy reviewing an observational comparison; reviewer checking selection-on-observables defensibility
- **Reviews the rigor**: Senior DA / DS — PSM is OFTEN over-claimed (selection-on-observables is strong); reviewer demands the Rosenbaum sensitivity

## Acceptance gate — declare PSM "credible" only if

1. **Covariate balance post-match**: |SDM| < 0.1 for ALL covariates (some say 0.25, but 0.1 is the strict standard)
2. **Common support diagnostic** passes: most treated units have nearby controls and vice versa
3. **Rosenbaum bounds reported**: at what Γ (unobserved confounder strength) does the effect become non-significant? Γ ≥ 1.5 is fair; Γ ≥ 2 is strong
4. **Matching algorithm and caliper documented**, NOT "matched with defaults"
5. **Sensitivity check across matching algorithms** (NN-1, NN-5, caliper-0.05, caliper-0.10): effect stable in sign and approximate magnitude
6. **Treatment-effect interpretation is ATT, not ATE** — the matched sample reflects treated unit composition, not the full population

## Template — copy-paste starter

```python
"""PSM template.

Source: Rosenbaum-Rubin (1983); Imbens-Rubin (2015).
Acceptance: post-match SDM < 0.1, common support, Rosenbaum Γ reported.
"""

import pandas as pd
from psmpy import PsmPy

df = pd.read_csv("data/observational.csv")

# 1. Build PSM with relevant covariates (NO outcome variable in PS regression)
psm = PsmPy(df, treatment="treated", indx="user_id", exclude=["outcome", "user_id"])

# 2. Estimate propensity score
psm.logistic_ps(balance=True)

# 3. Match (1:1 NN with caliper 0.05 SD)
psm.knn_matched(matcher="propensity_logit", replacement=False, caliper=0.05)

# 4. Inspect balance
psm.plot_match(Title='PS Distribution', Ylabel='Number of units', Xlabel='Propensity logit')
psm.effect_size_plot()  # SDM per covariate

# 5. ATT
print(psm.effect_size())
```

## Worked example — feature opt-in vs eventual usage

Setup: among users who have NEVER used a focal feature, did a subset who voluntarily clicked "Learn more" (treated) eventually deposit more once they did sign up, vs comparable users who didn't click?

Setup:
- Treated: ~50k users who clicked "Learn more" in Q1 2026
- Control: 2M users who didn't click
- Covariates: age, platform tenure, average wallet balance, transaction frequency, geo
- Outcome: focal AUM at month-6 post-signup

Result (illustrative):
- Pre-match SDM: 0.65 on tenure, 0.42 on transaction frequency (treated very different)
- Post-match (NN-1, caliper 0.05): SDM < 0.05 on all covariates ✓
- Common support: 96% of treated matched ✓
- ATT: +3.2M units in focal AUM at month-6 (95% CI: +2.8M to +3.6M)
- Rosenbaum bound: Γ = 1.4 (effect becomes non-significant if unobserved confounder makes treated 1.4× more likely to be treated) — modest

Verdict: clicking "Learn more" associated with +3.2M AUM at month-6. INTERPRET CAREFULLY: PSM identifies ATT under selection-on-observables; if motivated users would have deposited more regardless (motivation unobserved), Γ = 1.4 says "modest unobserved confounder could explain the effect." Report as "associated with" not "caused by" unless Γ ≥ 2.

## Anti-patterns

- **Including outcome in the PS regression.** Never. PS = P(treated | covariates), not P(outcome | covariates).
- **Reporting matched ATT as if it were the population ATE.** Matched sample is a subset; the estimate is ATT.
- **Not reporting covariate balance.** Without balance, PSM has done nothing — you might as well have not matched.
- **Skipping Rosenbaum sensitivity.** PSM's identifying assumption (selection-on-observables) is strong; quantifying robustness to its violation is mandatory.
- **Matching with too tight a caliper.** Discards too many treated units; remaining sample is non-representative.
- **Matching with no caliper.** Matches very far apart get accepted; bad balance.

## Cross-references

- **Required prereq method**: covariate selection — must be rich enough to capture confounding
- **Complementary methods**: `methods/sensitivity_analysis.md` (Rosenbaum bounds + caliper variation), `methods/robustness_checks.md` (algorithm robustness)
- **Alternative methods**: `methods/did.md` (panel data, parallel trends), `methods/iv.md` (instrument available)
- **Bundled scripts**: None; use `psmpy` or `causalinference`
- **Decision-table parent**: `references/causal-inference-toolkit.md`

## Reading order

1. THIS file
2. `references/causal-inference-toolkit.md` — for PSM-vs-alternatives positioning
3. `methods/sensitivity_analysis.md` — for Rosenbaum bounds (PSM-specific sensitivity)
4. Primary source: Imbens-Rubin (2015) "Causal Inference for Statistics" Part II for the full framework
