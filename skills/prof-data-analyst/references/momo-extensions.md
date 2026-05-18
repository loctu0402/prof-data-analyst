# MoMo Stakeholder Extensions

This reference bundles the MoMo-specific tooling (Semantic Cube, momo-data MCP, Mimir tags, OpenMetadata curation) that make this plugin a **complete harness for MoMo DA stakeholders**. The rest of the plugin is portable across companies; this file is the org-specific layer.

**Audience**: anyone using this plugin within MoMo's data platform (Semantic Cube + momo-data MCP + `datacatalog.mservice.io`). Non-MoMo users can ignore this file entirely — the plugin's portable behavior is unaffected.

## What MoMo adds on top of the portable plugin

| Capability | MoMo tool | Plugin reference (generic) |
|-----------|-----------|---------------------------|
| Semantic layer | Semantic Cube (Synmetrix + Cube.js) at `semanticcube-doc.mservice.io` | `references/semantic-layer-setup.md` |
| Schema catalog | OpenMetadata at `datacatalog.mservice.io` | `references/schema-source-hierarchy.md` T1 |
| LLM-grade schema tag | `mimir.*` tag namespace | `references/schema-source-hierarchy.md` T0 |
| MCP gateway | `momo-data` MCP (gateway: `mdp-mcp-gateway.mservice.io`) | (none — MoMo-only) |
| NL→SQL agent | Mimir (via MCP `mimir-da-sql`) | `references/mode-query.md` Step 2 semantic-first |
| Apollo trackify | Mini-app event explorer | (none — MoMo-only) |
| Data Portal | Documentation governance | (none — MoMo-only) |
| Journey Data | User journey analytics | (none — MoMo-only) |

## 1. Semantic Cube (Synmetrix + Cube.js)

MoMo's semantic layer = Synmetrix (open-source fork) + Cube.js core + Hasura (metadata GraphQL) + React UI (Explore / Models / Dictionary / Settings).

**Onboarding**: keep a full local reference for Semantic Cube spec + 5-step workflow + build recipe (see the publicly-linked docs at the bottom of this file). Cube YAML conventions, meta block, measure/dimension/join semantics, pre-aggregations, and Đặc Tả Tiêu Chuẩn are mandatory reading before authoring cubes.

**Quick links**:
- Production: `https://semanticcube-doc.mservice.io/docs/intro`
- Đặc Tả Tiêu Chuẩn (mandatory): `https://semanticcube-doc.mservice.io/docs/basic/data_modeling/cubejs_model_specification`
- Support: Google Chat group ["Claude With MoMo Data"](https://chat.google.com/app/chat/AAQAokD9l24)

**Workflow (5 steps, abbreviated)**:
1. **Create Team** — ping `son.hua1@` or `chinh.nguyen2@` with team name + admin list (1 business day)
2. **Create Data Source** — BQ / Lakehouse (Hive) / StarRocks (MySQL connector). BQ needs Service Account + Billing Project ID (request via `hai.nguyen1@`)
3. **Build Model (Cube)** — write YAML manually or auto-generate from `catalog.dataset.table`; MUST follow Đặc Tả Tiêu Chuẩn; prefer Git-versioned YAML
4. **Test via Explore** — measures + dimensions interactively; check generated SQL + result sanity
5. **Deliver** — Looker Studio / Ad-hoc Explore / Claude Desktop (MCP) / REST API / Alert

**Critical rules from Đặc Tả Tiêu Chuẩn**:
- Cube name = file name (snake_case)
- Cube MUST have `description` (Dictionary indexing)
- Meta block MANDATORY (author, email, dates, publicMcp, maintainers, tags)
- Cube MUST have `count` measure (`type: count`) — Looker bar-chart fails without it
- Joined cubes MUST set `primary_key: true` on dim id — prevents chasm/fan trap
- BQ time dim MUST wrap `TIMESTAMP({CUBE}.col, 'Asia/Ho_Chi_Minh')`
- NO `GROUP BY` in cube `sql:` — Cube re-aggregates from row level
- `publicMcp: true` only after AI access approved

For building a brand-new semantic layer (anywhere, not just MoMo), use the portable recipe in `references/semantic-layer-setup.md`.

## 2. momo-data MCP — the gateway

MoMo runs a unified MCP gateway at `https://mdp-mcp-gateway.mservice.io/servers/<server_id>/mcp` exposing multiple data tools through one HTTP MCP server. The plugin user adds it to their MCP config (see `<plugin_root>/mcp/example-momo-mcp.json`) to unlock these tools.

### Tool groups bundled in `momo-data` MCP

| Tool group | Prefix | What it does |
|-----------|--------|--------------|
| Semantic Cube | `semantic-*` | Query Semantic Cube programmatically (3-step: team → meta → load) |
| Data Portal | `data-portal-*` | Read/list/upload documentation entities (folders, documents, attachments, versions, feedback) |
| Journey Data | `journey-data-journey-*` | User journey analytics (list / detail / conversion / comparison / duration) |
| Apollo (mini-apps) | `apollo-*` | Mini-app event tracking + trackify search / validate (events, mini-apps, filters) |

### Semantic Cube tools (3-step query)

```
1. semantic-get-team-data        → returns teams + datasource_id list
2. semantic-fetch-meta-by-id(id) → returns cubes + measures + dimensions
3. semantic-load(query)          → executes cube query, returns rows
```

Optional: `semantic-greet`, `semantic-get-datasource-by-name`, `semantic-fetch-meta-by-id` for finer discovery.

### Data Portal tools (documentation governance)

Use when the analysis needs to reference or update documentation:
- `data-portal-list-folders` / `data-portal-list-documents` → browse
- `data-portal-get-folder` / `data-portal-get-document` / `data-portal-get-document-versions` → read
- `data-portal-search-documents` / `data-portal-search-document-content` → grep
- `data-portal-upload-attachment` / `data-portal-rename-document` / `data-portal-restore-document-version` → write
- `data-portal-submit-feedback` / `data-portal-list-feedback` → feedback loop

### Journey Data tools (user journey analytics)

Pre-built journey-analytics queries that would otherwise require complex window-function SQL:
- `journey-data-journey-list` → list available journey definitions
- `journey-data-journey-get-data` / `journey-data-journey-get-detail` → fetch step-by-step events
- `journey-data-journey-get-conversion` → conversion funnel
- `journey-data-journey-get-comparison` → A/B journey comparison
- `journey-data-journey-get-duration` → time-spent-per-step

### Apollo tools (mini-app event tracking)

For mini-app analytics:
- `apollo-execute-explorer-with-filters` / `apollo-execute-explorer-with-filter-groups` → ad-hoc explorer with filters
- `apollo-execute-extended-explorer` → richer query
- `apollo-get-all-events` / `apollo-get-mini-apps` / `apollo-get-allowed-filter-columns` → discovery
- `apollo-trackify-search-events` / `apollo-trackify-search-mini-apps` → search
- `apollo-trackify-validate-event` / `apollo-trackify-validate-mini-app` → validate tracking config

### When to use which group

| Question | Use |
|----------|-----|
| "TTT AUM tháng 4?" | semantic-* (cube already has metric) |
| "Cấu trúc folder bài MoAT là gì?" | data-portal-list-folders |
| "Conversion rate flow signup → first_cashin?" | journey-data-journey-get-conversion |
| "Mini-app X có event Y không?" | apollo-trackify-search-events |

## 3. Mimir — the NL→SQL agent + tag

Mimir is two things at MoMo:

### 3a. Mimir as MCP (`mimir-da-sql` MCP)

A separate MCP server (`mimir-da-sql`) exposes an NL→SQL agent specialized for MoMo's BQ schemas. Add to MCP config (`<plugin_root>/mcp/example-momo-mcp.json`).

Tools (when registered, schema differs from `momo-data`):
- `execute_sql` — run SQL against MoMo BQ with cost guardrails
- `get_domain_schema` — fetch schema for a domain (uses Mimir tag if present, else INFORMATION_SCHEMA)
- `glob_search` — search tables matching a pattern

Use Mimir MCP when the question is "give me data X" and you don't want to write SQL yourself. For tighter control or learning purposes, write SQL directly with the patterns in `references/mode-query.md`.

### 3b. Mimir as a tag namespace (T0 schema source)

Within OpenMetadata (`datacatalog.mservice.io`), the tag namespace `mimir.*` flags tables that owners have **deliberately curated for LLM / AI agent consumption**. Tagged tables typically have:

- Rich plain-language descriptions per column (not just type)
- Sample query patterns
- Business meaning + edge cases
- Cross-references to related tables

**Example**: the TTT mart `mart_ttt_daily_user_record` carries tag `mimir.BU_FS_InvestTech_Wealth_management` (URL: `https://datacatalog.mservice.io/tag/mimir.BU_FS_InvestTech_Wealth_management`). When you encounter a table with a `mimir.*` tag, **read the tag content FIRST** — it's the highest-quality schema source available (T0 in the schema-source-hierarchy ladder).

**Discovery flow**:
```python
import requests
H = {"Authorization": f"Bearer {PAT}"}
tbl = requests.get(
    f"https://datacatalog.mservice.io/api/v1/tables/name/bigquery.momovn-prod.<dataset>.<table>?fields=tags,columns,description",
    headers=H,
).json()
mimir_tags = [t for t in tbl.get("tags", []) if t["tagFQN"].startswith("mimir.")]
if mimir_tags:
    # T0 hit — read tag content for LLM-grade schema
    for tag in mimir_tags:
        tag_info = requests.get(
            f"https://datacatalog.mservice.io/api/v1/tags/name/{tag['tagFQN']}",
            headers=H,
        ).json()
        # tag_info has owner-curated content
```

## 4. OpenMetadata workflow (T1 schema source + curation)

OpenMetadata (`datacatalog.mservice.io`) is MoMo's canonical data catalog. Two layers:
1. **Auto-ingested** (column names, types, partition keys synced from BQ) — never edit
2. **Curated** (table desc, column desc, tags, ownership, lineage) — humans + agents own this

Full playbook (fetch → audit → dry-run → push → cross-validate) is summarized below; deep mechanics are at `https://datacatalog.mservice.io/swagger`. Key API mechanics:

### Auth + endpoints

```python
BASE = "https://datacatalog.mservice.io"
PAT = "<bearer_token>"   # rotate weekly via OM UI → user settings → access tokens
H = {"Authorization": f"Bearer {PAT}"}

# Read by FQN
GET {BASE}/api/v1/tables/name/bigquery.momovn-prod.<dataset>.<table>?fields=columns,description,tags,version

# Read by UUID
GET {BASE}/api/v1/tables/{uuid}?fields=columns,description,tags,version

# PATCH (JSON Patch RFC 6902)
PATCH {BASE}/api/v1/tables/{uuid}
Headers: Content-Type: application/json-patch+json  # ← MANDATORY, NOT application/json
Body: [{"op": "add", "path": "/columns/0/description", "value": "<new>"}, ...]
```

### 5-phase curation pattern

When refactoring schema descriptions (e.g. HTML→markdown cleanup, content fix, bi-ref insertion):

1. **Discovery** — fetch full schema, dump to UTF-8 file for diffability, count cols, scan formats
2. **Audit** (read-only) — compare against any local domain notes that exist; spot-check 5-10 cols; categorize issues (format / content / structural)
3. **Build** (dry-run) — write script with `--push` flag (default = dry-run); output old vs new side-by-side
4. **Push** — single PATCH with batched ops array (atomic); patch only changed cols; verify version bumped
5. **Cross-validate + record** — verify sibling tables (daily ↔ monthly) consistent; update your local domain notes

### Hard rules

| Rule | Why |
|------|-----|
| `Content-Type: application/json-patch+json` MANDATORY | Wrong Content-Type → 400 with cryptic error |
| `json.dumps(patches, ensure_ascii=False).encode("utf-8")` for Vietnamese | Default ASCII encoding stores escaped `ả` etc. |
| Column index `/columns/N` is array position OM returned, NOT alphabetical | Always fetch first, iterate, use the index you read |
| `"op": "add"` works as upsert; `"replace"` only if path exists | Use `add` to avoid surprises |
| Format-only push vs content push — DON'T MIX | A "format" push that touches content reads as authority claim under cover |
| Auto-derive across siblings is DANGEROUS | Source can have content bugs (`cashin_gmv` literally said "cashout"); auto-adapt propagates the bug |
| Bi-directional sibling reference MANDATORY | "For monthly grain → `<monthly>` (30× cheaper)" + reverse; without this, 30× cost incurred silently |
| Dry-run to file, READ IT, then push | Don't trust transformation function from samples alone |
| Independent-review checkpoint before push when scope expands beyond mechanical | A large auto-adapt plan can quietly corrupt sibling tables if source has content bugs; a fresh-eyes pass catches what the author misses |

### When to push T1 fix vs flag for owner

| Situation | Action |
|-----------|--------|
| Column description has typo / format issue | Push fix (mechanical) |
| Column description factually wrong (swap, wrong unit, wrong grain) | Flag for table owner; if you ARE owner, fix |
| Column description missing entirely | Push initial draft, ping owner to review |
| Description is rich but cube layer (T2) contradicts | Flag both, request alignment from semantic team |

## 5. Schema source preference for MoMo work

Putting the 5-tier ladder + MoMo tools together (instantiates `references/schema-source-hierarchy.md` for MoMo):

```
Question: schema of mart_ttt_daily_user_record? Do I have access? What's the business meaning?

T0 — Check OpenMetadata for mimir.* tag (owner-curated LLM-grade)
     → GET /api/v1/tables/name/bigquery.momovn-prod.BU_FI.mart_ttt_daily_user_record?fields=tags
     → tag mimir.BU_FS_InvestTech_Wealth_management present
     → Fetch tag content → if covers question, STOP

T1 — OpenMetadata catalog DIRECT API (full curated layer, admin visibility)
     → GET /api/v1/tables/name/bigquery.momovn-prod.BU_FI.mart_ttt_daily_user_record
        ?fields=columns,description,tags,version
     → 94 columns, all with markdown descriptions, bi-ref to monthly ✓
     → If sufficient AND you know you have BQ access, STOP

T2 — Access-aware MCPs (per-user scope, semantic cube, data portal docs)
     2a. mimir MCP — get_domain_schema('mart_ttt_daily_user_record')
         → Returns schema FILTERED to your BQ access scope + domain-knowledge layer
         → Confirms access AND adds analyst-written domain context catalog doesn't have
     2b. momo-data MCP — semantic cube check
         → semantic-get-team-data → datasource_id
         → semantic-fetch-meta-by-id(datasource_id) → list cubes
         → If TTT cube wraps this table → read measures + dimensions (business logic encoded)
     2c. momo-data MCP — data portal docs about this table
         → data-portal-search-document-content('mart_ttt_daily_user_record')
         → Find any prior analyst docs / handoff notes / known gotchas
     → If T2 covers question + confirms access, STOP

T3 — INFORMATION_SCHEMA fallback + brainstorm with user
     → SELECT column_name, data_type, is_nullable, partitioning_column FROM
       `momovn-prod.BU_FI.INFORMATION_SCHEMA.COLUMNS` WHERE table_name='mart_ttt_daily_user_record'
     → Then ask the human user (domain expert):
        "94 columns found — sentinels you know about?"
        "Any column deprecated since YYYY-MM-DD?"
        "Sibling table preferred for monthly grain (it's `mart_ttt_monthly_user_record`)?"

T4 — Sample 5 rows (only if T0–T3 still leave gaps about ACTUAL DATA values)
     → SELECT * FROM `momovn-prod.BU_FI.mart_ttt_daily_user_record` WHERE date='2026-05-15' LIMIT 5
     → MUST include partition filter; check sentinel values, NULL conventions, format quirks
```

**For non-MoMo tables**: drop T0 (Mimir-specific) and T2 (MoMo MCPs). Proceed T1 → T3 → T4 with whichever catalog tool + access-aware MCP (if any) your org runs.

**Key principle**: T2 sits ABOVE T3 because access-aware MCPs (a) confirm what you can actually query — no permission denied surprise mid-analysis, (b) bundle catalog + semantic cube + data portal docs in one user-scoped view, (c) often have richer schema notes + business glossary than raw catalog API alone.

## 6. MCP setup for MoMo stakeholders

Example MCP config snippet (`<plugin_root>/mcp/example-momo-mcp.json`) provides ready-to-paste config for adding all 3 MoMo MCPs at user scope:

```bash
# Install momo-data MCP (gateway)
claude mcp add -s user momo-data -- cmd /c npx -y mcp-remote https://mdp-mcp-gateway.mservice.io/servers/<server_id>/mcp

# Install mimir-da-sql MCP (NL→SQL)
claude mcp add -s user mimir-da-sql -- <path-to-mimir-mcp-launcher>

# Install powerbi-modeling MCP (PowerBI Desktop integration, if used)
claude mcp add -s user powerbi-modeling -- <path-to-vscode-ext-server>
```

See `<plugin_root>/mcp/example-momo-mcp.json` for the JSON form (drop-in for `~/.claude.json` user scope).

## 7. Cross-references

**Within this plugin**:
- Schema tier ladder → `references/schema-source-hierarchy.md`
- Building a semantic layer (portable) → `references/semantic-layer-setup.md`
- Query mode discovery step → `references/mode-query.md` Step 2
- Data modeling patterns → `references/mode-model.md`
- Governance → `references/governance.md`
- MCP suggestion at mode-exit → `references/suggestion-protocol.md` (MCP-tooling expansion category)

**External (docs)**:
- Semantic Cube: `https://semanticcube-doc.mservice.io/docs/intro`
- OpenMetadata Swagger: `https://datacatalog.mservice.io/swagger`
- Cube.js core docs: `https://cube.dev/docs`
- Synmetrix: `https://synmetrix.org`

## Why this file exists

The portable plugin is engine-agnostic (deliberately so), but MoMo DAs need one-stop access to MoMo-specific tooling (Semantic Cube, momo-data MCP, Mimir tag, OpenMetadata curation). Without this file, every new MoMo session re-discovers "wait, what MCP do I use for that?". This file consolidates the 5 MoMo-specific entry points (Cube + MCP + tag + catalog + portal) into one reference, hooked into the portable plugin's schema-discovery ladder. Adding a new MoMo-only feature → extend this file, not the portable references.
