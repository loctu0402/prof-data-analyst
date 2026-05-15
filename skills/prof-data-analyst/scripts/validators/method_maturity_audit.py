#!/usr/bin/env python3
"""Method Maturity Audit — heuristic check for method-vs-claim mismatch + validation gaps.

Scans project files for:
  1. Claim keywords (causal language: "caused", "drove", "X led to Y", "impact of X on Y")
  2. Method keywords (DiD, Pearson, regression, PSM, IV, t-test, Event Study, RDD, Synthetic Control)
  3. Validation keywords (bootstrap, robustness, sensitivity, falsification, parallel trends,
     multiple testing, Bonferroni, BH-FDR, pre-registration)

Then surfaces findings:
  - Method mismatch: causal claim made but only correlation method used → suggest causal toolkit method
  - Falsification missing: causal method used but no falsification test mentioned
  - Validation gap: method used but no validation stacking detected
  - Advanced-method opportunity: pattern suggests a more advanced method would strengthen the claim

This is HEURISTIC. Output is a recommendation list, not a hard-block diagnostic. Use as Pass 3
of Sub-mode B (Full Project Refine) in mode-review.

Usage:
  python method_maturity_audit.py <project-dir>
  python method_maturity_audit.py <project-dir> --json
  python method_maturity_audit.py <project-dir> --severity HIGH

Pure stdlib.

Why heuristic — semantic check (is THIS method appropriate for THIS question?) needs human
judgment. Script surfaces signals; auditor (or LLM-agent) decides. Codes the decision-table
from causal-inference-toolkit.md as keyword patterns so the human pass is informed, not blank.

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
AUDIT_EXTENSIONS = {".md", ".markdown", ".html", ".ipynb", ".py", ".sql"}
IGNORE_DIR_NAMES = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".idea", ".vscode", "dist", "build"}


# Keyword patterns ----

CAUSAL_CLAIM_PATTERNS = [
    r"\b(caused|gây ra|dẫn đến|do)\b",
    r"\b(led to|drove|drives|driving)\b",
    r"\b(impact of|effect of|tác động của|ảnh hưởng của)\b",
    r"\b(because of|do bởi|nhờ vào)\b",
    r"\b(attributable to|nguyên nhân là)\b",
]

CORRELATION_METHOD_KEYWORDS = ["pearson", "correlation", "tương quan", "spearman", "kendall", "r ="]

CAUSAL_METHOD_KEYWORDS = {
    "DiD": ["difference-in-difference", "difference in difference", "DiD ", "diff-in-diff", "diff in diff"],
    "Event Study": ["event study", "event-study"],
    "RDD": ["regression discontinuity", "RDD ", "discontinuity design"],
    "Synthetic Control": ["synthetic control", "synth-control"],
    "PSM": ["propensity score", "PSM ", "matching"],
    "IV": ["instrumental variable", "instrument variable", "2SLS", "two-stage least square"],
}

FALSIFICATION_KEYWORDS = {
    "DiD": ["parallel trend", "parallel-trend", "pre-trend test", "leads"],
    "Event Study": ["parallel trend", "pre-event lead"],
    "RDD": ["mccrary", "density test", "covariate balance"],
    "Synthetic Control": ["placebo", "in-space placebo", "donor permutation"],
    "PSM": ["covariate balance", "rosenbaum", "sensitivity"],
    "IV": ["first-stage F", "first stage f", "overidentification", "j-test"],
}

VALIDATION_KEYWORDS = {
    "bootstrap": ["bootstrap", "resampling", "percentile method"],
    "robustness": ["robustness check", "robustness test", "alternative specification", "sub-sample"],
    "sensitivity": ["sensitivity analysis", "bandwidth sensitivity", "parameter sensitivity"],
    "multi_test": ["bonferroni", "benjamini-hochberg", "bh-fdr", "fdr correction", "multiple testing"],
    "pre_reg": ["pre-registration", "pre-registered", "locked plan", "stopping rule"],
    "cross_val": ["cross-validation", "cross-val", "k-fold", "k fold"],
}

HEAVY_TAIL_HINT_KEYWORDS = ["heavy tail", "heavy-tail", "skewed", "median ≈ 0", "long tail", "outlier-driven"]

SHARP_CUTOFF_HINT_KEYWORDS = ["cutoff", "threshold-based", "if balance >=", "qualifies if", "discrete cutoff"]

STAGGERED_HINT_KEYWORDS = ["staggered", "rollout", "rolled out over", "different launch dates"]


class Finding(NamedTuple):
    rule_id: str
    rule_name: str
    severity: str
    location: str
    what_missing: str
    how_to_fix: str
    why_it_matters: str


# Helpers ----

def walk_project(project_dir: Path) -> list[Path]:
    files: list[Path] = []
    for p in project_dir.rglob("*"):
        if not p.is_file():
            continue
        if any(part in IGNORE_DIR_NAMES for part in p.parts):
            continue
        if p.suffix.lower() in AUDIT_EXTENSIONS:
            files.append(p)
    return sorted(files)


def load_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def has_any(text: str, patterns: list[str], flags: int = re.I) -> bool:
    for pat in patterns:
        if re.search(pat, text, flags):
            return True
    return False


def find_method_used(text: str) -> set[str]:
    used = set()
    for method, kws in CAUSAL_METHOD_KEYWORDS.items():
        if has_any(text, kws):
            used.add(method)
    return used


def find_correlation_used(text: str) -> bool:
    return has_any(text, CORRELATION_METHOD_KEYWORDS)


def find_validation_used(text: str) -> set[str]:
    used = set()
    for tag, kws in VALIDATION_KEYWORDS.items():
        if has_any(text, kws):
            used.add(tag)
    return used


def find_falsification_used(text: str, method: str) -> bool:
    return has_any(text, FALSIFICATION_KEYWORDS.get(method, []))


# Audit passes ----

def audit_method_vs_claim(text: str, rel: str) -> list[Finding]:
    out: list[Finding] = []
    has_causal_claim = has_any(text, CAUSAL_CLAIM_PATTERNS)
    methods_used = find_method_used(text)
    used_correlation = find_correlation_used(text)

    if has_causal_claim and not methods_used and used_correlation:
        out.append(Finding(
            "M1.CausalMismatch",
            "Causal claim with only correlation method",
            "BLOCKER",
            rel,
            "Text contains causal language (caused / led to / impact of) but only correlation methods (Pearson / Spearman / r =) detected. "
            "Correlation is not causation — claim is not identified.",
            "Either downgrade language to 'X is associated with Y' (correlation only), OR upgrade method per "
            "causal-inference-toolkit.md decision table (DiD / RDD / Synthetic Control / PSM / IV based on data setup).",
            "Stakeholder distrust scales on unsupported causal claims; one over-claim contaminates other findings.",
        ))

    if has_causal_claim and not methods_used and not used_correlation:
        out.append(Finding(
            "M1.CausalMismatch",
            "Causal claim with no method evidence",
            "HIGH",
            rel,
            "Text contains causal language but no method (causal or correlation) detected in the same file. "
            "Either method is undocumented or claim is unsupported.",
            "Document the method used inline near the claim, OR if no method was run, downgrade to descriptive language.",
            "An undocumented method cannot be audited or reproduced.",
        ))

    return out


def audit_falsification(text: str, rel: str) -> list[Finding]:
    out: list[Finding] = []
    methods_used = find_method_used(text)
    for method in methods_used:
        if not find_falsification_used(text, method):
            falsification_examples = FALSIFICATION_KEYWORDS.get(method, [])
            example = falsification_examples[0] if falsification_examples else "appropriate falsification test"
            out.append(Finding(
                "M2.FalsificationMissing",
                f"{method} used without falsification",
                "HIGH",
                rel,
                f"Method {method} detected but no falsification test mentioned (expected: {example} or similar).",
                f"Run the falsification test appropriate to {method}. See causal-inference-toolkit.md §relevant section. "
                f"For DiD/Event Study: scripts/causal/parallel_trends_test.py.",
                f"{method} requires a specific assumption check. Without it, the causal estimate is unidentified.",
            ))
    return out


def audit_validation_stacking(text: str, rel: str) -> list[Finding]:
    out: list[Finding] = []
    methods_used = find_method_used(text)
    correlation_used = find_correlation_used(text)
    if not (methods_used or correlation_used):
        return out
    validation_used = find_validation_used(text)
    missing = []
    if "bootstrap" not in validation_used:
        missing.append("bootstrap")
    if "robustness" not in validation_used:
        missing.append("robustness")
    if "multi_test" not in validation_used and re.search(r"\bp\s*[<=]\s*0\.\d+", text):
        # only flag multiple-testing if multiple p-values are visible
        if len(re.findall(r"\bp\s*[<=]\s*0\.\d+", text)) > 1:
            missing.append("multi_test")

    if len(missing) >= 2:
        suggestions = {
            "bootstrap": "scripts/stats/bootstrap_ci.py for non-parametric CI",
            "robustness": "Re-run analysis on 3 alternative specs (subsample / control / functional form); sign should hold",
            "multi_test": "scripts/stats/multiple_testing.py for Bonferroni or BH-FDR correction",
        }
        fix_lines = [f"  - {m}: {suggestions[m]}" for m in missing]
        out.append(Finding(
            "M3.ValidationGap",
            "Validation stacking insufficient",
            "HIGH",
            rel,
            f"Analysis uses statistical method(s) but missing validation: {', '.join(missing)}.",
            "Add missing validation steps:\n" + "\n".join(fix_lines),
            "No single test confirms a finding. Stacking validates the headline against sampling / specification / multiple-testing failure modes.",
        ))
    return out


def audit_advanced_opportunities(text: str, rel: str) -> list[Finding]:
    out: list[Finding] = []

    if has_any(text, HEAVY_TAIL_HINT_KEYWORDS):
        if "DiD" in find_method_used(text) and not re.search(r"\bwilcoxon|winsoriz|median[ -]?diff\b", text, re.I):
            out.append(Finding(
                "M4.AdvancedOpportunity",
                "Heavy-tail outcome — consider median-Δ + Wilcoxon",
                "MEDIUM",
                rel,
                "Heavy-tail hint detected alongside DiD on mean. Mean-DiD loses 3-5× power on skewed outcomes.",
                "Switch to Wilcoxon signed-rank + winsorize top-1% + median Δ. Recovers power; reports median treatment effect.",
                "Empirical lesson from heavy-tail incident: cashout/GMV-style outcomes have median ≈ 0; mean is dominated by tails.",
            ))

    if has_any(text, STAGGERED_HINT_KEYWORDS) and "DiD" in find_method_used(text):
        out.append(Finding(
            "M4.AdvancedOpportunity",
            "Staggered DiD — consider Callaway-Sant'Anna or Sun-Abraham",
            "MEDIUM",
            rel,
            "Staggered treatment hint detected with DiD. Two-way fixed-effects (TWFE) DiD is biased under staggered timing.",
            "Use Callaway-Sant'Anna or Sun-Abraham estimator (R: `did` package, Python: `differences` lib). "
            "Beyond stdlib — note in deliverable that TWFE is the current method and migration is the upgrade path.",
            "Goodman-Bacon (2021) decomposition shows TWFE bias on staggered designs; effect can flip sign in extreme cases.",
        ))

    if has_any(text, SHARP_CUTOFF_HINT_KEYWORDS) and not ("RDD" in find_method_used(text) or "synthetic" in text.lower()):
        out.append(Finding(
            "M4.AdvancedOpportunity",
            "Sharp cutoff — consider RDD",
            "MEDIUM",
            rel,
            "Sharp-cutoff hint detected (qualifies-if / threshold-based) but no RDD method in use.",
            "If treatment is genuinely assigned by a cutoff on a running variable, RDD is the credible identification strategy. "
            "See causal-inference-toolkit.md §3 (RDD).",
            "RDD is among the most credible designs when the cutoff is natural and units cannot precisely manipulate the running variable.",
        ))

    return out


def audit_project(project_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    for f in walk_project(project_dir):
        text = load_text(f)
        if not text.strip():
            continue
        rel = str(f.relative_to(project_dir))
        findings += audit_method_vs_claim(text, rel)
        findings += audit_falsification(text, rel)
        findings += audit_validation_stacking(text, rel)
        findings += audit_advanced_opportunities(text, rel)
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
            f.what_missing.replace("\t", " ").replace("\n", " | "),
            f.how_to_fix.replace("\t", " ").replace("\n", " | "),
            f.why_it_matters.replace("\t", " ").replace("\n", " | "),
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
        return f"METHOD-BLOCKER — {n_blocker} causal-claim/method mismatch(es); fix before ship. (HIGH: {n_high}, total: {len(findings)})"
    if n_high > 0:
        return f"METHOD-WEAK — {n_high} validation/falsification gap(s); strengthen before claiming confirmed. (Total: {len(findings)})"
    if findings:
        return f"METHOD-OK — {len(findings)} advanced-method opportunity note(s)."
    return "METHOD-OK — no method maturity gap detected by heuristics."


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", type=Path, help="Project directory to audit")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--severity", choices=SEVERITIES)
    args = ap.parse_args(argv)

    if not args.project.exists():
        print(f"[ERROR] Path does not exist: {args.project}", file=sys.stderr)
        print(f"        Pass the project ROOT FOLDER (e.g. ./output/projects/my-case/), not a file.", file=sys.stderr)
        return 2
    if args.project.is_file():
        print(f"[ERROR] '{args.project}' is a file, not a directory.", file=sys.stderr)
        print(f"        method_maturity_audit walks a project folder. Pass the folder containing your", file=sys.stderr)
        print(f"        notebook / SQL / report files, not an individual file.", file=sys.stderr)
        print(f"        Example: python method_maturity_audit.py ./output/projects/ttt-deep-dive/", file=sys.stderr)
        return 2
    if not args.project.is_dir():
        print(f"[ERROR] '{args.project}' is not a directory. Pass the project root folder.", file=sys.stderr)
        return 2

    findings = audit_project(args.project)
    if args.severity:
        findings = [f for f in findings if f.severity == args.severity]

    if args.json:
        print(render_json(findings))
    else:
        print(f"# project: {args.project}")
        print(f"# files scanned: {len(walk_project(args.project))}")
        print(render_tsv(findings))
        print()
        print(f"# headline: {headline_verdict(findings)}")

    return 0 if not [f for f in findings if f.severity == "BLOCKER"] else 1


if __name__ == "__main__":
    sys.exit(main())
