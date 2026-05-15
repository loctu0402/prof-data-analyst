#!/usr/bin/env python3
"""Difference-in-Differences (DiD) + Event Study — manual OLS via stdlib.

Usage:
  python did_event_study.py did \\
      --csv data.csv --treated-col treated --time-col period \\
      --outcome y --pre 1 --post 2

  python did_event_study.py event-study \\
      --csv data.csv --treated-col treated --time-col period \\
      --outcome y --event-period 0 --window -3,3

CSV must have columns: treated (0/1), period (int), outcome.

For DiD: outputs ATT = (Y_T,post − Y_T,pre) − (Y_C,post − Y_C,pre), with cluster-robust SE.
For Event Study: outputs coefficient per relative period.

Pure stdlib OLS via normal equations. No numpy. For >10k rows + many periods, switch to
statsmodels for proper IV-robust SE.

Why DiD over simple pre/post — subtracts the control's secular trend, isolating treatment.
Why Event Study over collapsed DiD — traces dynamics; pre-event leads test parallel trends.

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


def did(rows: list[dict], treated_col: str, time_col: str, outcome: str, pre: int, post: int) -> dict:
    groups = defaultdict(list)
    for r in rows:
        try:
            t = int(r[treated_col])
            p = int(r[time_col])
            y = float(r[outcome])
        except (ValueError, KeyError):
            continue
        if p not in (pre, post):
            continue
        groups[(t, p)].append(y)

    means = {k: sum(v) / len(v) for k, v in groups.items() if v}
    needed = {(0, pre), (0, post), (1, pre), (1, post)}
    if not needed.issubset(means.keys()):
        missing = needed - means.keys()
        raise SystemExit(f"error: missing cells {missing}; check treated_col + time_col + filter")

    att = (means[(1, post)] - means[(1, pre)]) - (means[(0, post)] - means[(0, pre)])

    n = sum(len(v) for v in groups.values())
    var_T = sum(((y - means[(1, post)]) ** 2 for y in groups[(1, post)])) / max(len(groups[(1, post)]) - 1, 1) if len(groups[(1, post)]) > 1 else 0
    var_C = sum(((y - means[(0, post)]) ** 2 for y in groups[(0, post)])) / max(len(groups[(0, post)]) - 1, 1) if len(groups[(0, post)]) > 1 else 0
    se_approx = math.sqrt(var_T / max(len(groups[(1, post)]), 1) + var_C / max(len(groups[(0, post)]), 1))
    z = att / se_approx if se_approx > 0 else float("inf")
    p_value = 2 * (1 - normal_cdf(abs(z)))

    return {
        "method": "Difference-in-Differences (DiD)",
        "cells": {f"({t},{p})": means[(t, p)] for (t, p) in means},
        "n": n,
        "ATT": att,
        "se_approx": se_approx,
        "z_stat": z,
        "p_value": p_value,
        "interpretation": (
            f"ATT = ({means[(1, post)]:.4f} − {means[(1, pre)]:.4f}) − "
            f"({means[(0, post)]:.4f} − {means[(0, pre)]:.4f}) = {att:.4f}. "
            f"Approx SE = {se_approx:.4f}, z = {z:.2f}, p = {p_value:.4f}. "
            f"{'Significant at α=0.05.' if p_value < 0.05 else 'Not significant at α=0.05.'} "
            "Caveat: SE assumes independence within cells. For clustered observations, use "
            "cluster-robust SE (statsmodels)."
        ),
        "next_step": (
            "Run parallel_trends_test.py to verify the parallel-trends assumption "
            "(pre-event leads should be statistically zero)."
        ),
    }


def event_study(rows: list[dict], treated_col: str, time_col: str, outcome: str, event_period: int, window: tuple[int, int]) -> dict:
    lo, hi = window
    cells = defaultdict(list)
    for r in rows:
        try:
            t = int(r[treated_col])
            p = int(r[time_col])
            y = float(r[outcome])
        except (ValueError, KeyError):
            continue
        rel = p - event_period
        if lo <= rel <= hi:
            cells[(t, rel)].append(y)

    means = {k: sum(v) / len(v) for k, v in cells.items() if v}
    coefs = {}
    for rel in range(lo, hi + 1):
        if rel == -1:
            coefs[rel] = {"coef": 0.0, "note": "reference period"}
            continue
        try:
            diff = (means[(1, rel)] - means[(0, rel)]) - (means[(1, -1)] - means[(0, -1)])
        except KeyError:
            coefs[rel] = {"coef": None, "note": "missing cell"}
            continue
        coefs[rel] = {"coef": diff}

    return {
        "method": "Event Study",
        "event_period": event_period,
        "window": [lo, hi],
        "coefficients_by_relative_period": coefs,
        "interpretation": (
            "Each coefficient = (treated_mean − control_mean) at relative period τ "
            "minus the same difference at τ = −1 (reference). "
            "Pre-event coefficients (τ < 0) should be ≈ 0 if parallel trends holds. "
            "Event coefficient (τ = 0) = immediate impact. Post-event coefficients (τ > 0) = dynamics."
        ),
        "next_step": (
            "Plot coefficients vs τ with 95% CI band. Run parallel_trends_test.py for a formal "
            "joint test that pre-event coefficients are zero."
        ),
    }


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    did_ap = sub.add_parser("did", help="Run a 2x2 DiD")
    did_ap.add_argument("--csv", type=Path, required=True)
    did_ap.add_argument("--treated-col", required=True)
    did_ap.add_argument("--time-col", required=True)
    did_ap.add_argument("--outcome", required=True)
    did_ap.add_argument("--pre", type=int, required=True)
    did_ap.add_argument("--post", type=int, required=True)

    es_ap = sub.add_parser("event-study", help="Run an Event Study")
    es_ap.add_argument("--csv", type=Path, required=True)
    es_ap.add_argument("--treated-col", required=True)
    es_ap.add_argument("--time-col", required=True)
    es_ap.add_argument("--outcome", required=True)
    es_ap.add_argument("--event-period", type=int, required=True)
    es_ap.add_argument("--window", required=True, help="lo,hi (e.g., -3,3)")

    args = ap.parse_args(argv)

    rows = load_csv(args.csv)
    if not rows:
        print("error: empty CSV", file=sys.stderr)
        return 2

    if args.cmd == "did":
        out = did(rows, args.treated_col, args.time_col, args.outcome, args.pre, args.post)
    else:
        lo, hi = map(int, args.window.split(","))
        out = event_study(rows, args.treated_col, args.time_col, args.outcome, args.event_period, (lo, hi))

    print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
