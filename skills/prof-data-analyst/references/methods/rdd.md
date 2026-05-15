# Method — Regression Discontinuity Design (RDD)

> When treatment is assigned by a SHARP cutoff on a continuous running variable, compare units just above the cutoff to units just below — they are quasi-randomly assigned.

## Overview — Quick reference card

| Attribute | Value |
|-----------|-------|
| Type | Causal inference |
| Cost (compute) | Cheap (local linear regression on bandwidth window) |
| Prerequisite data shape | Running variable + outcome + binary treatment that flips at known cutoff |
| Output | Local average treatment effect (LATE) at the cutoff + SE + CI |
| Bundled script | None bundled; use `rdrobust` Python package |
| Reading time | 10 minutes |
| Primary source | Imbens & Lemieux (2008); Calonico, Cattaneo & Titiunik (2014) for optimal bandwidth |

## What — definition

RDD exploits a feature of many policy rules: treatment turns on at a specific value of some running variable (credit score, exam grade, age, income). Units just above and just below the cutoff are almost identical in expectation, so their outcome difference at the cutoff identifies the causal effect — for units AT the cutoff (LATE, not ATE).

Two variants:
- **Sharp RDD**: cutoff perfectly determines treatment (everyone above gets treated, no one below). Estimand: jump in outcome at cutoff.
- **Fuzzy RDD**: cutoff changes treatment PROBABILITY but isn't deterministic. Estimand: jump in outcome / jump in treatment probability (Wald-type ratio).

## How — step-by-step protocol

1. **Verify the cutoff is sharp** (or measure the discontinuity in treatment probability for fuzzy).
2. **Plot the outcome against the running variable** with a binned scatter. Eyeball for a discontinuity at the cutoff — if invisible, RDD will likely fail.
3. **Choose a bandwidth** around the cutoff. Use Calonico-Cattaneo-Titiunik (CCT) optimal MSE-minimizing bandwidth; default in `rdrobust` package.
4. **Fit local linear regression** on each side of the cutoff within the bandwidth.
5. **The RDD estimate** is the difference in intercepts at the cutoff (sharp) or the ratio of outcome jump to treatment jump (fuzzy).
6. **Falsification**: McCrary density test (running variable should have continuous density at cutoff — manipulation breaks RDD); covariate-balance tests (other variables should be smooth across the cutoff).

```python
# Manual + rdrobust
from rdrobust import rdrobust, rdplot

rdr = rdrobust(y=df["outcome"], x=df["running_var"], c=CUTOFF)
print(rdr)
rdplot(y=df["outcome"], x=df["running_var"], c=CUTOFF)
```

## Why — Causal

RDD identifies a causal effect because at the cutoff, treatment assignment is AS-IF random — units with running variable c−ε and c+ε differ only by a tiny ε in the running variable, but one gets treatment and the other doesn't. The assumption (continuity of potential outcomes at the cutoff) is much weaker than the assumptions other methods require (no selection on unobservables, parallel trends, valid instrument, etc.). RDD's price: the effect identified is LATE — only for units at the cutoff, not the population.

This is a causal-rationale Why: the cutoff creates local quasi-randomization; the method exploits that.

## When — trigger conditions

**Use RDD when:**
- Treatment assigned by sharp cutoff on a continuous running variable
- Units cannot precisely manipulate the running variable to land on the desired side
- You have data on both sides of the cutoff within a sensible bandwidth
- You want a clean identification of the local treatment effect

**Skip RDD when:**
- No clear cutoff exists, OR the cutoff is a kink not a jump
- Running variable is manipulable (e.g., self-reported income on a loan application) — McCrary test catches this
- You need ATE (RDD identifies LATE only — at the cutoff)
- Too few observations near the cutoff → bandwidth has to include far points → identification weakens

## Where — workflow stage / artifact type

- Mode: `mode-insight` Phase 3 (Diagnostic)
- Phase: When the analytical setup features a known policy cutoff
- Artifact type: RDD plot (binned scatter + fitted local linear) + estimate + falsification table

## Who — target roles

- **Runs the method**: DA mid-level + (familiar with `rdrobust` package OR can write local linear regression)
- **Reads the output**: PM / Stakeholder defending policy effect estimation; reviewer checking density manipulation
- **Reviews the rigor**: Senior DA / DS — RDD is easy to do wrong (bandwidth choice, manipulation)

## Acceptance gate — declare RDD "credible" only if

1. **McCrary density test passes** (p > 0.05) — running variable is not manipulated at cutoff
2. **Covariate-balance check passes** — other variables are smooth across the cutoff (no jumps)
3. **Optimal bandwidth from CCT or equivalent is used** (NOT manual ad hoc choice)
4. **Robustness across bandwidths**: estimate stable at 0.5×, 1×, 2× optimal bandwidth (sign and magnitude similar) — see `methods/sensitivity_analysis.md`
5. **Effect interpreted as LATE at the cutoff**, NOT ATE
6. **Sample size in bandwidth** ≥ 30 per side (less and the local linear fit is unstable)

## Template — copy-paste starter

```python
"""RDD template.

Source: Imbens-Lemieux (2008); CCT (2014) for bandwidth.
Acceptance: McCrary passes, covariate balance, CCT bandwidth, robust to 0.5x/1x/2x.
"""
import pandas as pd
from rdrobust import rdrobust, rdplot

df = pd.read_csv("data/policy.csv")

# 1. Sharp RDD estimate
rdr = rdrobust(y=df["outcome"], x=df["running_var"], c=CUTOFF)
print(rdr)

# 2. McCrary density test (manipulation)
# Use rddensity package: rddensity.rddensity(df["running_var"], c=CUTOFF)

# 3. Plot
rdplot(y=df["outcome"], x=df["running_var"], c=CUTOFF, p=1)

# 4. Sensitivity to bandwidth
for bw_scale in (0.5, 1.0, 2.0):
    rdr_alt = rdrobust(y=df["outcome"], x=df["running_var"], c=CUTOFF, h=BW_OPT * bw_scale)
    print(f"bw×{bw_scale}: τ={rdr_alt.coef[0]:.3f}")
```

## Worked example — credit-card promo eligibility

Setup: MoMo offered a cashback promo to users with credit score ≥ 700. Question: did the promo increase transaction volume?

Setup:
- Running variable: credit score (300-850)
- Cutoff: 700
- Treatment: promo offered
- Outcome: monthly transaction count

Results (illustrative):
- RDD estimate at cutoff: +12 transactions / month (95% CI: +6 to +18)
- McCrary density test: p = 0.34 (passes — users cannot manipulate score precisely)
- Covariate balance: no jumps in age, geography, tenure (passes)
- Bandwidth = 35 points (CCT optimal); robustness at 18 + 70 points → estimate +10 and +14 (stable)
- n in bandwidth: 1,240 below, 1,180 above

Verdict: promo causes +12 monthly transactions for users near the 700 cutoff. Strict LATE interpretation: stakeholders must NOT extrapolate to users at score 500 or 800.

## Anti-patterns

- **Skipping McCrary.** If users can manipulate the running variable to land above the cutoff, the "as-if random" assumption fails. McCrary is non-negotiable.
- **Picking the bandwidth by eyeballing.** Reviewers should NOT have to guess. CCT optimal bandwidth is the default.
- **Extrapolating LATE to ATE.** "12 transactions" is for users near 700, not for everyone. Stakeholder communication MUST be explicit.
- **Using polynomial-order > 2.** Higher-order polynomials at the boundary are known to mislead (Gelman-Imbens 2019). Local LINEAR (p=1) or QUADRATIC (p=2) only.
- **Reporting RDD when there's no visible discontinuity in the plot.** The plot must show the jump. If it doesn't, the model is finding a phantom.

## Cross-references

- **Required prereq method**: McCrary density test (manipulation), covariate balance
- **Complementary methods**: `methods/sensitivity_analysis.md` (bandwidth robustness), `methods/falsification_tests.md` (placebo cutoffs)
- **Alternative methods**: `methods/did.md` (if pre/post available + control group), `methods/iv.md` (if cutoff is fuzzy and you have a valid instrument)
- **Bundled scripts**: None; use `rdrobust` Python package (`pip install rdrobust`)
- **Decision-table parent**: `references/causal-inference-toolkit.md`

## Reading order

1. THIS file
2. `methods/sensitivity_analysis.md` — for bandwidth robustness
3. `methods/falsification_tests.md` — for placebo cutoffs
4. Primary sources: Imbens-Lemieux (2008); Calonico-Cattaneo-Titiunik (2014); Gelman-Imbens (2019) on polynomial caveats
