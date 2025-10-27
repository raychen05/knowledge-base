
## Data Pipeline Versioning & Promotion: Best Practices

Achieve these goals:

- **Immutable historical data** (no changes to existing Delta tables)
- **Consistent promotion** from pre-prod → prod
- **No duplication or costly re-baselining**

These are essential for regulated analytics and compliance. Here’s a scalable approach:

---

### Best Practice Blueprint

#### 1. Separate Data Environments (No Double Ingestion)

Use a single, shared bronze (raw) layer for all environments:

| Layer  | Purpose                                 | Environment Scope            |
|--------|-----------------------------------------|-----------------------------|
| Bronze | Raw, immutable ingestion (append-only)  | ✅ Shared by Pre-Prod & Prod |
| Silver | Curated, cleaned, enriched data         | ⛔ Separate per environment  |
| Gold   | Aggregated, business logic applied      | ⛔ Separate per environment  |

- Raw data: shared
- Transformations: environment-specific
- Promotion: copy forward curated tables (not re-ingest)

---

#### 2. Delta Versioning for Promotion

Promote using Delta table version pointers, not by rewriting data.

**Example:**
```ini
prod_silver.customer = preprod_silver.customer @ version 189
```

**Promotion flow:**

1. Validate pipelines in pre-prod
2. Freeze table versions (tag/label)
3. Promote by cloning & pointing prod to that label

---

#### 3. Delta Clone Strategy

- **Shallow Clone** (default): Fast, space-efficient, uses copy-on-write
    ```sql
    CREATE OR REPLACE TABLE prod_silver.customer
    SHALLOW CLONE preprod_silver.customer VERSION AS OF 189;
    ```
- **Deep Clone** (for full independence):
    ```sql
    CREATE OR REPLACE TABLE prod_silver.customer
    DEEP CLONE preprod_silver.customer VERSION AS OF 189;
    ```

Use shallow by default; deep only for compliance/isolation.

---

#### 4. Data Lineage Tagging

Apply table properties for traceability:

```sql
ALTER TABLE preprod_silver.customer
SET TBLPROPERTIES (
  'release_tag' = '2025Q4_R1',
  'source_bronze_version' = '2025-10-20'
);
```

Prod inherits tags for audit compliance.

---

#### 5. Promote Metadata Too

Promote not just data, but also:

- Schema
- Constraints
- Table comments
- Pipeline version & transformations

Store as declarative config (e.g., .yaml/.json) in your repo. Use CI/CD to apply to prod.

---

### Logical Architecture

```pgsql
             ┌──────────────┐
 Raw Feed →  │ Bronze SHARED│
             └──────┬───────┘
           Transform in Pre-Prod
             ┌──────▼───────┐
             │ Silver PP    │
             └──────┬───────┘
         Validate & Tag
             ┌──────▼───────┐
           Clone From Tag
             │ Silver PROD  │
             └──────────────┘
```

- Never re-baseline
- Never duplicate ingest
- Always promote by version

---

**What NOT to Do**

- Ingest into pre-prod and prod independently
- Rewrite or merge old Delta data
- Run prod transformations from dev code

These cause drift and audit failures.

---

### Action Checklist

| Task                                             | Status |
|--------------------------------------------------|--------|
| Shared bronze data                               | ☐      |
| Pre-prod silver as source of truth for promotion | ☐      |
| Version tagging & shallow clone promotion        | ☐      |
| CI/CD for metadata + pipeline deployments        | ☐      |



---

## 📘 Data Promotion Design: Pre-Prod → Prod Using Delta Clone

Version: v1.0 
Scope: Apply to all curated Delta pipelines supporting 100+ academic datasets


### ✅ Overview

We enforce:

- ✔ Immutability of existing Delta tables
- ✔ Single source ingestion (no duplicate ingest into prod)
- ✔ Repeatable promotion from pre-prod → prod
- ✔ Auditability (pin to versions)
- ✔ Fast environment setup (no re-baseline)

We achieve this by:

**Shared Bronze Layer (raw)**: Environment-isolated Silver/Gold Layers managed via Delta Shallow Clone promotion


---

### 🧱 Data Architecture

```text
                       ┌───────────────────┐
 Raw Feeds (Grants,    │   Bronze (Shared) │
 Academic docs, WOS →  │   ✦ Immutable     │
 Patents, etc.         └───────┬──────────┘
                               │
                     Transform / Validate
                               │
                 ┌─────────────▼─────────────┐
                 │ Silver (Pre-Prod)         │
                 │ ✦ Where full testing      │
                 │   and validation occur    │
                 └─────────────┬────────────┘
                         Freeze + Tag
                               │
                 ┌────────────▼─────────────┐
                 │ Silver (Prod)            │
                 │ ✦ Promoted via           │
                 │   Delta Shallow Clone    │
                 └──────────────────────────┘
```

---

### ✅ Key Principles


| Principle               | Implementation                                 |
|-------------------------|------------------------------------------------|
| Avoid duplicate ingest  | Use a shared bronze (raw) layer                |
| No data rewrites        | Enforce Delta ACID with append-only operations |
| Stable promotion        | Promote via shallow clone pinned to version    |
| Environment isolation   | Maintain separate catalogs for curated layers  |
| Full traceability       | Apply table tags for release & data lineage    |


---

### 📌 Catalog & Naming Standards

| Layer              | Catalog         | Naming Rule / Prefix         | Example Table Name         |
|--------------------|----------------|------------------------------|---------------------------|
| Bronze             | dap_bronze     | `raw_` + domain              | `raw_wos_publications`    |
| Silver (Pre-Prod)  | dap_silver_pp  | business subject area        | `author_profile`          |
| Silver (Prod)      | dap_silver_pr  | same as pre-prod             | `author_profile`          |
| Gold (Pre-Prod/Prod)| dap_gold_pp/pr | KPI + reporting focus        | `funding_success_rate`    |

✅ Same table names → simple shallow clone promotion


---

### ✅ Promotion Workflow


#### Step 1 — Validate & Freeze Table in Pre-Prod

```sql
OPTIMIZE dap_silver_pp.author_profile;

ALTER TABLE dap_silver_pp.author_profile
SET TBLPROPERTIES (
  'release_tag' = '2025Q4_R1',
  'bronze_source_version' = '42'
);

```

#### Step 2 — Promote via Shallow Clone

```sql
CREATE OR REPLACE TABLE dap_silver_pr.author_profile
SHALLOW CLONE dap_silver_pp.author_profile
VERSION AS OF 189;

```

#### Step 3 — Sync Metadata Only (if needed)

```sql
MSCK REPAIR TABLE dap_silver_pr.author_profile;
```

---

### ✅ CI/CD Template (Azure DevOps / GitHub Actions)

```yaml
name: Promote Delta Release

on: [workflow_dispatch]

jobs:
  promote_delta:
    runs-on: ubuntu-latest
    steps:
    - name: Run Databricks SQL Promotion Script
      shell: bash
      run: |
        databricks sql < promote_release.sql \
        --param RELEASE_TAG="2025Q4_R1"

```

promote_release.sql includes:

- Tags query (to find versions)
- Shallow clone operations
- Audit logging insert

---

### 📓 Notebook Example (Databricks)

```python
release = "2025Q4_R1"

tables = [
    "author_profile",
    "grant_profile"
]

for tbl in tables:
    source = f"dap_silver_pp.{tbl}"
    target = f"dap_silver_pr.{tbl}"

    version = spark.sql(f"""
      SELECT version
      FROM delta.`{source}`_history
      WHERE operationMetrics['release_tag'] = '{release}'
      LIMIT 1
    """).first()[0]

    spark.sql(f"""
      CREATE OR REPLACE TABLE {target}
      SHALLOW CLONE {source}
      VERSION AS OF {version}
    """)

```

---

### 🔒 Governance & Retention Rules



| Asset           | Retention Policy           | Notes                        |
|-----------------|---------------------------|------------------------------|
| Pre-Prod tables | Keep last 3 releases      | For storage efficiency       |
| Prod tables     | Permanent (compliance)    | All immutable versions kept  |
| Clone history   | 180–365 days              | Subject to GC rules          |
| Tags/logs       | Permanent                 | For full lineage and audits  |


---

### 🧭 Rollback Strategy

```sql
CREATE OR REPLACE TABLE dap_silver_pr.author_profile
SHALLOW CLONE dap_silver_pp.author_profile
VERSION AS OF <previous_good_version>;
```

- ✅ Rollback in seconds
- ✅ No data rewrite

---

### 🎯 Summary

🎯 **Promotion Goals & Solutions**

| Goal                | Status | Solution                        |
|---------------------|--------|---------------------------------|
| Avoid re-baseline   | ✅     | Clone from pre-prod             |
| No duplicate ingest | ✅     | Shared bronze                   |
| Version safety      | ✅     | Delta versioning & tags         |
| Fast deployment     | ✅     | CI/CD automation                |
| Compliance-ready    | ✅     | Immutable lineage               |



---


Nice — I’ll build those pieces right now. Below I’ve put together:

- A compact diagram (ASCII + Mermaid you can drop into supported renderers) showing Bronze→Silver→Gold lineage and promotion.
- SQL files you can copy into Databricks SQL / notebook (promotion, tagging, rollback).
- A release tagging / tracking table DDL + helper queries.
- Quality-gate checks (SQL + lightweight Python notebook snippets) to run before promotion.
- Notification + CI/CD examples (GitHub Actions + Slack webhook + Databricks job) to automate promotion and alerts.


### Diagram — Bronze → Silver → Gold (lineage & promotion)

ASCII (quick pasteable)
```nginx
 Raw Feeds --> dap_bronze.raw_*  (shared, append-only)
                       |
         transformations / enrichment (pre-prod)
                       v
   dap_silver_pp.*  <-- full testing & validation (pin versions & tag)
        |  ^               ^ promotion: SHALLOW CLONE (version pinned)
        |  |               |
        v  |               |
   dap_silver_pr.*  <------+
        |
   transformations -> dap_gold_pr.* (reports, BI, ML)

```

**Mermaid** (for markdown renderers that support it)

```mermaid
flowchart LR
  A[Raw Feeds] --> B[dap_bronze.raw_*]
  B --> C[dap_silver_pp (Pre-Prod)]
  C -->|Validate & Tag| D[Release Tag: 2025Q4_R1]
  D -->|Shallow Clone (VERSION AS OF)| E[dap_silver_pr (Prod)]
  E --> F[dap_gold_pr (Reporting/ML)]
  style B fill:#f9f,stroke:#333,stroke-width:1px
  style C fill:#fffbcc
  style E fill:#ccffcc

```

---

#### 1) Release tagging / tracking table (central audit ledger)

Use a single audit table in a governance catalog (e.g., dap_meta.release_registry) to record promotions.

```sql
-- DDL: run in governance catalog (e.g., dap_meta)
CREATE DATABASE IF NOT EXISTS dap_meta;

CREATE TABLE IF NOT EXISTS dap_meta.release_registry (
  release_tag STRING,             -- e.g., '2025Q4_R1'
  table_name STRING,              -- 'dap_silver_pp.author_profile'
  source_version LONG,            -- delta version in pre-prod
  promoted_at TIMESTAMP,          -- promotion timestamp
  promoted_by STRING,             -- CI actor or username
  quality_status STRING,          -- PASS / FAIL / WARN
  quality_report STRING,          -- short JSON or link
  notes STRING
)
USING delta;

```

Helper: insert a row after promotion (example):

```sql
INSERT INTO dap_meta.release_registry
(release_tag, table_name, source_version, promoted_at, promoted_by, quality_status, quality_report, notes)
VALUES ('2025Q4_R1', 'dap_silver_pp.author_profile', 189, current_timestamp(), 'ci/bot', 'PASS', '{"row_count":12345}', 'Promoted after QC');
```

---

#### 2) How to find the version to promote (SQL snippet)

Delta history approach (Databricks SQL / Spark SQL):

```sql
-- Find the latest version tagged for a given release_tag
SELECT version, timestamp, operation, userId, operationMetrics
FROM table(dap_silver_pp.author_profile.history())
WHERE array_contains(split(operationMetrics['userMetadata'], ','), 'release_tag=2025Q4_R1')
ORDER BY version DESC
LIMIT 1;

```

If you prefer an explicit table property approach, store release_tag in TBLPROPERTIES on the pre-prod table when freezing:

```sql
ALTER TABLE dap_silver_pp.author_profile
SET TBLPROPERTIES ('release_tag' = '2025Q4_R1', 'frozen_at' = '2025-10-27T14:00:00Z');
```

---

#### 3) Promotion SQL (promote_release.sql)

promote_release.sql — idempotent pattern, used by CI:

```sql
-- Params: RELEASE_TAG, SOURCE_CATALOG (dap_silver_pp), TARGET_CATALOG (dap_silver_pr)
-- Example usage: databricks sql --param RELEASE_TAG="2025Q4_R1"

-- 1. Resolve tables to promote (could be a static list or read from config)
-- For simplicity, here is example for one table

-- 1.1 Get the version to promote (if you stored mapping in release_registry)
SELECT source_version
FROM dap_meta.release_registry
WHERE release_tag = '2025Q4_R1'
  AND table_name = 'dap_silver_pp.author_profile'
ORDER BY promoted_at DESC
LIMIT 1;

-- If above returns null, fall back to retrieving from pre-prod history (see snippet earlier)
-- Suppose resolved_version = 189

-- 2. Create target table by shallow clone
CREATE OR REPLACE TABLE dap_silver_pr.author_profile
SHALLOW CLONE dap_silver_pp.author_profile
VERSION AS OF 189;

-- 3. Optionally refresh metadata (MSCK-like) and set properties
ALTER TABLE dap_silver_pr.author_profile
SET TBLPROPERTIES (
  'promoted_from' = 'dap_silver_pp.author_profile',
  'promoted_version' = '189',
  'release_tag' = '2025Q4_R1',
  'promoted_at' = current_timestamp()
);

-- 4. Insert audit row (if not present)
MERGE INTO dap_meta.release_registry t
USING (SELECT '2025Q4_R1' as release_tag, 'dap_silver_pp.author_profile' as table_name, 189 as source_version, current_timestamp() as promoted_at, 'ci/bot' as promoted_by, 'PASS' as quality_status, '{}' as quality_report, '' as notes) s
ON t.release_tag = s.release_tag AND t.table_name = s.table_name AND t.source_version = s.source_version
WHEN NOT MATCHED THEN INSERT *
;

```

#### 4) Rollback SQL

To rollback to a previous known-good version:

```sql
-- Given: previous_good_version = 185
CREATE OR REPLACE TABLE dap_silver_pr.author_profile
SHALLOW CLONE dap_silver_pp.author_profile
VERSION AS OF 185;

-- Update audit table
INSERT INTO dap_meta.release_registry VALUES ('2025Q4_R1_ROLLBACK', 'dap_silver_pp.author_profile', 185, current_timestamp(), 'ci/bot', 'ROLLBACK', '{}', 'Rollback to previous good');


```

---

#### 5) Quality-gate checks (pre-promotion)

Run these checks in pre-prod and fail promotion if any check fails.

**5.1 Basic data health SQL checks**

```sql
-- row count sanity
SELECT COUNT(*) as cnt FROM dap_silver_pp.author_profile;

-- null check on primary key
SELECT COUNT(*) as null_pk FROM dap_silver_pp.author_profile WHERE author_id IS NULL;

-- duplicates if primary key is author_id
SELECT author_id, COUNT(*) c FROM dap_silver_pp.author_profile GROUP BY author_id HAVING c>1;

-- schema drift check: compare DESCRIBE DETAIL between last promoted version and current
DESCRIBE DETAIL dap_silver_pp.author_profile;

```

**5.2 Automated quality report** (Python notebook snippet)

This runs a set of checks, emits a JSON report, and writes to dap_meta.quality_reports.

```sql
# python pseudo-code for Databricks notebook
from pyspark.sql import SparkSession
import json
spark = SparkSession.builder.getOrCreate()

table = "dap_silver_pp.author_profile"

row_count = spark.table(table).count()
null_pk = spark.sql(f"SELECT COUNT(*) as c FROM {table} WHERE author_id IS NULL").collect()[0]['c']
dup_count = spark.sql(f"SELECT COUNT(*) as c FROM (SELECT author_id, COUNT(*) c FROM {table} GROUP BY author_id HAVING c>1)").collect()[0]['c']

report = {
  "table": table,
  "row_count": row_count,
  "null_pk": null_pk,
  "duplicate_pk_groups": dup_count,
  "timestamp": str(__import__('datetime').datetime.utcnow())
}

# save to a Delta table for audit
spark.createDataFrame([ (json.dumps(report),) ], schema=["report_json"]).write.format("delta").mode("append").saveAsTable("dap_meta.quality_reports")

```

Fail promotion if any critical metric exceeds thresholds (e.g., null_pk > 0, dup_count > 0, row_count change > 10% vs previous).

---

#### 6) CI/CD & Notifications


**6.1 GitHub Actions (simplified)**

.github/workflows/promote.yml
```yaml
name: Promote Delta Release

on:
  workflow_dispatch:
    inputs:
      release_tag:
        required: true
        default: "2025Q4_R1"

jobs:
  promote:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Run Databricks Promotion Notebook
        uses: databricks/actions@v1
        with:
          # adapt to your Databricks action usage
          databricks-host: ${{ secrets.DATABRICKS_HOST }}
          databricks-token: ${{ secrets.DATABRICKS_TOKEN }}
          notebook-path: /Repos/infra/promotion/promote_release_notebook
          notebook-params: '{"release_tag":"${{ github.event.inputs.release_tag }}"}'

      - name: Notify Slack on success
        if: success()
        run: |
          curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"Promotion ${{ github.event.inputs.release_tag }} completed successfully\"}" ${{ secrets.SLACK_WEBHOOK_URL }}

      - name: Notify Slack on failure
        if: failure()
        run: |
          curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"Promotion ${{ github.event.inputs.release_tag }} failed. Check CI logs.\"}" ${{ secrets.SLACK_WEBHOOK_URL }}

```

**6.2 Databricks Job approach**

Create a Databricks Job that runs the pre-promotion notebook (quality checks). If PASS -> runs promote notebook. Use webhooks or Databricks notifications to hook to Slack/Teams.

**6.3 Alert examples (Slack)**

```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"[ALERT] Promotion FAIL: release=2025Q4_R1 table=author_profile. See job: <link>"}' \
  https://hooks.slack.com/services/T000/BBBB/XXXX

```

---

#### 7) Metadata sync & schema verification

Before promoting, run schema comparison:
```sql
-- Schema detail pre-prod
SELECT * FROM (DESCRIBE DETAIL dap_silver_pp.author_profile) as p;

-- Schema detail last promoted (via audit table)
-- Use DESCRIBE DETAIL or store result from last promotion
```

If schema change is non-backward compatible (drop column, rename), require manual sign-off and deep clone option for prod (so you can transform independent copy).

---

#### 8) Storage & lifecycle considerations for shallow clones

- **Retention**: Keep pre-prod versions for at least N releases (e.g., 3). GC older versions after retention.
- **Storage risk**: Shallow clones reference same physical files. If you ever move/delete raw files, clones break. If you plan to delete source files, do a DEEP CLONE before deletion.
- **Access control**: Pre-prod storage should be readable by promotion job; prod should have stricter write/modify controls.

---

#### 9) Example repo structure (quick)

```pgsql
data-promotion/
├─ notebooks/
│  ├─ pre_promotion_checks.py
│  ├─ promote_release.py
│  └─ rollback_release.py
├─ sql/
│  ├─ promote_release.sql
│  ├─ rollback.sql
│  └─ release_registry_ddl.sql
├─ ci/
│  └─ promote.yml
├─ docs/
│  └─ promotion_design.md
└─ config/
   └─ release_tables.yaml   # list of tables to promote

```

**release_tables.yaml example:**

```yaml
release_tag: 2025Q4_R1
tables:
  - dap_silver_pp.author_profile
  - dap_silver_pp.grant_profile
  - dap_silver_pp.publication_index
```

---

#### 10) Quick operational playbook (TL;DR)

- In pre-prod, run full validation notebook. Produce quality_report in dap_meta.quality_reports.
- If PASS, CI triggers promote_release notebook.
- Promotion creates shallow clones in prod pinned to a version.
- CI inserts audit row to dap_meta.release_registry.
- CI sends Slack notification with summary + link to audit row.
- If cleanup required later, deep-clone any table that will have source deleted, then garbage collect.







---


##  Delta Table Clone Strategy


### Delta Table Clone Options

| Feature              | Shallow Clone                                 | Deep Clone                                 |
|----------------------|-----------------------------------------------|--------------------------------------------|
| Data files copied?   | ❌ No                                         | ✅ Yes                                     |
| Metadata copied?     | ✅ Yes                                        | ✅ Yes                                     |
| Storage size         | Very small (pointers only)                    | Full size (duplicate data)                 |
| Speed                | Extremely fast                                | Slower (copies files)                      |
| Isolation from source| Low                                           | High                                       |
| Cost                 | Very cheap                                    | Expensive (full data copy)                 |
| Use case             | Promotion between envs, testing               | Backup, environment separation, archival   |
| Post-clone changes   | Affects shared storage after copy-on-write    | Independent forever                        |

---

#### How They Work

**Shallow Clone**

- Copies only metadata + references to existing data
- Uses copy-on-write: data is copied only if changed later

Example:
```sql
CREATE OR REPLACE TABLE prod.table
SHALLOW CLONE preprod.table VERSION AS OF 157;
```

- Lightning fast
- Ideal for CI/CD pre-prod → prod promotion
- If source storage is deleted, clone breaks

---

**Deep Clone**

- Copies metadata and all physical Parquet files
- Clone becomes an independent full dataset

```sql
CREATE OR REPLACE TABLE prod.table
DEEP CLONE preprod.table VERSION AS OF 157;
```

- Best for disaster recovery
- Data isolation and compliance
- Requires same compute/storage as original table

---

#### Rule of Thumb

| Scenario                                 | Use           |
|------------------------------------------|---------------|
| Promote tested data pre-prod → prod      | Shallow Clone |
| Sandbox analytics/test environments      | Shallow Clone |
| Auditable long-term backup               | Deep Clone    |
| Migrate to new storage/cloud             | Deep Clone    |
| Real-time multi-region replication       | Deep Clone    |


Immutability + environment promotion is the mature model. The key: version-controlled Delta cloning as your promotion mechanism.

---

### 🧠 Why Databricks Recommends Shallow Clones for Environments

- Avoid duplicate ingestion
- Fast rollback and promotion
- Minimal storage
- Ability to pin table versions for releases
- This directly solves your earlier problem: "avoid rebaseline or duplicate the same data when promoting from pre-prod to prod"

- ✅ Promotion = “point prod to a tested version”
- ✅ No re-processing or duplication



---



## Delta Table Promotion, Versioning & Environment Separation


### ✅ Goals

- Pre-Prod and Prod both reference shared Bronze data — avoid duplicate ingestion.
- Silver tables are environment-separated for transformations and enriched schemas.
- Promotions pin exact Delta versions — enabling reproducibility and rollback.
- Immutable history: never rewrite existing data in place.

---

### 🏗️ Target Architecture (High-Level)

```pqsql
Raw → Bronze (Shared & Immutable)
                 |
        Transform & Validate
                 v
           Silver Pre-Prod
                 |
         Release Tag + QC
                 v
      Silver Prod ← Shallow Clone (VERSION AS OF)
                 |
           Gold / BI / ML
```

---

### 📂 Catalog & Naming Conventions

| Layer             | Catalog Example | Description                                      |
|-------------------|-----------------|--------------------------------------------------|
| Raw/Bronze        | dap_bronze      | Landing zone / append-only sync from sources     |
| Silver (Pre-Prod) | dap_silver_pp   | Iteration + schema evolution + UAT validation    |
| Silver (Prod)     | dap_silver_pr   | Only via promotion pipeline                      |
| Metadata/Audit    | dap_meta        | Promotion registry, QC results, lineage notes    |
| Gold              | dap_gold        | Business curated, optimized models               |


---


### 🔐 Security — Clear Separation

| Action        | Pre-Prod | Prod                                        |
|----------------|-----------|--------------------------------------------|
| Read          | ✅        | ✅                                          |
| Write/Modify  | ✅        | ❌ via users <br/> ✅ via CI promotion job  |
| Drop          | ✅        | ❌ (manual approval only)                   |


---


### 🔄 Promotion Pipeline (CI/CD Only)

**Command Pattern (Databricks SQL):**

```sql
CREATE OR REPLACE TABLE dap_silver_pr.{TABLE}
SHALLOW CLONE dap_silver_pp.{TABLE}
VERSION AS OF {SOURCE_VERSION};
```

**Everything is version-controlled**:

- source version pinned via Delta Time Travel
- release tag stored as TBLPROPERTY + registry record
- audit row inserted in dap_meta.release_registry


---

### 🏷️ Tagging Strategy

| Tag Example         | Meaning                                 |
|----------------------|------------------------------------------|
| 2025Q4_R1           | Release 1 of 2025 Q4                    |
| 2025Q4_UAT_Pass     | Frozen for release; candidate version    |
| rollback_2025Q4_R1  | Emergency rollback                       |


**Only tagged versions** are eligible for promotion.

TBLPROPERTIES example:
```sql
ALTER TABLE dap_silver_pp.author_profile
SET TBLPROPERTIES ('release_tag' = '2025Q4_R1', 'source_version' = '189');
```

---

### ✅ Quality Gates (Mandatory before Promotion)

| Category            | Check Examples                          |
|----------------------|------------------------------------------|
| Schema Consistency  | No breaking changes vs last promoted     |
| PK Health           | Nulls/duplicates > threshold?            |
| Row Count           | Sudden shrink/growth > 10%?              |
| Data Validity       | Critical business logic validation       |
| Operational         | Job runs clean / no warnings             |


Fail any gate → **block promotion**. Results written to dap_meta.quality_reports.


---

### ♻️ Data Retention & Version Cleanup


| Layer           | Strategy                                      |
|-----------------|------------------------------------------------|
| Bronze          | Store indefinitely (regulatory retention)      |
| Silver Pre-Prod | Keep last N=3 tagged versions per table        |
| Silver Prod     | Keep last N=6 promoted versions                |
| Auto VACUUM     | Enabled after retention checkpoint             |


⚠️ When deep clone is required:
- If Prod must survive Bronze cleanup
- If Pre-Prod history must be pruned aggressively

Else: shallow clone is default (lowest cost).

---

### 🚨 Rollback Plan

```sql
CREATE OR REPLACE TABLE dap_silver_pr.{TABLE}
SHALLOW CLONE dap_silver_pp.{TABLE}
VERSION AS OF {PREVIOUS_GOOD_VERSION};
```

Audit row:
quality_status=ROLLBACK + metadata.

---

### ✅ What This Delivers

| Benefit                     | Description                              |
|------------------------------|------------------------------------------|
| No duplication of Bronze     | Pre-Prod + Prod share raw data           |
| Minimal storage for Silver Prod | Only Delta metadata differs           |
| Traceable & recoverable      | Every Prod table has lineage + version pin |
| CI/CD compliance             | Only automation writes to Prod           |



---


### 📌 Summary Rulebook (Print This!)

Always update Pre-Prod. Never mutate Prod.
- Promote only by tag. Version pin every promotion.
- Shallow clone first. Deep clone only when deleting source files.
- All changes and QC saved in dap_meta registry.


---

## Schema or Table  Level Promotion


Great question — this is exactly the situation that gets messy if you try to “promote the whole schema at once.”

The right approach is:
- ✅ Promotion happens at table level, version by version — never schema-level cloning.

Let me break down why and how to handle each case.

---


### ✅ Why Table-Level Promotion?

| Requirement             | Schema-level clone                        | Table-level clone                          |
|-------------------------|-------------------------------------------|--------------------------------------------|
| Some tables unchanged   | ❌ Overwrites with old schema              | ✅ Leaves existing prod tables untouched    |
| Some tables changed     | ⚠️ May copy incomplete/untested metadata   | ✅ Promotes only tables that passed QC      |
| New tables introduced   | ❌ Difficult to isolate new additions      | ✅ Promotes only new tables as needed       |
| Rolling release support | ❌ All-or-nothing deployment               | ✅ Supports individual or grouped releases  |
| Rollback strategy       | ❌ Rollback affects all tables             | ✅ Roll back only the impacted table        |


Table-level = flexible, safe, least blast radius, ideal for 100+ tables evolving independently.

---

### ✅ How to Promote by Table Category

| Table Type               | Promotion Strategy                                      | Example Action                               |
|---------------------------|----------------------------------------------------------|-----------------------------------------------|
| ✅ Schema unchanged       | Promote only if data changed or business wants new version | Shallow clone from version X                 |
| ✅ Schema changed         | Requires validation + metadata checks                   | Shallow clone pinned version + metadata sync  |
| ✅ Net new table          | Promote only if needed in Prod                          | CREATE … SHALLOW CLONE                        |
| ⛔ Breaking schema change | Version bump + backward compatibility plan              | Block promotion until consumers ready         |


---

### ✅ Automation Logic (in CI/CD)


**Step 1 — Detect change category**

```sql
DESCRIBE HISTORY dap_silver_pp.{table}
ORDER BY version DESC LIMIT 1
```

**Rules**:
- operation = WRITE → data change
- operation = ALTER → schema change

**Step 2 — Classify**

```python
if schema_changed:
    category = "SCHEMA_CHANGE"
elif data_changed:
    category = "DATA_ONLY"
else:
    category = "NO_CHANGE"
```

**Step 3 — Promotion behavior**

```python
if category == "NO_CHANGE":
    skip
elif category in ["DATA_ONLY", "SCHEMA_CHANGE"]:
    shallow_clone()
```

**Step 4 — For new tables**
Check if exists in Prod:
```sql
SHOW TABLES IN dap_silver_pr LIKE '{table}'
```

If not → create via clone.

---

### ✅ Table Promotion SQL Examples


✅ Schema changed
```sql
CREATE OR REPLACE TABLE dap_silver_pr.author_profile
SHALLOW CLONE dap_silver_pp.author_profile
VERSION AS OF 200;
```

✅ Data change, same schema
```sql
Same command applies — version pins exact state.
```

✅ New table promotion
```sql
CREATE TABLE dap_silver_pr.new_metric_table
SHALLOW CLONE dap_silver_pp.new_metric_table;
```

---

### 🔐 Never promote entire schema — why?

If you do:
```sql
CREATE SCHEMA ... SHALLOW CLONE ...
```

**You risk**:

- ❌ Overwriting stable Prod tables
- ❌ Accidentally promoting tables that failed validation
- ❌ Propagating breaking schema to operational workloads
- ❌ Massive rollback required for a single mistake

**In short**:
- One bad table → entire environment is broken

Table-level promotion prevents this.


---


### ✅ Best Practice Deployment Pattern

- ✔ Promote small batches of related tables (by domain)
  - → e.g., only Author Domain tables in this release

- ✔ Use promotion registry to track:
```text
table name
version promoted
schema hash/migration flag
release tag
QC results
rollback pointer
```
- ✔ Add consumption contract validation:
  - Downstream dashboards must confirm readiness for schema change releases

---

### ✅ Rollback Ease

Because everything is version-pinned:
```sql
CREATE OR REPLACE TABLE dap_silver_pr.author_profile
SHALLOW CLONE dap_silver_pp.author_profile
VERSION AS OF <previous_good_version>;
```

Only problematic tables are touched.

---

### 🎯 Final Answer

- **Always table-level promotion** using Delta version pinning.
- Never clone at schema level.
- Promote only tables that have verified changes — data or schema.
- Leave stable tables untouched.

This is the **enterprise-safe** method — especially with 100+ tables evolving differently.


---

## Versioning Management


Great — this is the core governance question:

If each table in each environment may point to a different Delta version, how do we track, read, and write the correct version in Pre-Prod vs Prod?

Here’s the clean, scalable answer 

---

### ✅ Principle

- **Consumers never query by version**.
- The table reference defines which version is active in each environment.

Because:

- In Pre-Prod: table points to latest development version
- In Prod: table points to promoted, pinned version

So the versioning is managed by the table itself, not by pipeline code.

---

✅ How Versioning Works per Environment

| Environment | Table Name                | Delta Version Reference                |
|-------------|---------------------------|----------------------------------------|
| Pre-Prod    | dap_silver_pp.tableA      | Latest evolving version (dev/UAT)      |
| Prod        | dap_silver_pr.tableA      | Pinned, promoted version (immutable)   |


- In Pre-Prod, tables reflect ongoing development and validation.
- In Prod, tables always reference a specific, tested Delta version—ensuring stability and reproducibility.
- Consumers simply query the table; the environment determines which version is active.


Prod always uses **tested version**, not the latest development version.

---

### ✅ Example: Independent table versions


| Table           | Pre-Prod Version | Prod Version         |
|-----------------|------------------|----------------------|
| author_profile  | v205             | v198 ✅ (stable)     |
| grant_profile   | v149             | v149 ✅ (just promoted) |
| institution     | v12              | Not in Prod yet ✅ New table |


- Each table can have a different promoted version in Prod.
- New tables appear in Pre-Prod first, then are promoted individually.
- Promotion is explicit and version-pinned—Prod never auto-updates.

Prod never jumps automatically — CI/CD must promote.


---

### ✅ How Pipelines Read Correct Versions


**Production pipeline configuration**

```yaml
catalog: dap_silver_pr
env: prod

```

It reads from:

```ini
dap_silver_pr.* (all Prod-pinned versions)
```

**Pre-Prod pipeline configuration**

```yaml
catalog: dap_silver_pp
env: preprod

```

It reads from:

```ini
dap_silver_pp.* (latest dev versions)
```

Same code, different config

---

### ✅ How We Write Correct Versions

| Action | Environment | Behavior |
|--------|-------------|----------|
| Writes | Pre-Prod    | Allowed (development zone) |
| Writes | Prod        | ❌ Block direct writes — only CI/CD promotion jobs allowed |

Promotion SQL:
```sql
CREATE OR REPLACE TABLE dap_silver_pr.author_profile
SHALLOW CLONE dap_silver_pp.author_profile
VERSION AS OF {pin_version};
```

---


### ✅ Who tracks the version mapping?

We store it in a simple registry table:

**dap_meta.release_registry** Example

| Table Name      | Pre-Prod Version | Prod Version | Release Tag |
|-----------------|------------------|--------------|-------------|
| author_profile  | 205              | 198          | Q4_R1       |
| grant_profile   | 149              | 149          | Q4_R2       |

This enables:

- ✅ Full lineage
- ✅ Traceability
- ✅ Rollback to exact version
- ✅ Deployment auditing
- ✅ Change detection for next promotion


---

### ✅ What if pipelines must reference historical version?

Optional: Time Travel for debugging only, not standard consumption.
```sql
SELECT * FROM dap_silver_pr.author_profile VERSION AS OF 198;
```

Prod pipelines should not use this — stability requires a single active version per table.

--- 

✅ Final Guidance Summary

- ✔ Table-level promotion → each table can evolve independently
- ✔ Prod references pinned version internally → no version logic in code
- ✔ Environment separation by catalog configuration
- ✔ Promotion registry ensures traceability & automation
- ✔ Direct writes to Prod must be blocked

Pipelines remain simple — no version numbers in queries.

Versioning stays in metadata + CI/CD controls.

If you want, I can provide:

- ✅ Template registry table (SQL) 
- ✅ Promotion job sample (Databricks Workflow + GitHub Actions)
- ✅ SQL notebook to auto-detect version changes per table
- ✅ Dashboard to visualize diff between Pre-Prod and Prod


---

## Delta Promotion — Deliverables (All)


1. Registry & audit SQL (DDL + helper queries)
2. Quality report table & QC schema (DDL + checks SQL)
3. Notebook: **auto-detect changed tables** (Python for Databricks) — outputs classification: NO_CHANGE, DATA_ONLY, SCHEMA_CHANGE, NEW_TABLE
4. Notebook: **promotion driver** (uses auto-detect output + config to promote only changed/new tables)
5. CI/CD template (GitHub Actions) that runs QC → promotion → notifications 
6. Quick dashboard / queries to monitor Pre-Prod vs Prod diffs


---

### 1) Registry & Audit SQL

Save as sql/release_registry_and_audit.sql

```sql
-- 1.1 Governance DB
CREATE DATABASE IF NOT EXISTS dap_meta;

-- 1.2 Release registry: records promotions & rollbacks
CREATE TABLE IF NOT EXISTS dap_meta.release_registry (
  release_tag STRING,           -- e.g., '2025Q4_R1'
  table_name STRING,            -- fully qualified source table (dap_silver_pp.author_profile)
  source_version LONG,          -- version in pre-prod that was promoted
  promoted_to STRING,           -- fully qualified prod table (dap_silver_pr.author_profile)
  promoted_at TIMESTAMP,
  promoted_by STRING,
  quality_status STRING,        -- PASS / FAIL / WARN / ROLLBACK
  quality_report STRING,        -- JSON string summary (or link)
  notes STRING
) USING delta;

-- 1.3 Quality reports: stores QC outputs from pre-promotion checks
CREATE TABLE IF NOT EXISTS dap_meta.quality_reports (
  release_tag STRING,
  table_name STRING,
  report_json STRING,           -- JSON of checks and metrics
  checked_at TIMESTAMP
) USING delta;

-- 1.4 Optional: table-level metadata store (explicit pk, expected schema hash)
CREATE TABLE IF NOT EXISTS dap_meta.table_registry (
  table_name STRING PRIMARY KEY,   -- e.g., dap_silver_pp.author_profile
  expected_pk STRING,              -- e.g., author_id
  schema_hash STRING,              -- hash of last promoted schema
  last_promoted_version LONG,
  last_promoted_at TIMESTAMP
) USING delta;


```

**Helper: Insert audit row** (example)

```sql
INSERT INTO dap_meta.release_registry
(release_tag, table_name, source_version, promoted_to, promoted_at, promoted_by, quality_status, quality_report, notes)
VALUES ('2025Q4_R1', 'dap_silver_pp.author_profile', 205, 'dap_silver_pr.author_profile', current_timestamp(), 'ci/bot', 'PASS', '{"row_count":12345}', 'Promoted after full QC');

```

---

### 2) QC Schema & Example Checks

Save as sql/qc_checks_templates.sql

```sql
-- Row count sanity (example)
SELECT
  '{TABLE}' AS table_name,
  COUNT(*) AS row_count
FROM {TABLE};

-- PK nulls (replace PK_COLUMN)
SELECT
  '{TABLE}' AS table_name,
  SUM(CASE WHEN {PK_COLUMN} IS NULL THEN 1 ELSE 0 END) AS null_pk_count
FROM {TABLE};

-- Duplicate keys
SELECT
  '{TABLE}' AS table_name,
  COUNT(*) AS duplicate_groups
FROM (
  SELECT {PK_COLUMN}, COUNT(*) c FROM {TABLE} GROUP BY {PK_COLUMN} HAVING c > 1
);

-- Schema detail
DESCRIBE DETAIL {TABLE};

-- History inspection (return recent commits)
DESCRIBE HISTORY {TABLE} LIMIT 10;

```

Use thresholds in your automation (e.g., null_pk_count > 0 => FAIL; duplicate_groups > 0 => FAIL; row_count change > 10% => WARN/FAIL based on config).


---

### 3) Notebook — Auto-detect Changed Tables

Filename: notebooks/detect_table_changes.py

```python
"""
Detect table-level change categories between dap_silver_pp (pre-prod) and dap_silver_pr (prod).
Outputs a small CSV / Delta table 'dap_meta.promotion_candidates' with columns:
  table_name, category, resolved_version, notes
Categories: NO_CHANGE, DATA_ONLY, SCHEMA_CHANGE, NEW_TABLE
"""

from pyspark.sql import SparkSession
import yaml, pathlib, json, hashlib
from datetime import datetime

spark = SparkSession.builder.getOrCreate()

# CONFIG: path to release config listing tables (source/target) or infer from catalogue
config_path = "/Workspace/Repos/infra/config/release_tables.yaml"
p = pathlib.Path(config_path)
if not p.exists():
    raise FileNotFoundError(f"{config_path} missing")

cfg = yaml.safe_load(p.read_text())
tables = cfg.get("promote", [])  # list of dicts {source, target}

results = []

def schema_hash_from_descr_detail(tbl):
    """Generate a simple schema hash using DESCRIBE DETAIL columns (col name+type)"""
    try:
        desc = spark.sql(f"DESCRIBE DETAIL {tbl}").collect()[0]
        # Using schema JSON if available
        schema_str = desc.asDict().get('schemaString') or json.dumps(desc.asDict().get('partitionColumns', []))
        return hashlib.md5(schema_str.encode('utf-8')).hexdigest()
    except Exception:
        return None

def latest_version(tbl):
    # get latest version from history
    try:
        hist = spark.sql(f"DESCRIBE HISTORY {tbl} LIMIT 1").collect()
        if hist:
            return hist[0]['version']
    except Exception:
        return None

for row in tables:
    source = row['source']  # pre-prod table
    target = row['target']  # prod table
    entry = {'table_name': source, 'target_table': target, 'checked_at': datetime.utcnow().isoformat()}

    # Check if source exists
    try:
        spark.sql(f"SELECT 1 FROM {source} LIMIT 1")
        src_exists = True
    except Exception:
        src_exists = False

    # Check if target exists
    try:
        spark.sql(f"SELECT 1 FROM {target} LIMIT 1")
        tgt_exists = True
    except Exception:
        tgt_exists = False

    if not src_exists:
        entry.update({'category': 'MISSING_SOURCE', 'notes': 'source table missing'})
        results.append(entry); continue

    # New table if target not exist
    if not tgt_exists:
        ver = latest_version(source)
        entry.update({'category': 'NEW_TABLE', 'resolved_version': ver, 'notes': 'Will create in prod via clone'})
        results.append(entry); continue

    # both exist -> compare last promoted version vs current source
    src_version = latest_version(source)
    tgt_version = latest_version(target)

    # get schema hash
    src_schema_hash = schema_hash_from_descr_detail(source)
    tgt_schema_hash = schema_hash_from_descr_detail(target)

    if src_schema_hash != tgt_schema_hash:
        # Schema has changed
        entry.update({'category': 'SCHEMA_CHANGE', 'resolved_version': src_version, 'notes': f'schema_hash diff src:{src_schema_hash} tgt:{tgt_schema_hash}'})
    else:
        # Schema same, detect data change by comparing source_version vs promoted_version or row counts
        if src_version != tgt_version:
            entry.update({'category': 'DATA_ONLY', 'resolved_version': src_version, 'notes': f'version diff src:{src_version} tgt:{tgt_version}'})
        else:
            entry.update({'category': 'NO_CHANGE', 'resolved_version': src_version, 'notes': 'no version or schema change'})

    results.append(entry)

# Persist results to Delta for consumption by promotion notebook
out_df = spark.createDataFrame([ (r['table_name'], r['target_table'], r.get('category'), r.get('resolved_version'), r.get('notes'), datetime.utcnow()) for r in results ],
                               schema="table_name string, target_table string, category string, resolved_version long, notes string, checked_at timestamp")

out_df.write.format("delta").mode("overwrite").saveAsTable("dap_meta.promotion_candidates")

# Also print summary
print("Detection results:")
for r in results:
    print(r)

```

**Notes**:

- This script relies on release_tables.yaml and the tables listed there.
- schema_hash_from_descr_detail uses DESCRIBE DETAIL schemaString; you can improve by building deterministic column order hashing (name + type + nullable).
- You can extend to detect partitioning changes and column renames.

---

### 4) Notebook — Promotion Driver (promote only relevant tables)

Filename: notebooks/promote_driver.py

```python
"""
Promotion driver:
 - Reads dap_meta.promotion_candidates
 - Runs pre-promotion QC checks (calls pre_promotion_checks.py or inline)
 - Promotes tables where category in ['NEW_TABLE','DATA_ONLY','SCHEMA_CHANGE'] and QC PASS
 - Inserts audit row into dap_meta.release_registry
"""

from pyspark.sql import SparkSession
import yaml, pathlib, json
from datetime import datetime

spark = SparkSession.builder.getOrCreate()

config_path = "/Workspace/Repos/infra/config/release_tables.yaml"
cfg = yaml.safe_load(pathlib.Path(config_path).read_text())
release_tag = cfg.get('release_tag', 'UNSPECIFIED')

# Load candidates
candidates = spark.table("dap_meta.promotion_candidates").filter("category IS NOT NULL").collect()

def run_qc_for_table(source):
    """Run a subset of QC checks returning (status, report_json)"""
    try:
        # Basic checks
        row_count = spark.table(source).count()
        # Attempt PK check via table_registry expected_pk
        rows = spark.sql(f"SELECT expected_pk FROM dap_meta.table_registry WHERE table_name = '{source}'").collect()
        pk = rows[0]['expected_pk'] if rows else None
        null_pk = -1
        dup_count = -1
        if pk:
            null_pk = spark.sql(f"SELECT COUNT(*) c FROM {source} WHERE {pk} IS NULL").collect()[0]['c']
            dup_count = spark.sql(f"SELECT COUNT(*) c FROM (SELECT {pk}, COUNT(*) c FROM {source} GROUP BY {pk} HAVING c>1)").collect()[0]['c']

        report = {
            "table": source,
            "row_count": row_count,
            "pk": pk,
            "null_pk": null_pk,
            "duplicate_pk_groups": dup_count,
            "checked_at": datetime.utcnow().isoformat()
        }

        # Basic fail rules (tweak thresholds)
        if (pk and null_pk and null_pk > 0) or (dup_count and dup_count > 0):
            return ("FAIL", json.dumps(report))
        return ("PASS", json.dumps(report))

    except Exception as e:
        return ("FAIL", json.dumps({"error": str(e)}))

for r in candidates:
    src = r['table_name']
    tgt = r['target_table']
    cat = r['category']
    resolved_version = r['resolved_version']

    print(f"Processing {src} -> {tgt}: category={cat}, ver={resolved_version}")

    if cat == 'NO_CHANGE':
        print("Skipping - no change")
        continue

    # run QC
    qc_status, qc_report = run_qc_for_table(src)
    # write quality report
    spark.createDataFrame([(release_tag, src, qc_report, datetime.utcnow())], "release_tag string, table_name string, report_json string, checked_at timestamp") \
         .write.format("delta").mode("append").saveAsTable("dap_meta.quality_reports")

    if qc_status != "PASS":
        # Insert registry row with FAIL and skip
        spark.createDataFrame([(release_tag, src, resolved_version or -1, tgt, datetime.utcnow(), 'ci/bot', 'FAIL', qc_report, 'QC failed')], 
                              "release_tag string, table_name string, source_version long, promoted_to string, promoted_at timestamp, promoted_by string, quality_status string, quality_report string, notes string") \
             .write.format("delta").mode("append").saveAsTable("dap_meta.release_registry")
        print(f"QC failed for {src}: skipping promotion")
        continue

    # Perform shallow clone (idempotent)
    create_sql = f"CREATE OR REPLACE TABLE {tgt} SHALLOW CLONE {src} VERSION AS OF {resolved_version}"
    print(create_sql)
    spark.sql(create_sql)

    # Set table properties
    spark.sql(f"""
      ALTER TABLE {tgt}
      SET TBLPROPERTIES (
        'promoted_from' = '{src}',
        'promoted_version' = '{resolved_version}',
        'release_tag' = '{release_tag}',
        'promoted_at' = current_timestamp()
      )
    """)

    # Audit insert
    audit_vals = (release_tag, src, resolved_version or -1, tgt, datetime.utcnow(), 'ci/bot', 'PASS', qc_report, '')
    spark.createDataFrame([audit_vals], "release_tag string, table_name string, source_version long, promoted_to string, promoted_at timestamp, promoted_by string, quality_status string, quality_report string, notes string") \
         .write.format("delta").mode("append").saveAsTable("dap_meta.release_registry")

    print(f"Promoted {src} -> {tgt}")

print("Promotion run complete.")


```

**Notes**:

- This driver is intentionally simple; expand checks, implement retries, and wrap critical operations in transactions if desired.
- Ensure resolved_version is not None; you might want to pick the latest commit that was tagged/frozen rather than the very last version.


---

### 5) CI/CD Template — GitHub Actions

Save as .github/workflows/promote.yml

```yaml
name: CI Promote Delta Release

on:
  workflow_dispatch:
    inputs:
      release_tag:
        description: 'Release tag to promote'
        required: true
        default: '2025Q4_R1'

jobs:
  run-promotion:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set release tag file (optional)
        run: |
          python - <<'PY'
          import yaml, pathlib, sys
          cfg = yaml.safe_load(pathlib.Path('config/release_tables.yaml').read_text())
          cfg['release_tag'] = "${{ github.event.inputs.release_tag }}"
          pathlib.Path('config/release_tables.yaml').write_text(yaml.safe_dump(cfg))
          print("Updated release_tables.yaml with", cfg['release_tag'])
          PY

      - name: Run detect_table_changes notebook on Databricks
        uses: databricks/run-notebook@v1
        with:
          domain: ${{ secrets.DATABRICKS_HOST }}
          token: ${{ secrets.DATABRICKS_TOKEN }}
          notebook_path: /Repos/infra/notebooks/detect_table_changes
          # pass params if your action supports it

      - name: Run pre_promotion_checks notebook
        uses: databricks/run-notebook@v1
        with:
          domain: ${{ secrets.DATABRICKS_HOST }}
          token: ${{ secrets.DATABRICKS_TOKEN }}
          notebook_path: /Repos/infra/notebooks/pre_promotion_checks

      - name: Run promote_driver notebook
        uses: databricks/run-notebook@v1
        with:
          domain: ${{ secrets.DATABRICKS_HOST }}
          token: ${{ secrets.DATABRICKS_TOKEN }}
          notebook_path: /Repos/infra/notebooks/promote_driver

      - name: Notify Slack success
        if: success()
        run: |
          curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"Promotion ${{ github.event.inputs.release_tag }} completed successfully\"}" \
            ${{ secrets.SLACK_WEBHOOK_URL }}

      - name: Notify Slack failure
        if: failure()
        run: |
          curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"Promotion ${{ github.event.inputs.release_tag }} failed. Check logs.\"}" \
            ${{ secrets.SLACK_WEBHOOK_URL }}


```

Replace databricks/run-notebook@v1 with your org's Databricks action or mechanism. Use Databricks Jobs API if preferred.


---

### 6) Monitoring / Dashboard Queries

Quick queries you can put into a dashboard to monitor promotion state.

6.1 Current promotion candidates
`
``sql
SELECT * FROM dap_meta.promotion_candidates ORDER BY checked_at DESC;

```

6.2 Last promotions

```sql
SELECT release_tag, table_name, source_version, promoted_to, promoted_at, quality_status
FROM dap_meta.release_registry
ORDER BY promoted_at DESC
LIMIT 200;
```

6.3 QC failures (recent)

```sql
SELECT * FROM dap_meta.quality_reports
WHERE checked_at >= current_date() - INTERVAL 7 DAYS
  AND report_json LIKE '%"FAIL"%'
ORDER BY checked_at DESC;

```

6.4 Pre-Prod vs Prod schema diffs (example)

You can create a small helper table dap_meta.schema_snapshots (store schema JSON/hashes when promoting) and query diffs; simplified example:

```sql
SELECT t.table_name, t.schema_hash AS preprod_hash, r.schema_hash AS prod_hash
FROM dap_meta.schema_snapshots t
LEFT JOIN dap_meta.schema_snapshots r ON r.table_name = REPLACE(t.table_name, 'dap_silver_pp.', 'dap_silver_pr.')
WHERE t.snapshot_at = (SELECT MAX(snapshot_at) FROM dap_meta.schema_snapshots WHERE table_name = t.table_name)

```

---

### Operational Notes & Best-Practices (short)

- Table-level promotion only. Never promote an entire schema wholesale.
- Pin versions at promotion — use tags/frozen commits if possible.
- Store expected PKs in dap_meta.table_registry to make QC deterministic.
- Make Prod read-only to human users; only CI/CD may update via promotion jobs.
- Shallow clone by default. Use deep clone only if you must delete/GC source files or need complete independence.
- Retention: keep last N promoted versions and regularly vacuum older Delta versions using controlled GC windows.
- Backups: snapshot deep clones for archived releases you must retain beyond regular retention windows.



---

## How to Rebaseline all Delta Tables


Ah — this is a special case: when you need to rebaseline all tables, i.e., reset Pre-Prod + Prod to a new unified baseline, while still keeping history and audit intact.

Here’s how to handle it in the approach we just designed.

---

### 1️⃣ What “Rebaseline” Means

- You are essentially saying:
  - “I want all tables in Pre-Prod (and eventually Prod) to start from a clean, consistent state, ignoring incremental changes or prior promotions.”
- Common reasons:
  - Large schema evolution
  - Data quality issues accumulated over time
  - Migrating to a new source snapshot
- Must avoid breaking downstream consumers in Prod.

---

### 2️⃣ Steps to Rebaseline All Tables

#### Step 1 — Prepare New Baseline Source

- Identify or create a fresh snapshot of each Bronze / upstream table
- Validate full QC on the new baseline
- Optional: store in a temporary catalog like dap_silver_pp_rebaseline
```text
dap_bronze.* → dap_silver_pp_rebaseline.*
```
- This is your golden source for this rebaseline.

---

#### Step 2 — Pin Baseline Versions

- For each table, record the version of the baseline snapshot
- Insert into the promotion registry as special “baseline” entries:

|table_name|	baseline_version	|release_tag|
|-----------------|------------------|--------------| 
|author_profile	|230	|BASELINE_2025Q4|

---

### Step 3 — Promote Baseline to Pre-Prod

- Use table-level shallow clones from the new baseline:

```sql
CREATE OR REPLACE TABLE dap_silver_pp.author_profile
SHALLOW CLONE dap_silver_pp_rebaseline.author_profile
VERSION AS OF 230;
```

- All tables now have consistent, audited versions in Pre-Prod
- Run full QC on every table

---

#### Step 4 — Promote to Prod

- After validation, promote all tables as normal:
```sql
CREATE OR REPLACE TABLE dap_silver_pr.author_profile
SHALLOW CLONE dap_silver_pp.author_profile
VERSION AS OF 230;
```

- Insert baseline audit row in dap_meta.release_registry with release_tag = BASELINE_2025Q4
- Optional: mark all prior Prod versions as archived in registry

---

#### Step 5 — Clean Up / Retention

- Pre-Prod / baseline tables:
  - Keep last N baseline versions for rollback
- Old versions in Prod:
  - Retain last N versions for traceability
- Delta VACUUM can be run after QC and approval


---

### 3️⃣ Key Differences from Normal Promotion


| Normal Table Promotion                | Rebaseline                                   |
|---------------------------------------|----------------------------------------------|
| Only changed/new tables promoted      | All tables promoted                          |
| Incremental versioning                | Reset to new baseline versions               |
| Registry tracks per-table promotion   | Registry records a baseline `release_tag`    |
| Only tables with QC PASS are promoted | QC must run for every table                  |
| Shallow clone from Pre-Prod           | Shallow clone from baseline snapshot         |


---

### 4️⃣ Tips / Best Practices


- Do not overwrite Prod before Pre-Prod QC passes.
  - Baseline promotion is a big blast-radius change.
- Use release_tag = BASELINE_YYYYMM for clarity in registry.
- Keep baseline catalog separate (dap_silver_pp_rebaseline) to avoid interfering with normal incremental pipelines.
- Optional Deep Clone for Prod if you want full independence from Pre-Prod history.
- Document rollback path: old Prod version numbers and audit logs remain in registry.
- Update downstream consumers only after baseline is fully promoted and validated.

---

### ✅ Sample Rebaseline SQL Workflow

```sql
-- Step 1: Pre-Prod baseline clone
CREATE OR REPLACE TABLE dap_silver_pp.author_profile
SHALLOW CLONE dap_silver_pp_rebaseline.author_profile
VERSION AS OF 230;

-- Step 2: Insert baseline audit
INSERT INTO dap_meta.release_registry
(release_tag, table_name, source_version, promoted_to, promoted_at, promoted_by, quality_status, quality_report, notes)
VALUES ('BASELINE_2025Q4', 'dap_silver_pp.author_profile', 230, 'dap_silver_pp.author_profile', current_timestamp(), 'ci/bot', 'PASS', '{}', 'Rebaseline Pre-Prod');

-- Step 3: Promote to Prod after QC
CREATE OR REPLACE TABLE dap_silver_pr.author_profile
SHALLOW CLONE dap_silver_pp.author_profile
VERSION AS OF 230;

-- Step 4: Insert Prod baseline audit
INSERT INTO dap_meta.release_registry
(release_tag, table_name, source_version, promoted_to, promoted_at, promoted_by, quality_status, quality_report, notes)
VALUES ('BASELINE_2025Q4', 'dap_silver_pp.author_profile', 230, 'dap_silver_pr.author_profile', current_timestamp(), 'ci/bot', 'PASS', '{}', 'Rebaseline Prod');

```


✅ Takeaway:

- Always table-level, even in a full rebaseline
- Pin versions from the baseline catalog → no accidental drift
- Run QC on all tables before Prod promotion
- Use a clear release_tag “BASELINE_YYYYMM” to distinguish from normal incremental releases

---

## Delta Table Promotion & Rebaseline Diagram

Perfect — here’s a clear diagram concept for Delta Table Promotion & Rebaseline, showing both incremental promotion and full rebaseline. I’ll describe it textually and visually so you can render it in Lucidchart, Draw.io, or Databricks notebooks.


### 🎯 Delta Table Promotion & Rebaseline Flow

```pqsql
                  +-------------------+
                  |   Bronze Tables    |
                  |   (raw sources)    |
                  +-------------------+
                           |
                           v
               +----------------------+
               | Pre-Prod Transformation|
               |  Bronze → Silver       |
               |  (dap_silver_pp)      |
               +----------------------+
                   |         |
           Incremental     Full Rebaseline
           Promotion       (All tables)
             |                 |
   +----------------+    +--------------------+
   | Only changed/  |    | Clone all tables   |
   | new tables     |    | from baseline      |
   | shallow clone  |    | catalog:           |
   | pinned version |    | dap_silver_pp_rebaseline
   +----------------+    +--------------------+
             |                  |
             v                  v
      +----------------+  +----------------+
      | Prod Promotion |  | Prod Promotion |
      | (dap_silver_pr)|  | (dap_silver_pr)|
      | shallow clone  |  | shallow clone  |
      | pinned version |  | pinned baseline|
      +----------------+  +----------------+
             |
             v
   +-------------------------+
   | Promotion Registry       |
   | dap_meta.release_registry|
   | tracks: table, source   |
   | version, promoted_to,    |
   | release_tag, QC result   |
   +-------------------------+
             |
             v
   +-------------------------+
   | QC & Monitoring         |
   | dap_meta.quality_reports|
   | Dashboard: Pre-Prod vs  |
   | Prod, schema diffs, QC  |
   +-------------------------+

```


---


### 🔹 Key Points Illustrated


1. Bronze → Pre-Prod → Prod is always table-level.
2. Incremental Promotion:
  - Only tables with data or schema changes
  - Shallow clone from Pre-Prod to Prod
  - Version pinned in release_registry
3. Full Rebaseline:
  - Clone all tables from a baseline catalog
  - Each table gets baseline version pinned in Pre-Prod first
  - After QC, shallow clone to Prod
  - release_tag = BASELINE_YYYYMM
4. Registry + QC table tracks all versions, release tags, and quality checks.
5. Pipelines do not need to pass versions — table references point to correct environment & pinned version.


---


## Pipeline Version Promotion


Great — you’re asking the real production challenge:
```text
When we promote updated Delta tables (with new schema) from Pre-Prod → Prod,
the pipeline (code + schema expectations) must also update safely.
And Prod cannot break during the transition.
```
This is where Table Version Promotion must be synchronized with Pipeline Version Promotion.

---

### ✅ Core Principle

**Data promotion and pipeline promotion must be version-locked** using the same release_tag + CI/CD gate.

So:

- Pre-Prod runs new code + new schema
- Prod continues running old code + old schema
- Only after QC PASS, both are promoted together

---

###✅ How This Works in Practice

#### 1️⃣ Versioned Pipeline Config per Environment

Instead of hard-coding schema in code:

📌 Store pipeline config in release bundles, e.g.:

```pqsql
configs/
  prod_config.yaml        # pinned stable schema & table list
  preprod_config.yaml     # future / evolving schema

```

Prod pipeline uses:
```yaml
catalog: dap_silver_pr
release_tag: Q4_R1
```

Pre-Prod pipeline uses:
```yaml
catalog: dap_silver_pp
release_tag: Q4_R2_DEV
```

Same pipeline code, different config + table version pins.

---

#### 2️⃣ Schema Changes Applied Only in Pre-Prod First

Change code → run in Pre-Prod → QC → Approval → Promote

| Phase            | Env       | Schema  | Pipeline Code |
|------------------|-----------|----------|----------------|
| Current Run      | Prod      | v1       | v1             |
| Dev/Test         | Pre-Prod  | v2       | v2             |
| After Promotion  | Prod      | v2 ✅    | v2 ✅          |


Prod never sees schema v2 until code can handle it.


---

#### 3️⃣ CI/CD Pipeline Promotion Jobs

A typical GitHub Actions / Azure DevOps job:

Promote Release Steps:
- ✅ Freeze Pre-Prod table versions → insert into release_registry
- ✅ Copy new pipeline configs to Prod
- ✅ Update Prod pipeline code bundle
- ✅ Clone tables from Pre-Prod → Prod (pinned versions)
- ✅ Run QC again in Prod shadow mode
- ✅ Swap execution to new Prod config

---

#### 4️⃣ Safe Deployment: “Dual-Write / Dual-Read” Option (Optional)

For very high stability needs:
- New schema tables exist in parallel
- Pipelines write to both until cutover

Example:
```scss
author_profile_v1  (Prod)
author_profile_v2  (Pre-Prod → future Prod)
```

Cutover command:
```scala
RENAME TABLE dap_silver_pr.author_profile_v1 TO author_profile_v1_backup;
RENAME TABLE dap_silver_pr.author_profile_v2 TO author_profile;
```

Rollback = rename back ✅

---

#### 5️⃣ Registry Tracking

release_registry records:

| table_name      | preprod_version | prod_version | code_version | release_tag |
|-----------------|-----------------|---------------|---------------|--------------|
| author_profile  | 205             | 198           | pipeline_v1   | Q4_R1        |
| author_profile  | 230             | pending       | pipeline_v2   | Q4_R2_DEV    |


→ Promotion waits for QC PASS + deployment approvals

---

### ✅ Example End-to-End Flow

```pqsql
Developer changes code → Pre-Prod pipeline runs v2 schema
       |
       v
QC PASS (schema check, DQ, downstream impact)
       |
       v
Promotion pipeline freezes versions + code bundle
       |
       v
Prod table promoted to v2 + new code deployed

```

Zero downtime, no accidental schema drift.

--- 

### 🔒 Golden Rule

**Never allow Prod incremental pipelines to auto-adopt new schemas**
Promotion must be **explicit + audited.**


---

### ✅ Summary

| Concern                        | Solution                                  |
|--------------------------------|-------------------------------------------|
| How to avoid breaking Prod pipelines? | Prod pinned to code+data release bundle |
| How to change schema safely?          | Apply only in Pre-Prod first            |
| Who controls version?                 | CI/CD + registry table                  |
| How pipelines find correct schema?    | Environment-specific release config     |
