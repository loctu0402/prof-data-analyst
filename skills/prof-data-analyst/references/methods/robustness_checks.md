# Method — Robustness Checks

> Re-run the headline analysis under multiple ALTERNATIVE SPECIFICATIONS. If the sign and approximate magnitude survive → finding is robust. If a spec flips the sign or changes magnitude > 50% → finding is fragile.

## Overview — Quick reference card

| Attribute | Value |
|-----------|-------|
| Type | Validation |
| Cost (compute) | Cheap to medium (re-runs the original analysis 3-10×) |
| Prerequisite data shape | Same as original analysis; plus alternative spec definitions |
| Output | Robustness table: rows = specs, columns = estimate + SE + p-value |
| Bundled script | None bundled (orchestrate manually in notebook); each row uses your original analysis script |
| Reading time | 8 minutes |
| Primary source | Leamer (1983) "Let's Take the Con Out of Econometrics"; Athey & Imbens (2017) for the modern view |

## What — definition

Robustness checks are a STRUCTURED battery of alternative specifications: different functional forms, sub-samples, control sets, outcome definitions, sample windows. If the headline finding survives across all of them, the finding is credible. If it depends on one specific choice, the finding is fragile — the researcher's degrees of freedom drove the result.

The output is a robustness TABLE — readers see all the specs side-by-side, not just the headline.

## How — step-by-step protocol

1. **Identify the headline finding** + the specification used.
2. **Enumerate 3-5+ alternative specs** along these dimensions:
   - **Functional form**: linear → log → square root → polynomial → IHS
   - **Sub-samples**: drop top/bottom 1% (outliers), drop pre-event period, drop one major region/cohort, leave-one-out on key groups
   - **Controls**: minimal controls vs full controls vs alternative controls
   - **Outcome definition**: primary outcome vs alternative measure of the same construct
   - **Sample window**: extend / shrink the date range
3. **Re-run analysis** for each spec, recording point estimate + SE + p-value.
4. **Compile robustness table**.
5. **Verdict**:
   - All specs same sign + magnitude within ~50% of headline → ROBUST
   - One spec flips sign or magnitude ±50%+ → FRAGILE; investigate why; consider whether headline is the right spec
   - Most specs match, one outlier → FOLLOW UP on the outlier spec specifically

## Why — Empirical

Researcher degrees of freedom are large: in any analysis, the analyst chooses functional form, sample, controls, time window — and rarely reports the rejected choices. Robustness checks make those choices visible. A finding that holds under 5 plausible specs is far more credible than one that holds under 1 spec out of 30 tried.

This is empirical-rationale: in real-world data, the same hypothesis admits many "reasonable" tests; the test that produces significance is not necessarily the right one.

## When — trigger conditions

**Use Robustness checks when:**
- Headline finding is about to be published / shared with stakeholders
- Multiple plausible specifications exist
- Reviewer is likely to ask "what if you had used X instead?"

**Skip Robustness checks when:**
- Pre-registration locked the exact spec → robustness is "exploratory" rather than confirmatory; document accordingly
- Only one spec is plausible AND the analysis is exploratory rather than confirmatory
- Time-budget constraint genuinely impossible to fit even 3 alt specs → flag this explicitly as a limitation

## Where — workflow stage / artifact type

- Mode: `mode-insight` Phase 5 (Validation) — after headline computed, before declaring confirmed
- Phase: Validation, before report assembly
- Artifact type: Robustness table in report appendix + 1-line summary in main text

## Who — target roles

- **Runs the method**: Analyst who ran the headline analysis (knows the spec choices)
- **Reads the output**: Reviewer / stakeholder asking "is this finding real?"
- **Reviews the rigor**: Senior DA / DS in `mode-review` Sub-mode A Phase 3

## Acceptance gate — declare robust only if

1. **At least 3 alternative specs** run (one per dimension above; more for higher-stakes findings)
2. **All specs same sign** as headline
3. **Magnitude variation < 50%** across specs (no spec where estimate is half or double the headline)
4. **Robustness table reported in full** — readers see ALL specs, not just "we did robustness"
5. **If any spec flips sign**, investigate substantively: which spec caused it? Is that spec more correct or less? Report the answer.

## Template — copy-paste starter

```python
"""Robustness check template.

Source: Leamer (1983); Athey-Imbens (2017).
Acceptance: ≥3 alt specs, all same sign, magnitude variation <50%.
"""

import pandas as pd
import statsmodels.formula.api as smf

df = pd.read_csv("data/analysis.csv")

specs = {
    "headline": "y ~ x + control1 + control2",
    "log_y": "np.log(y) ~ x + control1 + control2",
    "drop_top_1pct": ("y ~ x + control1 + control2", df.query("y < y.quantile(0.99)")),
    "min_controls": "y ~ x + control1",
    "alt_outcome": "y_alternative ~ x + control1 + control2",
}

results = []
for label, spec in specs.items():
    if isinstance(spec, tuple):
        formula, data = spec
    else:
        formula, data = spec, df
    model = smf.ols(formula, data=data).fit()
    results.append({
        "spec": label,
        "estimate": model.params["x"],
        "se": model.bse["x"],
        "p_value": model.pvalues["x"],
    })

pd.DataFrame(results).to_csv("output/robustness_table.csv", index=False)
```

## Worked example — Tier 3 cashout intervention robustness

Continuing the DiD worked example from `methods/did.md`: headline = −18,500 VND per user (campaign reduced Tier 3 cashout).

Robustness specs:
| Spec | Estimate | SE | p | Status |
|------|----------|------|---|--------|
| Headline (linear, full sample, all controls) | −18,500 | 2,900 | <0.001 | ✓ |
| Log outcome (drop zeros) | −0.21 (log units) | 0.03 | <0.001 | ✓ same sign |
| Drop top 1% cashout outliers | −16,200 | 2,500 | <0.001 | ✓ within 50% |
| Minimal controls (only treated + post + DiD) | −17,800 | 3,200 | <0.001 | ✓ |
| Alt outcome (cashout count instead of amount) | −1.4 (count) | 0.3 | <0.001 | ✓ same sign |
| Drop pre-period > 30d before treatment | −19,200 | 3,100 | <0.001 | ✓ |
| Drop region North (1 specific large region) | −15,800 | 2,800 | <0.001 | ✓ |

Verdict: ROBUST. All 7 specs same sign; magnitude variation 15,800 to 19,200 (range = 22% of headline, well within 50%).

## Anti-patterns

- **Cherry-picking specs to report.** If you ran 10 alt specs and 7 disagreed, do not show only the 3 that agreed. Report ALL.
- **Treating robustness as "showed multiple specs gave significance."** Significance isn't the bar; CONSISTENT SIGN + magnitude is.
- **Defining "alt specs" too narrowly.** "I dropped 1% of data 5 different ways" is 5 versions of the same spec. Need DIFFERENT dimensions varied.
- **Skipping robustness because pre-registration locked the spec.** Pre-registration is the gold standard but robustness still helps the reader understand fragility. Just frame as "exploratory robustness."
- **Reporting "robust" when one spec flips.** One sign-flip is a finding worth investigating, not a footnote to ignore.

## Cross-references

- **Required prereq method**: a headline analysis to test (DiD, regression, RDD, etc.)
- **Complementary methods**: `methods/sensitivity_analysis.md` (varying ONE parameter continuously); `methods/falsification_tests.md` (testing where effect should be zero)
- **Alternative methods**: pre-registration locks specs upfront, reducing the need for post-hoc robustness — see `methods/pre_registration.md`
- **Bundled scripts**: None
- **Decision-table parent**: `references/validation-evaluation-methods.md`

## Reading order

1. THIS file
2. `methods/sensitivity_analysis.md` — for continuous-parameter variants
3. `methods/falsification_tests.md` — for zero-effect tests
4. Primary sources: Leamer (1983); Athey-Imbens (2017) "The State of Applied Econometrics — Causality and Policy Evaluation"
