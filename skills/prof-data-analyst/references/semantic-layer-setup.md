# Semantic Layer Setup — Portable 6-Phase Recipe

When a project needs a semantic layer (so multiple consumers — dashboards, ad-hoc SQL users, AI agents, REST API — share one metric definition), follow this 6-phase recipe. The recipe is **engine-agnostic** — works with Cube.js, dbt-metrics, LookML, MetricFlow, or any custom-built metric layer. Concrete tool names below are illustrations; substitute your org's stack.

For the MoMo Semantic Cube (Synmetrix + Cube.js) implementation specifically, see `references/momo-extensions.md` + the full Semantic Cube reference at `<workspace>/notes/loctu-pkm/1-notes/semantic-cube-reference.md`.

## When to use this recipe

| Trigger | Action |
|---------|--------|
| ≥ 3 consumer teams asking the same metric with slightly different formulas | Build semantic layer to fix definition drift |
| Same dashboard rebuilt in 2+ BI tools with diverging numbers | Build semantic layer to single-source the metric |
| AI agent / NL→SQL needs to query data without hallucinating column meaning | Build semantic layer so agent reads `cube.measure` instead of raw SQL |
| Recurring "what does this column mean?" questions in chat | Symptom of missing semantic layer (or missing catalog — see `schema-source-hierarchy.md` first) |

When NOT to use: small team (1-2 analysts), one-off analyses, ad-hoc exploration that won't be repeated.

## Phase 0 — Discovery & scope

Before writing any cube YAML:

1. **Collect top 10-20 business questions** end-users actually ask. These are the proxy for required measures + dimensions. Without this list, you'll build cubes nobody uses.
2. **List data sources** + their grain (row-level event log? aggregated daily mart? snapshot?). Avoid double-aggregation: if source is pre-grouped, the semantic layer can't re-group correctly.
3. **Identify ownership** — who maintains cubes? Who approves schema changes? Without a clear owner, cubes rot within 3 months.

**Why this phase exists**: skipping discovery leads to "build cubes for every table" anti-pattern → 200 cubes, 5% used, 95% stale.

## Phase 1 — Architecture decisions

Pick one option per row before writing code. Document the choice + rationale in `<repo>/docs/semantic-layer-decisions.md` so future maintainers don't relitigate.

| Decision | Options | Tiebreaker |
|----------|---------|-----------|
| Engine | Cube.js / dbt-metrics + MetricFlow / Looker LookML / custom | Open-source maturity, ecosystem, team skill, BI tool requirements |
| Source | Raw fact tables / dbt mart / data lake | Prefer dbt mart (already business-cleaned). Avoid raw if PII or sensitive |
| Layout | 1 cube / file (recommended) vs multi-cube / file | 1 cube / file — easier search + MR review |
| Storage | Push-down (engine computes) vs pre-aggregation cache | Default push-down; add pre-agg only when query > 5s persistently |
| Auth | SSO + RBAC at cube layer / engine-native RBAC / both | Both, if your org has SSO infrastructure |
| Source control | Cube YAML in Git monorepo / per-team repos | Monorepo if one platform team; per-team if BU-owned |

**Why this phase exists**: architecture changes mid-project cost 10× more than upfront decision. Lock these in writing first.

## Phase 2 — Foundation cube template

Build ONE canonical cube as a reference template. Every subsequent cube clones this shape.

Mandatory elements in the template:

```yaml
cubes:
  - name: <snake_case>                    # = filename
    title: <Human Display Name>
    description: <1-3 sentences, business meaning>  # MANDATORY
    sql_table: <warehouse.dataset.table>
    public: true

    meta:                                  # MANDATORY block
      author: <name>
      authorEmail: <email>
      createdAt: <ISO 8601>
      updatedAt: <ISO 8601>
      publicMcp: false                     # true only when AI access approved
      maintainers: [<email>, <email>]
      tags: [<domain_tag>, <criticality_tag>]

    refresh_key:
      every: 1 hour                        # or: sql: SELECT MAX(updated_at) FROM ...

    measures:
      - name: count                        # MANDATORY on every cube — see anti-pattern §
        type: count
        description: "Total record count"

      # Add domain-specific measures here

    dimensions:
      - name: id
        sql: id
        type: number
        primary_key: true                  # MANDATORY if cube has joins

      - name: created_at
        sql: "TIMESTAMP({CUBE}.created_at, 'UTC')"  # wrap for engine type safety
        type: time

    # joins, segments, hierarchies as needed
```

**Lint script**: before commit, run a validator that checks every cube has: `description`, full `meta` block, `count` measure, `primary_key: true` on PK dim, time dims wrapped in `TIMESTAMP()`. Reject commit on miss.

**Why this phase exists**: template = enforced consistency. Without template, every cube uses different conventions → impossible to maintain at > 20 cubes.

## Phase 3 — Layered modeling

Build cubes in 3 layers, never mix layers in one cube:

```
Raw tables  →  Staging cubes  →  Mart cubes  →  Views (BU-facing facade)
                  ↓                  ↓             ↓
              1:1 with fact       Joined +     Includes/excludes/
              No GROUP BY         business     prefix/alias for UX
              Expose PK           rules
```

| Layer | Purpose | Naming convention | Public |
|-------|---------|-------------------|--------|
| Staging cubes | 1:1 wrap raw / dbt fact, expose row-level columns + PK | `stg_<source>` | `public: false` typically |
| Mart cubes | Business logic, joins, segments | `<domain>_<entity>` | `public: true` if cube is the canonical metric |
| Views | Facade combining multiple mart cubes for BU UX | `<use_case>_view` | `public: true` |

**Anti-pattern**: putting `GROUP BY` in cube `sql:` → engine can't re-aggregate the data → all measure types break.

**Anti-pattern**: skipping PK on cube with joins → chasm trap (one_to_many duplicates rows) → SUM/AVG silently wrong.

**Why this phase exists**: layering = separation of concerns. Without it, BU sees 200 cubes with overlapping logic → can't pick which to use.

## Phase 4 — Pre-aggregation strategy

**Default: do NOT add pre-aggregations.** Push-down to engine works fine for most queries.

Add a pre-aggregation only when ALL hold:
- Query latency > 5s consistently (measured, not guessed)
- Dashboard refresh slow (BU complaint)
- Engine cost per query is significant (e.g. BQ scanning > 1 GB / dashboard load)

When you do add one:

```yaml
pre_aggregations:
  - name: <measure>_by_<dim>_<grain>
    type: rollup
    measures: [<additive_measures>]       # MUST be additive (sum/count/min/max)
    dimensions: [<low_card_dim>]
    time_dimension: <time_dim>
    granularity: day                       # or hour/week/month
    partition_granularity: month           # one shard per month
    refresh_key:
      every: 1 day
      incremental: true
      update_window: 7 day
      sql: SELECT MAX(<time_col>) FROM <source>
```

**Rules of thumb**:
- Max 500-1000 partitions per pre-agg (else refresh time explodes)
- Query MUST match pre-agg shape (same dims + same or coarser grain) to hit it
- Non-additive measures (avg, count_distinct, ratios) MUST decompose into additive leaves before pre-agg:

```yaml
# DO this (decomposed):
measures:
  - name: total_value      # additive
    type: sum
    sql: value
  - name: row_count        # additive
    type: count
  - name: avg_value        # calculated at query time, not pre-agg
    type: number
    sql: "{total_value} / NULLIF({row_count}, 0)"

# Don't pre-agg `avg_value` directly — averages don't roll up correctly
```

**Why this phase exists**: pre-agg is a load-bearing performance tool but expensive to maintain (storage + refresh + invalidation). Default OFF; turn ON only with measured justification.

## Phase 5 — Delivery & governance

Once cubes ship, set up the consumption + governance channels:

| Channel | Use case | Set up by |
|---------|----------|-----------|
| BI tool dashboards (Looker / Tableau / Metabase) | Recurring stakeholder reports | DA + BI engineer |
| Ad-hoc Explore UI | BU self-service when dashboard doesn't cover | DA enables team access |
| AI agent (Claude / ChatGPT / Copilot via MCP) | NL → cube query | Set `publicMcp: true` only on approved cubes |
| REST / GraphQL API | App integration, automation, n8n | Backend engineer |
| Alerts | Scheduled monitor → notification on threshold breach | DA writes alert SQL |

**Governance gates**:
- All YAML in Git, MR review required (no UI-only edits in production)
- CI validates YAML syntax + lint rules (Phase 2 template) on every commit
- `publicMcp: true` requires sign-off from cube maintainer + AI-access approver
- Quarterly review: deprecate unused cubes (query log < N times in 90d), refactor duplicates

**Why this phase exists**: cubes without governance turn into the same mess as raw tables — same definition drift, same trust collapse. Governance is what makes the semantic layer pay off.

## Phase 6 — Operate

Ongoing tasks once cubes are live:

| Task | Cadence | Owner |
|------|---------|-------|
| Monitor query latency p95 + cost | Daily auto-dashboard | Platform team |
| Add `tags:` to slice / route ownership | When new cubes ship | Cube author |
| Quarterly review: usage logs, deprecate unused | Quarterly | Platform team |
| Re-fetch + audit T1 catalog descriptions for drift | Quarterly | Domain owner |
| Refactor duplicate cubes (different names, same metric) | When duplicate found | Domain owner |
| Expand views as BU asks new questions | Continuous | DA on request |

## Adapting this recipe to non-Cube.js stacks

The 6-phase structure is the same. Only the YAML syntax differs:

| Engine | "Cube" equivalent | "Measure" equivalent | "Dimension" equivalent |
|--------|-------------------|---------------------|-----------------------|
| Cube.js | `cube` (YAML) | `measure` | `dimension` |
| dbt-metrics + MetricFlow | `semantic_model` | `metric` | `dimension` |
| LookML | `view` | `measure` | `dimension` |
| MetricFlow standalone | `semantic_model` | `metric` | `entity` / `dimension` |

For any engine: keep Phase 0 (discovery), Phase 1 (architecture), Phase 2 (template + lint), Phase 3 (layering), Phase 4 (pre-agg discipline), Phase 5 (governance), Phase 6 (operate). The phases are the recipe; YAML is just notation.

## Common traps (cross-engine)

| Trap | Symptom | Fix |
|------|---------|-----|
| Building cubes before discovery (Phase 0 skipped) | Cubes built, nobody uses them | Restart from Phase 0; talk to BU first |
| `GROUP BY` in cube `sql:` | Measure math breaks at query time | Refactor to row-level `SELECT *` + let engine aggregate |
| Missing `primary_key` on joined cube | SUM / COUNT silently double-counts | Add `primary_key: true` on dim id |
| Pre-aggregating non-additive measures | Wrong numbers in dashboard | Decompose into additive leaves + calculate at query time |
| Time dim not engine-cast properly | `Could not cast literal` errors | Wrap in `TIMESTAMP()` / `TO_TIMESTAMP()` etc. per engine |
| `description` empty | BU can't self-serve | Mandate in lint (Phase 2 template) |
| `publicMcp: true` enabled before AI approval | Unaudited AI access to sensitive cubes | Gate behind explicit sign-off |
| `tags:` empty | Can't route ownership / slice by domain | Mandate at least domain + criticality tag |

## Cross-references

- Schema discovery tiers (PRE-requisite to building semantic layer) → `references/schema-source-hierarchy.md`
- MoMo-specific implementation (Synmetrix + Cube.js + momo-data MCP) → `references/momo-extensions.md`
- Full Semantic Cube spec (MoMo) → `<workspace>/notes/loctu-pkm/1-notes/semantic-cube-reference.md`
- Data modeling patterns (upstream of semantic layer) → `references/mode-model.md`
- Governance (6-section framework) → `references/governance.md`

## Why this rule exists

Without a recipe, every semantic layer rollout reinvents Phase 0–1 mistakes (no discovery, no architecture write-down, no template). After 5 rollouts you have 5 inconsistent cube codebases that the same team can't maintain because each follows different conventions. The recipe = forced consistency. Future maintainers (including AI agents) read this recipe + the cube YAML and know exactly what they're looking at.
