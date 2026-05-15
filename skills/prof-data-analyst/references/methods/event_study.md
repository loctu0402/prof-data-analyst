# Method — Event Study

> Extension of DiD that estimates the treatment effect SEPARATELY for each period before and after the event, revealing dynamic effects + serving as a parallel-trends test.

## Overview — Quick reference card

| Attribute | Value |
|-----------|-------|
| Type | Causal inference |
| Cost (compute) | Cheap (one OLS regression with K event-time dummies) |
| Prerequisite data shape | Panel: ≥1 treated + ≥1 control + multiple pre + multiple post periods |
| Output | Coefficient per event-time `τ` (e.g., τ=-3,-2,-1,0,+1,+2,+3) with CIs |
| Bundled script | `scripts/causal/did_event_study.py event-study` |
| Reading time | 12 minutes |
| Primary source | Borusyak, Jaravel & Spiess (2024); Callaway & Sant'Anna (2021); Sun & Abraham (2021) |

## What — definition

Event Study generalizes the 2×2 DiD to many periods. Instead of one post-period dummy, the model uses one dummy PER event-time (τ = period − treatment_start). The coefficient at τ=k is the average treatment effect k periods after treatment. The pre-period coefficients (τ < 0) should be near zero — this IS the parallel-trends test, executed visually.

The plot of coefficients vs event-time tells the dynamic story: did the effect kick in immediately? Build up over time? Fade?

## How — step-by-step protocol

1. **Compute event-time** `τ = period − treatment_period`. For control units, treatment_period is conventionally set to a never-treated value (or excluded from event-time-specific coefficients).
2. **Pick the OMITTED CATEGORY** — typically τ = −1 (the period just before treatment). The omitted category is the baseline against which other event-times are estimated.
3. **Run regression** `y = α_unit + α_time + Σ_k β_k · 1{τ=k} + ε` for k ≠ −1.
4. **Cluster SEs at the unit level**.
5. **Plot** `β_k` vs `k` with CI band.
6. **Verify pre-treatment leads** (`β_k` for k < 0, k ≠ −1) are near zero and jointly insignificant — this is the parallel-trends test.

Bundled script call:
```bash
python scripts/causal/did_event_study.py event-study \
    --csv panel.csv --treated-col treated --time-col period \
    --treatment-period 2026-03-15 --outcome y \
    --pre-window="-6,-1" --post-window="0,6"
```

## Why — Empirical

Event Study exists because DiD's single post-period coefficient hides dynamics. A 5% average effect could be "0% immediately, growing to 10% by period 5" OR "12% immediately, fading to 3% by period 5" — these have very different policy implications. Event Study makes the dynamic shape visible, and incidentally builds the parallel-trends test directly into the estimation rather than treating it as a separate diagnostic.

This is an empirical-rationale Why: real treatment effects rarely arrive instantly and stay constant; the average DiD loses information that the period-by-period plot exposes.

## When — trigger conditions

**Use Event Study when:**
- Multiple pre and post periods available (≥3 pre, ≥3 post recommended)
- You suspect the effect has dynamic structure (warmup, fade, anticipation)
- Treatment timing is shared across treated units (or use Callaway-Sant'Anna for staggered)
- You want to visually validate parallel-trends (the lead coefficients ARE the validation)

**Skip Event Study when:**
- Only 1 pre + 1 post period → no event-time variation; DiD 2×2 is all you can do
- Treatment timing is staggered AND you use naïve TWFE → known to be biased (Goodman-Bacon 2021); use Callaway-Sant'Anna or Sun-Abraham
- Outcome is binary AND you need linear-probability dynamics — consider a more flexible link

## Where — workflow stage / artifact type

- Mode: `mode-insight` Phase 3 (Diagnostic) — typically AFTER a DiD point estimate, to characterize dynamics
- Phase: Diagnostic + parallel-trends validation
- Artifact type: Event-time coefficient plot + table of pre/post period estimates

## Who — target roles

- **Runs the method**: DA mid-level + (familiar with OLS + dummy variables)
- **Reads the output**: PM / Strategy reviewing treatment dynamics; reviewer checking parallel-trends visually
- **Reviews the rigor**: Senior DA / DS in `mode-review` Sub-mode B Pass 3

## Acceptance gate — declare Event Study result "credible" only if

1. **Pre-period leads jointly insignificant** (F-test p > 0.10) — parallel-trends OK
2. **At least 3 pre + 3 post event-times estimated** — fewer hides the pattern
3. **Omitted category named** (typically τ = −1)
4. **Clustered SEs at unit level**
5. **Plot includes CI band** (not just point estimates)
6. **If staggered timing**, Callaway-Sant'Anna or Sun-Abraham estimator used (NOT naïve TWFE)

## Template — copy-paste starter

```python
"""Event Study template.

Source: Borusyak-Jaravel-Spiess (2024) for the estimation, Goodman-Bacon (2021) for the TWFE bias warning.
Acceptance: pre-period leads insignificant, ≥3 pre + 3 post, clustered SE.
"""

import pandas as pd
import statsmodels.formula.api as smf

df = pd.read_csv("data/panel.csv")
df["event_time"] = df["period"] - TREATMENT_PERIOD
# Omit τ = -1 as baseline
df["event_time"] = df["event_time"].astype(str)
df.loc[df["event_time"] == "-1", "event_time"] = "_omit"

model = smf.ols(
    "y ~ C(event_time, Treatment(reference='_omit')) + C(unit_id) + C(period)",
    data=df,
).fit(cov_type="cluster", cov_kwds={"groups": df["unit_id"]})

# Extract event-time coefficients + CIs → plot
```

## Worked example — TTT campaign dynamics

Setup: same March 2026 Tier 3 notification campaign as in `methods/did.md`. Question moves from "did it work?" to "how did it work over time?"

Event-time coefficients (illustrative):
- τ = −6: −500 VND (CI: −2,200 to +1,200) — pre-period, near zero ✓
- τ = −5: +200 VND (CI: −1,800 to +2,200) ✓
- τ = −4: −1,100 VND (CI: −3,400 to +1,200) ✓
- τ = −3: +400 VND (CI: −1,500 to +2,300) ✓
- τ = −2: −300 VND (CI: −2,100 to +1,500) ✓
- τ = −1: OMITTED (baseline)
- τ =  0: −12,000 VND (CI: −16,500 to −7,500) — immediate effect ✗ (significant drop)
- τ = +1: −19,000 VND (CI: −24,000 to −14,000) — deepens
- τ = +2: −18,500 VND (CI: −23,800 to −13,200) — plateau
- τ = +3: −15,000 VND (CI: −20,200 to −9,800) — slight fade

Pre-period F-test on leads: p = 0.42 → parallel-trends passes.

Verdict: campaign reduces Tier 3 cashout, building from −12k to plateau ~−19k VND by period 2, slight fade by period 3. The average DiD of −18.5k (from `methods/did.md`) reflects the plateau period, not the immediate effect.

## Anti-patterns

- **Forgetting to omit a baseline event-time.** Multicollinearity will either drop a coefficient (statsmodels) or fail to invert (other software). Always omit τ = −1.
- **Pooling τ = −1 with the other pre-periods.** Then there's no baseline; the parallel-trends test becomes meaningless.
- **Naïve TWFE with staggered treatment.** Different treatment timings make TWFE a weighted average of all 2×2 DiD comparisons including "already-treated vs newly-treated" — sign-biased. Use Callaway-Sant'Anna.
- **Reporting only the average effect.** If you ran Event Study, SHOW the dynamics. Aggregating back to one number wastes the method.
- **Reading τ = +3 as "long-term effect"** when sample after period +3 is thin. Confidence drops as event-time gets far from 0; CI widens; do not over-interpret extreme event-times.

## Cross-references

- **Required prereq method**: panel data + treatment timing variable (no formal method needed)
- **Complementary methods**: `methods/did.md` (for the average), `methods/falsification_tests.md` (placebo periods)
- **Alternative methods**: `methods/synthetic_control.md` (single treated unit); Callaway-Sant'Anna or Sun-Abraham (staggered treatment — currently delegated to references in `causal-inference-toolkit.md` rather than a separate spec)
- **Bundled scripts**: `scripts/causal/did_event_study.py event-study`
- **Decision-table parent**: `references/causal-inference-toolkit.md`

## Reading order

1. THIS file
2. `methods/did.md` — Event Study extends DiD; understand DiD first
3. `references/causal-inference-toolkit.md` — for staggered-treatment warnings
4. Primary sources: Borusyak-Jaravel-Spiess (2024); Goodman-Bacon (2021) for TWFE bias
