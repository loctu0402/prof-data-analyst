# Method — Difference-in-Differences (DiD)

> Estimate the causal effect of a treatment by comparing the BEFORE-AFTER change in the treated group to the BEFORE-AFTER change in an untreated control group.

## Overview — Quick reference card

| Attribute | Value |
|-----------|-------|
| Type | Causal inference |
| Cost (compute) | Cheap (OLS on panel data) |
| Prerequisite data shape | Panel: ≥1 treated unit + ≥1 control unit + ≥1 pre period + ≥1 post period |
| Output | ATT (Average Treatment effect on the Treated) + SE + p-value |
| Bundled script | `scripts/causal/did_event_study.py did` |
| Reading time | 10 minutes |
| Primary source | Angrist & Pischke (2009) "Mostly Harmless Econometrics" Ch. 5 |

## What — definition

DiD estimates a treatment's causal effect by subtracting two differences. The first difference is the change in outcome from before to after for the TREATED group; the second difference is the same change for the CONTROL group. The DiD estimator is the treated change minus the control change — what would have happened to the treated group absent treatment is approximated by what happened to the control group.

DiD identifies ATT (Average Treatment effect on the Treated), not ATE.

## How — step-by-step protocol

1. **Build the 2×2 table**: treated outcome before, treated outcome after, control outcome before, control outcome after.
2. **Run parallel-trends test** on pre-treatment periods. If the trends differ before treatment, DiD assumption is violated → use an alternative method or document the violation. `python scripts/causal/parallel_trends_test.py --csv data.csv ...`
3. **Compute DiD estimate** as `(T_after − T_before) − (C_after − C_before)`.
4. **Run regression** `y = β0 + β1·treated + β2·post + β3·(treated × post) + controls + ε`. The DiD ATT is the coefficient `β3` on the interaction term.
5. **Get SE clustered at the unit level** (standard practice — within-unit autocorrelation inflates naïve SE).
6. **Report**: point estimate `β3`, clustered SE, 95% CI, p-value, parallel-trends test verdict, sample sizes per cell.

Bundled script call:
```bash
python scripts/causal/did_event_study.py did \
    --csv panel.csv \
    --treated-col treated --time-col period \
    --outcome y --pre 1 --post 2
```

## Why — Causal

DiD exists because in observational data, comparing treated vs control at one point in time confounds the treatment effect with pre-existing differences between the groups (selection bias). And comparing treated before vs after confounds the treatment with secular trends (other things that change over time). DiD differences out BOTH biases under one assumption — that the trend would have been the same in both groups absent treatment.

This is a causal-rationale Why: the method identifies a specific causal estimand (ATT) under a specific identifying assumption (parallel trends), and the assumption is testable on pre-treatment data.

## When — trigger conditions

**Use DiD when:**
- Panel data with at least one treated unit + one control unit + one pre + one post period (2×2 minimum)
- Parallel-trends test passes on pre-treatment periods (`scripts/causal/parallel_trends_test.py`)
- The treatment timing is shared (all treated units treated at the same time) — for staggered treatment, see "When to skip"
- You want ATT, not ATE

**Skip DiD when:**
- Pre-period available is <2 periods → cannot test parallel trends → use Synthetic Control or document the gap
- Staggered treatment timing → standard 2-way fixed effects (TWFE) DiD is biased; use Callaway-Sant'Anna or Sun-Abraham estimators
- Treatment assigned by sharp cutoff on a running variable → use RDD instead (cleaner identification)
- Single treated unit with no good comparison group → use Synthetic Control

## Where — workflow stage / artifact type

- Mode: `mode-insight` Phase 3 (Diagnostic techniques)
- Phase: Diagnostic — after Phase 2 data collection, before Phase 5 self-evaluation
- Artifact type: Insight report section + supporting notebook + acceptance gate verdict in Pass 3 of `mode-review`

## Who — target roles

- **Runs the method**: DA mid-level comfortable with `statsmodels` or panel regression
- **Reads the output**: PM / Business owner reviewing a causal claim before greenlight
- **Reviews the rigor**: Senior DA / DS in `mode-review` Sub-mode B Pass 3

## Acceptance gate — declare DiD result "confirmed" only if

1. **Parallel-trends test passes** — pre-period leads coefficients not jointly significant (use F-test, target p > 0.10)
2. **Standard errors clustered at the unit level** (NOT naïve / robust-only)
3. **Effect size has business-meaningful interpretation** (not just statistical p < 0.05 — translate to absolute units the stakeholder understands)
4. **At least one robustness check** showing sign-stable across alternative specs (drop top region, alternative outcome definition, narrower window) — see `methods/robustness_checks.md`
5. **Falsification test on placebo period** — re-run DiD on pre-pre vs pre (no treatment); should give zero — see `methods/falsification_tests.md`
6. **Sample size declared per cell** — `n_treated_pre`, `n_treated_post`, `n_control_pre`, `n_control_post` all reported

If any criterion fails: either re-run with adjusted spec, or downgrade the claim from causal to correlational.

## Template — copy-paste starter

```python
"""DiD analysis template.

Source: Angrist & Pischke (2009) Ch. 5.
Acceptance: parallel trends p > 0.10, clustered SE, robustness + falsification.
"""

import pandas as pd
import statsmodels.formula.api as smf

# 1. Load panel
df = pd.read_csv("data/panel.csv")   # cols: unit_id, period, treated, y, controls...

# 2. Define treatment × post interaction
df["post"] = (df["period"] >= TREATMENT_START_PERIOD).astype(int)
df["did"] = df["treated"] * df["post"]

# 3. Regress with clustered SE
model = smf.ols(
    "y ~ treated + post + did + C(unit_id) + C(period)",
    data=df,
).fit(cov_type="cluster", cov_kwds={"groups": df["unit_id"]})

print(model.summary())   # The DiD ATT is the `did` coefficient

# 4. Parallel-trends test (pre-period)
# Run: python scripts/causal/parallel_trends_test.py --csv data/panel.csv ...
```

## Worked example — notification-campaign intervention

Setup: in March 2026, a fintech app launched a notification campaign targeting a specific tier of active users (treatment group: ~50k users). The question: did the campaign reduce a focal withdrawal outcome on that tier?

Data: 60-day panel before campaign + 30-day panel after. Treated unit = tier users in the campaign cohort. Control unit = tier users NOT in the campaign cohort (selected by matching demographics).

```python
df = pd.read_csv("output/projects/<your-project>/panel.csv")
df["post"] = (df["period"] >= "2026-03-15").astype(int)
df["did"] = df["in_campaign"] * df["post"]

model = smf.ols(
    "outcome_amount ~ in_campaign + post + did + C(user_id) + C(period)",
    data=df,
).fit(cov_type="cluster", cov_kwds={"groups": df["user_id"]})
```

Result (illustrative):
- DiD coefficient: −18,500 units per user per period (95% CI: −24,200 to −12,800)
- p-value: < 0.001
- Parallel-trends test on pre-period: p = 0.34 → passes
- Clustered SE at user_id: yes
- Robustness — same result holds when dropping top 1% outliers
- Falsification — placebo DiD on Jan vs Feb (no treatment): coefficient = +450 units, p = 0.78 → passes

Verdict: campaign reduced the focal outcome by ~18,500 units per user per period. Confirmed under all 6 acceptance criteria.

Narrative for report:
> The notification campaign reduced the focal outcome on the targeted tier by 18,500 units per user per period (95% CI: 12,800 – 24,200). Result passes parallel-trends test (p=0.34), robustness (drop top 1% keeps the sign), and falsification (DiD placebo on pre-pre returned +450 units, not significant).

## Anti-patterns — what NOT to do

- **Skipping the parallel-trends test.** "We saw the gap widen after treatment" is descriptive, not causal. Without the test, DiD claim is unsupported.
- **Using naïve (or HC-robust) standard errors instead of clustered.** Within-unit autocorrelation makes naïve SE under-estimate by 2-4× → false significance.
- **Treating the DiD coefficient as ATE.** DiD identifies ATT (effect ON the treated), not ATE (effect IF everyone were treated). Stakeholder communication should reflect this.
- **Running TWFE DiD with staggered treatment timing.** TWFE is biased when treatment timing varies across units — use Callaway-Sant'Anna or Sun-Abraham. This is a known result (Goodman-Bacon 2021); ignoring it produces wrong-sign estimates.
- **Confusing "no parallel-trends violation in test" with "parallel trends holds in truth."** The test is an absence-of-evidence check, not evidence-of-absence. Pair with substantive argument about why control trend should equal treated trend.

## Cross-references — related methods + scripts

- **Required prereq method**: parallel-trends test → `methods/falsification_tests.md` (this method's specific falsification)
- **Complementary methods**: robustness checks → `methods/robustness_checks.md`; sensitivity to window → `methods/sensitivity_analysis.md`
- **Alternative methods**: Event Study (multi-period dynamics, see `methods/event_study.md`); Synthetic Control (single treated unit, see `methods/synthetic_control.md`); RDD (sharp cutoff, see `methods/rdd.md`)
- **Bundled scripts**: `scripts/causal/did_event_study.py did` (estimator), `scripts/causal/parallel_trends_test.py` (assumption test)
- **Decision-table parent**: `references/causal-inference-toolkit.md`

## Reading order — load these in this order

1. THIS file (you are here)
2. `methods/falsification_tests.md` — for the parallel-trends test details
3. `methods/robustness_checks.md` — for the post-DiD validation stack
4. `references/causal-inference-toolkit.md` — for when DiD vs alternatives
5. Primary source: Angrist & Pischke (2009) "Mostly Harmless Econometrics" Ch. 5 — for the theoretical foundation
