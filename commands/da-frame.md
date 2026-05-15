---
description: Professional Data Analyst — frame mode. Front-of-workflow planning. 4 gates (Business Understanding → Metric Define → Data Plan TH1/TH2 → Lock & Hand-off). Outputs PLANNING.md that downstream modes consume.
---

Invoke the `prof-data-analyst` skill in **frame mode**. Read these references before acting:
1. `references/mode-frame.md` — 4-gate workflow + when to use this mode
2. `references/planning-protocol.md` — Gate-by-gate detailed protocol with templates
3. `references/metric-framework.md` — Framework selection (NSM / OMTM / Growth Loop / HEART / AARRR / etc.) + 10-step KPI design protocol
4. `references/domain-discovery-protocol.md` — TH2 path (data missing) discovery flow with cost ceilings
5. `references/universal-workflow-rules.md` — Rules 1-4 (Orientation / Baseline-Noise-Impact / 5W1H / Why-Explanation)

User's request: $ARGUMENTS

Workflow:
- Gate 1: Capture stakeholder ask → fill 5W1H + stake + audience + reversibility
- Gate 2: Pick metric framework (decision table) → fill metric contract(s) with 10 fields
- Gate 3: Choose TH1 (data exists — verify schema) OR TH2 (data missing — design modeling pattern)
  - TH1: INFORMATION_SCHEMA verify → sample query < $0.10 → logic sketch
  - TH2: domain discovery (registry → schema scan → safe sample → user approval) → pick modeling pattern
- Gate 4: Write `PLANNING.md` → route to next mode (`/da-query` / `/da-process` / `/da-model` / `/da-insight` / `/da-automate` / `/da-report`)

Each gate has user-confirm checkpoint. Don't proceed without explicit OK. Cost of asking < cost of wrong direction.

Output: `<project>/PLANNING.md` with sections: Business Question / 5W1H / Metrics / Data Plan / Next Mode.

Hard rules:
- Each gate confirms with user before next
- TH1 vs TH2 explicit choice at Gate 3 (don't pretend data exists)
- Metric contract MUST include all 10 fields
- Output is a doc, not chat
- Cost ceilings respected at Gate 3 ($0.01 schema / $0.10 sample / $1.00 validation)
