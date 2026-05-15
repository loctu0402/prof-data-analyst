# Scripts Guide — CLI Reference

All scripts live in `scripts/` inside this skill folder. They exist to enforce the **script-over-agent-compute** rule: any numerical / statistical / formatting work happens in code, not in chat.

The agent INVOKES these scripts via Bash / PowerShell, reads the JSON output, and quotes the verdict in the deliverable. The agent does NOT re-implement the math inline.

## Dependencies

All scripts use only Python stdlib (no pandas, scipy, numpy). They run on any Python 3.9+ install. For CSV input modes, the `csv` module is used.

On Windows, set `PYTHONUTF8=1` if non-ASCII inputs / paths are involved.

## scripts/stats/

### effect_size.py
Cohen's d (continuous) and Cramer's V (categorical) with magnitude verdict + high-cardinality warning.

```bash
# Cohen's d from inline values
python scripts/stats/effect_size.py cohen-d --a "1,2,3,4,5" --b "3,4,5,6,7"

# Cohen's d from CSV columns
python scripts/stats/effect_size.py cohen-d \
    --csv-a data/control.csv --csv-b data/treatment.csv --col score

# Cramer's V from contingency table inline
python scripts/stats/effect_size.py cramer-v --contingency "10,20;30,40"

# Cramer's V from CSV with row and value columns
python scripts/stats/effect_size.py cramer-v --csv users.csv --row segment --col converted
```

Output: JSON with `d` / `v`, `magnitude` (negligible/small/medium/large), `warnings`.

### significance.py
Three tests, all with auto-warnings encoded:
- `t-test` — Welch's t (independent, two-sided)
- `pearson` — correlation with sample-size adequacy + step-function detection
- `prop-z` — z-test for proportion vs baseline

```bash
python scripts/stats/significance.py t-test --a "1,2,3" --b "4,5,6"
python scripts/stats/significance.py pearson --x "1,2,3,4,5" --y "2,4,6,8,10"
python scripts/stats/significance.py prop-z --successes 50 --trials 100 --baseline 0.40
```

Output JSON includes `p_two_sided`, `significant_at_0.05`, `warnings[]`.

### mde_sample_size.py
Minimum Detectable Effect ↔ required sample size, both directions.

```bash
# What MDE can I detect with n=100 and SD=40?
python scripts/stats/mde_sample_size.py mde-from-n --sd 40 --n 100
# Output: mde_absolute ≈ 11.2 at alpha=0.05 two-sided, power=0.80

# How many samples do I need to detect MDE=10 with SD=40?
python scripts/stats/mde_sample_size.py n-from-mde --sd 40 --target-mde 10
# Output: n_required = 126
```

### baseline_noise_impact.py
Runs the 3-rung Baseline-Noise-Impact ladder from universal-workflow-rules.md.

```bash
python scripts/stats/baseline_noise_impact.py \
    --current 12.65 --baseline 12.96 \
    --n 100 --sd 0.5 \
    --small 0.01 --medium 0.05 --large 0.10
```

Output: structured verdict per rung (`real (|z|>1.96); impact = small`).

Use this BEFORE writing the "finding" in a report.

### bootstrap_ci.py
Non-parametric confidence intervals via resampling. Use when n is small (< 30), the distribution is non-normal, or the statistic is non-standard (median, ratio, p90).

```bash
python scripts/stats/bootstrap_ci.py --csv data.csv --column y --statistic mean
python scripts/stats/bootstrap_ci.py --values "1,2,3,4,5" --statistic median --n-resamples 5000
python scripts/stats/bootstrap_ci.py --csv data.csv --column ratio --statistic mean --confidence 0.99
```

Output: point estimate, percentile-method CI, bootstrap SE, bias, interpretation. Statistics: mean, median, sum, min, max, std.

Why bootstrap — parametric CI assumes normal sampling distribution; bootstrap empirically constructs the sampling distribution without assumption.

### multiple_testing.py
Bonferroni FWER + Benjamini-Hochberg FDR correction for multiple-testing scenarios.

```bash
python scripts/stats/multiple_testing.py --p-values 0.01,0.04,0.001,0.03 --alpha 0.05 --method bonferroni
python scripts/stats/multiple_testing.py --p-values 0.01,0.04,0.001,0.03 --alpha 0.05 --method bh-fdr
python scripts/stats/multiple_testing.py --p-values-file pvals.txt --alpha 0.05 --method both
```

Output: per-test reject/accept decision + threshold + interpretation. Both methods returned with `--method both` for side-by-side comparison.

Why two methods — Bonferroni is conservative (controls family-wise error; cost-of-any-false-positive is high). BH-FDR is less conservative (controls false-discovery rate; preserves power for genuine signals). Stakes determine choice.

## scripts/causal/

### did_event_study.py
2×2 Difference-in-Differences + multi-period Event Study, manual OLS via stdlib.

```bash
# DiD (2 periods, 2 groups)
python scripts/causal/did_event_study.py did \
    --csv data.csv --treated-col treated --time-col period \
    --outcome y --pre 1 --post 2

# Event Study (multi-period dynamic effects)
python scripts/causal/did_event_study.py event-study \
    --csv data.csv --treated-col treated --time-col period \
    --outcome y --event-period 0 --window=-3,3
```

Output: ATT point estimate, approximate SE, z-stat, p-value (DiD); coefficients per relative period (Event Study).

Why this script — most analyst tasks have 2x2 setups that don't justify pulling in statsmodels. For staggered treatment timing or proper IV-robust SE, switch to statsmodels.

### parallel_trends_test.py
Falsification test for DiD/Event Study: regresses pre-period treated-vs-control difference on time; tests slope ≈ 0.

```bash
python scripts/causal/parallel_trends_test.py \
    --csv data.csv --treated-col treated --time-col period \
    --outcome y --pre-window="-3,-1"
```

Output: slope estimate + SE + t-stat + p-value with Student-t CDF, interpretation flag.

Why mandatory — parallel-trends is the ONE assumption that justifies DiD. Without testing it, the DiD coefficient is unidentified. Failure to reject is necessary (not sufficient) for the DiD claim.

## scripts/format/

### number_format.py
K/M/B/T units with optional sentiment color hint.

```bash
python scripts/format/number_format.py 1234567890                        # → "1.23 B"
python scripts/format/number_format.py 1234567890 --dense                # → "1.23B"
python scripts/format/number_format.py 1500 --people                     # → "1,500"
python scripts/format/number_format.py 12.5 --metric revenue --delta 0.05 # → "12.50 (green)"
python scripts/format/number_format.py 12.5 --metric cost --delta 0.05    # → "12.50 (red)"
python scripts/format/number_format.py 12.5 --json                        # → {"value":12.5,"formatted":"12.50","color":null}
```

Sentiment metric vocab (extend in code if your domain differs):
- RED on ↑: cashout, churn, cost, fail, drop, withdrawal, loss
- GREEN on ↑: cashin, net, aum, revenue, growth, deposit, gmv

## scripts/validators/

### orientation_block.py
Checks deliverable has Orientation Block at top (SCQR / 3-line intro / module docstring depending on file type).

```bash
python scripts/validators/orientation_block.py output/report.md
python scripts/validators/orientation_block.py pipeline.py --type code
```

Exit 0 = pass, 1 = missing.

### action_brief.py
Checks recommendation has all 8 fields (Question, Goal, Why, What, Who, When, Where, How).

```bash
python scripts/validators/action_brief.py output/report.md
python scripts/validators/action_brief.py output/report.md --section "Recommendations"
cat draft.md | python scripts/validators/action_brief.py
```

Exit 0 = all present, 1 = missing fields listed in JSON output.

### ai_tell_scan.py
Scans for `===`, `-----`, em-dash, `≈`, `→` in stakeholder prose. Skips fenced code blocks and inline code by default.

```bash
python scripts/validators/ai_tell_scan.py output/report.md
python scripts/validators/ai_tell_scan.py output/report.md --strict   # also scan inside code
```

Exit 0 = clean, 1 = findings.

### self_check.py
Bundles the 3 cheap validators above and reports a rolled-up verdict.

```bash
python scripts/validators/self_check.py output/report.md
python scripts/validators/self_check.py output/report.md --section "Recommendations"
python scripts/validators/self_check.py output/report.md --skip orientation
```

Exit 0 = all pass, 1 = at least one check failed. JSON output details each sub-check.

### rubric_audit.py
Mechanical ~30-check compliance audit against EVERY skill rule (Rules 1-4 + style + coding discipline). Output: structured gap table with rule citation + severity + concrete fix.

```bash
python scripts/validators/rubric_audit.py output/report.md
python scripts/validators/rubric_audit.py output/report.md --json
python scripts/validators/rubric_audit.py output/report.md --severity BLOCKER
python scripts/validators/rubric_audit.py output/report.md --rule R4   # Rule-4 family only
```

Output columns: `rule_id | rule_name | severity | location | what_missing | how_to_fix | why_it_matters`. Exit 0 if no BLOCKERs, 1 if any.

Use this for sub-mode C (Rubric Audit) in `mode-review.md`. Step 2 of the audit workflow.

Why this script — analyst cannot reliably remember ~50 rules while shipping. Mechanical pass catches what intuition skips. Output is actionable (Fix + Why) so reviewer is not punted back to the rule doc.

## Common Workflow Recipes

### Before declaring a report done
```bash
python scripts/validators/self_check.py output/<report>.md --section Recommendations
```

### Before claiming a finding
```bash
python scripts/stats/baseline_noise_impact.py --current X --baseline Y --n N --sd S \
    --small 0.01 --medium 0.05 --large 0.10
```

### Before sizing an A/B test
```bash
python scripts/stats/mde_sample_size.py n-from-mde --sd <pilot_sd> --target-mde <required_uplift>
```

### Comparing two cohorts
```bash
python scripts/stats/significance.py t-test --a "..." --b "..."
python scripts/stats/effect_size.py cohen-d --a "..." --b "..."
# Significance + effect size BOTH (one tells you it's real, the other tells you if it matters)
```

## Adding Your Own Scripts

If a calculation recurs in your workflow:
1. Add it under the right subfolder (`stats/`, `format/`, or `validators/`)
2. Match the existing pattern: argparse CLI + JSON stdout + non-zero exit on fail
3. Pure stdlib if possible (zero dependency = portable)
4. Document the new script here

Anti-pattern: importing `scipy` / `statsmodels` for a single function — copy the formula instead, keep zero-dep.
