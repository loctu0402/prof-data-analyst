# Method Spec Template

## Overview

This template is the canonical structure for every method spec under `references/methods/`. Each method spec MUST follow these section headings in order. The headings ARE the story — a reader scanning only the heading list should be able to predict what each section contains. That is the Outline / Story Flow Check self-applied to the template itself.

## When to use this template

- Adding a new method to the skill (causal inference family / validation family / new family)
- Refactoring a deep-dive section out of `causal-inference-toolkit.md` or `validation-evaluation-methods.md`
- Documenting a stats / ML method that the analyst will execute repeatedly

DO NOT use this template for:
- Universal workflow rules (use `references/universal-workflow-rules.md` format)
- Mode-specific reference files (use `references/mode-<name>.md` format)
- One-off knowledge memories (use `feedback_*.md` / `knowledge_*.md` in auto-memory)

## Required section structure (in this order)

```markdown
# Method — <Name>

> One-line plain-language summary. Reader scanning the index sees this first.

## Overview — Quick reference card

| Attribute | Value |
|-----------|-------|
| Type | <causal / validation / descriptive / predictive> |
| Cost (compute) | <free / cheap / medium / expensive> |
| Prerequisite data shape | <e.g., panel data with treated+control+pre+post> |
| Output | <e.g., point estimate + CI + falsification verdict> |
| Bundled script | `scripts/<family>/<name>.py` (if present) |
| Reading time | <5 / 10 / 15 minutes> |
| Primary source | <Angrist-Pischke 2009 / Imbens-Rubin 2015 / Efron-Tibshirani 1993 / ...> |

## What — definition

2-3 sentences. Plain language. No formulas in this section. A non-statistician should understand what the method DOES, not how it computes.

## How — step-by-step protocol

Numbered steps. Each step has:
1. The action (1 sentence)
2. The output of the action (1 sentence)
3. Code snippet (if a bundled script exists, show the invocation; otherwise show the manual code)

Example skeleton:
1. <Action> → produces <X>. `python scripts/<family>/<name>.py --arg ...`
2. <Action> → produces <Y>. (Manual: `import statsmodels...`)
3. <Action> → produces <Z>.

## Why — Causal / Empirical / Comparative / Theoretical / Operational

This is the Rule 4 Why-Explanation applied to the method itself. Answer ONE of the five rationale types in 2-4 sentences:

- **Causal** — the method exists because <causal mechanism it identifies>
- **Empirical** — the method exists because <empirical pattern it captures or corrects>
- **Comparative** — the method exists because it solves the same problem as <alternative> with <better property>
- **Theoretical** — the method exists because <statistical theorem or assumption it relies on>
- **Operational** — the method exists because <practical constraint of real workflows>

The Why is NOT a restatement of "How" — it justifies WHY this method, not what the method does.

## When — trigger conditions

When to USE this method:
- <condition 1, with concrete signal>
- <condition 2>
- <condition 3>

When to SKIP this method (use an alternative):
- <condition 1, with the alternative named>
- <condition 2, with alternative>

## Where — workflow stage / artifact type

In the 7-mode workflow, this method appears at:
- Mode: <query / process / insight / report / review / etc.>
- Phase: <which phase number, e.g., Phase 4 of mode-insight>
- Artifact type: <notebook cell / report section / dashboard panel>

## Who — target roles

- **Runs the method**: <analyst persona, e.g., "DA mid-level comfortable with statsmodels">
- **Reads the output**: <stakeholder persona, e.g., "PM reviewing causal claim before greenlight">
- **Reviews the rigor**: <reviewer persona, e.g., "senior DA / DS in Pass 3 of mode-review">

## Acceptance gate — declare "done" only if

Numbered checklist. Method-specific:
1. <criterion> — e.g., "parallel-trends test p > 0.10"
2. <criterion>
3. <criterion>
4. <criterion>

If any criterion fails, the finding is NOT confirmed. Either re-run with adjusted spec, or downgrade the claim from causal to correlational.

## Template — copy-paste starter

Concrete starter code / SQL / notebook cell, ready to paste into a real project:

```python
# Method: <name>
# Source: <ref>
# Acceptance: <numbered list summarized>

# [Code block]
```

This template is the LOWEST-friction entry point for the analyst — they should be able to paste, swap their data path, and run.

## Worked example — end-to-end walkthrough

A real-or-realistic 100-300 line example showing:
- The data setup (synthetic or real reference dataset)
- The method invocation
- The output interpretation
- The acceptance gate evaluation
- The narrative paragraph that goes into the final report

Walkthrough should NOT be self-correcting prose ("we made an error and fixed it") — the agent reads this as a guide, not a story. Just the clean end-to-end.

## Anti-patterns — what NOT to do

Bullet list of common mistakes specific to THIS method:
- Anti-pattern 1 + why it fails + correct alternative
- Anti-pattern 2 + why it fails + correct alternative
- Anti-pattern 3 + why it fails + correct alternative

These are different from "When to skip" — anti-patterns are USING the method incorrectly, not failing to use it.

## Cross-references — related methods + scripts

- **Required prereq method**: <e.g., parallel-trends test before DiD>
- **Complementary methods**: <e.g., robustness checks after DiD>
- **Alternative methods**: <e.g., Event Study for multi-period; Synthetic Control for single treated unit>
- **Bundled scripts**: `scripts/<family>/<name>.py`
- **Decision-table parent**: `references/causal-inference-toolkit.md` or `references/validation-evaluation-methods.md`

## Reading order — load these in this order

For a new analyst encountering this method:
1. <this file>
2. <prereq method file, if any>
3. <related script's CLI reference in `scripts-guide.md`>
4. <primary source citation>
```

## Self-applied outline check

The template's heading list above IS the story:
- Overview → What → How → Why → When → Where → Who → Acceptance → Template → Example → Anti-patterns → Cross-refs → Reading order

A reader scanning ONLY these headings should be able to predict what each section contains. If you write a method spec and find yourself needing to add a section outside this list, ask: is it a new universal heading (then update THIS template) or is it specific to one method (then move it to "Anti-patterns" or "Worked example")?

## Why this template exists (meta — Rule 4)

Without a template, every method gets a slightly different layout — readers cannot scan across methods, comparison tables break, the index file's per-method summaries diverge. The template costs ~80 lines of structure; it buys 14 specs that read like sibling chapters.

The template is also the gate against the "agent invents process on the spot" failure: forcing the analyst (or the agent writing the spec) to fill 12 named sections produces consistent specs even when the author is unsure about one specific section. Empty sections are visible; missing-but-needed sections are invisible.

## Validators

After writing a method spec following this template:
1. `python scripts/validators/rubric_audit.py <path-to-spec>` — should pass orientation + Rule 4 Why checks
2. Run the Outline / Story Flow Check on the spec: extract its headings standalone, ask "does this match the template heading list?" — if yes, the spec is structurally correct
3. Cross-check that the primary source named in Overview actually defines the method as described in What

If any validator fails, the spec is not ready to ship.
