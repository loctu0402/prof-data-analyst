#!/usr/bin/env python3
"""
Baseline → Noise → Impact 3-rung ladder runner.

Inputs the user provides per metric:
  - current value
  - baseline value (previous period / canonical / KVBD expected / etc.)
  - sample size n (and sd OR ci_lower/ci_upper) → for noise check
  - business-threshold rule for impact verdict (small/medium/large bands)

Outputs the 3-rung verdict in structured JSON the agent can quote directly.

This script is the bridge between the universal-workflow-rules.md Rule 2 and
deliverable copy. Run it; quote the verdict; do not compute inline.

Usage:
    python baseline_noise_impact.py \
        --current 12.65 --baseline 12.96 \
        --n 100 --sd 0.5 \
        --small 0.01 --medium 0.05 --large 0.10

    # Or with explicit CI:
    python baseline_noise_impact.py \
        --current 12.65 --baseline 12.96 \
        --ci-lower 12.50 --ci-upper 12.80 \
        --small 0.01 --medium 0.05 --large 0.10

— part of prof-data-analyst · Loc Tu, 2026
"""
from __future__ import annotations
import argparse
import json
import math
import sys


def ladder(
    current: float,
    baseline: float,
    n: int | None,
    sd: float | None,
    ci_lower: float | None,
    ci_upper: float | None,
    small: float,
    medium: float,
    large: float,
    baseline_label: str,
) -> dict:
    delta_abs = current - baseline
    delta_pct = (current - baseline) / baseline if baseline != 0 else None

    # Rung 1 — Baseline
    rung1 = {
        "baseline_value": baseline,
        "baseline_label": baseline_label,
        "current_value": current,
        "delta_abs": round(delta_abs, 6),
        "delta_pct": round(delta_pct, 6) if delta_pct is not None else None,
    }

    # Rung 2 — Noise
    if ci_lower is not None and ci_upper is not None:
        baseline_in_ci = ci_lower <= baseline <= ci_upper
        noise_verdict = "real (baseline outside 95% CI)" if not baseline_in_ci else "noise (baseline inside 95% CI)"
        rung2 = {
            "method": "ci_provided",
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "ci_width": round(ci_upper - ci_lower, 6),
            "baseline_in_ci": baseline_in_ci,
            "verdict": noise_verdict,
        }
    elif n is not None and sd is not None and n > 1:
        se = sd / math.sqrt(n)
        z = (current - baseline) / se if se > 0 else None
        derived_ci_lower = current - 1.96 * se
        derived_ci_upper = current + 1.96 * se
        baseline_in_ci = derived_ci_lower <= baseline <= derived_ci_upper
        noise_verdict = "real (|z|>1.96)" if z is not None and abs(z) > 1.96 else "noise (|z|<=1.96)"
        rung2 = {
            "method": "derived_from_n_sd",
            "se": round(se, 6),
            "z_score": round(z, 4) if z is not None else None,
            "ci_lower_95": round(derived_ci_lower, 6),
            "ci_upper_95": round(derived_ci_upper, 6),
            "baseline_in_ci": baseline_in_ci,
            "verdict": noise_verdict,
        }
    else:
        rung2 = {
            "method": "missing",
            "verdict": "REJECTED — Rung 2 requires CI or (n + sd). Bare delta is insufficient.",
        }

    # Rung 3 — Impact
    abs_delta_pct = abs(delta_pct) if delta_pct is not None else None
    if abs_delta_pct is None:
        impact = "undefined (baseline is zero)"
    elif abs_delta_pct < small:
        impact = "negligible"
    elif abs_delta_pct < medium:
        impact = "small"
    elif abs_delta_pct < large:
        impact = "medium"
    else:
        impact = "large"
    rung3 = {
        "thresholds_pct": {"small": small, "medium": medium, "large": large},
        "abs_delta_pct": round(abs_delta_pct, 6) if abs_delta_pct is not None else None,
        "verdict": impact,
    }

    overall = "REJECTED" if rung2.get("verdict", "").startswith("REJECTED") else f"{rung2['verdict']}; impact = {impact}"

    return {
        "rung1_baseline": rung1,
        "rung2_noise": rung2,
        "rung3_impact": rung3,
        "overall": overall,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--current", type=float, required=True)
    p.add_argument("--baseline", type=float, required=True)
    p.add_argument("--baseline-label", default="previous-period", help="What baseline represents")
    p.add_argument("--n", type=int)
    p.add_argument("--sd", type=float)
    p.add_argument("--ci-lower", type=float)
    p.add_argument("--ci-upper", type=float)
    p.add_argument("--small", type=float, default=0.01, help="Impact threshold for 'small' (as fraction, default 1%)")
    p.add_argument("--medium", type=float, default=0.05, help="Impact threshold for 'medium' (default 5%)")
    p.add_argument("--large", type=float, default=0.10, help="Impact threshold for 'large' (default 10%)")
    args = p.parse_args()

    out = ladder(
        current=args.current,
        baseline=args.baseline,
        n=args.n,
        sd=args.sd,
        ci_lower=args.ci_lower,
        ci_upper=args.ci_upper,
        small=args.small,
        medium=args.medium,
        large=args.large,
        baseline_label=args.baseline_label,
    )
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
