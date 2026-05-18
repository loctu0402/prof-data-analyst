# Method — Falsification Tests

> Run the SAME ANALYSIS on data where the effect SHOULD BE ZERO. If the method still finds an effect, either the method is broken or the original "finding" was spurious.

## Overview — Quick reference card

| Attribute | Value |
|-----------|-------|
| Type | Validation (method-level) |
| Cost (compute) | Cheap (re-run analysis on a placebo dataset) |
| Prerequisite data shape | Original analysis + identifiable "no-effect" subset |
| Output | Placebo estimate + verdict (should be ~zero; not statistically significant) |
| Bundled script | `scripts/causal/parallel_trends_test.py` (DiD-specific); falsification logic for other methods is method-specific |
| Reading time | 8 minutes |
| Primary source | Imbens & Rubin (2015) Ch. 12 (placebo testing in causal inference) |

## What — definition

A falsification test is a deliberately-constructed scenario in which the analysis should produce a NULL result. If the analysis produces a NULL result, that supports the method's validity. If it produces a "significant" result, the method is finding spurious correlations — the original analysis is suspect.

Examples by method:
- **DiD placebo period**: re-run DiD on pre-pre vs pre periods (no treatment); should give zero
- **RDD placebo cutoffs**: test false cutoffs at c+ε and c−ε; should give zero
- **Synthetic Control in-space placebo**: assign "treatment" to each donor unit; treated unit's effect should be extreme
- **IV reduced form on falsified outcome**: an outcome the instrument should NOT affect (placebo outcome); should give zero

## How — step-by-step protocol

1. **Identify a placebo construction** for your method:
   - DiD: pick pre-treatment periods only and pretend the treatment happened at a mid-pre date
   - RDD: pick fake cutoffs above or below the real cutoff where no policy changes
   - Synthetic Control: pretend each donor in turn is "the treated unit" → compute its effect → see if real-treated effect is extreme
   - IV: pick an outcome that the instrument should NOT affect (theory says so), re-run IV → should be zero
2. **Re-run the headline analysis** on the placebo construction.
3. **Verdict**:
   - Placebo estimate near zero, not significant → method PASSES falsification
   - Placebo estimate significant (similar magnitude to real effect) → method FAILS; real estimate is likely spurious
4. **For Synthetic Control specifically**: compute the placebo distribution (one per donor); the real-treated effect must be in the top X% to be credible at confidence 1-X.

## Why — Empirical

Falsification tests exist because real-world data has many spurious correlations. A "significant" finding under your method might mean the method finds significance where there is none (false positives). The only empirical defense: run the method where significance should NOT be found. If it isn't, the method has a working "off switch" and the real finding is more credible.

This is empirical-rationale: a method that always finds effects will also find spurious ones. Falsification is the empirical "method-knows-when-zero" check.

## When — trigger conditions

**Use Falsification tests when:**
- Headline finding is causal and high-stakes
- A natural placebo construction exists for your method
- Reviewer is likely to ask "what if your method finds effects in places it shouldn't?"

**Skip Falsification tests when:**
- Pure descriptive analysis (no causal claim → nothing to falsify)
- No natural placebo construction (rare; usually you can construct one)
- Pre-registration with locked falsification plan already executed — but document this

## Where — workflow stage / artifact type

- Mode: `mode-insight` Phase 5 (Validation)
- Phase: After robustness + sensitivity, before declaring confirmed
- Artifact type: Falsification table or plot showing placebo estimates near zero

## Who — target roles

- **Runs the method**: Analyst who ran the headline + chose the placebo construction
- **Reads the output**: Reviewer evaluating method validity; stakeholder taking causal claim seriously
- **Reviews the rigor**: Senior DA / DS in `mode-review` Sub-mode B Pass 3 — falsification is the strongest evidence of method validity, expected for causal claims

## Acceptance gate — declare passed only if

1. **At least one placebo construction** appropriate to the method
2. **Placebo estimate within ±20% of zero** (rule of thumb; small relative to real effect)
3. **Placebo estimate not statistically significant** at the same α as the real test
4. **For Synthetic Control**: real-treated effect ranked in top 1/(N_donors+1) of placebos for permutation p ≤ 1/(N+1)
5. **Placebo construction justified** in writing — readers must understand why the placebo SHOULD give zero
6. **Reported alongside the main finding** in the same table/section, not buried in an appendix

## Template — copy-paste starter

```python
"""Falsification test template.

Source: Imbens-Rubin (2015) Ch. 12.
Acceptance: placebo near zero, not significant, top of permutation distribution.
"""

# DiD placebo example: re-run on pre-pre vs pre (no real treatment)

import pandas as pd
import statsmodels.formula.api as smf

df = pd.read_csv("data/panel.csv")

# Pretend treatment happened mid-pre-period
PLACEBO_PERIOD = "2026-02-01"  # actual treatment was 2026-03-15
df_pre = df[df["period"] < "2026-03-15"]
df_pre["placebo_post"] = (df_pre["period"] >= PLACEBO_PERIOD).astype(int)
df_pre["placebo_did"] = df_pre["treated"] * df_pre["placebo_post"]

model = smf.ols(
    "y ~ treated + placebo_post + placebo_did + C(unit_id) + C(period)",
    data=df_pre,
).fit(cov_type="cluster", cov_kwds={"groups": df_pre["unit_id"]})

print(f"Placebo DiD: {model.params['placebo_did']:.3f} (p={model.pvalues['placebo_did']:.3f})")
# Should be near zero with p > 0.10
```

## Worked example — DiD placebo period

From `methods/did.md`: real DiD effect on the treated segment = −18,500 units per user per period (p < 0.001) with treatment at 2026-03-15.

Placebo: pretend treatment happened at 2026-02-01 (mid-pre-period). Re-run DiD on the pre-pre vs pre periods only.

Result (illustrative):
- Placebo DiD coefficient: +450 units per user per period
- 95% CI: (−1,800, +2,700)
- p-value: 0.78

Verdict: placebo near zero, not significant — DiD method PASSES falsification. The real estimate of −18,500 cannot be explained by "DiD always finds effects in this data" because in the pre-period, DiD correctly finds nothing.

For Synthetic Control (from `methods/synthetic_control.md`): in-space placebo distribution had Hà Nội ranked 1st of 21 placebos → permutation p = 1/21 ≈ 0.048. Placebo passes.

## Anti-patterns

- **Falsification with insufficient power.** If your placebo sample is too small, "not significant" might mean low power rather than null effect. Make sure the placebo has comparable n to the real test.
- **Choosing the placebo to confirm.** Picking the one placebo period where DiD is closest to zero, ignoring others. Use a fixed pre-determined placebo construction.
- **Skipping falsification because robustness checks "looked good."** Robustness varies specs; falsification varies the EFFECT (real vs placebo). They are complementary, not substitutes.
- **Misinterpreting in-space placebo for Synthetic Control.** The placebo distribution includes treated unit's pre-fit RMSE; outliers in pre-fit RMSE invalidate the comparison.
- **Reporting "falsification passed" without showing the placebo estimate.** Reviewer needs to see the magnitude, not just a yes/no.

## Cross-references

- **Required prereq method**: a headline causal finding to falsify
- **Complementary methods**: `methods/robustness_checks.md` (varies spec); `methods/sensitivity_analysis.md` (varies parameter); `methods/multiple_testing.md` (corrects across many tests)
- **Alternative methods**: pre-registration + locked falsification plan → see `methods/pre_registration.md`
- **Bundled scripts**: `scripts/causal/parallel_trends_test.py` (for DiD); method-specific elsewhere
- **Decision-table parent**: `references/validation-evaluation-methods.md`

## Reading order

1. THIS file
2. `methods/did.md` / `methods/rdd.md` / `methods/synthetic_control.md` / `methods/iv.md` — for the method-specific placebo
3. `methods/robustness_checks.md` — for the complementary spec-variation check
4. Primary source: Imbens-Rubin (2015) Ch. 12 for placebo logic
