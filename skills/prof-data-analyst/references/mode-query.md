# Mode — Query (NL → SQL with Engine-Agnostic Guardrails)

Invoke when user asks: "viết SQL", "query data", "lấy data", "NL→SQL", "/da-query".

This mode encodes the **agentic NL→SQL workflow** in a way that is **engine-agnostic**. Concrete SQL engines (BigQuery, Postgres, Snowflake, Redshift, DuckDB) and concrete semantic layers (Cube.js, dbt-metrics, LookML, MetricFlow, or any org-specific layer) are treated as **replaceable adapters** behind the same workflow.

## The Learning Loop (workflow contract)

```
RECALL → EXPLORE → LEARN  (repeat until question answered)
```

1. **RECALL** — read the local memory / index first. Find existing patterns, schemas, gotchas.
2. **EXPLORE** — write SQL, execute against the engine, get data back. Self-correct on errors.
3. **LEARN** — write what you discovered back into memory (new patterns, new gotchas).

The more you explore, the better future runs get. This pattern is engine-independent.

## Step 0 — Request Intake (BEFORE schema discovery)

The most common failure mode of NL→SQL is jumping into SQL before confirming what the requester actually wants. A senior DA always intakes the request first. The mode encodes that intake as Step 0; only proceed to Step 1 once the user (the requester or the analyst representing them) confirms.

### 0.1 — Restate the question

In ONE sentence, paraphrase what the user asked. Surface the implicit subject + action + time window.

Example:
- User: "cho xem cashin tháng 4"
- Restate: "You want the total cashin volume for April 2026, presented as one figure."

If the restatement doesn't match what the user meant, they will correct here — cheap. SQL rewrite later is expensive.

### 0.2 — Surface implicit choices

A real request always leaves 2-5 choices unspecified. List them as a short menu, default each one, and ask for confirmation or correction.

Common implicit choices to surface:

| Dimension | Why ask | Example options |
|-----------|---------|-----------------|
| **Grain** | Same metric at daily / weekly / monthly looks different | Daily / Weekly / Monthly / Single rollup |
| **Cohort filter** | Total includes test accounts / bots / internal | All / exclude internal / exclude bots / a specific tier |
| **Aggregation** | Sum / count / count-distinct / avg / median produce different stories | Sum amount / count events / count distinct users / median per user |
| **Dedup rule** | Same event logged twice → silent inflation | Dedupe by event_id / by (user, timestamp) / no dedup needed |
| **Time window** | "Tháng 4" = Apr only, vs. up-to-Apr, vs. last-30-days | Calendar month / rolling 30d / since launch |
| **Comparison** | A single number is noise; vs prior period is signal | DoD / WoW / MoM / YoY / vs plan / no comparison |
| **Breakdown** | Headline number alone vs by dimension | None / by region / by tier / by channel |

Pick reasonable defaults; don't ask all 7 every time. Surface the 2-4 that matter for THIS question.

### 0.3 — Propose calculation logic in plain language

Before writing any SQL, state the calculation as a one-paragraph English sentence. Example:

> "Logic: SUM of `cashin_amount` from the daily user mart, filtered to `date BETWEEN '2026-04-01' AND '2026-04-30'`, excluding internal accounts. Grouped by date for the DoD series, then aggregated to one figure for the headline. Expected output: 1 headline number + 30-row daily series."

The user can spot a logic mismatch in 10 seconds reading the paragraph; they'd need 2 minutes to spot the same mismatch reading the SQL.

### 0.4 — Suggest 1-2 extensions

A senior DA proposes extensions the requester didn't ask for but probably wants. Pick the 1-2 highest-leverage ones, never more (avoid scope creep).

Common high-leverage extensions:
- Sibling metric ("you asked for cashin; would cashout same period be useful for net flow?")
- DoD / 7d-avg comparison if the request asked for a single number
- Top-K breakdown ("top 10 days / users / tiers driving the total?")
- Quality caveat ("data is T-1, last value might be partial — flag in output?")

Frame extensions as "want me to also...?" — opt-in, not assumed.

### 0.5 — User confirms → proceed to Step 1

The user picks from the menu, OR corrects the restatement, OR rejects extensions. Once they confirm, proceed to Step 1 (engine identification) and beyond.

Pattern for confirmation:
```
[restate question]
[implicit-choices menu with defaults marked]
[proposed logic paragraph]
[1-2 extension proposals]

→ Confirm / correct / extend?
```

Cost: ~30 seconds of pre-flight. Saves 2-3 SQL rewrites + stakeholder back-and-forth when intent was misread.

### When to skip Step 0

| Situation | Action |
|-----------|--------|
| User pasted explicit SQL and asks to optimize / explain / validate | Skip Step 0; jump to Step 3 self-correction |
| Request is repeat of a query run earlier in the session with same parameters | Skip Step 0; jump to cache verify (Step 5) |
| Request is one of N atomic queries in an automated pipeline | Skip Step 0; the pipeline is the intake; proceed to Step 1 |
| Request has zero implicit choices (truly atomic: "what's the row count of table X?") | Skip Step 0; jump to Step 1 |

Default: DO run Step 0 unless one of the skip conditions clearly applies.

### Why this step exists (Operational)

Real-world DA failure mode: stakeholder DMs a one-line ask, analyst writes SQL based on what they ASSUME, runs it, ships number. Two days later stakeholder says "that's not what I wanted." The fix isn't to write better SQL — it's to confirm intent before writing any SQL. Step 0 enforces that handshake. Consulting playbook calls this "structuring the question before structuring the answer."

## Step 1 — Identify the Engine + Access Layer

Ask once at the start of a session:

| Question | Default if unspecified |
|----------|------------------------|
| Which SQL engine? (BQ / Postgres / Snowflake / Redshift / DuckDB / SQLite / other) | Ask |
| Semantic / cube layer available? (Cube.js / dbt-metrics / Mimir / LookML / none) | None |
| Read-only or write? | Read-only (enforce in tool guard) |
| Cost-billed? (BQ on-demand $5/TB, others mostly flat) | Treat as billed by default — dry-run for any large scan |

Engine-specific connection details (project IDs, credentials, host/port) live OUTSIDE the skill — in env vars, config files, or workspace-specific docs. The skill does not bake them in.

## Step 2 — Discovery Tier (schema-source hierarchy)

Reading a table's schema + access scope + business meaning is the first thing every query mode does. Use the 5-tier ladder:

```
T0 — Owner-curated LLM-grade tag (any catalog tag namespace your org reserves for LLM-ready tables)
T1 — Data catalog tool DIRECT API (OpenMetadata / DataHub / Atlan / Collibra)
T2 — Access-aware metadata MCPs (mimir MCP + momo-data MCP for MoMo; equivalent for other orgs)
T3 — Engine-native INFORMATION_SCHEMA + brainstorm step-by-step with user (the domain expert)
T4 — Direct LIMIT 5 sampling (last resort, always with partition filter)
```

Stop at the first tier that fully answers "what columns, what do they mean, do I have access?". Full ladder rationale, decision tree, audit-vs-trust matrix → `references/schema-source-hierarchy.md`.

**MoMo specifics** (Mimir tag + OpenMetadata API + mimir MCP `get_domain_schema` / `glob_search` + momo-data MCP semantic cube + data portal docs) → `references/momo-extensions.md` §5.

Rule: ALWAYS try the higher tiers (T0–T2) before raw INFORMATION_SCHEMA. Owner curation + access-aware MCPs exist precisely so downstream consumers don't reinvent column meaning or hit permission errors mid-analysis.

## Step 3 — Self-Correction Loop (engine-agnostic)

Inspired by a generic agentic NL→SQL pattern (ReAct loop with guardrails — see your local copy of the architecture SPEC, if available, for the full rationale; otherwise this section suffices):

```
write SQL
  ↓
execute via tool
  ↓
tool returns either DATA or ERROR string
  ↓
if ERROR: append error to context, re-prompt with full history
  ↓
LLM reasons about the error, writes new SQL
  ↓
loop until SUCCESS or error_count > N (suggested N=3)
```

Critical: the tool wrapper must enforce **read-only** at the SQL-parse layer. Reject `DROP / DELETE / UPDATE / TRUNCATE / INSERT / ALTER / CREATE`. Use `sqlglot` or equivalent — string match alone is insufficient.

This pattern works identically across BQ / Postgres / Snowflake / etc. — only the execution adapter changes.

## Step 4 — Cost Discipline (engine-agnostic but billing-aware)

| Engine | Cost mode | Dry-run command |
|--------|-----------|-----------------|
| BigQuery | $5/TB scanned (on-demand) | `bq query --dry_run --use_legacy_sql=false "..."` |
| Snowflake | Warehouse credits per second | `EXPLAIN <query>` + check estimated bytes |
| Redshift | Cluster cost is fixed; concurrency matters | `EXPLAIN <query>` |
| Postgres | Local / VM compute | `EXPLAIN (ANALYZE, BUFFERS)` |
| DuckDB | Free, local | `EXPLAIN` |

**Discipline rule** for any billed engine:
- Before backfill / large historical scan: dry-run FIRST
- Report bytes / cost estimate to user BEFORE running
- For BQ specifically: `> 1 month` backfill → mandatory dry-run + $ report

### BQ Safety Protocol (5-gate, billed-engine specific)

When the engine is BigQuery (or any other on-demand-scan-billed warehouse), every query passes 5 gates BEFORE execution. Order matters.

| Gate | Check | Fail action |
|------|-------|-------------|
| 1. **Partition check** | Is the target table partitioned? On what column? | Unpartitioned + large table → WARN user before run; explicit confirm to proceed |
| 2. **Query has partition filter** | Does `WHERE` include the partition column with a value or range? | Missing partition filter → REWRITE the query to add one; do NOT skip the gate |
| 3. **Dry-run** | Estimated bytes processed (`bq --dry_run`) | < 100 MB: auto-proceed. 100 MB – 10 GB: surface estimate to user. > 10 GB: require user "yes" |
| 4. **Cost gate** | Convert bytes → $ at $5/TB | > $5 estimated → user-confirm required |
| 5. **Unpartitioned warning** | If the table is unpartitioned AT ALL, surface that fact + recommend using a partitioned mart equivalent if one exists | User confirms or analyst pivots to mart-monthly equivalent |

Why each gate exists:
- Gate 1 prevents accidentally querying an unpartitioned 500 GB legacy table thinking it was the partitioned mart.
- Gate 2 catches the single most common cost-surprise: forgetting `WHERE date >= ...` on a partitioned table.
- Gate 3 cost-bounds the query before execution; an estimate is free, a wrong query is not.
- Gate 4 converts bytes into a number Loc can defend to his manager.
- Gate 5 surfaces tech-debt (unpartitioned production tables) instead of silently absorbing the cost.

## Step 4.5 — Query Logic Card (audit trail)

After a query executes successfully and the result is consumed, append a one-card entry to the query log (one log file per project / session).

Card schema:
```
- Date: <YYYY-MM-DD>
- Question: <one-line user-facing question this query answered>
- Engine: <BQ / Postgres / DuckDB / ...>
- Source table(s): <table names with partition filter shown>
- Partition filter: <e.g., WHERE date BETWEEN '2026-04-01' AND '2026-04-30'>
- Dry-run cost: <bytes, $>
- Actual cost: <bytes processed, $>
- Output rows: <count>
- Result location: <CSV / DuckDB / cache file path>
- Reusable as: <"yes — same question this week" / "no — one-off">
```

Why log this:
- **Lineage** — six weeks later, "where did that 12.96T figure come from?" answers itself by grep over the log
- **Cache reuse** — same question this week? Use the cached output, don't re-run
- **Duplicate prevention** — analyst sees "yes I already ran this last Tuesday" before running it again

Where the log lives — project-specific. Default: `<your-workspace>/output/projects/<name>/query_log.md`.

## Step 5 — Cache Verification (universal pattern)

CSV / Parquet / JSON caches are **CACHE only**, not source of truth. Pattern applies regardless of engine.

Before reading a cache:
- Check schema vs needed columns
- Check date range coverage
- Missing column → query the source engine, NEVER use placeholder

After incremental cache update:
- Verify lower bound preserved (incremental must not clip historical)
- Verify no duplicates: `GROUP BY pk HAVING COUNT(*) > 1`

When 2 cache files share prefix but different scope (operational vs cumulative), document the scope in each file's header. Wrong source pick = silent miss (lookup doesn't error, bug surfaces as model bias).

## Step 6 — RECALL → EXPLORE → LEARN Memory Pattern

If the workspace has a long-term memory layout (recommended):

```
<your-workspace>/memory/
├── _index.md         ← catalog of everything learned (READ FIRST)
├── domains/          ← machine-written raw schemas (NEVER hand-edit)
├── knowledge/        ← human-written gotchas + corrections (NEVER overwrite)
├── patterns/         ← SQL queries that worked (reusable templates)
└── errors/           ← engine-specific access maps, table availability
```

Rules:
- `domains/` = machine-refreshable
- `knowledge/` = human-curated, never auto-overwritten
- Always `RECALL` from `_index.md` first
- After session, `LEARN` by writing new gotchas to `knowledge/`

If the workspace doesn't have this layout: use whatever notes / docs convention is already in place. The pattern is portable.

## Step 7 — Query Output Verification

Before returning data to user:
- [ ] Row count matches expectation (e.g., daily window of 30 days returns ~30 rows)
- [ ] No NULLs in primary key columns
- [ ] No duplicates on the expected unique key
- [ ] Dates align with expected lag (T-1 typical for daily marts; T-2 on holidays)
- [ ] Aggregations cross-validate against a canonical headline table where available

## Engine-Specific Footnotes (concrete examples)

Treat these as **illustration**, not requirement.

### BigQuery
- Job billing project ≠ data project (separate by IAM)
- Use partitioned + clustered tables; prefer monthly aggregate marts (~30× cheaper than daily) when answer is monthly
- Dry-run flag: `--dry_run`

### Postgres
- Use `EXPLAIN ANALYZE` for cost
- Index hint: check `pg_stat_user_indexes` for unused indexes
- For time-series: consider `BRIN` index on date column

### Snowflake
- Warehouse size = cost lever
- Use `RESULT_SCAN(LAST_QUERY_ID())` to inspect previous result
- Suspend warehouse when idle to save credits

### Redshift
- Sort key + dist key choice dominates performance
- AQUA acceleration vs not

### DuckDB
- Local, free, persistent file (`my_db.duckdb`)
- Excellent for ML case study DWH (see `mode-process.md` for layered tables pattern)
- Use as drop-in for Postgres-compatible queries

### Semantic / Cube Layer (generic pattern)
- Step 1: get team / datasource ID
- Step 2: fetch meta (cubes / measures / dimensions)
- Step 3: query if cube matches; fallback to raw if not
- If your org has documented its own agentic NL→SQL architecture, keep that SPEC handy at `<your-reference-dir>/agentic-sql-spec.md` and adopt the **pattern** (semantic-first), not the specific cube names

## Universal Rules Reminder

After producing query results:
1. Apply Orientation Block (3-line intro: data + range + question)
2. Apply Baseline-Noise-Impact ladder before any "finding"
3. If recommending follow-up query → 8-field Action Brief

Use `scripts/stats/baseline_noise_impact.py` to compute rungs — don't compute inline.

See `references/universal-workflow-rules.md` and `references/style-rules.md`.

## Anti-patterns

- Calling raw SQL when a semantic / metric layer exists → tech-debt, brittle to schema changes
- Computing significance / effect size inline in chat → unauditable; use `scripts/stats/significance.py`
- Skipping dry-run on billed engine for backfill > 1 month
- Treating cache as source of truth — caches are derived artifacts
- Hardcoding project / dataset names in the skill — those live in env / config / workspace docs, not in skill

## Related Files

- ReAct architecture rationale → `<your-reference-dir>/agentic-sql-spec.md` (external, if you maintain one)
- Cost projection scripts → `scripts/stats/` (in skill)
- Domain memory pattern → your workspace's long-term memory / domain-knowledge directory if present
