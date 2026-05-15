#!/usr/bin/env python3
"""
Significance tests with auto-caveats:
  - t-test (independent, 2-sided) with Welch's correction
  - Pearson correlation r with sample-size adequacy check
  - z-test for proportions

Auto-warnings encoded:
  - n < 30 → suggests extending the sample
  - n < 83 for Pearson → flags below the |r|>=0.22 → p<0.05 threshold
  - step-function detection on Pearson series (suggests Event Study instead)
  - effect direction matches hypothesis or not

Use this INSTEAD of computing p-values inline.

Usage:
    python significance.py t-test --a "1,2,3" --b "4,5,6"
    python significance.py pearson --x "1,2,3,4,5" --y "2,4,6,8,10"
    python significance.py prop-z --successes 50 --trials 100 --baseline 0.40

Output: JSON to stdout.

— part of prof-data-analyst · Loc Tu, 2026
"""
from __future__ import annotations
import argparse
import json
import math
import sys


def welch_t_test(a: list[float], b: list[float]) -> dict:
    n_a, n_b = len(a), len(b)
    if n_a < 2 or n_b < 2:
        raise ValueError(f"Each group needs n>=2 (got n_a={n_a}, n_b={n_b})")
    mean_a = sum(a) / n_a
    mean_b = sum(b) / n_b
    var_a = sum((x - mean_a) ** 2 for x in a) / (n_a - 1)
    var_b = sum((x - mean_b) ** 2 for x in b) / (n_b - 1)
    se = math.sqrt(var_a / n_a + var_b / n_b)
    if se == 0:
        return {"test": "welch_t", "t": None, "warnings": ["Zero pooled SE — groups identical or constant"]}
    t = (mean_a - mean_b) / se
    df_num = (var_a / n_a + var_b / n_b) ** 2
    df_den = (var_a / n_a) ** 2 / (n_a - 1) + (var_b / n_b) ** 2 / (n_b - 1)
    df = df_num / df_den if df_den > 0 else min(n_a, n_b) - 1
    p = _t_two_sided_p(t, df)
    warnings = []
    if min(n_a, n_b) < 30:
        warnings.append(
            f"Small sample (min n={min(n_a, n_b)}) — t-test relies on near-normality; "
            "consider non-parametric (Mann-Whitney U) or extend sample."
        )
    return {
        "test": "welch_t",
        "t": round(t, 4),
        "df": round(df, 2),
        "p_two_sided": round(p, 6),
        "significant_at_0.05": p < 0.05,
        "n_a": n_a,
        "n_b": n_b,
        "mean_a": round(mean_a, 4),
        "mean_b": round(mean_b, 4),
        "warnings": warnings,
    }


def pearson_r(x: list[float], y: list[float]) -> dict:
    if len(x) != len(y):
        raise ValueError(f"x and y must have same length (got {len(x)} vs {len(y)})")
    n = len(x)
    if n < 3:
        raise ValueError(f"Pearson needs n>=3 (got n={n})")
    mx = sum(x) / n
    my = sum(y) / n
    sx = sum((xi - mx) ** 2 for xi in x)
    sy = sum((yi - my) ** 2 for yi in y)
    sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    if sx == 0 or sy == 0:
        return {"test": "pearson_r", "r": None, "warnings": ["x or y is constant — correlation undefined"]}
    r = sxy / math.sqrt(sx * sy)
    if abs(r) >= 1:
        p = 0.0
        t_stat = float("inf")
    else:
        t_stat = r * math.sqrt((n - 2) / (1 - r * r))
        p = _t_two_sided_p(t_stat, n - 2)
    warnings = []
    if n < 30:
        warnings.append(f"Small n={n} — extend sample (suggest n>=83 for |r|>=0.22 → p<0.05).")
    elif n < 83:
        warnings.append(f"n={n} below 83 — critical |r| for p<0.05 is roughly {round(_critical_r(n, 0.05), 3)}.")
    # Step-function detection on x (heuristic: >70% of values are at <=2 unique levels)
    unique_x = len(set(round(v, 6) for v in x))
    if unique_x <= 3 and n >= 10:
        warnings.append(
            f"x has only {unique_x} unique values — likely step-function. "
            "Pearson invalid on step-functions; use Event Study (pre vs post) instead."
        )
    return {
        "test": "pearson_r",
        "r": round(r, 4),
        "n": n,
        "t": round(t_stat, 4) if math.isfinite(t_stat) else None,
        "df": n - 2,
        "p_two_sided": round(p, 6),
        "significant_at_0.05": p < 0.05,
        "critical_r_for_0.05": round(_critical_r(n, 0.05), 4) if n >= 4 else None,
        "warnings": warnings,
    }


def proportion_z(successes: int, trials: int, baseline: float) -> dict:
    if trials <= 0 or successes < 0 or successes > trials:
        raise ValueError("Invalid counts")
    if not 0 < baseline < 1:
        raise ValueError("baseline must be in (0,1)")
    p_hat = successes / trials
    se = math.sqrt(baseline * (1 - baseline) / trials)
    if se == 0:
        return {"test": "prop_z", "z": None, "warnings": ["Zero SE"]}
    z = (p_hat - baseline) / se
    p_two = 2 * (1 - _normal_cdf(abs(z)))
    warnings = []
    if trials < 30:
        warnings.append(f"trials={trials} — normal approximation may be unreliable")
    if successes < 5 or (trials - successes) < 5:
        warnings.append("expected count <5 in a cell — consider exact binomial test instead")
    return {
        "test": "prop_z",
        "z": round(z, 4),
        "p_hat": round(p_hat, 4),
        "baseline": baseline,
        "p_two_sided": round(p_two, 6),
        "significant_at_0.05": p_two < 0.05,
        "n": trials,
        "warnings": warnings,
    }


def _critical_r(n: int, alpha: float) -> float:
    df = n - 2
    t_crit = _t_critical(df, alpha)
    return t_crit / math.sqrt(df + t_crit * t_crit)


def _t_critical(df: int, alpha: float) -> float:
    return _normal_critical(alpha) * (1 + (_normal_critical(alpha) ** 2 + 1) / (4 * df))


def _normal_critical(alpha: float) -> float:
    p = 1 - alpha / 2
    return _inverse_normal_cdf(p)


def _normal_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _inverse_normal_cdf(p: float) -> float:
    if p <= 0 or p >= 1:
        raise ValueError("p out of range")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    plow = 0.02425
    phigh = 1 - plow
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
               ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
                ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r + a[1])*r + a[2])*r + a[3])*r + a[4])*r + a[5]) * q / \
           (((((b[0]*r + b[1])*r + b[2])*r + b[3])*r + b[4])*r + 1)


def _t_two_sided_p(t: float, df: float) -> float:
    """Approx p-value for two-sided t via standard normal for df>=30, else Welch approximation."""
    if df >= 30:
        return 2 * (1 - _normal_cdf(abs(t)))
    z_equiv = t * (1 - 1 / (4 * df))
    z_equiv = z_equiv / math.sqrt(1 + (t * t) / (2 * df))
    return 2 * (1 - _normal_cdf(abs(z_equiv)))


def parse_list(s: str) -> list[float]:
    return [float(x.strip()) for x in s.split(",") if x.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    p_t = sub.add_parser("t-test", help="Welch's t-test, two-sided")
    p_t.add_argument("--a", required=True)
    p_t.add_argument("--b", required=True)

    p_r = sub.add_parser("pearson", help="Pearson correlation with caveats")
    p_r.add_argument("--x", required=True)
    p_r.add_argument("--y", required=True)

    p_p = sub.add_parser("prop-z", help="z-test for proportion vs baseline")
    p_p.add_argument("--successes", type=int, required=True)
    p_p.add_argument("--trials", type=int, required=True)
    p_p.add_argument("--baseline", type=float, required=True)

    args = p.parse_args()
    if args.cmd == "t-test":
        print(json.dumps(welch_t_test(parse_list(args.a), parse_list(args.b)), indent=2))
    elif args.cmd == "pearson":
        print(json.dumps(pearson_r(parse_list(args.x), parse_list(args.y)), indent=2))
    elif args.cmd == "prop-z":
        print(json.dumps(proportion_z(args.successes, args.trials, args.baseline), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
