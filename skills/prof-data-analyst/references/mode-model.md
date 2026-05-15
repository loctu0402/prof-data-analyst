# Mode — Model (Data Modeling Pipeline)

Invoke when user asks: "build data model", "data modeling", "design DWH", "build pipeline mới", "setup mart", "dbt project", "tạo bảng fact", "data architecture", "/da-model".

## Overview — Why this mode exists

After `da-frame` Gate 3 chose "TH2 — need new data model", someone has to design the actual tables + relationships + pipeline. This mode codifies the 4 industry-standard patterns + when to pick each.

**Why (Theoretical):** Kimball (1996) for Star/Snowflake + Inmon's CIF + dbt's modular convention (2018) + Medallion (Databricks 2020+) cover 95% of analytical modeling cases. Picking based on infrastructure + stage avoids the "I'll just write 5 ad-hoc tables" trap that creates technical debt.

## When to invoke

- **TH2 path from `da-frame` Gate 3** (new tables needed)
- **Existing pipeline lacks structure** (ad-hoc tables, no schema docs)
- **Migrating from spreadsheet/CSV to DWH** (file-based → table-based)
- **Adding new domain to existing DWH** (extend pattern, not reinvent)
- **User explicitly asks to design schema**

Skip when: existing tables solve the problem + just need SQL → `/da-query`. Don't model when you can reuse.

## Four Modeling Patterns

### Pattern 1 — Kimball Star / Snowflake

**Use when:** cloud DWH (BQ / Snowflake / Redshift); classic BI workload; multiple business processes.

**Structure:**
```
              ┌─ dim_user
              │
fact_orders ──┼─ dim_product
              │
              └─ dim_date

(Star = 1-hop join; Snowflake = normalized dims with their own joins)
```

**Naming convention:**
- `dim_<entity>` — entity tables (user, product, location, date)
- `fct_<event>` — event/transaction tables (orders, sessions, transactions)
- `agg_<metric>_<grain>` — pre-aggregated for dashboards

**Grain explicit:**
- `fct_orders`: 1 row = 1 order
- `dim_user`: 1 row = 1 user (or 1 user × 1 SCD-2 version)
- `agg_revenue_daily`: 1 row = 1 day

**Pros:** industry-standard; analysts know it; tools (BI / dbt) optimized for it.

**Cons:** rigid; changes require schema migrations; not great for streaming.

### Pattern 2 — dbt Staging → Marts (Modular SQL)

**Use when:** dbt project; modular SQL transformations; cloud DWH; team has dbt skill.

**Structure:**
```
sources (raw) → stg_<source> → int_<step> → fct_<event> / dim_<entity> → agg_<dashboard>
```

**Convention** (from `DBT-learn.md`):
- `sources.yml`: register raw tables
- `stg_<source>_<table>`: 1-to-1 with source, light cleaning
- `int_<step>`: intermediate models, business logic, not user-facing
- `fct_<event>` / `dim_<entity>`: final marts
- `agg_*`: pre-aggregated for BI

**Tests** (mandatory):
- Schema tests: `unique`, `not_null`, `accepted_values`, `relationships`
- Business tests: custom SQL singular tests
- Source freshness: `loaded_at_field` + `freshness:` thresholds

**Folder structure:**
```
models/
├── staging/
│   ├── jaffle_shop/
│   │   ├── stg_jaffle_shop__customers.sql
│   │   └── _jaffle_shop__sources.yml
│   └── stripe/...
├── intermediate/
└── marts/
    ├── finance/
    │   ├── fct_orders.sql
    │   └── dim_customers.sql
    └── marketing/
```

**Materialization:**
- `view` (default for stg/int)
- `table` (for fct/dim if large)
- `incremental` (for high-volume; only new/changed rows)

**Pros:** version-controlled SQL; tests + docs first-class; modular; deployable.

**Cons:** requires dbt setup; team learning curve; not free (cloud or local install).

### Pattern 3 — Medallion (Bronze / Silver / Gold)

**Use when:** lakehouse architecture (Databricks / Delta / Iceberg); multi-stage ELT; need full audit trail.

**Structure:**
```
Bronze (raw CDC, append-only, immutable)
   ↓
Silver (cleaned, normalized, daily snapshot)
   ↓
Gold (business-ready: facts, marts, dashboards)
```

**Layer responsibilities:**
- **Bronze:** full change history (I/U/D); used for audit + rebuild only
- **Silver staging:** daily snapshot from Bronze; schema normalized; minimal logic
- **Silver core/intermediate:** atomic grain (transaction, event); business-ready schema; single source of truth
- **Silver dimension:** User Entity Dim (SCD Type 2) + User Behavioral Snapshot (monthly/daily)
- **Gold fact/mart:** atomic Fact + Periodic Snapshot Fact + Flattened Mart
- **Gold agg/dashboard:** pre-aggregated for BI filter/breakdown

**Incremental & Refresh:**
- Core / Snapshot: Sliding Window last 3 days (Delete & Insert)
- Behavioral Snapshot: Monthly Overwrite
- Fact Daily: Incremental
- User SCD: Update SCD1

**Pros:** scales to streaming; full audit trail; popular at enterprise; lakehouse-native.

**Cons:** more layers = more orchestration complexity; not optimal for tiny projects.

### Pattern 4 — DuckDB Layered (Local File-Based)

**Use when:** local file input (CSV / Excel / Parquet); single-user analyst workflow; no cloud DWH access; rapid prototyping.

**Structure:**
```
1 .duckdb file containing:
  raw_<source>      → raw imports (read_csv_auto)
  stg_<source>      → typed, cleaned
  clean_<entity>    → de-duped, joined
  mart_<purpose>    → aggregated, business-ready
  ml_<model>        → feature-engineered for ML (if applicable)
```

**Convention:**
- All layers in 1 `.duckdb` file (single artifact to ship/share)
- `CREATE OR REPLACE TABLE` for idempotency
- Schema preserved (no pandas type drift)
- Cross-table SQL natural (no pd.merge gymnastics)

**Pros:** no infrastructure; portable single file; SQL all the way down; type-preserving; fast on local data.

**Cons:** single-user (no concurrent writes); not for production scale; analytical only.

**Promote path:** prototype in DuckDB → if recurring + scale → promote schema to dbt + cloud DWH (Pattern 2).

## Choosing the pattern (decision flow)

```
Q: Have cloud DWH (BQ / Snowflake / Redshift) access?
├── YES + dbt skill in team → Pattern 2 (dbt)
├── YES + no dbt → Pattern 1 (Kimball direct in DWH)
└── NO
    ├── Have lakehouse (Databricks / Delta)? → Pattern 3 (Medallion)
    └── NO → Pattern 4 (DuckDB local)
```

Hybrid common: start Pattern 4 (DuckDB prototype) → promote to Pattern 2 (dbt) when recurring.

## Schema documentation (mandatory)

EVERY table in EVERY pattern MUST have a Table Contract:

```markdown
## <table_name>
- **Business definition:** <1-sentence purpose>
- **Grain:** 1 row = <entity> × <event> × <time>
- **Primary key:** <col(s)>
- **Partition / cluster:** <col> (if applicable)
- **Incremental & backfill strategy:** <method>
- **SLA & freshness:** <update cadence + delay tolerance>
- **Owner (Business):** <name / role>
- **Owner (Data):** <name / role>
- **Downstream consumers:** <list>
- **Metric coverage:** <metrics this table supports>
```

Save as `<project>/schemas/<table>.md` OR inline in dbt `schema.yml`. Choose 1 location; don't fragment.

**Why mandatory:** future-you (or teammate) reading this table 3 months later cannot ask the original author. Schema doc IS the institutional memory.

## Data Governance hooks

After modeling, route to `governance.md` for:
- Metric & definition governance
- Modeling & grain governance (this section enforces some)
- Data quality validation (dbt tests or equivalent)
- Access control
- Reporting governance

Modeling pattern + governance setup go together. Don't ship model without governance plan.

## Anti-patterns

| Anti-pattern | Symptom | Fix |
|--------------|---------|-----|
| **No pattern, ad-hoc tables** | 47 tables, no consistent naming, can't trace lineage | Pick 1 pattern; refactor incrementally |
| **Wrong pattern for scale** | Medallion for a 10-row CSV project | Match pattern to actual scale |
| **No grain documentation** | Joining tables produces 10× duplication | Grain doc mandatory in Table Contract |
| **Skip tests** | Bug in stg layer, propagates to marts, dashboard shows wrong number | dbt tests OR equivalent assertions in pipeline |
| **No incremental strategy** | Daily full-table rebuild → cost explodes | Pick incremental method per Refresh Strategy section |
| **Owner blank** | Issue arises, no one to ping | Table Contract Owner field is mandatory |
| **Promote prototype without docs** | DuckDB → dbt migration drops 60% of schema knowledge | Migrate schema docs together with SQL |

## Cross-references
- Pre-modeling planning: `planning-protocol.md` Gate 3 + `mode-frame.md`
- Governance after modeling: `governance.md`
- Orchestration for the pipeline: `orchestration-patterns.md` + `mode-automate.md`
- dbt details: external — see `DBT-learn.md` in user's reference folder (if accessible)
- Quality gates per layer: `quality-pipeline.md`

— part of prof-data-analyst · Loc Tu, 2026
