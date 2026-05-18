# Domain Discovery Protocol

> When the analyst encounters a NEW domain (table family, product area, business unit) for the first time, follow this protocol to build the L1/L2/L3 domain hub safely.

## Overview — Why this file exists

Domain knowledge tends to scatter across notebooks, ad-hoc queries, and partial chat threads. The L1/L2/L3 Domain Hub pattern (`<your-workspace>/domain-knowledge/<product>/`) only works if discovery is structured. Unstructured discovery = expensive full scans + missed partition keys + cost surprises.

## Outline (story-flow check)

1. Step 0 — Registry check (does the domain already exist?)
2. Step 1 — Schema scan (metadata only, no data fetch)
3. Step 2 — Partition-safe sample (read 1 partition, not all)
4. Step 3 — User approval gate (before generating hub files)
5. Step 4 — Auto-generate L1/L2/L3 hub
6. Step 5 — Validate hub against canonical queries
7. Cost ceiling + escape valve

A reader scanning headings should be able to predict each step.

---

## Step 0: Registry check

**Action:** Search `<your-workspace>/domain-knowledge/` for any existing hub matching the user's domain name (fuzzy match).

**Pass:** Match found → load existing hub, do NOT re-discover. Update only if user reports staleness.
**Fail:** No match → continue to Step 1.

**Why (Operational):** Re-discovering an existing domain wastes BQ budget and produces conflicting hubs. The registry check is 1 file read; the alternative is a full scan.

## Step 1: Schema scan (metadata only)

**Action:** Use `INFORMATION_SCHEMA` queries (BigQuery) or equivalent. Read column names, types, partition keys, clustering keys. Do NOT fetch row data.

**BQ pattern:**
```sql
SELECT table_name, column_name, data_type, is_partitioning_column, clustering_ordinal_position
FROM `<dataset>.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name LIKE '<prefix>%'
ORDER BY table_name, ordinal_position
```

**Cost ceiling:** INFORMATION_SCHEMA is free. If it ever costs more than $0.01, stop and investigate — you queried the wrong thing.

**Output:** Schema dump per table — column names + types + partition key + clustering.

**Why (Operational):** A schema dump is 1 cheap query; the alternative is `SELECT * LIMIT 100` on N tables, each potentially full-scanning if partition keys are wrong.

## Step 2: Partition-safe sample

**Action:** Query ONE partition with an explicit partition filter. Choose the most recent complete partition (not today — today may be partial).

**BQ pattern:**
```sql
SELECT *
FROM `<dataset>.<table>`
WHERE <partition_col> = '<yesterday>'
LIMIT 100
```

**Cost ceiling:** Each sample query should report <100 MB scanned. If a partition is >1 GB, drop to 1-hour slice or sample by user_id hash.

**Output:** Per table, 100 rows of representative data.

**Why (Causal):** A partition-safe sample reveals real data shape (null patterns, value distributions, encoding quirks) that schema alone cannot. Without it, the L2 (column-level) docs are guesses.

## Step 3: User approval gate

**Action:** Present a discovery summary to the user before generating hub files. Include:
- List of tables found
- Partition key per table
- Estimated data volume (sum of rows per partition × partition count)
- Cost estimate for any planned aggregations
- Proposed L1/L2/L3 file structure

**Format:**
```
Domain: <name>
Tables found: <count>
Total estimated volume: <X GB across N partitions>
Estimated cost to run baseline aggregations: <$Y>
Proposed hub files:
  - L1 (_index.md): overview + key questions answered
  - L2 (tables.md): per-table schema + sample
  - L3 (kpis.md): canonical KPIs + SQL snippets
  - L3 (edge-cases.md): known gotchas
Proceed? [y/N]
```

Wait for explicit user confirmation. If user says "no" or asks for changes, iterate.

**Why (Operational):** Generating hub files commits 30-60 minutes of work and may pull GB of data for KPI baselines. Cheap to confirm scope; expensive to discover wrong scope after generation.

## Step 4: Auto-generate L1/L2/L3 hub

**Action:** Create `<your-workspace>/domain-knowledge/<product>/` with these files:

| File | Content |
|------|---------|
| `_index.md` | L1 — overview, key questions, navigation to L2/L3 files |
| `tables.md` | L2 — per-table schema (from Step 1), partition key, sample (from Step 2), join patterns |
| `kpis.md` | L3 — canonical KPI definitions + reference SQL |
| `edge-cases.md` | L3 — known gotchas (mart lag, dup risks, semantic quirks) |

Use whatever domain-contribution template exists in your workspace.

**Why (Operational):** A 4-file structure converges; a 10-file structure fragments. L1 + L2 + 2×L3 covers 95% of future queries; more files → harder to maintain.

## Step 5: Validate hub against canonical queries

**Action:** Pick 2-3 canonical questions for the domain (e.g., "DAU last 7 days," "GMV by tier last month"). Write each query using ONLY the hub files. If the hub is missing information to answer the canonical question, the hub is incomplete — return to Step 1 with the gap noted.

**Pass:** All 2-3 canonical queries write cleanly from hub.
**Fail:** Hub missing a join key, partition gotcha, or KPI definition. Patch the hub before declaring done.

**Why (Empirical):** A hub that cannot answer its own canonical questions is decoration. Validation catches gaps that look fine in the abstract but block real use.

---

## Cost ceiling + escape valve

**Hard ceilings:**
- Step 1 (schema scan): <$0.01 per domain. If exceeded → wrong dataset.
- Step 2 (partition sample): <$0.10 per domain (5 tables × $0.02 each). If exceeded → use smaller slice.
- Step 5 (validation queries): <$1.00 total. If exceeded → consult user before continuing.

**Escape valve:**
If discovery hits a hard ceiling or stalls 2x on the same step, STOP and surface to user with the partial discovery so far. Do not run unbounded discovery.

**Why (Operational):** Discovery cost should be a small fraction of value delivered. Hard ceilings prevent the protocol from becoming the expense it was meant to prevent.

---

## Anti-patterns

- **Skipping Step 0 (registry check).** Wastes BQ budget on already-known domains.
- **Step 1 with `SELECT *` instead of INFORMATION_SCHEMA.** May scan TB of data for column names that are free in metadata.
- **Step 2 with no partition filter.** Single biggest source of cost surprise.
- **Step 4 before Step 3 user approval.** Generates 4 files, user says "wrong scope," delete + redo.
- **Step 5 skipped.** Hub looks complete, fails on first real use.

## Cross-references

- BQ Safety Protocol (partition + dry-run + cost gate) → `mode-query.md`.
- L1/L2/L3 Domain Hub structure → whatever domain-contribution template your workspace maintains.
- Cost discipline meta → engine-specific cost guardrails in `mode-query.md` Step 4.

## Why this rule exists (Rule 4 meta)

Domain discovery sits at the crossroads of cost discipline and knowledge capture — done poorly it burns BQ budget AND produces hubs that go stale. A 5-step protocol with explicit gates and ceilings produces converging discovery: known time, known cost, known output shape.
