#!/usr/bin/env python3
"""
Number formatter with K/M/B/T units + sentiment color hint.

Rules (per style-rules.md):
  - < 1M  → K (e.g., 850K)
  - < 1B  → M (e.g., 12.5M)
  - < 1000B → B (e.g., 572B)
  - >= 1000B → T (e.g., 12.96T)
  - default decimals: 2 (summary), 1 (dense table)
  - people counts: no decimal, comma-separated
  - summary text: space before unit (1.97 T); dense tables: no space (123.4B)

Sentiment colors (for charts / tables):
  - cashout↑/churn↑/cost↑ = RED
  - cashin/net/aum↑/revenue↑ = GREEN

Usage:
    python number_format.py 1234567890                      # → "1.23 B"
    python number_format.py 1234567890 --dense              # → "1.23B"
    python number_format.py 1234567890 --decimals 1         # → "1.2 B"
    python number_format.py 1500 --people                   # → "1,500"
    python number_format.py 12.5 --metric cost --delta 0.05 # → "12.5 (red)"

— part of prof-data-analyst · Loc Tu, 2026
"""
from __future__ import annotations
import argparse
import json
import sys


RED_METRICS = {"cashout", "churn", "cost", "fail", "drop", "withdrawal", "loss"}
GREEN_METRICS = {"cashin", "net", "aum", "revenue", "growth", "deposit", "gmv"}


def format_unit(value: float, decimals: int, dense: bool) -> str:
    sep = "" if dense else " "
    abs_v = abs(value)
    sign = "-" if value < 0 else ""
    if abs_v >= 1_000_000_000_000:
        return f"{sign}{abs_v / 1_000_000_000_000:.{decimals}f}{sep}T"
    if abs_v >= 1_000_000_000:
        return f"{sign}{abs_v / 1_000_000_000:.{decimals}f}{sep}B"
    if abs_v >= 1_000_000:
        return f"{sign}{abs_v / 1_000_000:.{decimals}f}{sep}M"
    if abs_v >= 1_000:
        return f"{sign}{abs_v / 1_000:.{decimals}f}{sep}K"
    return f"{sign}{abs_v:.{decimals}f}"


def format_people(value: float) -> str:
    return f"{int(round(value)):,}"


def sentiment_color(metric: str | None, delta: float | None) -> str | None:
    if metric is None or delta is None:
        return None
    m = metric.lower()
    direction_up = delta > 0
    if m in RED_METRICS:
        return "red" if direction_up else "green"
    if m in GREEN_METRICS:
        return "green" if direction_up else "red"
    return None  # neutral / unknown


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("value", type=float)
    p.add_argument("--decimals", type=int, default=2)
    p.add_argument("--dense", action="store_true", help="No space before unit (for dense tables)")
    p.add_argument("--people", action="store_true", help="Comma-separated integer (for people counts)")
    p.add_argument("--metric", help="Metric name for sentiment color (e.g., 'cashout', 'revenue')")
    p.add_argument("--delta", type=float, help="Direction of change (positive = up). Used with --metric.")
    p.add_argument("--json", action="store_true", help="Output JSON instead of plain string")
    args = p.parse_args()

    if args.people:
        formatted = format_people(args.value)
    else:
        formatted = format_unit(args.value, args.decimals, args.dense)

    color = sentiment_color(args.metric, args.delta)

    if args.json:
        out = {"value": args.value, "formatted": formatted, "color": color}
        print(json.dumps(out))
    else:
        if color:
            print(f"{formatted} ({color})")
        else:
            print(formatted)
    return 0


if __name__ == "__main__":
    sys.exit(main())
