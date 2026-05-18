# Method — Pre-Registration

> BEFORE seeing the data, write down the hypothesis, metric, exclusion criteria, analysis spec, and decision rule. Then run the analysis. Any deviation from the plan is exploratory, not confirmatory.

## Overview — Quick reference card

| Attribute | Value |
|-----------|-------|
| Type | Validation (researcher-degrees-of-freedom control) |
| Cost (compute) | Zero (a 5-15 line markdown block) |
| Prerequisite data shape | A planned analysis (not yet executed) |
| Output | A pre-registration document committed to a timestamped store (git, OSF, internal log) |
| Bundled script | None |
| Reading time | 6 minutes |
| Primary source | Open Science Framework (osf.io); Munafò et al. (2017) "A manifesto for reproducible science" |

## What — definition

Pre-registration is a written commitment to the analysis plan made before observing data. The document covers:
- The hypothesis being tested (in falsifiable form)
- The outcome metric and its aggregation
- The sample inclusion / exclusion criteria
- The statistical method
- The threshold for declaring "real" (α, MDE, decision rule)

The pre-reg is timestamped (git commit, OSF submission, internal log) so anyone reviewing later can verify what was decided BEFORE vs AFTER seeing data.

## How — step-by-step protocol

1. **Write the pre-reg BEFORE EDA**. Even a 5-line markdown cell at the top of the notebook counts.
2. **Cover the 5 essentials** (see Template below).
3. **Commit the pre-reg** to git OR submit to OSF OR log it in an internal pre-reg system. Timestamp matters.
4. **Run the analysis**.
5. **Compare result vs plan**:
   - Followed plan → confirmatory finding
   - Deviated from plan → exploratory finding (label as such, do not claim confirmatory)
6. **Document any deviation** with a Why (e.g., "data quality issue forced us to drop region X" — defensible).

## Why — Theoretical

Researcher degrees of freedom (Simmons-Nelson-Simonsohn 2011) are large enough that "we found p < 0.05" is essentially uninformative without pre-specification. Across 100 reasonable analyses of the same dataset, several will yield p < 0.05 by chance. Pre-registration locks the choices so that "we found p < 0.05" is "we made the prediction and the data agreed," not "we tried many things until something stuck."

This is theoretical-rationale: the statistical machinery (α, p-value) assumes a pre-specified test. Without pre-specification, the assumption fails and the inference is invalid.

## When — trigger conditions

**Use Pre-registration when:**
- Confirmatory analysis — you are testing a specific hypothesis
- High-stakes finding (publication, decision, hiring case submission)
- A/B test (the canonical pre-reg domain — metric and stopping rule locked)
- Multiple plausible specifications exist (pre-reg picks one)

**Skip Pre-registration when:**
- Pure exploratory analysis (no specific hypothesis; describing the data)
- Time-constrained one-off analysis where no decision rides on the result
- Already-locked plan from a previous registration; just execute

## Where — workflow stage / artifact type

- Mode: BEFORE `mode-insight` Phase 1 (Scope & Hypothesize)
- Phase: Phase 0 — written before any data is touched
- Artifact type: markdown cell at notebook top OR `pre_registration.md` file in the project folder

## Who — target roles

- **Writes the pre-reg**: Analyst running the confirmatory analysis
- **Reads the pre-reg**: Reviewer / stakeholder / future-self
- **Reviews the rigor**: Senior DA / DS in `mode-review` Sub-mode B — checks that pre-reg exists AND was actually followed

## Acceptance gate — declare confirmatory only if

1. **Pre-reg document exists** AND is timestamped before data was analyzed
2. **All 5 essentials covered**: hypothesis + outcome + sample + method + threshold
3. **Analysis follows the pre-reg** OR deviations are documented with Why
4. **Verdict in pre-reg matches verdict in final report** — if pre-reg said "if p < 0.05, conclude X; else Y," the report says X or Y, NOT a third thing
5. **For A/B tests**, stopping rule and primary outcome locked BEFORE launch (NOT mid-experiment peeking)

## Template — copy-paste starter

```markdown
# Pre-Registration — [Project Name]

**Timestamp**: 2026-05-14
**Author**: [name]
**Status**: Locked — committed before EDA on 2026-05-14 at HH:MM

## Hypothesis (falsifiable)
[Specific, directional claim. E.g., "The treatment reduces the focal outcome on the targeted segment by at least 10,000 units per user per period."]

## Outcome metric
- Definition: [outcome name + unit]
- Aggregation: [mean per user per period]
- Sample unit: [user-period]

## Sample
- Inclusion: [users in the focal segment at treatment start; active 30d pre + 30d post]
- Exclusion: [users with <5 transactions in pre-period; flagged/non-organic users]
- Date range: [2026-02-15 to 2026-04-14]

## Method
- Statistical test: [DiD with clustered SE at user level]
- Identifying assumption: [parallel trends — to be tested on pre-period]
- Robustness: [drop top 1% outliers; alt outcome = event count]
- Falsification: [DiD placebo on pre-pre vs pre]

## Decision rule
- IF DiD coefficient ≤ −10,000 AND p < 0.05 AND parallel-trends p > 0.10 → conclude "treatment effective, recommend rollout"
- IF DiD coefficient > −10,000 OR p ≥ 0.05 OR parallel-trends fails → conclude "treatment ineffective at MDE, do not roll out"

## Multiple testing
- K = 1 primary outcome. Secondary outcomes (event count, related KPIs) are labeled exploratory.
```

## Worked example — campaign pre-registration

A treatment-effect study used this pre-registration committed at 2026-03-10, before data was pulled:

- Hypothesis: treatment reduces focal outcome on the targeted segment by ≥ 10,000 units / user / period
- Outcome: focal outcome amount, mean per user-period
- Sample: targeted segment, active 30d pre + 30d post, exclude flagged users
- Method: DiD with clustered SE; parallel-trends test
- Decision rule: ≤ −10,000 AND p<0.05 AND PT p>0.10 → effective; else not

Result: DiD = −18,500 (CI: −24,200 to −12,800), p < 0.001, PT p = 0.34 → CONFIRMATORY: "treatment effective, recommend rollout."

If instead DiD had been −5,000 with p < 0.05, the verdict would have been "ineffective at MDE, do not roll out" — even though p < 0.05. The pre-reg locked the MDE-based decision rule, not just a p-value.

## Anti-patterns

- **Writing the pre-reg AFTER looking at data.** Defeats the purpose. Pre-reg must be timestamped before EDA.
- **Pre-reg is vague.** "I will analyze whether X relates to Y" is not a pre-reg. Falsifiable, specific, directional.
- **Pre-reg doesn't include decision rule.** "I will report p-value" is not a decision rule. The rule says what to do GIVEN the p-value.
- **Deviating without documenting.** "We added a control variable" without explanation makes it impossible to tell whether it was a sensible adaptation or motivated reasoning.
- **Calling exploratory work "pre-registered."** Pre-reg means specific advance commitment. Exploratory work is legitimate but should be labeled as such.

## Cross-references

- **Required prereq method**: none (pre-reg is itself the prereq for confirmatory analysis)
- **Complementary methods**: `methods/multiple_testing.md` (locking K beforehand simplifies correction); `methods/robustness_checks.md` (pre-reg locked specs, robustness adds exploratory alternates labeled clearly)
- **Alternative methods**: replication on independent dataset (also strong; complementary not alternative)
- **Bundled scripts**: None
- **Decision-table parent**: `references/validation-evaluation-methods.md`

## Reading order

1. THIS file
2. `references/validation-evaluation-methods.md` §8
3. Primary sources: Munafò et al. (2017) Nature Human Behaviour; Simmons-Nelson-Simonsohn (2011) "False-Positive Psychology"
