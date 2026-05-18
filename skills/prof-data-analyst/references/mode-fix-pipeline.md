# Mode — Fix / Debug Pipeline

## Overview

Invoke when user asks: "fix pipeline", "sửa pipeline", "debug pipeline", "report sai", "bug ở ...", "/da-fix".

This mode handles surgical pipeline patches — never edit the generator; always write `update_report_vN.py` overlay scripts that load the artifact, patch, write a versioned new file. The decision tree below routes the symptom to the right repair pattern.

## Bug Triage Decision Tree

```
What is the symptom?
  │
  ├─ HTML report visually wrong (chart missing, label off, color wrong)
  │   └─ Patch path: update_report_vN.py (NOT generate_report.py)
  │       └─ See "HTML patch — never edit generator"
  │
  ├─ Data missing in cache / report
  │   └─ Check cache → BQ query → verify pipeline pull
  │       └─ See "Cache verify" + "Backfill"
  │
  ├─ Pipeline failed silently (no output, no email)
  │   └─ Email-on-fail not wired OR caught broad exception
  │       └─ See "Wire email-on-fail"
  │
  ├─ Pipeline produced wrong numbers (math / aggregation bug)
  │   └─ Cross-card reconciliation → back-derive → find computation
  │       └─ See "Numerical debug"
  │
  ├─ Pipeline output looks right but model bias / surprising drift
  │   └─ Check: state-machine neighbor inheritance OR two-cache-files mismatch
  │       └─ See "Silent data-layer bugs"
  │
  ├─ Same bug recurring across patches (≥3 distinct in same artifact)
  │   └─ STOP patching → surface rebuild / handoff options
  │       └─ See "Patch ceiling"
  │
  └─ Behavior changed after recent code change
      └─ git log + git diff on the file → identify commit → revert or fix forward
```

## HTML Patch — NEVER Edit Generator

When user reports "the HTML has bug X":
- Do NOT modify `generate_report.py`
- CREATE `update_report_vN.py` that:
  1. Loads the already-generated HTML
  2. Applies the patch (BeautifulSoup / string replace / regex)
  3. Writes a new file (e.g., `<base>_v<N>.html`)

Why:
- `generate_report.py` is the next-day pipeline source
- Patching it side-channels into next-day output without review
- Backfill / re-run would now produce a different artifact than past runs

Pattern:
```python
# update_report_v2.py
from bs4 import BeautifulSoup
html = open("output/<report>_<date>.html").read()
soup = BeautifulSoup(html, "html.parser")
# ... patch logic ...
open("output/<report>_<date>_v2.html", "w").write(str(soup))
```

After patch validated: PROPOSE the equivalent change to `generate_report.py` — do not commit until user confirms.

## Cache Verify

Symptom: data missing or NULL in report.

Steps:
1. Read cache file metadata (last-updated date, row count, column list)
2. Check expected columns vs needed columns — schema drift?
3. Check date range — is the missing date covered?
4. Cross-validate with a direct engine query for the missing slice
5. If cache missing data → repull via `--backfill-from <date>` or equivalent
6. After backfill: verify no duplicates (`GROUP BY pk HAVING COUNT(*) > 1`)

Common cache schema drift to check:
- A column got split into N sub-columns at a known cutover date — UNION old + new for full history
- A conversion ratio changed at a known date — branch the formula on date
- An entity-classification changed (e.g. tier definition refactor) — verify alignment with new taxonomy

## Numerical Debug

Symptom: report numbers don't reconcile across cards / tables / charts.

Self-check protocol:
1. **Cross-card reconciliation**: every metric in 2+ places — list them
2. **Implied parameter check**: if A says "−2.5%" and B says "12.96T → 12.65T", does 12.65/12.96 = 0.975? Calculate by hand
3. **Back-derive headlines**: take each headline, recompute from raw source (CSV / BQ query)
4. **Structural self-checks miss this**: grep / keyword scan WON'T surface cross-card numerical contradictions — manual required

When stuck on conflicting numbers, call `advisor()`. Keyword checks alone won't surface the contradiction.

## Silent Data-Layer Bugs (highest pain class)

These appear as "model is biased" but root is data-layer mismatch.

### State machine neighbor inheritance
- Bug: lookup table mixes focal + neighbor states with per-event coefficients
- Neighbors inheriting focal's empirical drop = category error
- Fix: gate lookup to focal state only; add edge-case test (pure-neighbor input MUST NOT return focal's coefficient)
- See `feedback_state_machine_neighbor_inheritance.md`

### Two cache files, different scope
- Bug: 2 caches share prefix but different scope (e.g., `events_history.json` operational vs `events_timeline.json` cumulative)
- Wrong pick = silent miss (calendar lookup doesn't error)
- Bug surfaces as model bias, NOT data-layer mismatch
- Fix: document scope in each cache header; consumer picks matching source
- See `feedback_two_cache_files_different_scope.md`

### OLS anomaly window
- Bug: OLS regression includes structural breaks → drift in coefficients
- Fix: exclude structural breaks; use last-3M window
- See `feedback_ols_anomaly_window.md`

### W_7d corner solution
- Bug: per-metric coefficient `w_7d = 0` (corner of optimization)
- Fix: floor at 0.05; empirical N=180 elbow
- See `knowledge_kvbd_w7d_floor_fix.md`

## Wire Email-on-Fail (when pipeline failed silently)

If pipeline didn't email on failure:
1. Check `try / except` block exists around `pipeline.run()`
2. Check `send_failure_email` is called inside `except`
3. Check exception is re-raised (else cron treats it as success)
4. Test by raising synthetic exception → confirm email arrives

Standard wiring (substitute YOUR notification module):
```python
# Example using a hypothetical org module — substitute SMTP / Slack / Teams / PagerDuty / your internal module
from your_org.notifications.email_on_fail import send_failure_email
try:
    pipeline.run()
except Exception as exc:
    send_failure_email(reason="<natural-language reason>", traceback=exc)
    raise
```

## Patch Ceiling — Escalate to Rebuild

After ≥3 distinct bugs in the same artifact across 2-3 patch rounds:
- STOP patching
- Surface to user: "rebuild / handoff / switch tool" options
- Write a self-contained handoff spec document
- Your role shifts to: input-pipeline + planning + tool choice
- Visual / patching layer = NOT yours anymore in this artifact

See `feedback_patch_ceiling_escalate_rebuild.md`.

## Defensive Parser (HTML parsing bugs)

When parsing HTML / webhook payloads (e.g., daily report deltas):
- Normalize classes (lowercase, strip whitespace)
- Keyword match labels (don't rely on exact text)
- Robust to whitespace / case / formatting variation

See `feedback_html_parser_robustness.md`.

## MCP Fetch — Pure Python

For an app performance dashboard pipeline:
- Use a direct HTTP MCP client (NOT a Claude CLI subprocess)
- Kill any silent HTML fallback (it hides real fetch failures)
- Add DoD + 7d-avg deltas + duration p50 / p90 (with a minimum-sample filter) to the webhook payload

## Validate Fix Before Declaring Done

Per `references/self-check-protocol.md` section J + L:
- [ ] Run the pipeline end-to-end (not just unit test)
- [ ] Compare output checksum / row count vs expected
- [ ] Cross-validate numbers vs BQ direct query
- [ ] Test backfill range — incremental update doesn't clip cache history
- [ ] Email-on-fail still wired (test with synthetic exception)
- [ ] No emojis introduced in code
- [ ] Surgical: every changed line traces to the bug

## When to Call Advisor

Call `advisor()` if:
- You've patched same artifact ≥3 times
- Numerical contradictions resisted reconciliation
- Bug appears intermittently (data race? caching?)
- User reports "the fix made another thing break"

## Universal Rules Reminder

Fix-pipeline deliverable = patched code + Vietnamese commit message + verification log. Apply:
- Surgical Karpathy principle: every changed line traces to the bug
- Self-check protocol L (Pipeline) before declaring fixed
- Update Personal Kanban with the fix entry (session-end)
- If the bug pattern is novel → write feedback memory for future sessions
