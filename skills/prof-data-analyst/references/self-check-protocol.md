# Self-Check Protocol (Pre-Ship)

Before declaring ANY deliverable done, walk through this checklist. Stop at the first ✗ — fix before continuing.

## Section A — Orientation & Structure

- [ ] Orientation Block present at top (SCQR / 3-line intro / module docstring)
- [ ] Terminology Block added if any complex / niche / multi-meaning term appears
- [ ] "How to read" guide added if artifact is non-text (chart-heavy / multi-tab / JSON / HTML SPA)
- [ ] Section ordering logical (Orientation → Body → Recommendations → Appendix)

## Section A2 — Outline / Story Flow Check (entire deliverable)

DISTINCT from Section A. Section A checks the OPENING; Section A2 checks the WHOLE-DELIVERABLE structure.

Procedure:
1. Extract ALL headings + sub-headings + 1-line section summaries (grep `^#{1,6}` for markdown, `<h1>-<h6>` for HTML, slide titles + speaker-note 1-liner for decks).
2. Read THAT outline standalone — DO NOT read body content.
3. Ask three questions and mark a verdict per:
   - [ ] **Big-picture**: with outline-only info, does the reader see the overall story?
   - [ ] **Logic flow**: is the heading order coherent? Any "why is this section here?" gap?
   - [ ] **Step-traceability**: can the reader trace each project step from headings alone?
4. If ANY question fails → fix is at the STRUCTURE level (heading naming / section order / missing bridge sections), NOT body-patching.

Why this check is mandatory — stakeholder readers skim headings before deciding to read body. Bad outline = bounce even when body excellent. Past incident: TymeX case study draft caught M3 placed mid-sequence with non-self-explanatory heading; fix was rename + reorder, not body rewrite.

Distinct from neighboring checks:
- Section A (Orientation) — only the opening block.
- Connect-the-Dots (Section C) — per-finding reasoning chain.
- Numerical consistency (Section D) — number reconciliation across cards.
- Outline check (this section) — macro narrative across the whole deliverable.

## Section B — Numerical Rigor (Baseline-Noise-Impact Ladder)

For EVERY headline number:
- [ ] Rung 1: baseline stated (DoD / WoW / MoM / YoY / canonical / KVBD expected)
- [ ] Rung 2: noise check provided (CI / p-value / effect size / z-score)
- [ ] Rung 3: business-impact verdict (negligible / small / medium / large) + quantified in business terms

## Section C — Reasoning Chain

For EVERY finding:
- [ ] 5-stage chain present: Fact → Mechanism → Behavior → Product Impact → Evidence
- [ ] No state-the-fact alone
- [ ] No label glue implying causation ("X = 0.98 · Ngày 5 payday" — BAN)
- [ ] If using a proxy variable, proxy limitations noted

## Section D — Numerical Consistency

- [ ] Cross-card reconciliation: every metric in 2+ places matches
- [ ] Implied parameter back-derived (if A says −2.5% and B says 12.96T→12.65T, does 12.65/12.96 = 0.975? CHECK)
- [ ] Headline figures back-derived from raw source

## Section E — Action Brief (if recommending action)

For EVERY recommendation:
- [ ] Question — frame as a question
- [ ] Goal — measurable + deadline
- [ ] Why — link to evidence in report
- [ ] What — scope in / out
- [ ] Who — owner (team / role / individual)
- [ ] When — absolute date
- [ ] Where — system / team / region / cohort
- [ ] How — concrete first step

## Section E2 — Why-Explanation (Rule 4 meta-rule)

For EVERY method, threshold, tool, framework, or non-trivial choice introduced:
- [ ] `Why` is present inline (not deferred to appendix / footnote)
- [ ] `Why` answers one of: Causal / Empirical / Comparative / Theoretical / Operational
- [ ] `Why` is NOT a restatement of the action ("use X because we need X" — REJECTED)
- [ ] Method-comparison / formula / Bayesian / cross-period tables have a `Why this method` (or "Reading in business terms") column
- [ ] Threshold values (n-cutoff, α, MDE target, sample size) anchored to evidence or principle
- [ ] Tool / engine choice has a 1-sentence comparative Why (or pointer to comparison table)

## Section F — Style Polish

- [ ] No AI-tell symbols: `===`, `-----`, em-dash (`—`), `≈`, `→` (in stakeholder text)
- [ ] No Mermaid diagrams in .md (use ASCII)
- [ ] No fabricated credentials for Loc
- [ ] Vietnamese with diacritics for stakeholder output (all `ệ`, `ỉ`, `ổ` correct)
- [ ] Technical terms (API, mart, dry-run) in English in any language
- [ ] No emojis in code / file content unless user explicitly asked

## Section G — Number Formatting

- [ ] Units: K / M / B / T per scale
- [ ] Decimals: 2 default, 1 in dense tables, 0 for people counts
- [ ] Spacing: space before unit in summary (`1.97 T`), no space in dense tables (`123.4B`)
- [ ] Every metric has absolute + % + total / denominator
- [ ] Sentiment colors: Cashout↑/Churn↑/Cost↑ = RED; Cashin/Net/AUM↑/Revenue↑ = GREEN
- [ ] "Top X" tables sorted DESC

## Section H — Charts

- [ ] MoMo theme applied (Matplotlib `momo.apply_theme()` or Plotly `momo_plotly_theme`)
- [ ] Brand colors: pink `#d82d8b`, cream `#fdf6ee`, teal `#00b4a0`
- [ ] Per-chart inline `→ takeaway` verdict (drop / negligible / candidate / strong)
- [ ] Significant data records highlighted (color / bold / border) with WHY annotation

## Section I — Presentation Layer

- [ ] "Reading in business terms" column on number / method / formula tables
- [ ] Unusual metrics annotated inline (if differs from canonical baseline)
- [ ] Univariate vs Bivariate sections clearly separated (no duplicate t-test)
- [ ] Tone: directive (next steps timeline) for C-level, not approval-ask

## Section J — Code Discipline (if code involved)

- [ ] No comments unless explicitly asked
- [ ] Edit > Write (no whole-file rewrites for small changes)
- [ ] Surgical: every changed line traces to user's request
- [ ] No speculative features / config / error handling for impossible scenarios
- [ ] No emojis in code
- [ ] Senior-engineer test: would they call it overcomplicated? If yes, simplify.

## Section K — File Output

- [ ] Saved to `<your-workspace>/output/<type>/` or `<your-workspace>/output/projects/<name>/`
- [ ] NOT saved to workspace root or any non-output folder
- [ ] Filename includes date stamp where applicable

## Section L — Pipeline (if automation involved)

- [ ] Fail-alert wired (org-specific channel: SMTP / Slack / Teams / PagerDuty / internal notification module)
- [ ] Reason in natural Vietnamese
- [ ] No full stacktrace in email body
- [ ] Cache files preserve history on incremental update
- [ ] BQ dry-run done for backfill > 1 month, $ reported to user

## Section M — Auto-send Safety

- [ ] No auto-send email / Slack to stakeholders
- [ ] Generated → wait for user "send" confirmation
- [ ] Exception: pipeline-fail alert to configured oncall recipient only (auto-send by design)

## Section N — Session-End

- [ ] If substantive work shipped → update Personal Kanban + Weekly Log
- [ ] If your workspace's long-term-memory rules changed → run your sync command (e.g., `/claude-sync push`)
- [ ] If new template stabilized → drift-check canonical artifact + extract template

## When to Call Advisor

Call `advisor()` before declaring done if:
- The deliverable is high-stakes (hiring submission, executive report, public-facing)
- Numerical contradictions resisted resolution
- Approach changed mid-task
- You've patched the same artifact 3+ times (escalate to rebuild option)

## When to Spawn Student-POV Subagent

For academic / teaching deck deliverables: spawn a student-POV agent to review BEFORE declaring done. Then advisor triage. See `feedback_presentation_student_review.md` pattern.
