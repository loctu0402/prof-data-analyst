#!/usr/bin/env python3
"""
Minimum Detectable Effect (MDE) + required sample size.

Two modes:
  - mde-from-n: given n and SD, compute smallest detectable effect
  - n-from-mde: given target MDE and SD, compute required sample size

Formulas (per user's statistical_inference_cheat_sheet.md):
  SE  = SD / sqrt(n)
  MDE = (z_alpha + z_power) * SE
  At alpha=0.05 two-sided + power=0.80: z_alpha ≈ 1.96, z_power ≈ 0.84
  → MDE ≈ 2.8 * SE

Usage:
    python mde_sample_size.py mde-from-n --sd 40 --n 100
    python mde_sample_size.py n-from-mde --sd 40 --target-mde 10 --alpha 0.05 --power 0.80

— part of prof-data-analyst · Loc Tu, 2026
"""
from __future__ import annotations
import argparse
import json
import math
import sys


Z_TABLE = {
    (0.05, 0.80, "two"): (1.96, 0.84),
    (0.05, 0.90, "two"): (1.96, 1.28),
    (0.01, 0.80, "two"): (2.576, 0.84),
    (0.05, 0.80, "one"): (1.645, 0.84),
    (0.05, 0.90, "one"): (1.645, 1.28),
}


def get_z(alpha: float, power: float, tail: str) -> tuple[float, float]:
    key = (alpha, power, tail)
    if key in Z_TABLE:
        return Z_TABLE[key]
    raise ValueError(
        f"Unsupported combination alpha={alpha}, power={power}, tail={tail}. "
        f"Supported: {list(Z_TABLE.keys())}"
    )


def mde_from_n(sd: float, n: int, alpha: float, power: float, tail: str) -> dict:
    if n <= 0 or sd < 0:
        raise ValueError("n must be > 0, sd must be >= 0")
    z_alpha, z_power = get_z(alpha, power, tail)
    se = sd / math.sqrt(n)
    mde = (z_alpha + z_power) * se
    return {
        "mode": "mde_from_n",
        "inputs": {"sd": sd, "n": n, "alpha": alpha, "power": power, "tail": tail},
        "se": round(se, 4),
        "mde_absolute": round(mde, 4),
        "z_alpha": z_alpha,
        "z_power": z_power,
        "interpretation": (
            f"With n={n} and SD={sd}, smallest detectable absolute effect "
            f"(alpha={alpha} {tail}-sided, power={power}) is {round(mde, 4)}."
        ),
    }


def n_from_mde(sd: float, target_mde: float, alpha: float, power: float, tail: str) -> dict:
    if sd <= 0 or target_mde <= 0:
        raise ValueError("sd and target_mde must be > 0")
    z_alpha, z_power = get_z(alpha, power, tail)
    n = ((z_alpha + z_power) * sd / target_mde) ** 2
    n_ceil = math.ceil(n)
    return {
        "mode": "n_from_mde",
        "inputs": {"sd": sd, "target_mde": target_mde, "alpha": alpha, "power": power, "tail": tail},
        "n_exact": round(n, 2),
        "n_required": n_ceil,
        "z_alpha": z_alpha,
        "z_power": z_power,
        "interpretation": (
            f"To detect an absolute effect of {target_mde} given SD={sd} "
            f"(alpha={alpha} {tail}-sided, power={power}), need n >= {n_ceil} per group."
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    for name in ("mde-from-n", "n-from-mde"):
        sp = sub.add_parser(name)
        sp.add_argument("--sd", type=float, required=True)
        sp.add_argument("--alpha", type=float, default=0.05)
        sp.add_argument("--power", type=float, default=0.80)
        sp.add_argument("--tail", choices=("one", "two"), default="two")
    sub.choices["mde-from-n"].add_argument("--n", type=int, required=True)
    sub.choices["n-from-mde"].add_argument("--target-mde", type=float, required=True)

    args = p.parse_args()
    if args.cmd == "mde-from-n":
        out = mde_from_n(args.sd, args.n, args.alpha, args.power, args.tail)
    else:
        out = n_from_mde(args.sd, args.target_mde, args.alpha, args.power, args.tail)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
