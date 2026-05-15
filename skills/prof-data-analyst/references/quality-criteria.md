# 5 Quality Criteria Framework

> Every deliverable that ships from this skill MUST pass 5 criteria. A deliverable that passes 4/5 is still rejected — the criteria are interlocked.

## Overview — Why this file exists

Loc's earlier review work surfaced a recurring failure: deliverables passed individual rules (orientation present, numbers right, charts themed) yet still felt incoherent at the whole-artifact level. The 5 criteria below give a single, named test that catches whole-artifact failures the per-rule checks miss.

## Outline (story-flow check passes)

1. The five criteria, named (Interconnect / Compact / Insightful / Sufficient / Logical Reason)
2. How to test each criterion (pass / fail signal)
3. Gate placement — when in the workflow each criterion is checked
4. Anti-patterns (deliverables that pass 4/5 and still fail)

A reader scanning the headings should be able to predict each criterion's test.

---

## 1. Interconnect — every part references its neighbors

**Definition:** Sections, charts, and findings reference each other. The reader does not encounter an orphan section that floats with no connection to what came before or after.

**Pass signal:** Every body section has either (a) "this follows from §X" or (b) "this sets up §Y" or both. Charts referenced inline by section heading, not only by figure number.

**Fail signal:** Section 4 introduces a new metric never mentioned in §1-3, and §5 never references §4 again. Or: charts appear with no callout in prose.

**Why (Empirical):** Stakeholder readers skim. An orphan section is the section they skip — and if it carried the key finding, the report fails its primary job.

## 2. Compact — every line earns its place

**Definition:** No filler. Every sentence either reveals new information or links two pieces the reader needs to connect. Cut adjectives, throat-clearing, and meta-commentary about the analysis.

**Pass signal:** A reader can quote any random sentence and explain why it is in the report.

**Fail signal:** "This analysis aims to provide a comprehensive view of..." — pure filler. Or: a sentence that restates the section heading.

**Why (Operational):** Stakeholders read in 5-10 minutes. Padding pushes the actual findings off the screen.

## 3. Insightful — at least one non-obvious finding per major section

**Definition:** The report surfaces something a stakeholder could NOT have inferred from the metric name alone. "GMV down 5%" is data; "GMV down 5% concentrated in tier 3 because of a holiday calendar shift" is insight.

**Pass signal:** Each H2 section has at least one sentence that surprises the reader, or names a mechanism / driver / segment effect that was not obvious.

**Fail signal:** Every section restates the chart title in prose. Or: the entire report could be replaced by a dashboard.

**Why (Theoretical):** The Connect-the-Dots rule (Fact → Mechanism → Behavior → Impact → Evidence) operationalizes this. A section with only the Fact rung is not insightful.

## 4. Sufficient — every claim has the evidence chain attached

**Definition:** For every finding, the report exposes (a) the data slice the finding came from, (b) the test that ruled out noise, (c) the impact verdict. No "trust me" findings.

**Pass signal:** Every numeric claim passes Rule 2's Baseline-Noise-Impact ladder visible to the reader, not just performed by the analyst.

**Fail signal:** "Conversion dropped" with no baseline comparison shown. Or: a p-value cited but no effect size.

**Why (Causal):** Stakeholders question findings only when they cannot follow the chain. Exposing the chain shortcuts the back-and-forth.

## 5. Logical Reason — the order of sections matches the question's logic

**Definition:** Section order reflects how a reasonable analyst would explore the question. Setup → Observation → Diagnostic → Decision. Not: Decision → Setup → Observation → Diagnostic.

**Pass signal:** Reading section headings in order tells the same story as reading the body.

**Fail signal:** "Recommendations" appears before "Analysis." Or: the report opens with a methodology dump and the headline finding is in §6.

**Why (Comparative):** Compare to a debugging session — you do not jump to "fix" before stating "what broke." Reports follow the same logic. This is the Outline / Story Flow Check applied at gate time.

---

## When to check (gate placement)

Run the 5-criterion check at exactly TWO points:

1. **Self-check before review.** After drafting, before invoking `/da-review`. Catches obvious orphan sections.
2. **Review-gate.** First pass in `/da-review` Sub-mode A or Sub-mode B. The review pass starts by listing the 5 criteria and ruling each pass/fail with one line of evidence.

Do NOT run inline during drafting — premature criterion-checking kills drafting flow. The criteria are a gate, not a guide.

## Anti-patterns (deliverables that pass 4/5 and still fail)

| 4/5 pattern | What is missing | Why it still fails |
|-------------|-----------------|--------------------|
| Interconnect + Compact + Sufficient + Logical, no Insight | All "describe what happened" sections | Stakeholder reads, then asks "so what?" — the report does not answer |
| Compact + Insight + Sufficient + Logical, no Interconnect | Standalone-good sections, no narrative arc | Reader cannot summarize the report in one sentence |
| Interconnect + Insight + Sufficient + Logical, not Compact | Twice as long as needed | Skimmed; insights buried |
| Interconnect + Compact + Insight + Logical, not Sufficient | Findings unsupported | Stakeholder doubts → cycle of back-and-forth |
| Interconnect + Compact + Insight + Sufficient, not Logical | Right content, wrong order | Reader exits before the conclusion |

A 5/5 deliverable is short, every section refers to its neighbors, each section has a non-obvious finding backed by visible evidence, and the order matches the question.

## Cross-references

- Outline / Story Flow Check (gate for criterion 5) → `self-check-protocol.md` Section A2.
- Connect-the-Dots reasoning (gate for criterion 3) → `mode-insight.md`.
- Baseline-Noise-Impact ladder (gate for criterion 4) → `universal-workflow-rules.md` Rule 2.
- 5-Gate Quality Pipeline (where this lives in workflow) → `quality-pipeline.md`.

## Why this rule exists (Rule 4 meta-application)

Without a whole-artifact quality check, per-rule passes accumulate without composing into a coherent deliverable. The 5 criteria force the analyst to evaluate at the same level the reader will — whole-artifact, not line-by-line.
