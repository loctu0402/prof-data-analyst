#!/usr/bin/env python3
"""
Orientation Block validator.

Checks a deliverable (markdown / HTML / python) has the required Orientation
Block at the top, per universal-workflow-rules.md Rule 1.

Detected types (auto-inferred from extension):
  - .md / .markdown        → looks for SCQR sections OR a 3-line intro
  - .html                  → looks for SCQR-styled section OR 3-line intro
  - .py / .ipynb           → looks for module docstring with required fields

Exit codes:
  0 = pass
  1 = missing or malformed Orientation Block
  2 = file not found / unreadable

Usage:
    python orientation_block.py output/report.md
    python orientation_block.py pipeline.py --type code

— part of prof-data-analyst · Loc Tu, 2026
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path


SCQR_KEYS = ("situation", "complication", "question", "resolution")
CODE_DOCSTRING_KEYS = ("purpose", "input", "output", "owner")


def check_text(text: str) -> dict:
    """Look for SCQR labels OR a 3-line intro at the top."""
    lower = text.lower()
    head = "\n".join(text.splitlines()[:60])
    head_lower = head.lower()
    scqr_hits = [k for k in SCQR_KEYS if k in head_lower]
    if len(scqr_hits) >= 3:
        return {"pattern": "SCQR", "found": scqr_hits, "pass": True}
    non_blank = [ln for ln in text.splitlines()[:10] if ln.strip()]
    if len(non_blank) >= 3:
        first3 = "\n".join(non_blank[:3])
        has_data_marker = any(w in first3.lower() for w in ("data", "range", "period", "time", "snapshot"))
        has_question = any(w in first3.lower() for w in ("question", "why", "what", "how", "?"))
        if has_data_marker and has_question:
            return {"pattern": "3-line-intro", "found": non_blank[:3], "pass": True}
    return {
        "pattern": None,
        "found": scqr_hits,
        "pass": False,
        "hint": "Add SCQR (Situation/Complication/Question/Resolution) at top, or a 3-line intro "
                "(what data + time range / primary question / reading order).",
    }


def check_code(text: str) -> dict:
    """Look for module docstring with purpose / input / output / owner."""
    m = re.match(r'(?s)\s*("""|\'\'\')(.+?)\1', text)
    if not m:
        return {
            "pattern": "module_docstring",
            "found": [],
            "pass": False,
            "hint": "Add module docstring at top with: Purpose, Inputs, Outputs, Owner, Last-updated.",
        }
    docstring_lower = m.group(2).lower()
    hits = [k for k in CODE_DOCSTRING_KEYS if k in docstring_lower]
    if len(hits) >= 3:
        return {"pattern": "module_docstring", "found": hits, "pass": True}
    return {
        "pattern": "module_docstring",
        "found": hits,
        "pass": False,
        "hint": f"Module docstring present but missing fields. Found: {hits}. "
                f"Required at least 3 of: {list(CODE_DOCSTRING_KEYS)}.",
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("path", type=Path)
    p.add_argument("--type", choices=("auto", "text", "code"), default="auto")
    args = p.parse_args()
    if not args.path.is_file():
        print(json.dumps({"error": f"not a file: {args.path}"}), file=sys.stderr)
        return 2
    try:
        text = args.path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = args.path.read_text(encoding="latin-1")

    if args.type == "auto":
        kind = "code" if args.path.suffix in (".py", ".ipynb") else "text"
    else:
        kind = args.type

    result = check_code(text) if kind == "code" else check_text(text)
    result["file"] = str(args.path)
    result["kind"] = kind
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
