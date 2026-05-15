# Method — Bootstrap Confidence Interval

> Estimate a confidence interval by RESAMPLING the data with replacement many times and computing the statistic on each resample. Makes no normality assumption.

## Overview — Quick reference card

| Attribute | Value |
|-----------|-------|
| Type | Validation / inference |
| Cost (compute) | Cheap (≤1s for n≤10k, B=10k resamples) |
| Prerequisite data shape | Single sample of size n; statistic computable on the sample |
| Output | Confidence interval (e.g., 95%) for the statistic + bootstrap SE |
| Bundled script | `scripts/stats/bootstrap_ci.py` |
| Reading time | 8 minutes |
| Primary source | Efron & Tibshirani (1993) "An Introduction to the Bootstrap" |

## What — definition

The bootstrap creates B "bootstrap samples" by resampling the original sample WITH replacement, each of size n. The statistic of interest (mean, median, ratio, custom metric) is computed on each bootstrap sample, producing a distribution of B values. The 2.5th and 97.5th percentiles of that distribution form the 95% bootstrap CI.

The bootstrap turns "what would the statistic look like across hypothetical repeated samples?" into "what does the statistic look like across resamples of the one sample we have?" — and shows empirically that the two distributions converge as n grows.

## How — step-by-step protocol

1. **Define the statistic** as a function `θ(data) → scalar`. Could be mean, median, percentile, ratio, custom KPI.
2. **Set B (number of bootstrap samples)**. B ≥ 1000 for reasonable CI stability; B = 10000 for publication-grade. Cost is linear in B.
3. **Resample**: for `b = 1..B`, draw n observations from the original sample WITH replacement → compute `θ_b`.
4. **Aggregate**: the B values `{θ_1, ..., θ_B}` form the empirical sampling distribution.
5. **Extract CI**: percentile CI is `[θ_(α/2), θ_(1-α/2)]` for confidence level `1-α`. For 95%, use the 2.5th and 97.5th percentiles.
6. **Bootstrap SE** is the standard deviation of `{θ_b}`.

Bundled script call:
```bash
python scripts/stats/bootstrap_ci.py \
    --csv data.csv --column y --statistic mean \
    --n-resamples 10000 --confidence 0.95
```

## Why — Empirical

The bootstrap exists because parametric confidence intervals require a known sampling distribution (typically Normal via Central Limit Theorem). For small samples, skewed data, custom statistics (medians, ratios, complex KPIs), the parametric assumption is wrong or unverifiable. The bootstrap replaces the assumption with empirics: the resampling distribution IS the sampling distribution to good approximation when n is moderate.

This is an empirical-rationale Why: the method's foundation is the empirical claim that resampling-with-replacement reproduces the sampling-distribution shape for a wide class of statistics (precisely defined: smooth functionals of the empirical distribution).

## When — trigger conditions

**Use Bootstrap CI when:**
- Sample size small (n < 30) and parametric CI assumptions shaky
- Statistic is non-standard: median, ratio, percentile, custom KPI, complex aggregate
- Distribution is non-normal or unknown
- You want a CI without normality assumptions

**Skip Bootstrap CI when:**
- Statistic depends on extremes (max, min, top-1%) — extremes do not bootstrap well
- Data is dependent (time series) — use block bootstrap, not standard bootstrap
- n is so small (< 10) that the empirical distribution itself is degenerate
- Parametric CI is well-justified (n ≥ 30, near-normal, standard statistic) — bootstrap adds compute cost without much benefit

## Where — workflow stage / artifact type

- Mode: `mode-insight` Phase 4 (Statistical Methodology) and `mode-process` Phase 2 (Data Quality Audit — CI for sample statistics)
- Phase: After point estimate is computed, BEFORE declaring a finding confirmed
- Artifact type: Notebook cell + report sidebar table + CI band on charts

## Who — target roles

- **Runs the method**: DA fresher and above (one CLI call or a 10-line Python loop)
- **Reads the output**: Anyone consuming the CI in a report — stakeholders care about the CI width, not the bootstrap mechanics
- **Reviews the rigor**: Senior DA / DS in `mode-review` Sub-mode A — verifies bootstrap was used appropriately (not for extremes, not for time-series without blocks)

## Acceptance gate — declare bootstrap CI "valid" only if

1. **B ≥ 1000** (preferably 10000 for publication)
2. **Statistic is NOT extreme-dependent** (no max, min, top-1% bootstraps)
3. **Data is NOT time-correlated** OR block bootstrap is used (block size justified)
4. **CI is shown alongside the point estimate**, not in lieu of it
5. **CI width interpretation is included** — narrow CI = high precision; wide CI = low precision; both deserve a one-line interpretation

If any criterion fails: re-run with more B, or switch to a different validation method.

## Template — copy-paste starter

```python
"""Bootstrap CI template.

Source: Efron & Tibshirani (1993).
Acceptance: B >= 1000, statistic not extreme-dependent, independent data.
"""

import numpy as np
import pandas as pd

def bootstrap_ci(values, statistic=np.mean, B=10000, conf=0.95):
    """Return (point_est, lower, upper, bootstrap_se)."""
    values = np.asarray(values)
    n = len(values)
    rng = np.random.default_rng(42)
    boot_stats = np.empty(B)
    for b in range(B):
        sample = rng.choice(values, size=n, replace=True)
        boot_stats[b] = statistic(sample)
    point = statistic(values)
    alpha = 1 - conf
    lower = np.percentile(boot_stats, 100 * alpha / 2)
    upper = np.percentile(boot_stats, 100 * (1 - alpha / 2))
    se = boot_stats.std(ddof=1)
    return point, lower, upper, se

# Usage
point, lo, hi, se = bootstrap_ci(df["metric"].values)
print(f"{point:.3f} (95% CI: {lo:.3f} – {hi:.3f}; SE = {se:.3f})")
```

## Worked example — median cashout per user (small sample)

Setup: a pilot Tier 3 cohort of n=21 users completed the new flow. Headline: median cashout amount.

```python
import numpy as np
import pandas as pd

df = pd.read_csv("output/projects/pilot-cohort/cashout.csv")  # n=21
point, lo, hi, se = bootstrap_ci(df["cashout"].values, statistic=np.median, B=10000)

print(f"Median cashout: {point:,.0f} VND (95% CI: {lo:,.0f} – {hi:,.0f}; bootstrap SE = {se:,.0f})")
```

Result (illustrative):
- Median cashout: 280,000 VND
- 95% bootstrap CI: 95,000 – 450,000 VND
- Bootstrap SE: 92,000 VND

Verdict: pilot median is reportable, but CI is wide (gap = 355k VND vs point estimate 280k) — pilot needs scaling to narrow precision before any business decision.

Narrative for report:
> Pilot cohort n=21 cho median cashout 280k VND (95% bootstrap CI: 95k – 450k). CI rộng so với point estimate — cần mở pilot rộng hơn (target n=100) trước khi quyết định scale.

## Anti-patterns — what NOT to do

- **Bootstrapping a max / min / extreme percentile.** The bootstrap distribution of extremes is biased toward the observed extreme; CI is invalid. Use a different method (e.g., extreme value theory).
- **Bootstrapping time-series data with standard (i.i.d.) resampling.** Breaks the autocorrelation structure → CI is too narrow. Use block bootstrap with block size ≈ √n or theoretically motivated.
- **Reporting only the CI without the point estimate.** The CI is a range; stakeholders need both the center and the spread.
- **Treating bootstrap CI as a substitute for falsification.** A narrow bootstrap CI says the statistic is precisely estimated; it does NOT say the statistic is the right statistic or that the method is appropriate. Pair bootstrap with method-level falsification (see `methods/falsification_tests.md`).
- **Setting B too low to save compute.** B = 100 gives unstable CIs (different runs disagree); B = 1000 is minimum; B = 10000 is standard.

## Cross-references — related methods + scripts

- **Required prereq method**: a point estimate computed on the sample (no method needed; just `np.mean`, `np.median`, or custom)
- **Complementary methods**: robustness checks → `methods/robustness_checks.md`; multiple testing → `methods/multiple_testing.md` (if reporting multiple CIs)
- **Alternative methods**: parametric CI if assumptions hold; Bayesian credible interval if priors available; jackknife (similar idea but no replacement)
- **Bundled scripts**: `scripts/stats/bootstrap_ci.py`
- **Decision-table parent**: `references/validation-evaluation-methods.md`

## Reading order — load these in this order

1. THIS file (you are here)
2. `references/validation-evaluation-methods.md` §1 — for the decision-table context
3. `methods/multiple_testing.md` — if reporting multiple bootstrap CIs (correct for multiplicity)
4. Primary source: Efron & Tibshirani (1993) "An Introduction to the Bootstrap" — Chapters 1-3 for the foundational mechanics
