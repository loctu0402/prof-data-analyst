#!/usr/bin/env python3
"""
Effect size calculators — Cohen's d (continuous) and Cramer's V (categorical).

Use this INSTEAD of computing effect sizes inline in chat. The agent reads the
output and reasons about it; it should never do the arithmetic itself.

Usage:
    python effect_size.py cohen-d --a "1,2,3,4,5" --b "3,4,5,6,7"
    python effect_size.py cohen-d --csv-a data/a.csv --csv-b data/b.csv --col score
    python effect_size.py cramer-v --contingency "10,20;30,40"
    python effect_size.py cramer-v --csv data/users.csv --row segment --col converted

Output: JSON to stdout, exit 0 on success.

— part of prof-data-analyst · Loc Tu, 2026
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import sys
from pathlib import Path


def cohen_d(a: list[float], b: list[float]) -> dict:
    """Cohen's d for two independent groups with pooled SD."""
    if len(a) < 2 or len(b) < 2:
        raise ValueError(f"Each group needs n>=2 (got n_a={len(a)}, n_b={len(b)})")
    mean_a = sum(a) / len(a)
    mean_b = sum(b) / len(b)
    var_a = sum((x - mean_a) ** 2 for x in a) / (len(a) - 1)
    var_b = sum((x - mean_b) ** 2 for x in b) / (len(b) - 1)
    pooled_sd = math.sqrt(((len(a) - 1) * var_a + (len(b) - 1) * var_b) / (len(a) + len(b) - 2))
    if pooled_sd == 0:
        return {
            "metric": "cohen_d",
            "d": None,
            "magnitude": "undefined (zero variance)",
            "n_a": len(a),
            "n_b": len(b),
        }
    d = (mean_a - mean_b) / pooled_sd
    abs_d = abs(d)
    if abs_d < 0.2:
        mag = "negligible"
    elif abs_d < 0.5:
        mag = "small"
    elif abs_d < 0.8:
        mag = "medium"
    else:
        mag = "large"
    return {
        "metric": "cohen_d",
        "d": round(d, 4),
        "magnitude": mag,
        "n_a": len(a),
        "n_b": len(b),
        "mean_a": round(mean_a, 4),
        "mean_b": round(mean_b, 4),
        "pooled_sd": round(pooled_sd, 4),
    }


def cramer_v(contingency: list[list[int]]) -> dict:
    """Cramer's V for a contingency table. Warns on high cardinality."""
    rows = len(contingency)
    cols = len(contingency[0]) if rows else 0
    if rows < 2 or cols < 2:
        raise ValueError(f"Contingency table needs >=2 rows and >=2 cols (got {rows}x{cols})")
    n = sum(sum(row) for row in contingency)
    if n == 0:
        raise ValueError("Contingency table is empty")
    row_totals = [sum(row) for row in contingency]
    col_totals = [sum(contingency[r][c] for r in range(rows)) for c in range(cols)]
    chi2 = 0.0
    for r in range(rows):
        for c in range(cols):
            expected = row_totals[r] * col_totals[c] / n
            if expected > 0:
                chi2 += (contingency[r][c] - expected) ** 2 / expected
    min_dim = min(rows, cols)
    v = math.sqrt(chi2 / (n * (min_dim - 1)))
    if v < 0.1:
        mag = "negligible"
    elif v < 0.3:
        mag = "small"
    elif v < 0.5:
        mag = "medium"
    else:
        mag = "large"
    warnings = []
    if rows > 50 or cols > 50:
        warnings.append(
            f"HIGH CARDINALITY WARNING: {rows}x{cols} table. Cramer's V inflates on high-cardinality columns "
            "(chi-square scales with df). Verify column is not an identifier (user_id, transaction_id, etc.)."
        )
    if n < 30:
        warnings.append(f"Small sample (n={n}) — chi-square approximation may be unreliable")
    return {
        "metric": "cramer_v",
        "v": round(v, 4),
        "magnitude": mag,
        "chi2": round(chi2, 4),
        "n": n,
        "shape": [rows, cols],
        "warnings": warnings,
    }


def parse_list(s: str) -> list[float]:
    return [float(x.strip()) for x in s.split(",") if x.strip()]


def parse_contingency(s: str) -> list[list[int]]:
    return [[int(x.strip()) for x in row.split(",") if x.strip()] for row in s.split(";") if row.strip()]


def load_csv_col(path: Path, col: str) -> list[float]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [float(row[col]) for row in reader if row.get(col) not in (None, "")]


def load_csv_contingency(path: Path, row_col: str, val_col: str) -> list[list[int]]:
    counts: dict[tuple, int] = {}
    rows: list = []
    cols: list = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            key = (r[row_col], r[val_col])
            counts[key] = counts.get(key, 0) + 1
            if r[row_col] not in rows:
                rows.append(r[row_col])
            if r[val_col] not in cols:
                cols.append(r[val_col])
    return [[counts.get((row, col), 0) for col in cols] for row in rows]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    p_d = sub.add_parser("cohen-d", help="Cohen's d for two groups")
    p_d.add_argument("--a", help="Comma-separated values for group A")
    p_d.add_argument("--b", help="Comma-separated values for group B")
    p_d.add_argument("--csv-a", type=Path, help="CSV path for group A")
    p_d.add_argument("--csv-b", type=Path, help="CSV path for group B")
    p_d.add_argument("--col", help="Column name in CSV")

    p_v = sub.add_parser("cramer-v", help="Cramer's V for contingency")
    p_v.add_argument("--contingency", help='Rows separated by ";", values by "," — e.g., "10,20;30,40"')
    p_v.add_argument("--csv", type=Path, help="CSV path with row + value columns")
    p_v.add_argument("--row", help="Row column name in CSV")
    p_v.add_argument("--col", help="Value column name in CSV")

    args = p.parse_args()

    if args.cmd == "cohen-d":
        if args.a and args.b:
            a, b = parse_list(args.a), parse_list(args.b)
        elif args.csv_a and args.csv_b and args.col:
            a = load_csv_col(args.csv_a, args.col)
            b = load_csv_col(args.csv_b, args.col)
        else:
            p.error("cohen-d requires either --a/--b OR --csv-a/--csv-b/--col")
        print(json.dumps(cohen_d(a, b), indent=2))
        return 0

    if args.cmd == "cramer-v":
        if args.contingency:
            table = parse_contingency(args.contingency)
        elif args.csv and args.row and args.col:
            table = load_csv_contingency(args.csv, args.row, args.col)
        else:
            p.error("cramer-v requires either --contingency OR --csv/--row/--col")
        print(json.dumps(cramer_v(table), indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
