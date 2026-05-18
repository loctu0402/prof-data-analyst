# Method — Cross-Validation (K-fold CV)

> Estimate how well a model / rule / threshold GENERALIZES to unseen data by training on K-1 folds and testing on the held-out fold, rotating across all K folds, then averaging.

## Overview — Quick reference card

| Attribute | Value |
|-----------|-------|
| Type | Validation (generalization) |
| Cost (compute) | K × cost of training (typically K=5 or 10) |
| Prerequisite data shape | Single dataset + a model / threshold / rule to evaluate |
| Output | K-fold-averaged performance metric (AUC, accuracy, RMSE, etc.) + std across folds |
| Bundled script | None bundled; use `sklearn.model_selection.cross_val_score` |
| Reading time | 8 minutes |
| Primary source | Hastie, Tibshirani & Friedman (2009) "Elements of Statistical Learning" Ch. 7 |

## What — definition

K-fold CV splits the data into K equal partitions ("folds"). For each fold k = 1..K, the model is trained on the OTHER K-1 folds and evaluated on fold k. The K performance values are averaged to give an estimate of generalization performance.

CV evaluates the MODELING PIPELINE, not a specific trained model. The averaging captures both the bias and variance of model performance under different train-test splits.

## How — step-by-step protocol

1. **Choose K** — typically 5 or 10. Smaller K → faster but higher variance; larger K → slower but lower variance.
2. **Choose the SPLITTER** — appropriate to the data:
   - i.i.d. continuous outcome: standard K-fold
   - Imbalanced classification: STRATIFIED K-fold (preserves class balance per fold)
   - Time series: ROLLING-WINDOW or expanding-window CV (no leakage from future into past)
   - Grouped data (multiple rows per user): LEAVE-ONE-GROUP-OUT (hold out an entire group)
3. **For each fold**: train on K-1 folds, predict on held-out fold, compute metric.
4. **Aggregate**: report mean + std of the metric across folds. The std tells the reader how stable the estimate is.

```python
from sklearn.model_selection import cross_val_score, KFold, StratifiedKFold, TimeSeriesSplit

# Standard K-fold
scores = cross_val_score(model, X, y, cv=KFold(n_splits=5, shuffle=True, random_state=42), scoring="roc_auc")
print(f"AUC: {scores.mean():.3f} ± {scores.std():.3f}")
```

## Why — Empirical

CV exists because a SINGLE train-test split is one realization — it could be lucky or unlucky. CV averages across K realizations, giving a tighter estimate of generalization performance. The standard deviation across folds also quantifies how stable the performance is.

This is empirical-rationale: the train-test split is itself a sampling decision; CV samples that decision K times.

## When — trigger conditions

**Use CV when:**
- You want a generalization estimate beyond a single hold-out set
- Hyperparameter tuning (use nested CV to avoid leakage)
- Comparing models (CV gives a stable comparison metric)
- Reporting model performance to stakeholders (CV mean ± std is more honest than single-split number)

**Skip CV when:**
- Time series with strict ordering AND you only care about the LAST hold-out (use rolling-window CV, not K-fold)
- Massive datasets where a single train-test split is statistically stable
- Single descriptive analysis (no model to evaluate)
- You're evaluating final model on a CONFIRMATORY test set after CV — don't iterate further on the same data

## Where — workflow stage / artifact type

- Mode: `mode-process` Phase 4 (Model / Analysis) — for ML pipelines
- Phase: Before deployment, after a candidate model is built
- Artifact type: CV results table + cross-fold variance + chosen-fold visualization

## Who — target roles

- **Runs the method**: DA / DS building a model
- **Reads the output**: Reviewer evaluating model robustness; stakeholder asking "will it work on next month's data?"
- **Reviews the rigor**: Senior DA / DS in `mode-review` Sub-mode B Pass 3

## Acceptance gate — declare CV valid only if

1. **Correct splitter for data type** — stratified for imbalanced, time-series for time, group-out for groups
2. **K ≥ 5** (smaller has high variance)
3. **Cross-fold std reported alongside mean** (single number hides variance)
4. **Hyperparameter tuning, if done, was NESTED in the CV** (otherwise leakage)
5. **No CV folds used twice** (one model evaluation per CV; iterating on the same CV creates optimism)
6. **For time series**, no future-to-past leakage (K-fold ON RANDOM SHUFFLE is WRONG for time series)

## Template — copy-paste starter

```python
"""K-fold CV template.

Source: Hastie-Tibshirani-Friedman (2009) Ch. 7.
Acceptance: correct splitter, K≥5, std reported, nested CV if tuning.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score, StratifiedKFold

X, y = ...   # load features, target

cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc")
print(f"AUC: {scores.mean():.3f} ± {scores.std():.3f}")
print(f"Per-fold: {scores.round(3).tolist()}")
```

For time-series:
```python
from sklearn.model_selection import TimeSeriesSplit

cv = TimeSeriesSplit(n_splits=5)
scores = cross_val_score(model, X, y, cv=cv, scoring="neg_mean_squared_error")
print(f"RMSE: {np.sqrt(-scores).mean():.3f} ± {np.sqrt(-scores).std():.3f}")
```

## Worked example — first-action classifier

Setup: build a model predicting whether a new user will perform a focal action (sign up for a feature) in their first 30 days. Outcome is imbalanced (~5% positive).

Setup:
- 100,000 users, 5% positive (5,000 events)
- Features: age, tenure on platform, average balance, transaction frequency, geo
- Model: gradient boosting

CV: stratified 10-fold, scoring AUC.

Result (illustrative):
- Per-fold AUCs: [0.812, 0.808, 0.821, 0.806, 0.815, 0.819, 0.810, 0.823, 0.814, 0.811]
- Mean: 0.814
- Std: 0.006
- Verdict: stable estimate; model achieves AUC 0.81 with low cross-fold variance

If we had used unstratified K-fold instead, one fold might end up with 100% negatives → undefined AUC → invalid result. Stratification fixes this.

If we had iterated hyperparameter tuning by re-running CV on the same data 50 times, picking the best fold result, we'd over-fit to the CV — this is data leakage. Use NESTED CV (inner CV for tuning, outer for reporting).

## Anti-patterns

- **K-fold on time series with random shuffle.** Trains on Feb + predicts Jan → leaks future into past. ALWAYS use time-series CV for ordered data.
- **Reporting mean without std.** Reader cannot tell whether the model is stable or just lucky on average.
- **Hyperparameter tuning on the same CV folds used for reporting.** Optimism bias; use nested CV.
- **Single-fold CV (K = 2 or 3).** Too few folds → high variance estimate.
- **Re-using the CV "test" data for final evaluation.** After CV, evaluate on a TRULY HELD-OUT set you have not touched.

## Cross-references

- **Required prereq method**: a model / threshold / rule that produces predictions
- **Complementary methods**: `methods/bootstrap_ci.md` for CI on the CV estimate; `methods/robustness_checks.md` for spec variation
- **Alternative methods**: hold-out validation (single split, simpler but higher variance); leave-one-out CV (K = n, very high variance)
- **Bundled scripts**: None; use `sklearn.model_selection`
- **Decision-table parent**: `references/validation-evaluation-methods.md`

## Reading order

1. THIS file
2. `references/validation-evaluation-methods.md` §7
3. Primary source: Hastie-Tibshirani-Friedman (2009) "Elements of Statistical Learning" Ch. 7
