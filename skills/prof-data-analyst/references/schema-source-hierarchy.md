# Schema Source Hierarchy — Where to Read Schema From, In Order

Most DA work starts the same way: "what columns does this table have, and what do they mean, and do I have access?". The naive answer (`SELECT * FROM table LIMIT 5`) is the LAST resort, not the first. This reference encodes the **preferred tier ladder** for answering that question.

The ladder is engine-agnostic — concrete tool names (BigQuery `INFORMATION_SCHEMA`, OpenMetadata, `mimir.*` tag namespace, semantic-cube layer, NL→SQL MCP) are illustrative. Substitute your org's equivalents.

## The Five Tiers (read top-down, stop at the first that suffices)

| Tier | Source | What you get | Cost | When to use |
|------|--------|--------------|------|-------------|
| **T0** | Owner-curated LLM-grade tag (e.g. MoMo `mimir.*` tag in OpenMetadata) | Plain-language descriptions + sample queries + business meaning + lineage hint, deliberately written for AI consumption | Free (one tag fetch) | ALWAYS check first if your catalog supports it |
| **T1** | Data catalog tool DIRECT API (OpenMetadata / DataHub / Atlan / Collibra) | Table + column descriptions, tags, ownership, lineage — full catalog visibility regardless of user access | One API call (PAT) | When T0 absent or thin |
| **T2** | Access-aware metadata MCPs (org-provided) — for MoMo: **mimir MCP** + **momo-data MCP** | Domain knowledge + schema + business glossary + semantic cube layer, FILTERED to tables the current user can actually access. Plus data-portal docs, sample query patterns, access-list info | A few MCP tool calls | When T1 incomplete / doesn't reflect user access scope / no semantic cube metadata in catalog |
| **T3** | Engine-native `INFORMATION_SCHEMA` + brainstorm with user | Column names + types + partition keys + NULL flag (baseline floor); combine with asking the user (domain expert) for context the catalog can't provide | One query + conversational | Always available; use AFTER T0–T2 to fill the structural gap + tap human domain knowledge |
| **T4** | Direct sampling (`LIMIT 5` with partition filter) | Actual data values + type inference from rows + sentinel discovery | One query (billed) | Last resort when T0–T3 leave gaps about actual data shape / NULL convention / format quirks |

## Why this ordering

| Rung | Why it sits where it does | What you lose by skipping it |
|------|---------------------------|------------------------------|
| T0 — owner-curated LLM tag | Owner has DELIBERATELY invested for AI/LLM consumption → highest signal-to-noise per token | Skip → read raw schema, hallucinate column meaning, waste owner's curation effort |
| T1 — catalog direct API | Catalog = org-wide single source of truth for column meaning; full visibility (admin scope) | Skip → 5 teams write 5 different definitions of the same column |
| T2 — access-aware MCPs | (a) MCPs filter to YOUR access (no "permission denied" surprise at query time), (b) bundle multiple sources (semantic cube + data portal + glossary), (c) per-user view of what data is actually queryable, (d) often expose `description` / `schema_notes` / `access_list` tools beyond what catalog REST has | Skip → query a table, hit permission error mid-analysis; or miss the semantic-cube business logic that already encodes the metric you're recomputing |
| T3 — INFORMATION_SCHEMA + brainstorm with user | Engine truth (partition keys cost-critical) + human user has domain context that no metadata system encodes ("this `flag_x` column always = 1 since 2024-Q3, ignore it") | Skip → guess column existence, miss the human shortcut, waste sampling cost |
| T4 — sampling | Only way to discover actual data distribution + edge cases (NULL sentinels, format quirks) | Skip → assume idealized data, miss the `0.00` that means "missing" |

## Tier 0 — Owner-curated LLM-grade tag (highest priority when available)

Some catalogs let table owners apply a special tag indicating "this table has been deliberately curated for LLM / AI agent consumption". Owners populate the tag with:

- Plain-language table description (1-2 paragraphs)
- Per-column business meaning (not just type)
- Common query patterns + canned examples
- Joins to related tables
- Known gotchas / sentinels / partition discipline

**Example — `mimir.*` tag pattern (any catalog can adopt)**:

A catalog can reserve a `mimir.*` tag namespace specifically for LLM-grade curation. A table tagged `mimir.<business_unit>` means the owner of that BU has invested in LLM-grade schema curation for downstream agent use. The MoMo-specific implementation of this pattern is documented separately in `references/momo-extensions.md`.

Discovery pattern:
```
1. Fetch table metadata from catalog (e.g. OpenMetadata API)
2. Check tag list for tags matching `mimir.*` namespace
3. If present → read the linked content / tag definition FIRST before any other tier
4. If absent → proceed to T1 (catalog baseline curated layer)
```

In other orgs, the equivalent might be: a `llm-ready` tag, a `documented-for-agents` boolean property, a `description_for_ai` custom property. Whatever your catalog encodes as "owner has invested for AI" — that's T0.

## Tier 1 — Data catalog DIRECT API (OpenMetadata / DataHub / Atlan / Collibra)

Most orgs ship one canonical catalog tool. Direct REST/GraphQL API access gives full catalog visibility (admin scope, regardless of which tables the current user can actually query).

**Engine examples**:

| Tool | API style | Auth | Read pattern |
|------|----------|------|--------------|
| OpenMetadata | REST (OpenAPI 3) | PAT bearer | `GET /api/v1/tables/name/<fqn>?fields=columns,description,tags,version` |
| DataHub | GraphQL | OIDC / token | GraphQL query `dataset(urn: ...)` |
| Atlan | REST | API token | `GET /api/atlas/v2/entity/uniqueAttribute/type/Table?attr:qualifiedName=<fqn>` |
| Collibra | REST | OAuth2 | `GET /rest/2.0/assets?type=Table&name=<name>` |

**MoMo specifics**: see `references/momo-extensions.md` → "OpenMetadata workflow" section.

### What to check in T1
- Table-level description (1-paragraph)
- Per-column descriptions (the 80% of the value)
- Tags (T0 tag may surface here as a regular tag)
- Last `updatedAt` + `updatedBy` (staleness check)
- Cross-references / lineage to upstream / downstream tables

### When T1 is wrong / incomplete
Catalog curation can be silently incorrect — a `cashin_gmv` column description that literally said "cashout" was found in production (2026-05-15 incident). Audit: if T1 description contradicts T4 sample, T4 wins → fix T1 via curated push.

T1 is also INCOMPLETE for: per-user access scope, semantic-cube business logic, business glossary terms, sample queries by other analysts, journey/event tracking metadata. For those → T2.

## Tier 2 — Access-aware metadata MCPs (NEW — bridges T1 and engine-native)

T1 catalog API shows you EVERYTHING in the catalog. T2 MCPs show you what YOU can actually query, with extra metadata layers stitched in.

When the catalog API (T1) doesn't have the table, has thin curation, or doesn't tell you whether you have access → use the org's access-aware metadata MCPs. These typically wrap multiple sources (catalog + semantic layer + business glossary + lineage + data portal docs) into one user-scoped interface.

### MoMo specifics — two MCPs cover T2

| MCP | What it scopes | Tools relevant to schema discovery |
|-----|----------------|------------------------------------|
| `mimir-da-sql` MCP | Tables in user's BQ access scope across MoMo domains, with domain knowledge layered on | `get_domain_schema` (returns schema + descriptions filtered to user access), `glob_search` (find tables matching pattern in user scope) |
| `momo-data` MCP | Semantic Cube + Data Portal + Journey + Apollo, scoped to user's team membership | `semantic-get-team-data` → `semantic-fetch-meta-by-id` (cube measures + dimensions + descriptions); `data-portal-search-document-content` (find existing docs about a table); `data-portal-list-documents` (browse domain folders); `apollo-get-allowed-filter-columns` (event schema if applicable) |

### Why T2 sits above T3
- **Access-awareness** — MCP returns ONLY tables you can query → no permission denied surprise during analysis
- **Semantic richness** — cube YAML has measures + dimensions + business logic that catalog descriptions don't capture
- **Documentation cross-link** — data portal docs may have analyst-written context about the table (use cases, gotchas, prior analyses)
- **Multi-source aggregation** — one MCP call returns catalog + cube + docs + glossary in unified form

### Discovery pattern (MoMo)
```
1. mimir MCP → get_domain_schema(table_or_domain) → check description + access flag
   - If returned schema rich enough, STOP
2. momo-data MCP → semantic-get-team-data → semantic-fetch-meta-by-id(datasource)
   - Find cube wrapping the table → read measures + dimensions
3. momo-data MCP → data-portal-search-document-content(table_name)
   - Find any docs analysts wrote about this table → richer than catalog alone
```

For non-MoMo orgs: substitute your access-aware metadata MCP (e.g. dbt-mcp, semantic-mcp, dataworks-mcp). If your org has NO access-aware MCP layer, skip T2 and go T1 → T3.

## Tier 3 — INFORMATION_SCHEMA + brainstorm step-by-step with user

When T0–T2 still don't fully answer the question, combine two cheap-but-effective sources:

### 3a. Engine-native INFORMATION_SCHEMA

Every SQL engine ships an `INFORMATION_SCHEMA` (or equivalent system catalog). This is the FLOOR for structural info.

| Engine | Schema query |
|--------|--------------|
| BigQuery | `SELECT column_name, data_type, is_nullable FROM \`<project>.<dataset>.INFORMATION_SCHEMA.COLUMNS\` WHERE table_name='<t>'` |
| Postgres | `SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name='<t>'` |
| Snowflake | `SHOW COLUMNS IN <db>.<schema>.<t>` |
| Redshift | `SELECT column_name, data_type FROM information_schema.columns WHERE table_name='<t>'` |
| DuckDB | `DESCRIBE <t>` or `SELECT * FROM information_schema.columns WHERE table_name='<t>'` |

**Partition discipline note for BQ**: also check `INFORMATION_SCHEMA.TABLES.partitioning_column` to know which column to filter on. Forgetting this is the #1 BQ cost-surprise (mode-query.md §4 gate 2).

### 3b. Brainstorm step-by-step with the user (the domain expert)

The user (human DA, PO, or analyst sitting next to you) often knows things no metadata system encodes:
- "This `flag_X` column has always been 1 since Q3 2024 — ignore it"
- "Column `amount` is in xu before 2026-04-01, VND after"
- "Table is supposedly daily but we only really have data from `dt='2025-09-01'` onward, anything before is backfill"
- "There's a sibling table you should also check: `<sibling>` (~30× cheaper for monthly grain)"
- "Talk to <owner-email> before assuming anything — there was a swap bug last quarter"

Ask the user, step by step, in plain language:
1. "Do you know what each of these columns means? [list T3a output]"
2. "Are there sentinel values, deprecated columns, or known data-quality issues?"
3. "Is there a sibling / canonical / preferred table for this question?"
4. "Who owns this table if I need to ask for clarification?"

The user's domain context is THE missing layer. T3b is "ask the human" — never skip it just because you have raw schema.

### When you DON'T get enough from T3
- What the column MEANS BUSINESS-WISE if user hasn't seen it (rare but possible)
- Sentinels, edge cases that the user hasn't personally encountered
- Distributional info (NULL %, p95, mode)

→ Drop to T4.

## Tier 4 — Direct LIMIT 5 sampling (last resort)

When T0–T3 still leave open questions about ACTUAL DATA (not schema), sample:

```sql
SELECT * FROM <table> WHERE <partition_filter> LIMIT 5
```

Always include the partition filter even for sampling — unpartitioned LIMIT 5 on a large table can still scan TB on some engines.

**What you learn from T4**:
- Actual values + format (`"2026-05-16"` vs `1715817600` epoch?)
- NULL frequency in the sample
- Sentinel values (`-1` / `0` / `"N/A"` patterns)
- Multi-format quirks (mixed case, trailing whitespace, leading zeros)

**What you don't learn from T4**:
- Whether the sample is representative
- Edge cases that occur 0.1% of the time
- Business meaning of values you can see

## Decision tree (one-page, updated)

```
Question: What columns does <table> have, and what do they mean, and do I have access?
   │
   ▼
T0 — Does the catalog expose an owner-curated LLM tag (e.g. mimir.*)?
   ├── YES → Read T0 content. If sufficient, STOP.
   │         If still incomplete, drop to T1 for column-level fill-in.
   ▼ NO
T1 — Does the catalog DIRECT API have a curated entry for this table?
   ├── YES → Read table desc + column descs + tags. If sufficient, STOP.
   ▼ NO (or thin / stale / unsure of access)
T2 — Does the org have access-aware metadata MCPs (mimir / momo-data / equivalent)?
   ├── YES → Query MCP for: (a) per-user-access schema, (b) semantic cube layer if any,
   │           (c) data portal docs about this table. STOP if MCP covers question.
   ▼ NO MCP or MCP returns nothing
T3 — Run INFORMATION_SCHEMA (engine query for raw column list + partition key).
     THEN brainstorm step-by-step with the human user:
       "Here are the columns I found — do you know what each means?"
       "Sentinels / deprecated / known issues?"
       "Sibling tables / owner contact?"
   │
   ▼ Still gaps about ACTUAL DATA shape?
T4 — Sample 5 rows with partition filter. Verify your T3 inference + spot sentinels.
   │
   ▼
   Combine findings. If contradictions across tiers → trust the higher tier UNLESS data
   (T4) directly contradicts (then T4 wins + flag T0/T1/T2 for correction).
```

## When to AUDIT versus when to TRUST

| Scenario | Action |
|----------|--------|
| T0 / T1 / T2 description present, plausible, fresh (< 90 days `updatedAt`) | TRUST, proceed |
| T0 / T1 description stale (> 180 days) | TRUST for now, flag for re-audit |
| T2 MCP says user lacks access | Believe it; do NOT try `SELECT *` to confirm (wastes quota + may trigger audit log) |
| T0 / T1 description plausible but you've never used this column → spot-check with T4 sample | AUDIT lightly |
| T1 description contradicts T4 sample (e.g. desc says "cashout" but data is positive deposits) | T4 WINS → curate T1 fix (see momo-extensions.md → "OpenMetadata curation playbook") |
| T0 missing AND T1 thin (< 50 char description) AND T2 MCP returns nothing meaningful AND table is critical to downstream analysis | INVEST: write T0 / T1 curation FIRST, then continue analysis. Brainstorm in T3 with user about what good description SHOULD say |

## Cross-references

- `references/mode-query.md` Step 2 — invokes this hierarchy when a query mode starts
- `references/momo-extensions.md` — MoMo-specific T0/T1/T2 implementations (Mimir tag, OpenMetadata, mimir MCP, momo-data MCP semantic cube + data portal)
- `references/semantic-layer-setup.md` — building T2 semantic-cube layer from scratch when none exists
- `references/domain-discovery-protocol.md` — new-domain L1/L2/L3 generation builds on T0–T3 findings

## Why this rule exists

Reading TIME spent on schema discovery dominates the first 30 min of any new analysis. Without a tier ladder, agents and humans both default to T4 sampling (slow, billed, limited insight) or T3 INFORMATION_SCHEMA (free but meaningless without business context). The ladder forces you to USE the org's investment in T0/T1/T2 — that investment exists precisely so downstream consumers don't have to reinvent column meaning.

T2 (access-aware MCPs) was added in v3.3 after observing that T1 catalog API and T3 INFORMATION_SCHEMA both fail the SAME way: they show you what the org has, not what YOU can use. Access-aware MCPs bridge that gap + bundle semantic-cube business logic + data portal docs that T1 alone doesn't expose. Skipping T2 → permission errors mid-analysis + reinvented metric definitions + missed analyst-written documentation.
