#!/usr/bin/env python3
"""
Scan for AI-tell symbols in stakeholder-facing text.

Per style-rules.md, the following symbols are banned in stakeholder prose:
  - === (use markdown headings #/##/### instead)
  - ----- (separator)
  - em-dash —
  - approx ≈
  - arrow → (in stakeholder prose; OK inside code blocks)

Note: skips fenced code blocks (```...```) and inline code (`...`) — these are
syntactically legitimate places for symbols.

Exit:
  0 = clean
  1 = found AI tells
  2 = file error

Usage:
    python ai_tell_scan.py output/report.md
    python ai_tell_scan.py output/report.md --strict  # also flag — and → in code

— part of prof-data-analyst · Loc Tu, 2026
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path


PATTERNS = {
    "triple_equals_header": re.compile(r"^={3,}\s*$", re.MULTILINE),
    "dash_separator":       re.compile(r"^-{5,}\s*$", re.MULTILINE),
    "em_dash":              re.compile(r"—"),
    "approx_symbol":        re.compile(r"≈"),
    "arrow_in_prose":       re.compile(r"→"),
}


def strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks and inline code so we only scan prose."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]*`", "", text)
    return text


def scan(text: str, strict: bool = False) -> dict:
    target = text if strict else strip_code_blocks(text)
    findings = {}
    for name, pat in PATTERNS.items():
        matches = list(pat.finditer(target))
        if matches:
            line_nums = []
            for m in matches:
                line_nums.append(target.count("\n", 0, m.start()) + 1)
            findings[name] = {"count": len(matches), "lines": line_nums[:20]}
    return {
        "findings": findings,
        "n_issues": sum(v["count"] for v in findings.values()),
        "pass": len(findings) == 0,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("path", type=Path)
    p.add_argument("--strict", action="store_true", help="Also scan inside code blocks")
    args = p.parse_args()
    if not args.path.is_file():
        print(json.dumps({"error": f"not a file: {args.path}"}), file=sys.stderr)
        return 2
    try:
        text = args.path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = args.path.read_text(encoding="latin-1")
    result = scan(text, strict=args.strict)
    result["file"] = str(args.path)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
