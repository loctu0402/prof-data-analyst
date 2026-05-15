# Method — Instrumental Variable (IV)

> When the treatment is ENDOGENOUS (correlated with the error term) and you have an INSTRUMENT — a variable that affects treatment but has no direct effect on the outcome — use IV / 2SLS to recover the causal effect.

## Overview — Quick reference card

| Attribute | Value |
|-----------|-------|
| Type | Causal inference (endogeneity correction) |
| Cost (compute) | Cheap (two OLS regressions for 2SLS) |
| Prerequisite data shape | Cross-sectional or panel; outcome + endogenous treatment + valid instrument |
| Output | LATE (Local Average Treatment Effect) on compliers + SE + first-stage F |
| Bundled script | None bundled; use `linearmodels.IV2SLS` |
| Reading time | 12 minutes |
| Primary source | Angrist & Pischke (2009) Ch. 4; Imbens & Angrist (1994) for LATE interpretation |

## What — definition

IV addresses endogeneity: treatment is correlated with unobserved variables that also affect the outcome (OLS is biased). The instrument is a variable Z that satisfies two conditions:
1. **Relevance**: Z affects the treatment X (strong first stage)
2. **Exclusion**: Z affects the outcome Y ONLY through X (no direct path)

Under these conditions, the 2SLS estimator (regress X on Z; regress Y on predicted X) identifies the causal effect of X on Y for COMPLIERS — units whose treatment status was changed by the instrument.

## How — step-by-step protocol

1. **State the instrument** and defend BOTH conditions in writing — relevance (testable) + exclusion (NOT testable, defended substantively).
2. **First-stage regression**: `X = π0 + π1·Z + controls + u`. Check `F-statistic on Z ≥ 10` (rule of thumb; Stock & Yogo critical values for precise threshold).
3. **Reduced-form regression**: `Y = γ0 + γ1·Z + controls + ε`. Sign should match expected.
4. **2SLS estimator**: `β_IV = γ1 / π1`. In `linearmodels`, use `IV2SLS` which does both stages and gives correct SE.
5. **Weak-instrument-robust SE** if F < 10 OR if F is borderline (use Anderson-Rubin CI).
6. **Over-identification test** (Sargan / Hansen J) if you have MORE instruments than endogenous variables — overid p > 0.10 supports exclusion.

```python
from linearmodels.iv import IV2SLS

results = IV2SLS.from_formula(
    "y ~ 1 + control1 + control2 + [x ~ z]",   # x is endogenous; z is instrument
    data=df,
).fit(cov_type="robust")
print(results)
print(f"First-stage F: {results.first_stage.diagnostics.loc['x', 'f.stat']:.2f}")
```

## Why — Causal

IV exists because some treatments are jointly determined with the outcome (e.g., wages and education — unobserved ability affects both). OLS regression of Y on X is biased by this endogeneity. An instrument that is "as-if random" in its effect on X but has no direct effect on Y — like a policy change, distance to a clinic, or lottery — recovers the causal effect for the subpopulation whose treatment status moves with the instrument (compliers).

This is a causal-rationale Why: the instrument breaks the endogenous-treatment problem by providing exogenous variation in X. The LATE interpretation is a feature, not a bug — it identifies the effect on the units actually moved by the policy.

## When — trigger conditions

**Use IV when:**
- Treatment is endogenous (selection-on-unobservables; reverse causation; measurement error)
- A valid instrument exists — variation that affects treatment but has no direct outcome path
- First-stage F ≥ 10 (strong instrument)
- You can defend exclusion substantively (Z's mechanism on Y goes ONLY through X)

**Skip IV when:**
- First-stage F < 10 (weak instrument → 2SLS biased AND SE under-coverage)
- Exclusion is implausible (your "instrument" plausibly affects Y directly)
- Selection-on-observables is sufficient → use PSM or regression with controls
- Panel data + parallel trends available → DiD is cleaner

## Where — workflow stage / artifact type

- Mode: `mode-insight` Phase 3 (Diagnostic, endogeneity present)
- Phase: When OLS is suspected biased by endogeneity AND an instrument exists
- Artifact type: First-stage regression table + 2SLS estimate + over-id test (if applicable) + Anderson-Rubin CI

## Who — target roles

- **Runs the method**: DA senior or DS — IV is unforgiving of weak instruments; running it without knowing the assumptions is dangerous
- **Reads the output**: PM / Strategy / Researcher; reviewer evaluating the exclusion-restriction argument
- **Reviews the rigor**: Senior DA / DS in `mode-review` Sub-mode B Pass 3 — IV is the most-misused method in applied work; reviewer demands the F-stat + exclusion defense

## Acceptance gate — declare IV "credible" only if

1. **First-stage F-statistic ≥ 10** on the instrument (Stock-Yogo; some demand F ≥ 23 for ≤10% bias)
2. **Exclusion restriction defended in writing** with substantive argument (statistical tests cannot verify exclusion — only narrative can)
3. **Reduced form has the expected sign and significance**
4. **Over-id test passes** (if applicable; p > 0.10)
5. **Anderson-Rubin CI reported** if F < 100 (robust to weak instruments)
6. **LATE interpretation is explicit**: the effect identified is for COMPLIERS, not ATE — communicate this to stakeholders
7. **Sensitivity to instrument exclusion**: discuss what would happen if exclusion were partially violated (Conley-bound or similar)

## Template — copy-paste starter

```python
"""IV / 2SLS template.

Source: Angrist-Pischke (2009) Ch. 4; Imbens-Angrist (1994).
Acceptance: F ≥ 10, exclusion defended, AR CI if F < 100.
"""

import pandas as pd
from linearmodels.iv import IV2SLS

df = pd.read_csv("data/iv_setup.csv")

# 2SLS: y on x (endogenous) instrumented by z
results = IV2SLS.from_formula(
    "y ~ 1 + control1 + control2 + [x ~ z]",
    data=df,
).fit(cov_type="robust")
print(results)

# First-stage F-statistic
print(results.first_stage)

# Anderson-Rubin CI (for weak-instrument robustness)
print(results.anderson_rubin)
```

## Worked example — TTT signup driven by promo

Setup: stakeholder claims that TTT signup CAUSES higher wallet retention. OLS regression shows positive correlation, but signup is endogenous — motivated users both sign up AND retain (selection bias).

Instrument: random A/B-test exposure to a one-time TTT promo (50% of new users randomly saw the promo banner, 50% didn't).

- Treatment (X): signs up for TTT (binary)
- Outcome (Y): wallet active 90 days post-signup
- Instrument (Z): random promo exposure
- Relevance: promo increases signup ✓ (testable; first-stage)
- Exclusion: promo affects retention ONLY through making users sign up (defended: promo is random, doesn't change wallet utility otherwise)

First stage:
- `signup ~ promo + controls` → coefficient = 0.08 (promo increases signup probability by 8pp)
- F-statistic on promo = 142 ✓ (very strong)

Reduced form:
- `retained ~ promo + controls` → coefficient = 0.04 (promo increases retention by 4pp)
- Sign matches expectation ✓

2SLS estimate:
- β_IV = 0.04 / 0.08 = 0.50 → signing up for TTT increases 90-day retention by ~50pp for compliers
- Anderson-Rubin 95% CI: 0.32 – 0.71 ✓

OLS estimate (for comparison): 0.65 — overstates the causal effect; selection bias inflated by ~30%.

Verdict: TTT signup causes ~50pp retention increase for users who would sign up because of a promo (compliers). NOT the same as "if everyone signed up, retention would be 50pp higher" (ATE) — that requires extra assumptions.

## Anti-patterns

- **Weak instrument with F < 10.** 2SLS estimates are heavily biased; SE are wrong. Pivot to Anderson-Rubin inference OR find a stronger instrument.
- **Indefensible exclusion.** "I'll use distance-to-clinic as an instrument for healthcare use" — but distance also correlates with rural-urban income, which affects outcomes directly. Exclusion fails; IV invalid.
- **Treating LATE as ATE.** The 2SLS effect is for compliers, not the population. Communicate this carefully.
- **Forgetting to cluster SE** when data has natural clusters (state, firm, user with repeated observations).
- **Hunting for instruments post-hoc** (data-snooping). Instruments must be motivated SUBSTANTIVELY before estimation, not by p-value shopping.
- **Stacking many "instruments" of dubious quality.** A single strong, defensible instrument beats five weak ones.

## Cross-references

- **Required prereq method**: substantive argument for exclusion (cannot be skipped; cannot be tested statistically)
- **Complementary methods**: first-stage diagnostics (relevance test), over-id test (if multiple instruments), `methods/sensitivity_analysis.md` (exclusion-violation bounds)
- **Alternative methods**: `methods/did.md` (panel data, no endogeneity assumption); `methods/psm.md` (selection-on-observables); `methods/rdd.md` (sharp cutoff)
- **Bundled scripts**: None; use `linearmodels.IV2SLS`
- **Decision-table parent**: `references/causal-inference-toolkit.md`

## Reading order

1. THIS file
2. `references/causal-inference-toolkit.md` — for endogeneity context
3. Primary sources: Angrist-Pischke (2009) Ch. 4; Imbens-Angrist (1994) "Identification and Estimation of Local Average Treatment Effects" Econometrica
