#!/usr/bin/env python3
"""
Action Brief validator — checks 5W1H 8-field brief presence.

Per universal-workflow-rules.md Rule 3, every recommendation MUST have all 8 fields:
  Question, Goal, Why, What, Who, When, Where, How

Reads stdin OR file. Reports which fields are present / missing.

Exit:
  0 = all 8 fields detected
  1 = one or more missing

Usage:
    cat recommendation.md | python action_brief.py
    python action_brief.py output/report.md
    python action_brief.py output/report.md --section "Recommendations"

— part of prof-data-analyst · Loc Tu, 2026
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED = ("question", "goal", "why", "what", "who", "when", "where", "how")


def check(text: str) -> dict:
    lower = text.lower()
    found = {}
    for field in REQUIRED:
        patterns = [
            rf"\*\*{field}\*\*\s*[:\-]",     # **Question:**
            rf"^\s*[-*]\s*\*\*{field}\*\*",  # - **Question**
            rf"^\s*{field}\s*[:\-]",          # Question:
            rf"^\s*-\s*{field}\s*[:\-]",      # - Question:
        ]
        present = any(re.search(pat, lower, re.MULTILINE) for pat in patterns)
        found[field] = present
    missing = [k for k, v in found.items() if not v]
    return {
        "found": found,
        "missing": missing,
        "n_missing": len(missing),
        "pass": len(missing) == 0,
    }


def extract_section(text: str, section: str) -> str:
    pattern = re.compile(
        rf"#+\s+{re.escape(section)}.*?(?=\n#+\s+|\Z)",
        re.DOTALL | re.IGNORECASE,
    )
    m = pattern.search(text)
    return m.group(0) if m else text


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("path", type=Path, nargs="?", help="File path; reads stdin if omitted")
    p.add_argument("--section", help="Only check inside a named section (e.g., 'Recommendations')")
    args = p.parse_args()

    if args.path:
        try:
            text = args.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(json.dumps({"error": f"not found: {args.path}"}), file=sys.stderr)
            return 2
    else:
        text = sys.stdin.read()

    if args.section:
        text = extract_section(text, args.section)

    result = check(text)
    if args.path:
        result["file"] = str(args.path)
    if args.section:
        result["section"] = args.section
    print(json.dumps(result, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
