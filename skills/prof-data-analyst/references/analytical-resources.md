# External Analytical Resources (User-Configurable Pointers)

This skill does NOT bundle textbooks or full analytical frameworks. Instead, it points to the **kind** of resource you should keep accessible in your workspace.

**All paths below are EXAMPLES.** Substitute the equivalent location in your workspace. The skill's value is the workflow + scripts; the analytical foundations live wherever you curate them.

## Convention used in this file

Throughout: `<your-workspace>` = root of your working directory (e.g., `~/projects/data-analytics/`, `D:\work\`, `/home/<you>/code/`). `<your-reference-dir>` = wherever you keep curated analytical docs / PDFs / notebooks. If you don't have these layouts yet, the skill still works — just call the bundled scripts in `scripts/` for stats / formatting / validators.

## Statistical Inference

| Kind of resource | Example local path | When to read |
|------------------|--------------------|--------------|
| Statistical inference cheat sheet (distribution → SD → SE → CI → effect size → MDE → OLS → CV) | `<your-reference-dir>/statistic-abtest/statistical_inference_cheat_sheet.md` | New product / feature with no historical data |
| A/B testing playbook (production + academic) | `<your-reference-dir>/statistic-abtest/abtest-full.md` | Designing or analyzing an A/B test — unit of analysis, mean/SD/SE, p-value, CI, MDE, power, gotchas |
| T-test code patterns | `<your-reference-dir>/statistic-abtest/T_test_code.ipynb` | Reproducible t-test examples |
| A/B testing notebook | `<your-reference-dir>/statistic-abtest/A_B_Testing.ipynb` | End-to-end A/B test in Jupyter |
| OLS regression notebook | `<your-reference-dir>/statistic-abtest/regression.ipynb` | Regression patterns |

Bundled scripts in this skill (`scripts/stats/`) implement the FORMULAS from these references. Call the scripts; treat the references as the textbook.

## Analytic Frameworks (visual references)

| Framework | Example local path | When to read |
|-----------|--------------------|--------------|
| AARRR (pirate metrics) | `<your-reference-dir>/analytic-framework/AARRR.jpg` | User-journey funnel — Acquisition / Activation / Retention / Referral / Revenue |
| Growth Loop | `<your-reference-dir>/analytic-framework/growthloop.jpg` | Compounding growth mechanisms (input → action → output → re-input) |
| Logic Tree | `<your-reference-dir>/analytic-framework/logic-tree.jpg` | Decomposing a vague business question into measurable sub-questions |
| North Star Metric | `<your-reference-dir>/analytic-framework/northstar.jpg` | Picking the single metric that aligns the organization |
| One Metric That Matters (OMTM) | `<your-reference-dir>/analytic-framework/one-metric-that-matters.jpg` | Stage-appropriate single-metric focus |
| Framework comparison overview | `<your-reference-dir>/analytic-framework/overview4framework.jpg` | Pick AARRR vs Growth Loop vs Logic Tree vs OMTM |
| Anomaly + problem-solving | `<your-reference-dir>/analytic-framework/anomaly_problem_solving.pdf` | Diagnostic flow when a metric anomalies |

If your workspace doesn't have these, they are widely available online (search the framework name).

## Segmentation

| Kind of resource | Example local path |
|------------------|--------------------|
| Segmentation framework | `<your-reference-dir>/segmentation/segmentation-framework.pdf` |

When to use: classifying users by behavior / value / lifecycle stage.

## Visualization

| Kind of resource | Example local path |
|------------------|--------------------|
| Standard chart design guide | `<your-reference-dir>/viz/chart-design-standards.jpg` |

When to use: picking the right chart type for the data + audience.

## Math / Stats / Probability (textbooks)

| Topic | Example local path |
|-------|--------------------|
| Data Science / ML course (general) | `<your-reference-dir>/math-stats/data-science-ml-course.pdf` |
| Essential Math for DS / ML / DL | `<your-reference-dir>/math-stats/essential-math-for-ds.pdf` |
| Essential Math exercises | `<your-reference-dir>/math-stats/essential-math-exercises.pdf` |

Use as foundational reference (probability theory, linear algebra, optimization). Read targeted chapters — don't dump entire content into context.

## Agentic NL→SQL Architecture (optional, for query mode)

| Kind of resource | Example local path |
|------------------|--------------------|
| Agentic NL→SQL SPEC (ReAct loop + semantic layer + guardrails) | `<your-reference-dir>/agentic-sql-spec.md` |

The `mode-query.md` in this skill adopts the **pattern** (RECALL→EXPLORE→LEARN, ReAct loop with guardrails, semantic-first). Read your equivalent SPEC when implementing the full architecture.

## When To Read Which

```
Designing a metric for a new product
  → North Star + OMTM (analytic-framework)
  → Then statistical inference cheat sheet for variability estimation

Diagnosing a metric drop
  → Anomaly + problem-solving framework
  → Then mode-insight.md (this skill)

Designing an A/B test
  → A/B testing playbook
  → Then scripts/stats/mde_sample_size.py to size it

User behavior segmentation
  → Segmentation framework
  → Then mode-process.md (this skill) for the DWH layered tables pattern

Building an internal NL→SQL tool
  → Your agentic-sql SPEC (architecture)
  → mode-query.md (this skill, engine-agnostic adaptation)

Picking a chart for a report
  → Chart design standards
  → Then style-rules.md (this skill) for AI-tell scrub + brand theme application
```

## If You Don't Have These References Yet

The skill works **without** any external references. The bundled `scripts/` folder covers the operational computations (stats, formatting, validators). External references are for DEEPER understanding when you want to study the foundation rather than just apply the formula.

**Minimum viable setup:** clone this skill, run scripts directly. Add reference docs to your workspace over time as you encounter topics deserving deeper study.

## Refresh Policy

These external references are user-curated. They are NOT loaded into the skill — only referenced by path convention. When your workspace layout changes, update YOUR copy of this file to match. The skill itself ships only the patterns + scripts; analytical foundations stay where humans can curate them without skill versioning overhead.
