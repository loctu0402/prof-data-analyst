# Coding Discipline

## Overview

Applies whenever the task involves writing or editing code (SQL, Python, JavaScript, HTML, YAML, shell). Source: Karpathy LLM-coding observations + Loc's accumulated feedback.

Bias: **caution over speed**. For trivial one-liners, use judgment — but the senior-engineer test applies even then.

## The 4 Karpathy Principles

### 1. Think Before Coding — Don't assume. Don't hide confusion. Surface tradeoffs.

- State assumptions explicitly. If uncertain, ASK.
- If multiple interpretations of the task exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, STOP. Name what's confusing. Ask.

### 2. Simplicity First — Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked
- No abstractions for single-use code
- No "flexibility" or "configurability" that wasn't requested
- No error handling for impossible scenarios
- If 200 lines could be 50, rewrite it
- **Senior engineer test**: would a senior engineer call it overcomplicated? If yes, simplify.

### 3. Surgical Changes — Touch only what you must. Clean up only your own mess.

- Don't "improve" adjacent code, comments, or formatting
- Don't refactor things that aren't broken
- Match existing style even if you'd do it differently
- If you notice unrelated dead code, mention it — don't delete it
- Remove imports / variables / functions YOUR changes made unused. Leave pre-existing dead code alone unless asked.
- **Test**: every changed line traces directly to the user's request

### 4. Goal-Driven Execution — Define success criteria. Loop until verified.

Transform imperative tasks into verifiable goals:

| Instead of… | Transform to… |
|-------------|---------------|
| "Add validation" | "Write tests for invalid inputs, then make them pass" |
| "Fix the bug" | "Write a test reproducing it, then make it pass" |
| "Refactor X" | "Ensure tests pass before and after" |

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong criteria let the agent loop independently. Weak criteria ("make it work") force constant clarification.

**Working signal**: fewer unnecessary diffs, fewer rewrites from overcomplication, clarifying questions BEFORE implementation, clean / minimal PRs with no drive-by refactoring.

## Model Delegation Strategy

Default: **Haiku**. Escalate via `Agent(model=...)` with explicit model param.

| Task type | Model | Examples |
|-----------|-------|----------|
| Mechanical | `haiku` | File ops, lookup, format, scaffold, calculate, weekly-log entry insertion |
| Reasoning / Docs | `sonnet` | Spec / doc writing, analysis, code review, slide narration |
| Deep planning | `opus` | Multi-step architecture plans — **rare** |

Rules:
- Self-classify task BEFORE executing
- Spawn `Agent(model=...)` for reasoning subtasks — DO NOT switch session model
- Advisory pattern: Sonnet → Opus on demand for hard reasoning (document your own advisory workflow in your workspace's rules / memory directory)
- For LLM-as-judge subagents: bake pos/neg examples + ban heuristic-script shortcut explicitly in prompt (subagents shortcut to 87% category default otherwise)

## Comments Policy

**Never write comments unless asked.** Code should be self-documenting via names.

- Don't add task-referencing comments ("used by X", "added for Y flow", "handles case from issue #123")
- Don't explain WHAT the code does — names already do that
- Only add a comment when the WHY is non-obvious: hidden constraint, subtle invariant, workaround for specific bug
- If removing the comment wouldn't confuse a future reader, don't write it

## Edit > Write

- For existing files: use `Edit` tool, not `Write`
- Only use `Write` for new files or complete rewrites
- If 5 lines change, send 5 lines, not the whole file

## No Emojis in Files

- Never use emojis in code, comments, or generated files unless user explicitly asks
- Exception: chart icons / status indicators in HTML reports if user-approved
- Applies to commit messages too

## File Output Discipline

- Never save generated files (charts, reports, data exports) to workspace root or non-output folders
- All output goes to `<your-workspace>/output/<type>/` or `<your-workspace>/output/projects/<name>/`
- Convention: every workspace using this skill should have an `output/` root + subfolder mapping (charts/reports/data/exports). Document your own mapping in `<your-workspace>/.claude/rules/output-policy.md` or equivalent.

## Defensive Coding Patterns

### Cache file verification
- CSV / JSON caches = CACHE only, not source of truth
- Missing data → query BQ directly, NEVER use placeholder values
- See `feedback_csv_cache_must_verify.md` in auto-memory

### Market data — no hardcode
- Daily-changing fields (CPI, bank rates, gold price, RON95, USD/VND) MUST auto-fetch into versioned cache with staleness gate (50d default)
- NEVER hardcode constants in `config.py` or fallback values in templates
- Source priority: realtime / news (Google Finance, Dân Trí) > bank-official sites
- STALE warning → triggers refresh, NEVER ignored
- Pattern: `cpi_history.json` + `cpi_source.py` + 50d staleness gate

### Curated override wins scrape
- Override JSON = source of truth for curated values (e.g., bank CASA rates)
- Scraper only fills gap when override absent
- Example: Simplize wrong VCB rate (5.45%) — override JSON corrects

### Date robustness
- Derive `data_date` from `df.iloc[-1]`, NOT `REPORT_DATE − 1d`
- Mart lag can be T-2 on holidays — code must tolerate

### Pipeline preserve cache history
- Incremental mode MUST NOT clip the lower bound of cache
- Daily pipeline silently wiping backfilled history = silent data loss
- Always test backfill range AFTER incremental update

### Two cache files, different scope
- Bug pattern: 2 cache files share prefix but different scope (operational vs cumulative)
- Consumer MUST pick source matching use case — wrong pick = silent miss (calendar lookup doesn't error)
- Bug appears as model bias, not data-layer mismatch
- Document scope in each cache file's header

### State machine neighbor inheritance
- Mixing focal + neighbor states in same lookup table → must gate lookup to focal state only
- Neighbors inheriting focal's learned coefficients = category error
- Verify with edge case: pure-neighbor input should NOT return focal's coefficient

## Pipeline Fail-Alert Standard

Any scheduled job MUST send a fail-alert to the on-call recipient. Channel is org-specific (SMTP / Slack / Teams / PagerDuty / internal module). Generic pattern:

```python
# Example using a hypothetical org module — substitute YOUR notifications module
from your_org.notifications.email_on_fail import send_failure_email
send_failure_email(reason="<natural-language reason>", traceback=exc)
```
- Reason in the team's primary language (e.g., natural Vietnamese: "Pipeline daily lỗi khi đọc mart — chưa có data ngày 2026-05-08")
- NEVER paste full stacktrace in alert body — log it separately
- Subject / title: `[FAIL] <pipeline name> <date>`

## Billed-Engine Cost Discipline (BQ / Snowflake / Redshift / etc.)

- Backfill > 1 month → ALWAYS dry-run first
- Report bytes processed + estimated $ to user before running
- Prefer monthly-aggregate marts over daily marts when answer is monthly (often 10-30× cheaper)
- Engine-specific connection details (project IDs, credentials, user emails) live in **env vars / config files / workspace docs**, NOT in this skill

## LLM Eval — Score Logic, Not Result

When evaluating LLM / agent output:
- Score the **query / code logic** (dry-run only)
- DO NOT score the executed result match
- Datasource drift makes result comparison invalid

## Code Output ≠ Professional Deliverable

Raw library output is NOT a stakeholder deliverable. The gap between "the code ran" and "the artifact is professional" is large enough to matter.

Examples:
- `openpyxl` raw worksheet write → looks like a CSV pasted into Excel; FAIL for stakeholder
- `XLSXReport`-style template builder with merged cells, headers, themes → PASS
- `matplotlib` default styling → FAIL for stakeholder
- Brand-themed wrapper (e.g., `momo.apply_theme()`) → PASS
- `pptx.add_slide()` with raw textboxes → FAIL
- `PPTXReport`-style template with brand layout → PASS

Rule: when producing stakeholder-facing files (XLSX / PPTX / PDF / HTML report / chart export), USE THE TEMPLATE BUILDER, not the raw library call. If your workspace doesn't have one yet, write a thin wrapper and SAVE it — every workspace eventually needs this layer.

Why — the difference between "intern-level output" and "senior analyst output" is exactly this layer. Stakeholders read polish before content; failing this gate makes correct work look unfinished.

## Patch Ceiling — Escalate to Rebuild

After ≥3 distinct bugs in the same artifact across 2-3 patch rounds:
- STOP patching
- Surface "rebuild / handoff / switch tool" options to user
- Write a self-contained handoff spec doc
- Your role shifts to input-pipeline + planning + tool choice — NOT visual layer patching

## Reverse-Engineering = Lower Bound, Not Spec

When mapping API surface from SPA bundle / mobile app / CLI:
- This gives the LOWER BOUND of endpoints, not the complete spec
- Always: probe `OPTIONS` / test `PUT-PATCH-DELETE` / read docs before concluding "endpoint absent"

## Prototype Before Batch

When bulk-rewriting N similar items (slides, scripts, tests):
1. Prototype 1
2. User confirms cadence
3. Mass-produce remaining N − 1

Skip prototype → user rejects cadence → rewrite cost = N − 1 items. Complementary to stabilize-to-template (this rule = BEFORE ship; stabilize = AFTER ship).

## OS-Specific Gotchas (illustrative — adapt to your environment)

### Windows
- Reading files with non-ASCII chars (Vietnamese, CJK, accented Latin): set `PYTHONUTF8=1` or use `open(path, encoding='utf-8')` explicitly. Default `cp1252` codec fails on `ệ` `ỉ` `ổ` etc.
- Bash `/tmp/...` doesn't translate — use absolute Windows paths like `C:/Users/<you>/AppData/Local/Temp/...`
- MCP servers: use `cmd /c` wrapper for npx
- PowerShell 5.1 pipeline operators `&&` and `||` are NOT available — use `; if ($?) { ... }`

### macOS / Linux
- Default UTF-8 — encoding issues rare
- `/tmp` is writable + auto-cleaned
- `find` / `grep` syntax differs from PowerShell

### Cross-platform
- Use `pathlib.Path` over manual string concat — handles `/` vs `\`
- Never hardcode user paths in scripts — use `os.path.expanduser('~')` or env vars
- Line endings: use `.gitattributes` to normalize
