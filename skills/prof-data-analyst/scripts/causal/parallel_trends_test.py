#!/usr/bin/env python3
"""Parallel-Trends Test — falsification check for DiD / Event Study assumption.

Usage:
  python parallel_trends_test.py \\
      --csv data.csv --treated-col treated --time-col period \\
      --outcome y --pre-window -3,-1

Tests whether the difference in outcomes between treated and control is constant across
pre-treatment periods. If the difference trends → parallel trends assumption fails → DiD biased.

Method (no numpy / no statsmodels):
1. Compute pre-period diff_t = mean(Y_T at t) − mean(Y_C at t) for each t in pre-window
2. Test whether diff_t is flat (regress diff_t on t; slope ≈ 0 → trends parallel)
3. Report slope, SE, t-stat, p-value (manual OLS)

Pure stdlib.

Why test pre-periods only — post-treatment differences mix treatment effect with any trend
divergence; pre-treatment differences SHOULD reflect only any pre-existing trend divergence.
Zero pre-trend → parallel-trends assumption supported.

— part of prof-data-analyst · Loc Tu, 2026
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ols_slope(x: list[float], y: list[float]) -> tuple[float, float, float, float, float]:
    """Manual OLS: return (intercept, slope, slope_se, t_stat, p_value)."""
    n = len(x)
    if n < 3:
        raise SystemExit("error: need at least 3 pre-period points to fit a trend")
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    sxx = sum((xi - x_mean) ** 2 for xi in x)
    sxy = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    if sxx == 0:
        raise SystemExit("error: zero variance in time variable")
    slope = sxy / sxx
    intercept = y_mean - slope * x_mean
    residuals = [yi - (intercept + slope * xi) for xi, yi in zip(x, y)]
    rss = sum(r ** 2 for r in residuals)
    df = n - 2
    sigma_sq = rss / df if df > 0 else float("inf")
    slope_se = math.sqrt(sigma_sq / sxx) if sxx > 0 else float("inf")
    t_stat = slope / slope_se if slope_se > 0 else float("inf")
    p_value = 2 * (1 - student_t_cdf(abs(t_stat), df)) if df > 0 else float("nan")
    return intercept, slope, slope_se, t_stat, p_value


def student_t_cdf(t: float, df: int) -> float:
    """Approx Student-t CDF via regularized incomplete beta (Boost/NR style)."""
    if df <= 0:
        return float("nan")
    x = df / (df + t * t)
    a = df / 2.0
    b = 0.5
    cdf_tail = 0.5 * regularized_incomplete_beta(x, a, b)
    return 1.0 - cdf_tail if t > 0 else cdf_tail


def regularized_incomplete_beta(x: float, a: float, b: float) -> float:
    """Continued-fraction approx (Numerical Recipes style)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(log_gamma(a + b) - log_gamma(a) - log_gamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * betacf(x, a, b) / a
    return 1 - bt * betacf(1 - x, b, a) / b


def betacf(x: float, a: float, b: float, max_iter: int = 200, eps: float = 3e-7) -> float:
    qab = a + b
    qap = a + 1
    qam = a - 1
    c = 1.0
    d = 1 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1 / d
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < eps:
            break
    return h


def log_gamma(x: float) -> float:
    return math.lgamma(x)


def parallel_trends(rows: list[dict], treated_col: str, time_col: str, outcome: str, lo: int, hi: int) -> dict:
    groups = defaultdict(list)
    for r in rows:
        try:
            t = int(r[treated_col])
            p = int(r[time_col])
            y = float(r[outcome])
        except (ValueError, KeyError):
            continue
        if lo <= p <= hi:
            groups[(t, p)].append(y)

    diffs: list[tuple[int, float]] = []
    for p in range(lo, hi + 1):
        if (1, p) in groups and (0, p) in groups:
            m_t = sum(groups[(1, p)]) / len(groups[(1, p)])
            m_c = sum(groups[(0, p)]) / len(groups[(0, p)])
            diffs.append((p, m_t - m_c))
    if len(diffs) < 3:
        raise SystemExit("error: need at least 3 pre-periods with both treated + control data")

    x = [float(p) for p, _ in diffs]
    y = [d for _, d in diffs]
    intercept, slope, slope_se, t_stat, p_value = ols_slope(x, y)

    return {
        "method": "Parallel-Trends Test (pre-period diff regressed on time)",
        "pre_window": [lo, hi],
        "n_periods": len(diffs),
        "diffs_by_period": dict(diffs),
        "intercept": intercept,
        "slope": slope,
        "slope_se": slope_se,
        "t_stat": t_stat,
        "p_value": p_value,
        "interpretation": (
            f"Slope of (Y_T − Y_C) over pre-periods = {slope:.6f} (SE = {slope_se:.6f}, "
            f"t = {t_stat:.2f}, p = {p_value:.4f}). "
            f"{'Parallel trends REJECTED at α=0.05 — DiD assumption violated; consider Synthetic Control or PSM-DiD.' if p_value < 0.05 else 'Parallel trends NOT REJECTED — DiD assumption supported by this falsification test.'}"
        ),
        "caveat": (
            "Failure to reject ≠ confirmation. Pre-period parallel trends is necessary but not sufficient. "
            "Also inspect the plot visually: trends can be parallel on average but diverge late-pre-period."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--treated-col", required=True)
    ap.add_argument("--time-col", required=True)
    ap.add_argument("--outcome", required=True)
    ap.add_argument("--pre-window", required=True, help="lo,hi (e.g., -3,-1)")
    args = ap.parse_args(argv)

    rows = load_csv(args.csv)
    lo, hi = map(int, args.pre_window.split(","))
    result = parallel_trends(rows, args.treated_col, args.time_col, args.outcome, lo, hi)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
