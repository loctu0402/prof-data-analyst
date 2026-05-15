#!/usr/bin/env python3
"""
Pre-ship self-check runner — combines orientation_block + ai_tell_scan + action_brief
and reports a single rolled-up verdict per the self-check protocol.

Runs the 3 cheap checks in sequence on a deliverable, prints a pass/fail summary.
Statistical-rigor checks (Rung 2 noise) are intentionally NOT bundled here —
they require human input (baseline + n + sd) per metric.

Exit:
  0 = all checks pass
  1 = at least one check failed
  2 = file error

Usage:
    python self_check.py output/report.md
    python self_check.py output/report.md --skip orientation
    python self_check.py output/report.md --section Recommendations  # action-brief on this section only

— part of prof-data-analyst · Loc Tu, 2026
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def run_validator(script_name: str, args: list[str]) -> dict:
    script = HERE / script_name
    cmd = [sys.executable, str(script), *args]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    try:
        out = json.loads(result.stdout)
    except json.JSONDecodeError:
        out = {"raw": result.stdout, "stderr": result.stderr}
    out["exit_code"] = result.returncode
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("path", type=Path)
    p.add_argument("--type", choices=("auto", "text", "code"), default="auto",
                   help="Type passed to orientation_block.py")
    p.add_argument("--section", help="Section name for action-brief check")
    p.add_argument("--skip", choices=("orientation", "ai-tell", "action-brief"), action="append", default=[])
    p.add_argument("--strict", action="store_true", help="Strict mode for ai-tell scan")
    args = p.parse_args()

    if not args.path.is_file():
        print(json.dumps({"error": f"not a file: {args.path}"}), file=sys.stderr)
        return 2

    summary = {"file": str(args.path), "checks": {}}

    if "orientation" not in args.skip:
        summary["checks"]["orientation_block"] = run_validator(
            "orientation_block.py", [str(args.path), "--type", args.type]
        )
    if "ai-tell" not in args.skip:
        ai_args = [str(args.path)]
        if args.strict:
            ai_args.append("--strict")
        summary["checks"]["ai_tell_scan"] = run_validator("ai_tell_scan.py", ai_args)
    if "action-brief" not in args.skip:
        brief_args = [str(args.path)]
        if args.section:
            brief_args.extend(["--section", args.section])
        summary["checks"]["action_brief"] = run_validator("action_brief.py", brief_args)

    failures = [name for name, c in summary["checks"].items() if c.get("exit_code", 0) != 0]
    summary["failed_checks"] = failures
    summary["overall_pass"] = len(failures) == 0
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
