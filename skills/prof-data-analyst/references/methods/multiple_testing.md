# Method — Multiple Testing Correction (Bonferroni / Benjamini-Hochberg FDR)

> When you run K hypothesis tests at α = 0.05, the probability of AT LEAST ONE false positive across the family is `1 − (1 − 0.05)^K`, which exceeds 0.05 for K ≥ 2. Correct for it.

## Overview — Quick reference card

| Attribute | Value |
|-----------|-------|
| Type | Validation (multiplicity) |
| Cost (compute) | Trivial (closed-form formulas on p-values) |
| Prerequisite data shape | K p-values from K hypothesis tests |
| Output | Adjusted p-values OR adjusted α threshold OR rejection set |
| Bundled script | `scripts/stats/multiple_testing.py` |
| Reading time | 8 minutes |
| Primary source | Bonferroni (1936); Benjamini & Hochberg (1995) for FDR |

## What — definition

When you test K hypotheses, "α = 0.05 per test" does NOT control the family-wise error rate (FWER, probability of any false positive). Two correction approaches:

**Bonferroni (FWER)**: Use α / K per test. Controls FWER strictly. Conservative; loses power as K grows.

**Benjamini-Hochberg (FDR, False Discovery Rate)**: Order p-values, find the largest k such that `p_(k) ≤ (k / K) × α`. Reject hypotheses 1..k. Controls EXPECTED proportion of false positives among rejections; less conservative; preserves power for genuine signals.

## How — step-by-step protocol

### Bonferroni
1. Collect K p-values.
2. New significance threshold per test: `α_corrected = α / K`.
3. Reject H_i if p_i ≤ α / K.

### Benjamini-Hochberg (BH-FDR)
1. Order p-values ascending: p_(1) ≤ p_(2) ≤ ... ≤ p_(K).
2. For each rank k, check whether `p_(k) ≤ (k / K) × α`.
3. Let k* be the largest k satisfying this. Reject hypotheses with rank 1..k*.

Bundled script call:
```bash
python scripts/stats/multiple_testing.py \
    --p-values 0.01,0.04,0.03,0.001,0.05 --alpha 0.05 --method bonferroni
python scripts/stats/multiple_testing.py \
    --p-values 0.01,0.04,0.03,0.001,0.05 --alpha 0.05 --method bh-fdr
```

## Why — Theoretical

The multiplicity problem is rooted in probability theory: under K independent null hypotheses, the probability of at least one false rejection at uncorrected α is `1 − (1 − α)^K`. At α = 0.05 and K = 20, this is 64% — wildly above the nominal 5%. Bonferroni controls this by dividing α among tests; BH-FDR controls a different quantity (proportion of false-positives among rejections) and is more powerful.

This is theoretical-rationale: the correction is mathematically required to make the rejection rate match the claimed rate.

## When — trigger conditions

**Use Multiple testing correction when:**
- K ≥ 2 hypotheses tested in the same study
- The hypotheses are pre-specified or you are reporting all of them
- Stakes are confirmatory (regulatory, scientific, decision-grade)

**Use Bonferroni specifically when:**
- ANY false positive is costly (regulatory submission, fraud detection, safety)
- K is small (≤ 20)

**Use BH-FDR specifically when:**
- You're identifying a shortlist for follow-up (top-K candidates)
- K is moderate to large (genomics, A/B at scale, exploratory ranking)
- False discoveries are tolerable in proportion to total discoveries

**Skip correction when:**
- Truly single-hypothesis test (K = 1)
- Pre-registered SINGLE primary outcome + secondary outcomes labeled exploratory (commonly accepted in clinical trials)
- Different families of hypotheses tested separately, each treated as K = 1 within its family

## Where — workflow stage / artifact type

- Mode: `mode-insight` Phase 5 (Validation) — after running K tests, before publishing K verdicts
- Phase: Final validation gate before declaring confirmed
- Artifact type: Table of K hypotheses + raw p + corrected p + verdict

## Who — target roles

- **Runs the method**: Anyone reporting K p-values (every analyst, every causal analysis with multiple hypotheses)
- **Reads the output**: Reviewer / stakeholder asking "how many tests did you run?"
- **Reviews the rigor**: Senior DA / DS in `mode-review` Sub-mode A Phase 3 / Sub-mode B Pass 3 — multiplicity correction is the most-forgotten validation

## Acceptance gate — declare corrected only if

1. **K (total number of tests) is explicit** in the report
2. **Correction method chosen with a Why** — Bonferroni (FWER control) vs BH-FDR (FDR control)
3. **Adjusted thresholds OR adjusted p-values** reported alongside raw
4. **If using BH-FDR**, the chosen α is explicit (often 0.05 or 0.10)
5. **Per-test denominator stated**: α corresponds to "P(reject | H0 true)"; FDR corresponds to "P(H0 true | reject)" — different denominators
6. **For K very large** (genomics-scale K > 100), consider Storey q-value approach as alternative

## Template — copy-paste starter

```python
"""Multiple testing correction template.

Source: Bonferroni (1936); BH (1995).
Acceptance: K explicit, method chosen with Why, adjusted reported alongside raw.
"""

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

p_values = pd.Series([0.01, 0.04, 0.03, 0.001, 0.05])
K = len(p_values)
ALPHA = 0.05

# Bonferroni
reject_bf, p_bf, _, _ = multipletests(p_values, alpha=ALPHA, method="bonferroni")

# BH-FDR
reject_bh, p_bh, _, _ = multipletests(p_values, alpha=ALPHA, method="fdr_bh")

print(pd.DataFrame({
    "hypothesis": [f"H{i+1}" for i in range(K)],
    "p_raw": p_values,
    "p_bonferroni": p_bf,
    "reject_bonferroni": reject_bf,
    "p_bh_fdr": p_bh,
    "reject_bh_fdr": reject_bh,
}))
```

## Worked example — Tier-3 campaign on 6 outcomes

Setup: the TTT campaign DiD from `methods/did.md` was run on 6 outcomes simultaneously (cashout amount, cashout count, AUM, login frequency, screen views, churn rate). All 6 p-values reported.

Raw p-values: 0.001, 0.04, 0.018, 0.045, 0.07, 0.30.

| H | Outcome | p_raw | Bonferroni (α=0.05/6=0.0083) | BH-FDR (rank/6 × 0.05) | BF verdict | BH verdict |
|---|---------|-------|------------------------------|------------------------|------------|------------|
| H1 | Cashout amount | 0.001 | 0.0083 | 1/6×0.05 = 0.0083 | reject | reject |
| H2 | AUM | 0.018 | 0.0083 | 2/6×0.05 = 0.0167 | NS | NS |
| H3 | Cashout count | 0.040 | 0.0083 | 3/6×0.05 = 0.025 | NS | NS |
| H4 | Login freq | 0.045 | 0.0083 | 4/6×0.05 = 0.0333 | NS | NS |
| H5 | Screen views | 0.070 | 0.0083 | 5/6×0.05 = 0.0417 | NS | NS |
| H6 | Churn rate | 0.300 | 0.0083 | 6/6×0.05 = 0.050 | NS | NS |

Verdict: under both Bonferroni and BH-FDR, only H1 (cashout amount) survives. The other 4 "significant" raw-p findings disappear after correction — they were likely false positives from running 6 tests.

This changes the report's claim from "campaign affected cashout amount, count, AUM, login freq" to "campaign affected cashout amount only at strict significance."

## Anti-patterns

- **Reporting raw p < 0.05 across K tests as "5 findings."** Multiplicity inflates false-positives; the "5 findings" might be 1 real + 4 false.
- **Cherry-picking which hypotheses to count.** If you ran 30 tests and report only the 6 significant raw-p, K = 30 not 6. Be honest about the family.
- **Conflating α with FDR.** They have different denominators (FPR vs proportion-of-rejections). Cite the denominator explicitly. See `feedback_alpha_vs_fdr_distinction.md`.
- **Applying Bonferroni to gigantic K.** For K = 10,000 (genomics), Bonferroni demands α = 0.000005 per test — virtually no signal survives. Use BH-FDR or Storey q-value.
- **Skipping correction for "exploratory analysis."** If exploratory findings will inform decisions, they should be corrected OR labeled as exploratory and not treated as confirmatory.

## Cross-references

- **Required prereq method**: K hypothesis tests with p-values
- **Complementary methods**: `methods/pre_registration.md` (locking the K hypotheses upfront eliminates the temptation to count fewer); `methods/robustness_checks.md` (different validation dimension)
- **Alternative methods**: Holm-Bonferroni (stepdown, more powerful than plain Bonferroni); Storey q-value (FDR for very large K)
- **Bundled scripts**: `scripts/stats/multiple_testing.py`
- **Decision-table parent**: `references/validation-evaluation-methods.md`

## Reading order

1. THIS file
2. `validation-evaluation-methods.md` §5 (decision-table context)
3. `methods/pre_registration.md` (best practice for fixing K upfront)
4. Primary sources: Benjamini & Hochberg (1995) "Controlling the False Discovery Rate"; Storey (2002) for q-value
