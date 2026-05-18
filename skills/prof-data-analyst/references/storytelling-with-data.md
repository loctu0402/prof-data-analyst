# Storytelling with Data — Visualization Discipline

Practical rules for chart + dashboard + slide deliverables. Apply on every visual artifact produced by `mode-report`, `mode-process` (charts inside notebooks), `mode-insight` (diagnostic plots), and any other stakeholder-facing visual.

**Primary source**: Cole Nussbaumer Knaflic, *Storytelling with Data: A Data Visualization Guide for Business Professionals* (Wiley, 2015) + storytellingwithdata.com blog corpus. The six lessons below are the canonical SWD framework; the rest are practical extensions for analytics dashboards.

## Quick reference — the 5-rule cheatsheet

Print this. Put it next to your monitor. Apply before every chart ships.

```
RULE 1 — ACTION TITLE
   Every visual title states a CONCLUSION, not a topic.
   BAD:  "Brand Awareness (%)"
   GOOD: "Brand X leads at 78% — 7pp gap vs runner-up"

RULE 2 — GREY + 1 ACCENT
   Default everything to grey (#CCCCCC or #999999).
   Use ONE accent color for the focal element.
   "When everything is emphasized, nothing is emphasized." — Cole Knaflic

RULE 3 — NO PIE, NO 3D
   Horizontal bar > pie (length is more accurate than angle).
   2D > 3D (perspective distorts comparison).
   Use slopegraph for 2-point trends, not grouped bars.

RULE 4 — CLUTTER CHECKLIST (apply in 5 min before submit)
   □ Remove chart border       □ Reduce gridlines (max 1 baseline)
   □ Remove legend if direct labels available  □ Strip 3D / shadow / gradient
   □ Add 1 "Key Takeaway" text per page / per chart

RULE 5 — HORIZONTAL LOGIC
   Read page titles (or chart titles) in order → must form 1 coherent story.
   Setup → Conflict → Resolution structure across the deck.
```

## The 6 SWD Lessons (full framework)

### Lesson 1 — Understand the context

> "You should always want your audience to know or do something. If you can't concisely articulate that, you should revisit whether you need to communicate in the first place." — Cole Knaflic

Actionable rules:

1. **Audience first** — write down WHO the audience is + WHAT decision they need to make BEFORE choosing chart type. Executive ≠ analyst ≠ engineer; same data, different visualization.
2. **Exploratory vs explanatory** — exploratory (you discovering) and explanatory (you communicating one finding) are two different designs. Don't ship exploratory charts to stakeholders.
3. **Big Idea in one sentence** — draft the headline before building the visual. Example: *"Region X grew 18% MoM while regions Y/Z stayed flat — Region X drivers warrant deeper investigation."*

Hook to plugin: `references/narrative-template.md` (SCQR + Key Terms + Impact Cards) operationalizes Lesson 1 at deliverable level. Big Idea = the Resolution in SCQR.

### Lesson 2 — Choose an appropriate visual display

| Question type | Right chart | Wrong chart (common) |
|---------------|-------------|---------------------|
| Compare categories (≤ ~10) | Horizontal bar, sorted | Pie / donut (poor angle comparison) |
| Trend over time (continuous) | Line chart | Bar chart with date X-axis |
| 2-point change (period A vs B) | Slopegraph or connected dots | Side-by-side grouped bars |
| Distribution | Histogram / density / boxplot | Bar with binned X |
| Part-to-whole (single point) | 100% stacked bar / waffle | Pie chart (only ok if exactly 2 slices) |
| Correlation / scatter | Scatter plot | Line connecting unrelated points |
| Matrix (entity × attribute) | Heatmap (color intensity) | Table of raw numbers |
| Cumulative / running total | Area chart or step chart | Stacked bar over time |
| Single big number (KPI) | Large numeric callout + 1-2 deltas | Speedometer / gauge / dial |

Default to the LEFT column. Deviate only with explicit Why (Rule 4 of the universal rules).

### Lesson 3 — Eliminate clutter

> "Clutter is your enemy. Clutter refers to visual elements that take up space but don't add information." — Cole Knaflic

Apply Tufte's "data-ink ratio" test: ask each element "if I removed this, would the chart become harder to understand?" If no → remove.

Standard removals on every chart:
- Chart border
- Background fill of plot area
- Heavy gridlines (max 1 baseline gridline, light grey)
- Legend if there's only 1 series, or if direct labels are used
- Axis labels that repeat title information
- Tick marks beyond the necessary (every 5th or 10th, not every unit)
- 3D effects (always)
- Drop shadows
- Gradient fills on bars

Gestalt principles to leverage (built-in clutter reducers):

| Principle | How it cuts clutter |
|-----------|--------------------|
| Proximity | Related elements close → no need to draw boxes around them |
| Similarity | Same color = same category → no need for repeated labels |
| Enclosure | Light background tint = group → no need for borders |
| Closure | Brain completes shapes → axes don't need to fully box the chart |
| Continuity | Line implies relationship → no need to label each point |
| Connection | Same accent color across pages = same focal entity → no need to re-explain |

### Lesson 4 — Focus attention where you want it

> "Make it clear where to look. Don't make your audience process everything to figure out where they should pay attention." — Cole Knaflic

**Preattentive attributes** (brain processes < 250ms, before conscious thought):

| Attribute | Strength | Use when |
|-----------|----------|----------|
| Color (hue) | Highest | Highlight the focal entity / metric |
| Size | High | KPI callouts (focal metric 40%+ larger than context) |
| Position on page | High | Z-pattern: top-left = most important |
| Intensity (shade) | Medium | Heatmaps, density encoding |
| Length | Medium | Bar chart length = value |
| Enclosure | Medium | Group "current period" cells in a chart |
| Orientation | Low | Rare; can confuse |
| Motion | Highest but distracting | AVOID in static dashboards |

**Where-are-your-eyes-drawn test**: look away, look back. Where do your eyes land first? If not on the most important element → redesign.

**Grey + 1 Accent rule** (operational form of Lesson 4):
- Default all non-focal elements to neutral grey (`#CCCCCC` or `#999999`).
- Use ONE accent color for the entity / metric being discussed.
- Add a second color ONLY with explicit semantic meaning (e.g. green = on-target, red = off-target).

### Lesson 5 — Think like a designer

| Design dimension | Rule |
|------------------|------|
| **Alignment** | Everything left-aligned (text + titles + chart edges). No center alignment for titles. |
| **Proximity** | Related visuals near each other; unrelated visuals separated by whitespace |
| **White space** | Padding between visuals ≥ 12-16px (≈ 1 text line). Whitespace is not waste. |
| **Hierarchy** | Title text 18-24px, body 12-14px, KPI numbers 32-48px. Audience scans largest first. |
| **Affordance** | Slicers / filters look clickable; static labels don't. Match visual to function. |
| **Accessibility** | Color-blind-safe palettes (test with Coblis / Sim Daltonism). Don't rely on color alone — pair with shape or label. |
| **Aesthetic** | Consistent fonts (max 2 families), consistent color palette across deck, consistent date/number formats. |
| **Acceptance** | Solicit feedback from a target-audience member before shipping. |

### Lesson 6 — Tell a story

Structure every deck (or dashboard) as **Setup → Conflict → Resolution**:

1. **Setup** — what was the situation / baseline / context?
2. **Conflict** — what changed / what's the problem / what's the gap?
3. **Resolution** — what's the recommendation / decision / next step?

**Horizontal logic test**: read ONLY the page titles (or chart titles) in order. Do they form a coherent story by themselves? If yes → narrative is strong. If no → titles are decorative, not informational → upgrade to action titles.

**Action title vs topic title**:

| Type | Example | Use when |
|------|---------|----------|
| Topic (weak) | "Sales by Region" | You want the audience to draw their own conclusion (rare) |
| Action (strong) | "Region X is the only region growing — Q3 effort should concentrate there" | You want to communicate a specific finding (default) |

Cole: *"Titles are prime real estate — never waste them on a descriptor like 'Findings'."*

Hook to plugin: `mode-report.md` Step 5 storyline pattern already enforces `[Q] → [A] → [Why]` triplet per section, which operationalizes action titles + horizontal logic.

## Preattentive attribute mini-cookbook

Use these as defaults when you need to draw attention without adding clutter:

| Want to highlight | Use |
|-------------------|-----|
| One entity in a comparison chart | Accent color on that one bar / line; grey everything else |
| One time period (e.g. forecast vs actual) | Different line style (dashed for forecast) + lighter color |
| Threshold crossing | Reference line + label at threshold value |
| Single most-important KPI | 32-48px number; everything else 14-18px |
| Recent / live data | Slight color saturation increase; older data desaturated |
| Outlier | Annotation arrow + label, leave bar/point default color |
| Direction of change | Up/down arrow next to delta (▲ ▼); avoid em-dash glyphs (Rule per style-rules.md) |

Anti-pattern: applying ALL of the above simultaneously to one chart. Pick the ONE thing the audience should see first.

## Z-pattern + F-pattern reading flow

Western audiences scan left-to-right, top-to-bottom:

- **Z-pattern** (charts + visuals): top-left → top-right → diagonal to bottom-left → bottom-right. Put most important KPI top-left, filters / metadata top-right, supporting details bottom.
- **F-pattern** (text-heavy or table-heavy): scan first 2 rows fully, then only the left column. Put critical labels in the first 2 rows and the leftmost column.

Dashboard layout default (3 zones top to bottom):

```
[ Top strip ]    KPI summary cards (3-5 numbers, focal first on left)
[ Middle band ]  Main chart (1-2 visuals, the "headline" finding)
[ Bottom band ]  Supporting detail (3-4 visuals, drill-down or breakdown)
```

Max 3-4 visual units per page. Don't cram 8 charts onto one page — that's exploratory thinking, not explanatory.

## Top 10 anti-patterns (each = one line ban)

| # | Anti-pattern | Replace with |
|---|--------------|--------------|
| 1 | Pie chart with > 2 slices | Horizontal bar sorted descending + direct labels |
| 2 | 3D chart of any kind | 2D equivalent (perspective distorts comparison) |
| 3 | Dual Y-axis with unrelated units | Two separate charts OR slopegraph if showing relative change |
| 4 | Rainbow color palette (6+ colors no semantic meaning) | Grey baseline + 1 accent on focal entity |
| 5 | Chart junk (gradient fills, drop shadows, thick borders) | Flat fill, no shadow, no border |
| 6 | Default BI-tool color palette without choosing | Org brand palette OR intentional 1-accent palette |
| 7 | Chart with no takeaway annotation | Inline "Key insight: ..." text near the chart |
| 8 | Line chart for categorical comparison (or bar for time series) | Match chart type to data type (line=time, bar=category) |
| 9 | Bar chart Y-axis not starting at 0 | Bar charts MUST start at 0; line charts may not, but call it out |
| 10 | Table with 20+ columns and no formatting | Max 6-7 columns, conditional formatting on key cells, bold focal row |

## Pre-ship checklist (per visual)

Run this in 60 seconds before shipping any chart:

- [ ] Title is an action title (states a conclusion, not a topic)
- [ ] One focal entity / metric is visually emphasized (color, size, position)
- [ ] All non-focal elements are neutral grey
- [ ] Chart type matches the question type (Lesson 2 table)
- [ ] Border, heavy gridlines, redundant axis labels removed
- [ ] Legend only if necessary; direct labels preferred
- [ ] No 3D, no gradient fills, no shadows
- [ ] Numbers formatted consistently (K/M/B units, decimal places — see `format/number_format.py`)
- [ ] Color-blind safe (don't rely on red/green alone; add shape or label)
- [ ] At least 1 takeaway annotation per chart or per page

## Pre-ship checklist (per dashboard / deck)

- [ ] Horizontal logic test: read all titles in order → forms a coherent story
- [ ] Setup → Conflict → Resolution structure visible across pages
- [ ] Top-left of page 1 = most important headline / KPI
- [ ] Max 3-4 visual units per page (no clutter)
- [ ] Padding between visuals ≥ 12-16px
- [ ] Font hierarchy consistent (title 18-24px, body 12-14px, KPI 32-48px)
- [ ] Same accent color used for the focal entity across all pages
- [ ] Each page has a 15-20 word "Key Takeaway" text box
- [ ] No AI-tells: `===`, `-----`, em-dash, `≈` (use plain text — see `style-rules.md`)
- [ ] Numbers tied to denominators / baselines (see Rule 2 baseline-noise-impact)

## Cross-references

- **Narrative structure** → `references/narrative-template.md` (SCQR + Key Terms + Impact Cards)
- **Number formatting** → `scripts/format/number_format.py` (K/M/B/T units + sentiment color)
- **AI-tell scan** → `scripts/validators/ai_tell_scan.py` (catches em-dash, `===`, etc. in stakeholder text)
- **Style rules** → `references/style-rules.md` (chart anatomy 7-element + sentiment colors + dual comparison)
- **Report mode storyline** → `references/mode-report.md` Step 5 (`[Q] [A] [Why]` triplet per section)
- **Review mode polish gates** → `references/mode-review.md` Sub-mode A (polish pass invokes this checklist)
- **Quality criteria** → `references/quality-criteria.md` (Insightful + Sufficient criteria map to action titles + takeaway annotation)

## Why this rule exists

Statistical rigor (Rules 1-4 of universal-workflow-rules) gets you correct numbers. SWD discipline gets those numbers READ. A defensible analysis communicated through a cluttered rainbow pie chart loses every executive in the room within 10 seconds — the work effectively didn't ship. SWD is the layer that converts internal rigor into external decision-making impact. Default-OFF for SWD = analysis dies on arrival; default-ON = analysis lands.
