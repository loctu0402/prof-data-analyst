# Method — Post-Hoc Power Analysis

> You ran a test, got p > 0.05, concluded "no effect." Was that conclusion driven by truly-zero effect, or by too-small sample? Post-hoc power tells you which.

## Overview — Quick reference card

| Attribute | Value |
|-----------|-------|
| Type | Validation (inference about null results) |
| Cost (compute) | Trivial (closed-form power formulas) |
| Prerequisite data shape | Test result + sample size + α + reference effect size (MDE recommended) |
| Output | Power value (between 0 and 1) at the given effect size |
| Bundled script | `scripts/stats/mde_sample_size.py` |
| Reading time | 6 minutes |
| Primary source | Cohen (1988) "Statistical Power Analysis for the Behavioral Sciences"; Hoenig & Heisey (2001) for the observed-power critique |

## What — definition

Statistical power is the probability of correctly rejecting a false null when the alternative is true. Post-hoc, given the sample size n, α, and an effect size of interest δ, power answers: "If the true effect were δ, what was the probability our test would have detected it?"

A "not significant" result with high power → null is likely true.
A "not significant" result with low power → null might be false but the test had no chance.

The honest use is to compute power for the SMALLEST effect that would matter to the business (MDE — minimum detectable effect), NOT for the observed effect size. Observed-effect-size power is monotonically tied to the p-value and provides no additional information.

## How — step-by-step protocol

1. **State the MDE** — the smallest effect that would matter to the business. This must be set BEFORE looking at data, otherwise it is motivated reasoning.
2. **Use sample size n, α, and MDE** to compute power.
3. **Verdict**:
   - Power ≥ 0.80 → null is informative; "no effect at MDE" is credible
   - Power < 0.80 → null is uninformative; the test was under-powered to detect MDE
4. **If under-powered**, recommend: extend sample OR accept that the conclusion is "we cannot rule out an effect smaller than X"

Bundled script call:
```bash
python scripts/stats/mde_sample_size.py \
    --n 100 --alpha 0.05 --mde 0.5 --metric mean
# Returns: power at this MDE
```

## Why — Theoretical

Power exists because the null hypothesis test has TWO errors: Type I (false positive, controlled by α) and Type II (false negative, controlled by 1 − power). When p > 0.05, the analyst usually focuses on α (we did not reject) but ignores Type II (we may have failed to detect). Power makes the Type II rate explicit.

This is theoretical-rationale: power is part of the same statistical framework as α; treating one without the other is incomplete inference.

## When — trigger conditions

**Use Post-hoc Power when:**
- A test produced "not significant" and the analyst wants to claim "no effect"
- Sample size is small or moderate (large samples usually have high power for any MDE)
- The stakeholder will act on the null result (e.g., "we won't invest in this intervention because it didn't work")

**Skip Post-hoc Power when:**
- The test produced p < 0.05 — power analysis adds nothing
- Sample size is huge (n > 10000) — power is essentially 1 for any sensible MDE
- The analyst computes power at the OBSERVED effect (this provides no information; do not do this)

## Where — workflow stage / artifact type

- Mode: `mode-insight` Phase 5 (Validation, null results)
- Phase: After a null finding, before reporting "no effect"
- Artifact type: Power statement in report: "Power to detect MDE = X% was Y; null result is [informative / uninformative]"

## Who — target roles

- **Runs the method**: Analyst who got a null result
- **Reads the output**: Stakeholder weighing whether to act on the null (e.g., kill a feature, drop a hypothesis)
- **Reviews the rigor**: Senior DA / DS in `mode-review`

## Acceptance gate — declare null informative only if

1. **MDE stated BEFORE looking at the data** (or stated based on business meaning, not statistical convenience)
2. **Power at MDE ≥ 0.80** (some demand 0.90 for high-stakes decisions)
3. **Sample size, α, MDE all reported alongside power**
4. **NOT using observed-effect-size power** (Hoenig & Heisey 2001 — this is misleading)
5. **If under-powered**, the conclusion is explicit: "we cannot rule out an effect of size < MDE; the sample is insufficient"

## Template — copy-paste starter

```python
"""Post-hoc power template.

Source: Cohen (1988); Hoenig-Heisey (2001) on observed-power critique.
Acceptance: MDE set BEFORE data; power at MDE ≥ 0.80; NOT observed-effect power.
"""

from statsmodels.stats.power import TTestIndPower

n = 100  # observed sample size per group
alpha = 0.05
mde_effect_size = 0.5  # Cohen's d, set BEFORE data based on business meaning

power = TTestIndPower().power(effect_size=mde_effect_size, nobs1=n, alpha=alpha)
print(f"Power to detect d = {mde_effect_size} at n = {n}, α = {alpha}: {power:.3f}")

if power < 0.80:
    print("Under-powered for MDE — null result is uninformative.")
else:
    print("Adequate power — null result is informative for effect at MDE or larger.")
```

## Worked example — null result on screen-views outcome

Setup: in the same TTT campaign analysis, the screen-views outcome had a DiD p-value of 0.07 → "not significant." Stakeholder asks: does this mean no effect, or weak power?

Setup:
- n_treated = 50,000; n_control = 50,000
- α = 0.05
- Business MDE for screen views: 0.10 screen views/user/period (the smallest change that would matter)
- Observed effect: 0.06 screen views/user/period

Power calculation at MDE (NOT observed):
- Effect size at MDE: d ≈ 0.05 (since SD of screen views ≈ 2)
- Power = 0.92 at n = 50,000, α = 0.05, d = 0.05 ✓

Verdict: power was 92% to detect an effect at MDE. The null result is INFORMATIVE — we can confidently say the campaign did not change screen views by 0.10 or more. The 0.06 point estimate is below MDE.

Anti-pattern (DO NOT do this): computing power at observed d = 0.03 → power ≈ 0.45 → conclude "under-powered." This is misleading; observed-effect-size power always indicates "under-powered" for borderline-non-significant results.

## Anti-patterns

- **Computing power at the OBSERVED effect size.** This is the most common error. It produces a power value that is monotonically tied to the p-value; it adds no information. Use MDE, not observed.
- **Choosing MDE AFTER seeing the result.** "We define MDE as 0.5 because our observed effect is 0.3, which is below MDE." This is motivated reasoning. MDE comes from BUSINESS meaning.
- **Claiming "no effect" with low power.** A null result with 30% power is "we don't know" not "no effect." Communicate accurately.
- **Stating power as a single number without context.** Power depends on MDE, n, α — all three must be reported.

## Cross-references

- **Required prereq method**: a null hypothesis test result (p > 0.05)
- **Complementary methods**: `methods/multiple_testing.md` (if many null results from many tests); pre-registration of MDE → `methods/pre_registration.md`
- **Alternative methods**: Bayes factors quantify evidence for null vs alternative more directly; equivalence testing (TOST) tests for absence of effect
- **Bundled scripts**: `scripts/stats/mde_sample_size.py`
- **Decision-table parent**: `references/validation-evaluation-methods.md`

## Reading order

1. THIS file
2. `references/validation-evaluation-methods.md` §6
3. Primary source: Hoenig & Heisey (2001) "The Abuse of Power" — for why observed-power is misleading
