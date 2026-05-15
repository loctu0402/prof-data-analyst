#!/usr/bin/env python3
"""Rubric Audit — mechanical compliance check of a deliverable against prof-data-analyst rules.

Walks the input file (markdown, notebook, .py, .sql, .html) and runs ~30 regex/structural
checks tied to Rules 1-4 + style + coding discipline. Outputs a gap table (TSV or JSON)
with columns: rule_id | rule_name | severity | location | what_missing | how_to_fix | why_it_matters.

Two modes:
  - Single file: audit one deliverable (Sub-mode A — Delivery Refine)
  - Project dir: walk all narrative + code files under a folder (Sub-mode B — Full Project Refine)

Usage:
  python rubric_audit.py <file>                       # TSV gap table for one file
  python rubric_audit.py <file> --json                # JSON output
  python rubric_audit.py <file> --severity BLOCKER    # filter to severity
  python rubric_audit.py <file> --rule R2             # filter to one rule family
  python rubric_audit.py --project <dir>              # walk a project folder
  python rubric_audit.py --project <dir> --json       # JSON rollup across all files

Pure stdlib (re, json, argparse, pathlib, sys). No external deps.

— part of prof-data-analyst · Loc Tu, 2026
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple


SEVERITIES = ("BLOCKER", "HIGH", "MEDIUM", "LOW")


class Finding(NamedTuple):
    rule_id: str
    rule_name: str
    severity: str
    location: str
    what_missing: str
    how_to_fix: str
    why_it_matters: str


def load(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def line_locator(text: str, pattern: str, flags: int = 0) -> list[int]:
    """Return 1-indexed line numbers where pattern matches."""
    lines = text.splitlines()
    rx = re.compile(pattern, flags)
    return [i + 1 for i, ln in enumerate(lines) if rx.search(ln)]


# ---------------- Rule 1 — Orientation Block ----------------

def check_orientation(text: str, path: Path) -> list[Finding]:
    out: list[Finding] = []
    ext = path.suffix.lower()

    has_scqr = bool(re.search(r"\b(situation|complication|question|resolution)\b", text, re.I))
    has_3line_intro = bool(re.search(r"^(#|##)\s*(intro|overview|read me|how to read|orientation)", text, re.I | re.M))
    has_docstring = bool(re.search(r'^\s*"""', text, re.M)) or bool(re.search(r"^\s*'''", text, re.M))

    if ext in (".md", ".markdown", ".html"):
        if not (has_scqr or has_3line_intro):
            out.append(Finding(
                "R1.Orientation",
                "Orientation Block",
                "BLOCKER",
                f"{path.name}:1",
                "No SCQR / 3-line intro / How-to-read block detected at top.",
                "Add a Situation-Complication-Question-Resolution block (reports) or a 3-line intro "
                "stating data scope + primary question + reading order (dashboards).",
                "Cold readers bounce in 30s without orientation. Skill Rule 1.",
            ))
    elif ext in (".py", ".sql", ".ipynb"):
        if not has_docstring and ext == ".py":
            out.append(Finding(
                "R1.Orientation",
                "Module Docstring (Orientation)",
                "BLOCKER",
                f"{path.name}:1",
                "Module-level docstring missing.",
                'Add """purpose / inputs / outputs / side effects / owner / last-updated""" at top.',
                "Code module without docstring fails Rule 1 Orientation requirement.",
            ))
    return out


# ---------------- Rule 2 — Baseline-Noise-Impact Ladder ----------------

def check_baseline_noise_impact(text: str, path: Path) -> list[Finding]:
    out: list[Finding] = []
    if path.suffix.lower() in (".py", ".sql"):
        return out  # rule applies to narrative deliverables

    bare_pct = re.findall(r"(?<![\d\.])([+\-]?\d+(?:\.\d+)?)\s*%", text)
    has_baseline_keyword = bool(re.search(r"\b(baseline|MoM|WoW|YoY|DoD|so v[oớ]i|vs)\b", text, re.I))
    has_noise_keyword = bool(re.search(r"\b(p[-\s]?value|95%\s*CI|p<0\.\d+|z[-\s]?score|effect size|Cohen|Cramer)\b", text, re.I))
    has_impact_keyword = bool(re.search(r"\b(impact|negligible|small|medium|large|t[aá]c [đd][oộ]ng|m[ứu]c [đd][oộ])\b", text, re.I))

    if bare_pct and not has_baseline_keyword:
        out.append(Finding(
            "R2.Rung1",
            "Baseline missing",
            "BLOCKER",
            f"{path.name}",
            f"Found {len(bare_pct)} bare percentage(s) (e.g., '{bare_pct[0]}%') with no baseline anchor.",
            "Add baseline reference: 'vs MoM 13.20T (-1.8%)' or 'vs canonical 5.0%' next to each headline number.",
            "Bare delta without baseline = REJECTED. Reader cannot judge magnitude.",
        ))

    if bare_pct and not has_noise_keyword:
        out.append(Finding(
            "R2.Rung2",
            "Noise check missing",
            "HIGH",
            f"{path.name}",
            "Numeric statements lack noise check (CI / p-value / effect size / z-score).",
            "Add CI or p-value or effect size next to each headline. Use scripts/stats/significance.py.",
            "Bare delta could be noise. Statistical-confidence layer is Rung 2 of the ladder.",
        ))

    if bare_pct and not has_impact_keyword:
        out.append(Finding(
            "R2.Rung3",
            "Business impact verdict missing",
            "HIGH",
            f"{path.name}",
            "Numeric statements lack impact verdict (negligible / small / medium / large in business terms).",
            "Add business-unit translation: '−1.8% AUM = ~6.5B VND gap, sustained 3 days, medium impact'.",
            "Statistical significance is not business significance. Reader needs verdict in their unit.",
        ))
    return out


# ---------------- Rule 3 — 5W1H Action Brief ----------------

def check_action_brief(text: str, path: Path) -> list[Finding]:
    out: list[Finding] = []
    if path.suffix.lower() in (".py", ".sql"):
        return out

    has_recommend_section = bool(re.search(r"\b(recommend|đề xuất|next step|action|đề nghị)\b", text, re.I))
    if not has_recommend_section:
        return out  # no recommendation section → rule doesn't trigger

    fields = ["question", "goal", "why", "what", "who", "when", "where", "how"]
    field_present = {f: bool(re.search(rf"\b{f}\b\s*[:\-—]", text, re.I)) for f in fields}
    missing = [f for f, present in field_present.items() if not present]
    if missing:
        out.append(Finding(
            "R3.5W1H",
            "5W1H Action Brief incomplete",
            "BLOCKER",
            f"{path.name}",
            f"Recommendation section present but missing fields: {', '.join(missing)}.",
            "Fill all 8 fields per recommendation: Question, Goal, Why, What, Who, When, Where, How. "
            "Use scripts/validators/action_brief.py to verify.",
            "Missing field = action does not ship. Rule 3 universal-workflow-rules.md.",
        ))
    return out


# ---------------- Rule 4 — Why-Explanation Meta-Rule ----------------

def check_why_explanation(text: str, path: Path) -> list[Finding]:
    out: list[Finding] = []
    if path.suffix.lower() in (".sql",):
        return out

    # Tool / method / threshold introductions need a Why nearby
    method_intros = re.findall(
        r"(?:use|chose|pick|chọn|dùng|sử dụng)\s+(\w[\w\-]*)",
        text, re.I,
    )
    why_keywords = bool(re.search(r"\b(why|because|lý do|vì|because of|so that|để|tại sao)\b", text, re.I))

    if method_intros and not why_keywords:
        out.append(Finding(
            "R4.WhyExplanation",
            "Why-Explanation missing on method/tool choice",
            "HIGH",
            f"{path.name}",
            f"Detected {len(method_intros)} method/tool introduction(s) (e.g., 'use {method_intros[0]}') "
            "but no Why-keyword nearby (because / lý do / vì / so that).",
            "Add a 1-sentence Why next to each choice: Causal / Empirical / Comparative / Theoretical / Operational. "
            "See Rule 4 in references/universal-workflow-rules.md.",
            "Bare prescription reads as gut-feel. Why-line transforms 'I think we should do X' into "
            "'X follows from evidence Y, principle Z'.",
        ))

    # Threshold values often missing rationale
    thresholds = re.findall(r"(?:threshold|cutoff|alpha|α|p\s*<\s*0\.\d+|MDE)\s*[=:]\s*[\d\.]+", text, re.I)
    if thresholds and not why_keywords:
        out.append(Finding(
            "R4.WhyExplanation",
            "Threshold value lacks justification",
            "HIGH",
            f"{path.name}",
            f"Detected threshold/cutoff values (e.g., '{thresholds[0]}') with no nearby justification.",
            "Anchor each threshold to evidence or principle: 'α=0.01 because we run 5 tests, "
            "Bonferroni FWER 0.05/5=0.01'.",
            "Threshold without Why is arbitrary. Future reader cannot reverse-engineer decision.",
        ))
    return out


# ---------------- Style Rules ----------------

def check_style(text: str, path: Path) -> list[Finding]:
    out: list[Finding] = []
    ext = path.suffix.lower()
    if ext not in (".md", ".markdown", ".html", ".ipynb"):
        return out

    # AI-tell symbols in stakeholder text
    if re.search(r"^={3,}\s*$", text, re.M):
        out.append(Finding(
            "Style.AITell",
            "AI-tell `===` separator",
            "MEDIUM",
            f"{path.name}",
            "Found `===` separator line(s).",
            "Use markdown headings (`#`, `##`) instead.",
            "`===` reads as AI artefact in stakeholder prose. Drop to look human-authored.",
        ))
    if re.search(r"^-{3,}\s*$", text, re.M):
        out.append(Finding(
            "Style.AITell",
            "AI-tell `---` separator",
            "LOW",
            f"{path.name}",
            "Found `---` separator line(s) (note: also legitimate markdown horizontal rule).",
            "Use a heading or paragraph break instead unless the rule is necessary.",
            "Over-use of `---` separators reads as AI artefact.",
        ))
    em_dash_count = text.count("—")
    if em_dash_count > 5:
        out.append(Finding(
            "Style.AITell",
            "Em-dash overuse",
            "LOW",
            f"{path.name}",
            f"Found {em_dash_count} em-dashes ({chr(8212)}). Heavy em-dash use is an AI tell.",
            "Replace most with comma / period / colon. Reserve em-dash for true parenthetical aside.",
            "Em-dash overuse is one of the most-cited AI-style markers.",
        ))
    if "≈" in text:
        out.append(Finding(
            "Style.AITell",
            "Approximation symbol ≈",
            "LOW",
            f"{path.name}",
            "Found `≈` (approximation symbol).",
            'Use plain language: "khoảng" or "around" or "~".',
            "`≈` is rare in human-authored stakeholder prose; reads as machine output.",
        ))

    # Bare percentage without denominator (count all % then check for n/n nearby pattern)
    bare_pct_only = re.findall(r"\b\d+(?:\.\d+)?\s*%", text)
    has_denominator_pattern = bool(re.search(r"\d+\s*/\s*\d+\s*\w*\s*\(\s*\d", text))
    if len(bare_pct_only) > 3 and not has_denominator_pattern:
        out.append(Finding(
            "Style.Denominator",
            "Bare percentage without denominator",
            "HIGH",
            f"{path.name}",
            f"Found {len(bare_pct_only)} bare percentage(s) with no absolute/total nearby.",
            'Format every percentage as "absolute / total (% )": "100 / 176 sessions (56.8%)".',
            "Bare % without denominator: reader cannot weight. 76% of 17 vs 1700 = different decisions.",
        ))

    # Mermaid in markdown
    if re.search(r"```\s*mermaid", text, re.I):
        out.append(Finding(
            "Style.NoMermaid",
            "Mermaid diagram in .md",
            "MEDIUM",
            f"{path.name}",
            "Mermaid code block found.",
            "Replace with ASCII art. Mermaid renders badly in Obsidian and other markdown viewers.",
            "Mermaid is fragile across editors; ASCII works everywhere.",
        ))

    # "Top X" tables — heuristic check that next-line ordering is descending
    # (skip — semantic check, requires Step 3 human pass)

    # Hardcoded "fabricated credentials" sniff
    if re.search(r"\b(BSc|MSc|PhD|Bachelor of (Science|Arts)|Master of)\b.*\bLoc\b", text):
        out.append(Finding(
            "Style.NoFabricatedCredentials",
            "Possible fabricated academic credential",
            "BLOCKER",
            f"{path.name}",
            "Academic credential detected near author name. Verify against actual CV.",
            "Default bio: job title + company + years experience. NO academic credentials unless on actual CV.",
            "Past incident: unverified 'BSc & MSc Statistics' caught before lecture. Re-verify each time.",
        ))

    # No auto-email
    if re.search(r"(smtplib|send_message|sendgrid|mailgun).{0,200}(stakeholder|recipient|to=)", text, re.I | re.S):
        out.append(Finding(
            "Style.NoAutoEmail",
            "Possible auto-send email to stakeholder",
            "BLOCKER",
            f"{path.name}",
            "Email-sending code found near stakeholder reference.",
            "Generate report → write to output/ → wait for user explicit 'send' command. "
            "Exception: pipeline-fail alert to configured oncall is OK by design.",
            "Auto-sending stakeholder report = trust-breaking incident. Confirm before send.",
        ))
    return out


# ---------------- Code Discipline ----------------

def check_code(text: str, path: Path) -> list[Finding]:
    out: list[Finding] = []
    ext = path.suffix.lower()
    if ext not in (".py",):
        return out

    # Emojis in code
    emoji_rx = re.compile(r"[\U0001F300-\U0001FAFF\U0001F000-\U0001F0FF☀-➿]")
    if emoji_rx.search(text):
        out.append(Finding(
            "Code.NoEmojis",
            "Emoji in code",
            "MEDIUM",
            f"{path.name}",
            "Emoji character(s) found in code.",
            "Remove unless user explicitly requested emojis.",
            "Emojis in code break Windows cp1252 reads + look unprofessional in production.",
        ))

    # Heavy commenting (>30% of non-blank lines starting with #)
    non_blank = [ln for ln in text.splitlines() if ln.strip()]
    comment_lines = [ln for ln in non_blank if ln.lstrip().startswith("#")]
    if non_blank and len(comment_lines) / len(non_blank) > 0.3:
        out.append(Finding(
            "Code.CommentDiscipline",
            "Over-commented code",
            "LOW",
            f"{path.name}",
            f"{len(comment_lines)}/{len(non_blank)} lines are comments (>30%).",
            "Default: no comments. Only comment WHY when non-obvious. Names should self-document.",
            "Over-commenting buries the code; reader skims comments and misses logic.",
        ))
    return out


# ---------------- Output Folder Discipline ----------------

def check_output_path(text: str, path: Path) -> list[Finding]:
    out: list[Finding] = []
    # Look for paths that write to workspace root instead of output/
    suspicious = re.findall(r"['\"]([\w\-\.]+\.(csv|html|pdf|xlsx|png|svg|pptx|docx))['\"]", text)
    # If file path doesn't have output/ prefix → flag
    flagged = [s[0] for s in suspicious if not s[0].lower().startswith(("output/", "output\\", ".output/", "tmp/", "test"))]
    if flagged:
        out.append(Finding(
            "OutputPath.Discipline",
            "Output file written outside output/",
            "MEDIUM",
            f"{path.name}",
            f"Found writes to {flagged[:3]}... (workspace root or wrong folder).",
            "Save to <your-workspace>/output/<type>/ or output/projects/<name>/. "
            "Never save generated files to workspace root.",
            "Output discipline keeps generated files separate from source — clean gitignore + handoff.",
        ))
    return out


# ---------------- Orchestrator ----------------

def audit(path: Path) -> list[Finding]:
    text = load(path)
    findings: list[Finding] = []
    findings += check_orientation(text, path)
    findings += check_baseline_noise_impact(text, path)
    findings += check_action_brief(text, path)
    findings += check_why_explanation(text, path)
    findings += check_style(text, path)
    findings += check_code(text, path)
    findings += check_output_path(text, path)
    return findings


def render_tsv(findings: list[Finding]) -> str:
    header = "rule_id\trule_name\tseverity\tlocation\twhat_missing\thow_to_fix\twhy_it_matters"
    lines = [header]
    sev_order = {s: i for i, s in enumerate(SEVERITIES)}
    findings_sorted = sorted(findings, key=lambda f: (sev_order.get(f.severity, 99), f.rule_id))
    for f in findings_sorted:
        row = "\t".join([
            f.rule_id,
            f.rule_name,
            f.severity,
            f.location,
            f.what_missing.replace("\t", " "),
            f.how_to_fix.replace("\t", " "),
            f.why_it_matters.replace("\t", " "),
        ])
        lines.append(row)
    return "\n".join(lines)


def render_json(findings: list[Finding]) -> str:
    sev_order = {s: i for i, s in enumerate(SEVERITIES)}
    findings_sorted = sorted(findings, key=lambda f: (sev_order.get(f.severity, 99), f.rule_id))
    return json.dumps([f._asdict() for f in findings_sorted], indent=2, ensure_ascii=False)


def headline_verdict(findings: list[Finding]) -> str:
    by_sev: dict[str, int] = {}
    for f in findings:
        by_sev[f.severity] = by_sev.get(f.severity, 0) + 1
    n_blocker = by_sev.get("BLOCKER", 0)
    n_high = by_sev.get("HIGH", 0)
    if n_blocker > 0:
        return f"HOLD — fix {n_blocker} BLOCKER(s) before ship. (HIGH: {n_high}, total findings: {len(findings)})"
    if n_high > 0:
        return f"SHIP-WITH-CAVEAT — {n_high} HIGH issues, queue for next polish round. (Total: {len(findings)})"
    if findings:
        return f"SHIP — {len(findings)} polish notes."
    return "SHIP — clean, all checks passed."


AUDIT_EXTENSIONS = {".md", ".markdown", ".html", ".ipynb", ".py", ".sql"}
IGNORE_DIR_NAMES = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".idea", ".vscode", "dist", "build"}


def walk_project(project_dir: Path) -> list[Path]:
    """Walk a project directory and return all auditable files."""
    files: list[Path] = []
    for p in project_dir.rglob("*"):
        if not p.is_file():
            continue
        if any(part in IGNORE_DIR_NAMES for part in p.parts):
            continue
        if p.suffix.lower() in AUDIT_EXTENSIONS:
            files.append(p)
    return sorted(files)


def audit_project(project_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    for f in walk_project(project_dir):
        rel = f.relative_to(project_dir)
        for finding in audit(f):
            # Re-anchor location to project-relative path
            findings.append(finding._replace(location=str(rel) + (":" + finding.location.split(":")[-1] if ":" in finding.location else "")))
    return findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", type=Path, nargs="?", help="Path to deliverable to audit (single-file mode)")
    ap.add_argument("--project", type=Path, help="Walk a project directory instead of single file")
    ap.add_argument("--json", action="store_true", help="Output JSON instead of TSV")
    ap.add_argument("--severity", choices=SEVERITIES, help="Filter to single severity")
    ap.add_argument("--rule", help="Filter to rule family prefix (e.g., R2 for all Rung checks)")
    args = ap.parse_args(argv)

    if args.project:
        if not args.project.is_dir():
            print(f"error: project dir not found: {args.project}", file=sys.stderr)
            return 2
        findings = audit_project(args.project)
        source = f"project={args.project}"
    elif args.file:
        if not args.file.exists():
            print(f"error: file not found: {args.file}", file=sys.stderr)
            return 2
        findings = audit(args.file)
        source = f"file={args.file}"
    else:
        ap.print_help()
        return 2

    if args.severity:
        findings = [f for f in findings if f.severity == args.severity]
    if args.rule:
        findings = [f for f in findings if f.rule_id.startswith(args.rule)]

    if args.json:
        print(render_json(findings))
    else:
        print(f"# source: {source}")
        print(f"# files audited: {len(walk_project(args.project)) if args.project else 1}")
        print(render_tsv(findings))
        print()
        print(f"# headline: {headline_verdict(findings)}")
    return 0 if not [f for f in findings if f.severity == "BLOCKER"] else 1


if __name__ == "__main__":
    sys.exit(main())
