# Metric Framework — Choosing the Right KPI for the Question

> Loaded from `da-frame` Gate 2 (Metric Define). Decision table + per-framework deep dive + KPI design protocol.

## Overview — Why this file exists

Picking the wrong metric framework gives the wrong answer.

- North Star applied to a feature → measures product, not feature ROI
- HEART applied to whole product → over-indexes UX, misses revenue
- OMTM applied to a mature stable product → false focus on a single number when balance matters

**Why (Empirical):** large product orgs (Airbnb / Meta / Spotify) document this pattern: framework-mismatch causes more wasted analyst time than wrong-method. Choosing the right framework upfront beats refining one wrong number for weeks.

This file gives: (1) the KPI Framework foundation, (2) decision table for framework selection, (3) deep dive per framework, (4) KPI design protocol when no framework fits.

---

## Section 0 — KPI Framework (Foundation)

**Source:** Data Analytics Series, @bitesbybytes — packaged here as the foundational layer before framework selection. The frameworks in Section 1 (NSM / OMTM / Growth Loop / HEART / AARRR / Unit Econ) are ways to ORGANIZE KPIs. This section is the rule for what makes a metric BE a KPI in the first place.

### 0.1 — Definition + Formula

```
KPI = Metric × Goal
```

- **Metric** — what you measure (e.g., 30-day retention rate)
- **Goal** — what you're trying to achieve (e.g., increase customer retention)
- **KPI** — the measurable value that tracks progress toward the specific goal

**Most dashboards show numbers. Few actually drive decisions.** The difference is the Goal column — without it, a dashboard is a numeric report, not a decision tool.

### 0.2 — Not all metrics are KPIs

A KPI MUST:
- [ ] Be tied to a business goal
- [ ] Influence decisions
- [ ] Drive action
- [ ] Have a clear owner
- [ ] Be tracked consistently

If a proposed metric fails any of these 5, it's a metric, not a KPI. Track it if useful, but don't elevate it to KPI status (which carries decision-rights weight).

### 0.3 — From Data to KPI (4-step protocol)

```
1. DEFINE THE OBJECTIVE
   Start with the business goal.
   e.g. "Increase customer retention"

2. CHOOSE THE RIGHT METRIC
   Pick a metric that reflects progress.
   e.g. "30-day retention rate"

3. MAKE IT A KPI
   Ensure it's actionable + tracked consistently.
   e.g. "Track weekly, review monthly"

4. USE IT TO DRIVE ACTION
   Let the KPI guide decisions + improvements.
   e.g. "Improve onboarding flow"
```

**Cycle:** action (step 4) feeds back → adjusts objective (step 1) next quarter. KPIs are designed for closed-loop, not one-shot reporting.

### 0.4 — Good vs Bad KPIs (the Vanity vs Actionable distinction)

| | **BAD KPIs (Vanity)** | **GOOD KPIs (Actionable)** |
|---|---|---|
| **What** | Looks impressive. Means nothing. | Drives action. Drives results. |
| **Examples** | Total users · Page views · Downloads | Conversion rate · Customer acquisition cost · Retention rate |
| **Reality** | High traffic ≠ revenue · More users ≠ growth · Activity ≠ success | Where you're losing customers · What's working vs not · What to fix next |
| **Decision impact** | ❌ Doesn't explain performance · ❌ Doesn't guide decisions · ❌ Easy to inflate | ✓ Tied to business goals · ✓ Leads to decisions · ✓ Drives real outcomes |

**Same data, different thinking:**
> Traffic ↑40%. But conversions ↓.
>
> ❌ **Vanity view:** "We're growing!"
> ✓ **KPI view:** "We have a funnel problem."

The data is identical. The framing makes one useful and one misleading. Always ask: "what does this number tell me to DO?"

### 0.5 — Think Like a Data Analyst (4 design principles)

| # | Principle | Anti-pattern → Right pattern |
|---|-----------|------------------------------|
| 1 | **Ask the Right Question** | "How many users?" → "Where are we losing conversions?" — focus on decisions, not numbers |
| 2 | **Tie to a Goal** | Tracking a metric in isolation → Every KPI connects to Revenue / Retention / Efficiency. If not tied to a goal, it's just a metric. |
| 3 | **Make it Clear** | Definition unclear → Simple, defined, measurable. Everyone calculates it the same way. |
| 4 | **Predict, not just Report** | Lagging only (what happened) → Pair Lagging + Leading. Leading = what happens next. Use both to guide decisions early. |

**Lagging vs Leading examples:**
- Lagging: Quarterly revenue, churn rate (measure outcomes)
- Leading: Trial-to-paid conversion at week 1, in-app onboarding completion (predict outcomes)

Good KPI portfolio: 1 NSM (overall) + 2-3 leading indicators + 2-3 lagging outcomes.

### 0.6 — KPI Stress Test (3 archetype interview questions, also useful for self-audit)

Three diagnostic question patterns. Apply these to your KPI portfolio to test if it's well-designed:

**Test 1 — Product Thinking**
> "Our traffic is growing, but revenue isn't. What would you look at?"

Strong KPI portfolio answers in 4 moves:
- Check the conversion funnel for drop-offs
- Look at user quality vs volume
- Identify where revenue is leaking
- Suggest what to fix and why it will help

If your KPI portfolio CAN'T support this descent, you're tracking vanity. Add: funnel-stage conversion, user-quality segmentation, revenue-per-user.

**Test 2 — KPI Judgment**
> "Is 'total users' a good KPI?"

Right answer pattern:
- "It depends on the goal"
- Alone, it's a vanity metric
- Pair with conversion, retention, or engagement
- Focus on metrics that drive action and outcomes

If your portfolio elevates `total users` to NSM-level, you've failed this test. Re-pair.

**Test 3 — Problem Solving (diagnostic)**
> "Sales dropped 20% this week. What's your approach?"

5-step descent:
1. **Validate data first** — is this a tracking / reporting issue, not a real drop?
2. **Break down by dimension** — channel, region, device, segment
3. **Check external factors** — campaigns, outages, seasonality
4. **Form hypotheses** → find the root cause
5. **Recommend clear next steps** and measure impact

If your KPI portfolio doesn't have the dimensional breakdowns + hypothesis-testing primitives to do this in <1 day, you have alerting without diagnostic capability. Add: segment splits, external-factor flags, hypothesis-validation playbook.

### 0.7 — Where Section 0 plugs into the workflow

- **`da-frame` Gate 2 (Metric Define):** Run the 4-step From Data to KPI protocol per metric → fill the 10-field contract → judge with the 5-criterion "must" checklist
- **`da-review` Sub-mode B Pass 2 (Business Logic + Domain Accuracy):** apply Vanity-vs-Actionable distinction to existing metrics in the project; flag vanity metrics as gaps
- **Stress test pre-ship:** run the 3 archetype questions against your KPI portfolio. If portfolio fails ≥ 1, you have a metric design problem, not an analysis problem.

---

## Quick decision table

| Question being answered | Framework | When to pick |
|-------------------------|-----------|--------------|
| "Are we winning as a product?" | **North Star Metric** | Mature product; 1 KPI everyone aligns on |
| "What's the MOST important number THIS quarter?" | **OMTM (One Metric That Matters)** | Early stage / pivot / phase change |
| "Is our growth flywheel working?" | **Growth Loop** | Network effects; user acquires more users |
| "Is THIS feature working?" | **HEART** (Google) | Feature evaluation; UX-focused product |
| "What broke? Why?" | **Diagnostic Funnel / Cohort / Driver Decomp** | Reactive analysis; metric dropped, find why |
| "How are we balancing growth vs quality?" | **Counter-metric pairs** | High-stakes optimization; prevent gaming |
| "How does the user journey work?" | **AARRR (Pirate Funnel)** | B2C SaaS; conversion-focused |
| "How is the business doing financially?" | **Unit Economics** (CAC/LTV/Payback) | Investor-facing / financial review |

---

## Framework 1 — North Star Metric (NSM)

### What
ONE primary metric that captures product value delivered. Whole org rallies around it.

### Properties of a good NSM
- **Captures value delivered to user** (not internal process)
- **Leading indicator of revenue** (correlated, ahead of revenue)
- **Measurable now** (not a 6-month survey result)
- **Actionable** (teams can move the needle)

### Examples
| Company | NSM |
|---------|-----|
| Spotify | Time spent listening |
| Airbnb | Nights booked |
| Facebook (early) | DAU |
| Slack | Messages sent in active teams |
| Quora | Knowledge-content created |

### Anti-patterns
- Picking revenue as NSM directly (lagging; team can't move it directly)
- Picking a vanity metric (registrations, pageviews; not value-capturing)
- Multiple NSMs (defeats the purpose)

### When NOT to use
- Early stage (product not stable enough for 1 metric)
- Multi-product company (each product needs its own)
- Quarter-specific question (use OMTM instead)

---

## Framework 2 — OMTM (One Metric That Matters)

### What
ONE metric that captures the most important question NOW, at the current stage. Changes between stages.

### Why different from NSM
- NSM is product-life-long; OMTM is phase-specific
- Example: NSM might be "MAU"; OMTM at the moment is "% of trials converting to paid"

### Lean Analytics stage mapping
| Stage | OMTM example |
|-------|--------------|
| Empathy (problem discovery) | % of users describing the problem unprompted |
| Stickiness (early product-market fit) | DAU/MAU ratio |
| Virality (growth) | Viral coefficient (k > 1?) |
| Revenue (monetization) | LTV/CAC payback months |
| Scale (mature) | Unit margin |

### How to pick OMTM this quarter
1. What's the riskiest assumption right now?
2. What metric, if it moves, kills/validates that assumption?
3. Can the team move it in this quarter?

If yes to all 3 → that's the OMTM.

### Cadence
Revisit OMTM every quarter. Don't switch monthly (no time to learn). Don't lock for a year (stage changes).

---

## Framework 3 — Growth Loop

### What
Self-reinforcing cycle: input → user action → output → reinvest into input.

### Pattern
```
[Input] → [Action by user] → [Output] → [Reinvest as input]
   ↑                                            │
   └────────────────────────────────────────────┘
```

### Examples
| Loop | Input → Action → Output → Reinvest |
|------|------------------------------------|
| Viral | New user → invites friends → invited friends → become new users |
| Content | Content creator → publishes → viewers find → some become creators |
| Paid | Revenue → ad spend → new users → more revenue |
| Network | New seller → lists item → buyers find → some become sellers |

### Metric design
Per loop, define:
- **Input rate**: how fast does input come in? (new users / dollar / content piece per day)
- **Conversion at each step**: % completing each transition
- **Output rate**: how much output per input?
- **Reinvest fraction**: what % of output becomes new input?

Loop sustainable if `reinvest fraction × output / input > 1` (compounds).

### When to use
- Network-effect products (marketplaces, social, content platforms)
- Growth-stage companies measuring compound vs paid
- Strategy discussions ("how do we scale efficiently?")

---

## Framework 4 — HEART (Google's UX framework)

### What
5 categories for feature/product evaluation. Pick metrics in each category.

| Letter | Category | Sample metric |
|--------|----------|---------------|
| **H** | Happiness | Survey score, NPS, app rating |
| **E** | Engagement | Sessions/user/week, depth of interaction |
| **A** | Adoption | New users trying feature in N days |
| **R** | Retention | % returning after N days |
| **T** | Task success | Task completion rate, time to complete |

### Use case
Feature launch evaluation. "Did this new feature help users?"

### Anti-pattern
Track all 5 with equal weight → diluted focus. Pick top 2-3 per feature, rank.

---

## Framework 5 — Diagnostic Funnel / Cohort / Driver Decomposition

### What
Reactive — metric moved, find WHY. Not a primary KPI; an investigation toolkit.

### Funnel (when conversion-focused)
```
Step 1 → Step 2 → Step 3 → Outcome
  N₁       N₂       N₃       N₄
```
Compute conversion per step (N₂/N₁, N₃/N₂, N₄/N₃). Find the leakiest step.

### Cohort (when retention-focused)
Group users by acquisition month/feature/segment; track retention curve per cohort.

### Driver Decomposition (when aggregated metric moved)
```
Total = Segment_A × weight_A + Segment_B × weight_B + ...
```
Decompose: which segment drove the change? Volume change vs rate change?

Example: MAU dropped 15% → break by tier. If Tier_3 dropped 60% and others stable → not a product problem, a Tier_3 problem.

### When to use
Always reactive. Used together with insight mode (`mode-insight.md` Phase 3).

---

## Framework 6 — Counter-metric pairs

### What
Optimizing for X risks gaming Y. Track Y alongside X.

| Optimized metric | Counter-metric |
|------------------|----------------|
| Revenue | NPS / customer satisfaction |
| Speed of delivery | Bug rate / quality score |
| Conversion rate | LTV (no, lifetime value, not just first purchase) |
| Click rate | Time spent / scroll depth |
| Engagement | Well-being / retention |

### Why
Without counter-metric, teams optimize the primary at the cost of the counter. Tie incentives to both.

---

## Framework 7 — AARRR (Pirate Funnel)

### What
B2C SaaS conversion funnel. 5 stages.

| Stage | Question |
|-------|----------|
| **Acquisition** | Where do users come from? |
| **Activation** | Do they have a good first experience? |
| **Retention** | Do they come back? |
| **Referral** | Do they tell others? |
| **Revenue** | Do they pay? |

### Use case
B2C product mapping; identifying bottleneck stage to invest in.

### Companion: Reverse AARRR
Some experts argue Retention first (no point acquiring if no retention). Strategy choice.

---

## Framework 8 — Unit Economics

### What
Financial metrics per user / per unit. Investor + leadership view.

| Metric | Formula |
|--------|---------|
| **CAC** (Customer Acquisition Cost) | Total acquisition spend / new customers acquired |
| **LTV** (Lifetime Value) | Avg revenue per customer × avg lifespan |
| **LTV/CAC ratio** | LTV / CAC — should be > 3 |
| **Payback period** | CAC / (monthly revenue per user × margin) — in months |
| **Burn multiple** | Net burn / net new ARR |

### Use case
Profitability assessment; investor pitch; pricing decisions.

---

## KPI Design Protocol (when no framework fits)

### Step 1 — Capture the question
"What decision will this metric inform?"

### Step 2 — Define the unit
- Per user? Per session? Per transaction? Per dollar?

### Step 3 — Numerator
What's being counted/measured?

### Step 4 — Denominator
What's the base? Activity rate (users active / users total) vs absolute count.

### Step 5 — Time window
- Snapshot (point in time)
- Rolling (last 7d / 30d / 90d)
- Cumulative (since start)

### Step 6 — Filter
Who/what is included? Excluded?

### Step 7 — Comparability
What baseline do we compare against?
- Previous period (DoD, WoW, MoM, YoY)
- Cohort average
- Control group
- Target / forecast

### Step 8 — Direction
Higher is better, or lower? Both directions?

### Step 9 — Significance threshold
What change is meaningful? (≥ 2σ from baseline? > 5%? > MDE from power calc?)

### Step 10 — Owner & cadence
Who owns it? How often reviewed?

### Output: Metric Contract
Fill the `planning-protocol.md` Gate 2 contract template.

---

## Anti-patterns across frameworks

| Anti-pattern | Symptom | Fix |
|--------------|---------|-----|
| **Vanity metrics** | "MAU is up!" but revenue flat, NPS down | Pair with counter-metric; require LTV/value link |
| **Goodhart's Law** | Metric becomes target → people game it | Counter-metric pair; rotate metrics; check second-order effects |
| **Framework overload** | 47 KPIs tracked, none prioritized | Pick 1 NSM + 1 OMTM + 2-3 supporting. Rest = drill-down only |
| **Activity = Value** | Sessions up but engagement down | Distinguish activity (did X) from value (X mattered) |
| **No denominator** | "1000 users did X" without total | Always pair count with rate |
| **Comparing apples to oranges** | "Revenue up 5%, last year vs this month" | Apples-to-apples: same period length, same cohort, same filter |

---

## Cross-references
- Planning gate: `planning-protocol.md` Gate 2
- Validate metric → diagnostic: `mode-insight.md` Phase 3
- Display rules (DoD + 7d-avg dual comparison): `style-rules.md`
- Hypothesis validation (when metric moved): `mode-insight.md` + `methods/falsification_tests.md`

— part of prof-data-analyst · Loc Tu, 2026
