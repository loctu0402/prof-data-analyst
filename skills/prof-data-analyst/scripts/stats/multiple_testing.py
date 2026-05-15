#!/usr/bin/env python3
"""Multiple-Testing Correction — Bonferroni FWER + Benjamini-Hochberg FDR.

Usage:
  python multiple_testing.py --p-values 0.01,0.04,0.001,0.03 --alpha 0.05 --method bonferroni
  python multiple_testing.py --p-values 0.01,0.04,0.001,0.03 --alpha 0.05 --method bh-fdr
  python multiple_testing.py --p-values-file pvals.txt --alpha 0.05 --method both

Pure stdlib. Output: JSON with adjusted thresholds + reject/accept per test + which method recommended.

Why this script — running K tests at α=0.05 each gives ~1−0.95^K family-wise false-positive rate
(e.g., K=10 → 40%). Bonferroni controls FWER (any false positive); BH-FDR controls FDR (false-positive
share among rejections). Stakes determine method: confirmatory → Bonferroni, exploratory → BH-FDR.

— part of prof-data-analyst · Loc Tu, 2026
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_p_values(arg: str) -> list[float]:
    return [float(x.strip()) for x in arg.split(",") if x.strip()]


def bonferroni(p_values: list[float], alpha: float) -> dict:
    K = len(p_values)
    adjusted_alpha = alpha / K
    rejects = [p < adjusted_alpha for p in p_values]
    return {
        "method": "Bonferroni FWER",
        "K": K,
        "alpha_original": alpha,
        "alpha_adjusted_per_test": adjusted_alpha,
        "rejections": sum(rejects),
        "per_test": [
            {"index": i, "p_value": p, "reject_H0": r}
            for i, (p, r) in enumerate(zip(p_values, rejects))
        ],
        "interpretation": (
            f"With Bonferroni at α={alpha}, each test must satisfy p < {adjusted_alpha:.6f} "
            f"to be declared significant. {sum(rejects)} of {K} tests pass. "
            "Conservative — controls family-wise error (probability of ANY false positive)."
        ),
    }


def bh_fdr(p_values: list[float], alpha: float) -> dict:
    K = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    sorted_p = [p for _, p in indexed]
    thresholds = [(k + 1) / K * alpha for k in range(K)]

    rejected_set: set[int] = set()
    largest_k = -1
    for k in range(K - 1, -1, -1):
        if sorted_p[k] <= thresholds[k]:
            largest_k = k
            break
    if largest_k >= 0:
        rejected_indices_sorted = list(range(largest_k + 1))
        rejected_set = {indexed[k][0] for k in rejected_indices_sorted}

    per_test = []
    for i, p in enumerate(p_values):
        rank_in_sorted = next(k for k, (orig_i, _) in enumerate(indexed) if orig_i == i) + 1
        per_test.append({
            "index": i,
            "p_value": p,
            "rank": rank_in_sorted,
            "threshold_at_rank": rank_in_sorted / K * alpha,
            "reject_H0": i in rejected_set,
        })

    return {
        "method": "Benjamini-Hochberg FDR",
        "K": K,
        "alpha_original": alpha,
        "largest_rank_rejected": largest_k + 1 if largest_k >= 0 else 0,
        "rejections": len(rejected_set),
        "per_test": per_test,
        "interpretation": (
            f"With BH-FDR at α={alpha}, the largest rank k where p_(k) ≤ (k/K)·α defines the "
            f"rejection threshold. {len(rejected_set)} of {K} tests rejected. "
            "Less conservative than Bonferroni — controls expected proportion of false positives "
            "among rejections (FDR), preserves more power for genuine signals."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--p-values", type=str, help="Comma-separated p-values")
    ap.add_argument("--p-values-file", type=Path, help="File with one p-value per line")
    ap.add_argument("--alpha", type=float, default=0.05, help="Family-wise alpha (default 0.05)")
    ap.add_argument("--method", choices=["bonferroni", "bh-fdr", "both"], default="both")
    args = ap.parse_args(argv)

    if args.p_values:
        p_values = parse_p_values(args.p_values)
    elif args.p_values_file:
        p_values = [float(line.strip()) for line in args.p_values_file.read_text().splitlines() if line.strip()]
    else:
        print("error: provide --p-values or --p-values-file", file=sys.stderr)
        return 2

    if any(p < 0 or p > 1 for p in p_values):
        print("error: p-values must be in [0, 1]", file=sys.stderr)
        return 2

    out: dict = {"input": {"p_values": p_values, "alpha": args.alpha, "K": len(p_values)}}
    if args.method in ("bonferroni", "both"):
        out["bonferroni"] = bonferroni(p_values, args.alpha)
    if args.method in ("bh-fdr", "both"):
        out["bh_fdr"] = bh_fdr(p_values, args.alpha)

    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
