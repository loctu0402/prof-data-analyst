# Method — Sensitivity Analysis

> Vary ONE PARAMETER of the analysis (cutoff, bandwidth, window length, threshold) across a RANGE; trace how the result moves. A stable finding survives the range; a fragile finding moves with the parameter.

## Overview — Quick reference card

| Attribute | Value |
|-----------|-------|
| Type | Validation |
| Cost (compute) | Cheap to medium (re-run analysis at K parameter values) |
| Prerequisite data shape | Same as headline analysis; parameter to vary identified |
| Output | Sensitivity plot: x = parameter value, y = estimate with CI band |
| Bundled script | None bundled (orchestrate loop in notebook) |
| Reading time | 7 minutes |
| Primary source | Imbens & Rubin (2015) Ch. 12 (Rosenbaum bounds); Calonico-Cattaneo-Titiunik (2014) for RDD bandwidth |

## What — definition

Sensitivity analysis varies ONE parameter at a time while holding others fixed. The output is a plot or table showing how the estimate changes as the parameter sweeps a plausible range. If the estimate is flat across the range, the parameter choice did not drive the finding. If the estimate moves a lot, the finding is sensitive to a choice the analyst made.

Distinct from `methods/robustness_checks.md`: robustness varies SPEC dimensions (different specs); sensitivity varies ONE parameter (continuous or near-continuous). They complement each other.

## How — step-by-step protocol

1. **Identify the parameter** that the analyst chose subjectively (bandwidth in RDD, window in DiD, caliper in PSM, threshold for material effect, time window for OLS anomaly detection).
2. **Define a plausible range** for that parameter. For RDD bandwidth: 0.5×, 1×, 2× the optimal. For DiD window: 30d, 60d, 90d, 120d.
3. **Re-run the analysis at each parameter value**, recording estimate + CI.
4. **Plot or tabulate**: x-axis = parameter, y-axis = estimate with CI band.
5. **Interpret**:
   - Flat line within CI band → INSENSITIVE; choice didn't drive result
   - Estimate monotonically changes → result depends on parameter; defend the chosen value
   - Estimate noisy / non-monotonic → potentially small-sample noise; investigate

## Why — Empirical

Sensitivity analysis exists because EVERY non-trivial analysis has a parameter the analyst chose with limited justification: a bandwidth, a window, a threshold. The reader cannot know whether the choice mattered without seeing the parameter swept. Sensitivity analysis exposes this choice; pre-specification + sensitivity together are the standard for serious quantitative work.

This is empirical-rationale: in practice, "robust to parameter choice" is the only credible way to defend a parameter that lacks a theoretical mandate.

## When — trigger conditions

**Use Sensitivity analysis when:**
- The analysis has a subjective parameter (bandwidth, window, threshold, caliper)
- The reader / reviewer is likely to ask "why this parameter value?"
- The finding's magnitude or significance might depend on the parameter
- For RDD, DiD with subjective window, PSM with subjective caliper, OLS anomaly windows

**Skip Sensitivity analysis when:**
- The parameter has a strong theoretical or empirical mandate (e.g., CCT optimal bandwidth in RDD with no manual override)
- Single-shot analysis with no tunable parameter (pure descriptive)
- The parameter is data-determined (e.g., sample size dictated by available data)

## Where — workflow stage / artifact type

- Mode: `mode-insight` Phase 5 (Validation)
- Phase: After headline computed, alongside robustness checks
- Artifact type: Sensitivity plot in appendix + one-line summary in main text

## Who — target roles

- **Runs the method**: Analyst who chose the parameter
- **Reads the output**: Reviewer asking "is the answer 5 because of the data, or because you picked window = 30?"
- **Reviews the rigor**: Senior DA / DS in `mode-review` Sub-mode B Pass 3

## Acceptance gate — declare insensitive only if

1. **At least 3 parameter values tested**, spanning a plausible range (not 3 nearby values)
2. **Plot or table includes CI band**, not just point estimates
3. **Range of estimates** across the parameter sweep is within ~30% of the headline estimate (some allow up to 50%)
4. **The headline value of the parameter is justified** with a Why — theoretical, empirical, or operational
5. **If estimate moves a lot** with parameter, the FINDING is downgraded (report range as "estimate ranges from X to Y depending on parameter choice")

## Template — copy-paste starter

```python
"""Sensitivity analysis template.

Source: Imbens-Rubin (2015) Ch. 12 (PSM Rosenbaum bounds); CCT (2014) for RDD bandwidth.
Acceptance: ≥3 parameter values, CI band, estimate range <30% of headline.
"""

import pandas as pd
import numpy as np

# Example: DiD with varying pre-window length

df = pd.read_csv("data/panel.csv")
results = []

for window_days in [30, 60, 90, 120, 180]:
    df_window = df.query(f"days_to_treatment >= -{window_days}")
    # Re-fit your headline analysis on df_window
    estimate, ci_lo, ci_hi = your_headline_analysis(df_window)
    results.append({
        "window_days": window_days,
        "estimate": estimate,
        "ci_lo": ci_lo,
        "ci_hi": ci_hi,
    })

sens_df = pd.DataFrame(results)
# Plot: x = window_days, y = estimate with CI band
```

## Worked example — RDD bandwidth sensitivity

Continuing the RDD example from `methods/rdd.md`: credit-card promo, cutoff = 700, headline estimate at CCT-optimal bandwidth = +12 transactions/month.

Sensitivity table:
| Bandwidth (credit score points) | Estimate | 95% CI | n (each side) |
|---------------------------------|----------|--------|---------------|
| 10 (very tight) | +9 | (+1, +17) | 250 / 240 |
| 17.5 (0.5× CCT) | +10 | (+4, +16) | 620 / 590 |
| 35 (CCT optimal) | +12 | (+6, +18) | 1,240 / 1,180 |
| 70 (2× CCT) | +14 | (+9, +19) | 2,500 / 2,400 |
| 105 (3× CCT) | +16 | (+12, +20) | 3,800 / 3,600 |

Verdict: estimate ranges 9 to 16 across bandwidth, with CCT-optimal at 12. The range is ~58% of the headline, slightly above the 50% threshold. Reportable nuance: "promo effect is 9-16 transactions/month depending on bandwidth; at the CCT-optimal bandwidth it is 12."

For higher-stakes work, also report the sensitivity to KERNEL CHOICE (uniform vs triangular) and to POLYNOMIAL ORDER (p=1 vs p=2). RDD has 3 tunable parameters; sensitivity to all three is the gold standard.

## Anti-patterns

- **One-sided sensitivity.** Trying only "wider bandwidth" not "narrower" — readers cannot tell whether tighter would flip.
- **Reporting only the parameter values where headline survived.** If you tried 7 windows and 2 disagreed, report all 7.
- **No CI band.** Point estimates without uncertainty cannot distinguish noise from sensitivity.
- **Confusing sensitivity (one parameter) with robustness (different specs).** They are different validations; do both.
- **Hiding sensitivity in appendix only.** If sensitivity is interesting, mention it in main text — "estimate is 12 transactions/month, ranging 9-16 across bandwidth choices."

## Cross-references

- **Required prereq method**: headline analysis with a tunable parameter
- **Complementary methods**: `methods/robustness_checks.md` (varying spec dimensions); `methods/falsification_tests.md` (placebo cutoffs); Rosenbaum bounds in `methods/psm.md` for PSM-specific sensitivity to unobserved confounders
- **Alternative methods**: pre-registration that LOCKS the parameter eliminates the need for post-hoc sensitivity — but most analyses do not have this
- **Bundled scripts**: None
- **Decision-table parent**: `references/validation-evaluation-methods.md`

## Reading order

1. THIS file
2. `methods/robustness_checks.md` — for the spec-dimension complement
3. `validation-evaluation-methods.md` §3 (OLS anomaly window) — for time-series window sensitivity rule
4. Primary sources: CCT (2014) for RDD bandwidth; Imbens-Rubin (2015) Ch. 12 for Rosenbaum bounds
