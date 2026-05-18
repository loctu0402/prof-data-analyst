# Mode — Insight Extraction (Hypothesis → Diagnostic → Recommendation)

Invoke when user asks: "phân tích insight", "hypothesis validation", "diagnostic", "tại sao X", "why analysis", "root cause", "/da-insight".

For deep-dive WHY questions on fintech behavior (AUM decline, net cash, churn): consider invoking the `deep-dive-analysis` SKILL instead (heavyweight framework with 4-tab HTML output).

This mode is for LIGHTER insight work — single-question analysis, hypothesis validation, ad-hoc diagnostic.

## Analytical Flow

```
Descriptive (what happened)
  ↓
Diagnostic (why it happened) ← THIS MODE focuses here
  ↓
Predictive (what's likely next)
  ↓
Prescriptive (what to do)
```

## Phase 1 — Scope & Hypothesize

1. **Define the WHY question**: phrase it as a question. "Why AUM declined 572B over 24 days?"
2. **Formulate 3-5 hypotheses** covering at least:
   - Internal product (feature change, pricing, schema migration)
   - External market (competitor, macro, regulation)
   - Seasonal / calendar (payday, holiday, end-of-quarter)
   - Behavioral (cohort-specific shift, segment migration)
3. **Per hypothesis, define validation criteria**: what data confirms / rejects?

Output of Phase 1: hypothesis matrix (one row per hypothesis, columns: criterion, data source, expected sign).

## Phase 2 — Data Collection

Gather data covering EACH hypothesis. Parallelize where possible (mode-query mode):

### Internal data
- User segmentation by accumulated behavior (not daily snapshot)
- Cashflow by ALL channels (CO + CI both directions)
- Tier classification + high-balance breakdown
- Cross-period: same month last year + recent stable + pre-event

### Market data
- VNI, Gold, Oil, BTC, USD/VND, Bank rates, RON95
- Min 3 months for Pearson n ≥ 83 → |r| ≥ 0.22 for p < 0.05
- Pull from live cache, NOT hardcoded — see `feedback_no_market_data_hardcode.md`

### Competitor data
- Bank CASA SLTU rates (Techcom, VIB, LPBank, VPBank, MSB, Cake)
- Q1 2026 verified: Techcom 5.5%, LPBank 4.5%, MSB 4.2%, Cake 3.6%

### Cache verification
- Verify cache files have ALL needed columns
- Missing column → query BQ immediately, NEVER fallback to placeholder

## Phase 3 — Diagnostic Techniques (match to situation)

| Situation | Technique | Full reference |
|-----------|-----------|----------------|
| Policy / feature change with treatment + control + pre/post | Difference-in-Differences | `references/causal-inference-toolkit.md` §1 |
| Same as DiD + multi-period dynamics | Event Study | `references/causal-inference-toolkit.md` §2 |
| Treatment assigned by sharp cutoff on a running variable | Regression Discontinuity (RDD) | `references/causal-inference-toolkit.md` §3 |
| One treated unit, no good control, long pre-series | Synthetic Control | `references/causal-inference-toolkit.md` §4 |
| Observational, known confounders, want ATT | Propensity Score Matching | `references/causal-inference-toolkit.md` §5 |
| Endogenous treatment, valid instrument exists | Instrumental Variable (IV) | `references/causal-inference-toolkit.md` §6 |
| Unusual data point | Anomaly Reasoning (explain mechanism) | this file |
| Trend reversal | Turning Point Analysis (date + compound factors) | this file |
| Indirect proxy (e.g., Brent oil → retail behavior) | Sentiment Channel (proxy ≠ direct cause) | this file |
| Continuous correlation, n ≥ 83 | Pearson r with significance threshold | this file Phase 4 |
| Step-function variable (rate flat then jumps) | Event Study (NOT Pearson — Pearson invalid on step) | `references/causal-inference-toolkit.md` §2 |

Why this table — picking the wrong technique produces wrong-but-plausible numbers. Each technique solves a specific identification problem; the assumptions are the price you pay for the causal claim. Load `causal-inference-toolkit.md` for the full assumption + falsification spec per method.

## Phase 4 — Statistical Methodology

### Pearson r — when valid
- n ≥ 83 → |r| ≥ 0.22 for p < 0.05
- n < 30 → ASK user to extend date range, DON'T force a conclusion
- Report: r-value + significance threshold + CI width note + proxy limitations

### Effect size — not just r
- Continuous outcome: Cohen's d
- Categorical outcome: Cramer's V — but FLAG inflation on high-cardinality columns (chi-square scales with df)

### When n=24 and n=83 give different signs
- Flag as "spurious at short range"
- Use extended range as primary
- Example: Gold r=+0.734 (n=24) vs r=−0.097 (n=83) — different conclusion

### CV vs MDE — choose the right threshold
- CV (n=1 monitoring) for daily anomaly detection
- MDE (n>1 decision gate) for A/B test sizing
- Linked: MDE / mean ≈ 4 · CV / √n
- Same tool, different n. Don't conflate.

### Alpha vs FDR — distinct concepts
- Strict α (FPR) ≠ (1 − Precision) (FDR)
- Denominators differ; class-imbalanced contexts diverge 4-10×
- Cite denominator explicitly when teaching

### Hypothesis validation — 3 traps (from past incidents)

When validating a hypothesis with treated + control setup, three trap-shaped errors recur. Catching them at validation time is far cheaper than surfacing them at delivery.

**Trap (a) — n_T inflated by wrong table.**
Symptom: hypothesis "treated cohort = 12,400" but the upstream event log only has 8 raw events on the treatment day; n_T off by 1493×.
Cause: pulled count from an aggregated downstream table (already deduped, joined, expanded) rather than the raw event table.
Fix: VERIFY n_T against the raw event count. Always cite the table source for the headline n.

**Trap (b) — single-outcome DiD hides the mechanism.**
Symptom: DiD on "cashout amount" shows effect, but stakeholder asks "why" and you have no mechanism.
Cause: ran the single-outcome estimation only; never tested the chain of intermediate outcomes (login frequency → screen view → cashout intent → cashout amount).
Fix: run multi-outcome DiD across the behavioral chain. The pattern of which outcomes move tells the mechanism.

**Trap (c) — wrong-sign result without reframing.**
Symptom: hypothesis predicts +X, data shows −X. You report "hypothesis rejected" and stop.
Cause: assumed the test answered ONE question (does X drive Y?); never reframed as "what does the wrong direction tell us about cohort heterogeneity?"
Fix: when sign is wrong, reframe as TIER identification — which sub-cohort drives the unexpected direction? Often the wrong-sign average hides a tier where the predicted sign is correct + a tier where the opposite happens; the heterogeneity IS the finding.

See `feedback_hypothesis_validation_method_traps.md` for the original incident chain.

## Phase 5 — Self-Evaluation (CRITICAL)

Run AFTER every analysis, BEFORE finalizing conclusion. Self-check audits:

1. **Methodology audit**: "Is Pearson appropriate here? Or is this a step-function / event needing DiD / Event Study?"
2. **Proxy audit**: "Am I using a proxy as direct measure? (e.g., Brent oil ≠ Vietnam retail fuel — Price Stabilization Fund decouples)"
3. **Sample size audit**: "Is n sufficient? Would conclusion change with more data? → suggest user extend range"
4. **Confounding audit**: "Could a third variable explain both? (e.g., global risk sentiment drives BOTH oil AND withdrawals)"
5. **Direction audit**: "Am I stating something obvious by definition? (e.g., 'the heavy-withdrawal tier withdraws a lot' — they're classified that way by definition)"
6. **Numerical consistency audit**: cross-card reconciliation; back-derive headlines from raw

If limitations found → add qualification notes IN the report, don't hide them.

Use `deep-research` skill to validate causal mechanisms with academic references when available.

## Phase 6 — Anti-Bias Protocol (CRITICAL)

- **Never one-sided**: for every negative finding, actively search for counter-argument or recovery signal. "Heavy-tier drain −1,649B BUT lighter tier still net positive +1,445B = recovery foundation."
- **Challenge user framing**: if user's hypothesis leads to bias, present data objectively. If data contradicts hypothesis, SAY SO clearly — don't force-fit evidence.
- **Multi-dimensional**: every metric examined from ≥2 angles. "CO > 100M users +22.5% (bad) BUT total T1 users grew 7.8M → 9.1M (good) — product is GROWING overall despite drain."
- **Structural vs cyclical**: always distinguish: "Is this structural (scheme design flaw) or cyclical (market downturn reversing)?" → different recommendations for each.
- **Avoid confirmation bias**: when correlation supports hypothesis, list reasons it might be spurious. When it doesn't, don't dismiss — explain why.

## Phase 7 — Reasoning Output (5-stage chain)

Every finding ships in the 5-stage chain:

```
Fact → Mechanism → Behavioral Change → Product Impact → Evidence
```

WRONG: "Oil correlation r = −0.751"

RIGHT: "Oil price +31% in March (FACT) → transport + food prices ↑ (MECHANISM) → households reallocate cash toward expenses (BEHAVIORAL CHANGE) → withdrawal from a savings product for daily payments (PRODUCT IMPACT) → Payment Cashout +13.2% same period, daily mart section 4.1 (EVIDENCE)"

If any stage missing, finding is incomplete.

## Phase 8 — Hypothesis Verdicts

For each hypothesis from Phase 1, give a verdict:
- **ĐÚNG** (confirmed): evidence matches all criteria
- **MỘT PHẦN** (partial): evidence matches some criteria, not all — quantify which
- **KHÔNG** (rejected): evidence contradicts criteria

Format:
```
H1: <hypothesis>
  Criteria: <what would confirm>
  Evidence: <what we found>
  Limitations: <proxy / sample / confounding caveats>
  Verdict: ĐÚNG / MỘT PHẦN / KHÔNG
```

## Phase 9 — Recommendations (8-field Action Brief)

For each recommendation, fill 8 fields (see `universal-workflow-rules.md` Rule 3):
- Question, Goal, Why, What, Who, When, Where, How

Tone for C-level: "Next steps" timeline directive, NOT "Cần phê duyệt" checkbox.

## Quick-Win Patterns

For light insight work (no need for full deep-dive):

### Spike investigation
1. Identify the spike date
2. Pull 14d before + 14d after
3. Look for: feature deploy, marketing campaign, holiday, market event, competitor action
4. 5-stage chain on top 2 hypotheses
5. Recommendation: monitor / intervene / accept

### Drop investigation
1. Identify the drop trigger
2. Cohort decomp: who dropped (segments, tiers, regions)
3. Channel decomp: which channels (CO / CI, in-app / external)
4. Cross-period: was the drop level a structural reset or a cyclical dip?
5. Anti-bias: is there a counter-recovery signal in another segment?

### Correlation flag
1. State the correlation (r, n, p)
2. Methodology audit: Pearson appropriate or step-function?
3. Proxy audit: is X a direct measure or proxy?
4. Confounding audit: third variable possible?
5. 5-stage chain explaining the causal mechanism (or note "correlation only, mechanism unclear")

## Validation & Robustness (before declaring a finding confirmed)

Before shipping an insight as a "confirmed" finding, run the relevant subset of validation methods from `references/validation-evaluation-methods.md`:

- **Bootstrap CI** if n < 30 or non-normal distribution → `scripts/stats/bootstrap_ci.py`
- **Robustness checks** across 3+ specifications → vary functional form, subsample, controls
- **Sensitivity** across parameter ranges → bandwidth, time window, threshold
- **Multiple-testing correction** if K > 1 tests → `scripts/stats/multiple_testing.py` (Bonferroni / BH-FDR)
- **Falsification test** appropriate to the method → e.g., `scripts/causal/parallel_trends_test.py` for DiD
- **Pre-registration check** — does the result match what you planned to find?

Why stack these — no single test confirms a finding. Each method addresses one failure mode (sampling, specification, multiple-testing, power, researcher freedom). Findings that survive 6 of 7 are credible.

## Universal Rules Reminder

Insight deliverable applies all 4 universal rules:
- **Rule 1** — Orientation Block (SCQR for written, 3-line intro for dashboard)
- **Rule 2** — Baseline-Noise-Impact ladder for every numeric finding
- **Rule 3** — 8-field Action Brief for any recommendation
- **Rule 4** — Why-Explanation on every method choice (DiD over Pearson? Why. Bootstrap CI vs parametric? Why.)

Plus:
- Connect-the-Dots reasoning (5-stage chain)
- Self-Check numerical consistency
- "Reading in business terms" column on number tables

## When to Escalate to Deep-Dive Skill

Switch to `deep-dive-analysis` skill when:
- Question requires multi-tab HTML report
- Multi-factor correlation with ≥4 market variables
- Behavioral segmentation by accumulated tier (not daily snapshot)
- Stakeholder = C-level + cross-functional team
- Time budget ≥ 2 days

Otherwise stay in this mode for ad-hoc / single-day insight work.
