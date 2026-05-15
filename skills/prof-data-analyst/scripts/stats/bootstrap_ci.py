#!/usr/bin/env python3
"""Bootstrap Confidence Intervals — non-parametric CI via resampling.

Usage:
  python bootstrap_ci.py --csv data.csv --column y --statistic mean
  python bootstrap_ci.py --values 1,2,3,4,5,6 --statistic median --n-resamples 5000
  python bootstrap_ci.py --csv data.csv --column ratio --statistic mean --confidence 0.99

Pure stdlib. Statistics supported: mean, median, sum, min, max, std.

Why bootstrap — parametric CI (mean ± 1.96·SE) assumes the sampling distribution is normal.
For small n, skewed data, or non-standard statistics (median, ratio, p90), this assumption fails.
Bootstrap makes no assumption: the resampling distribution IS the sampling distribution empirically.
Caveat — bootstrap fails for extreme-tail statistics (max, min, top-1%).

— part of prof-data-analyst · Loc Tu, 2026
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
import sys
from pathlib import Path


STATISTICS = {
    "mean": statistics.mean,
    "median": statistics.median,
    "sum": sum,
    "min": min,
    "max": max,
    "std": statistics.stdev,
}


def load_csv_column(path: Path, column: str) -> list[float]:
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if column not in reader.fieldnames:
            raise SystemExit(f"error: column '{column}' not found. Available: {reader.fieldnames}")
        values = []
        for row in reader:
            raw = row[column].strip()
            if raw == "":
                continue
            try:
                values.append(float(raw))
            except ValueError:
                continue
    return values


def bootstrap_ci(
    data: list[float],
    statistic_name: str,
    n_resamples: int,
    confidence: float,
    seed: int | None,
) -> dict:
    if statistic_name not in STATISTICS:
        raise SystemExit(f"error: statistic '{statistic_name}' not supported. Available: {list(STATISTICS)}")
    stat_fn = STATISTICS[statistic_name]
    rng = random.Random(seed)
    n = len(data)
    if n < 2:
        raise SystemExit("error: need at least 2 data points")

    point_estimate = stat_fn(data)

    resampled_stats = []
    for _ in range(n_resamples):
        resample = [data[rng.randrange(n)] for _ in range(n)]
        try:
            resampled_stats.append(stat_fn(resample))
        except statistics.StatisticsError:
            continue

    resampled_stats.sort()
    alpha = 1.0 - confidence
    lo_idx = int(alpha / 2 * len(resampled_stats))
    hi_idx = int((1.0 - alpha / 2) * len(resampled_stats)) - 1
    ci_low = resampled_stats[lo_idx]
    ci_high = resampled_stats[hi_idx]

    bootstrap_mean = statistics.mean(resampled_stats)
    bootstrap_se = statistics.stdev(resampled_stats) if len(resampled_stats) > 1 else 0.0
    bias = bootstrap_mean - point_estimate

    return {
        "input": {"n": n, "statistic": statistic_name, "n_resamples": n_resamples, "confidence": confidence},
        "point_estimate": point_estimate,
        "ci_lower": ci_low,
        "ci_upper": ci_high,
        "bootstrap_se": bootstrap_se,
        "bias": bias,
        "interpretation": (
            f"Point estimate {statistic_name} = {point_estimate:.6g}. "
            f"{int(confidence*100)}% bootstrap CI = [{ci_low:.6g}, {ci_high:.6g}] "
            f"(percentile method, {n_resamples} resamples). "
            f"Bias = {bias:.6g} (bootstrap mean − point); SE = {bootstrap_se:.6g}. "
            f"{'CI excludes 0 → significant at this level.' if (ci_low > 0 or ci_high < 0) else 'CI includes 0 → not significant at this level.'}"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", type=Path, help="CSV file path")
    ap.add_argument("--column", type=str, help="Column name in CSV")
    ap.add_argument("--values", type=str, help="Comma-separated values (alternative to --csv)")
    ap.add_argument("--statistic", choices=list(STATISTICS), default="mean")
    ap.add_argument("--n-resamples", type=int, default=10000)
    ap.add_argument("--confidence", type=float, default=0.95)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args(argv)

    if args.csv:
        if not args.column:
            print("error: --column required with --csv", file=sys.stderr)
            return 2
        data = load_csv_column(args.csv, args.column)
    elif args.values:
        data = [float(x.strip()) for x in args.values.split(",") if x.strip()]
    else:
        print("error: provide --csv + --column OR --values", file=sys.stderr)
        return 2

    if not (0 < args.confidence < 1):
        print("error: --confidence must be in (0, 1)", file=sys.stderr)
        return 2

    result = bootstrap_ci(data, args.statistic, args.n_resamples, args.confidence, args.seed)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
