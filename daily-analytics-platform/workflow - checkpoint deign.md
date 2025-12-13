

## Production-ready Checkpoint Schema 


Below is a clean, minimal, production-ready checkpoint schema set that fits exactly with your framework goals:

-	YAML-defined multi-task pipelines
-	Single watermark per run
-	Task-level recovery (skip succeeded tasks)
-	Safe restart without rerunning completed work
-	Databricks + Delta friendly

I’ll give you 3 tables (pipeline, task, watermark) and explain why each exists and how they interact.


---

### 1️⃣ Pipeline Run Checkpoint (Run-level state)

**Purpose**

-	One row per pipeline run
-	Controls overall lifecycle
-	Owns the watermark commit decision


Table: dap_meta.pipeline_runs

```sql
CREATE TABLE dap_meta.pipeline_runs (
    pipeline_name        STRING,
    run_id               STRING,
    status               STRING,   -- RUNNING | SUCCESS | FAILED | SKIPPED
    trigger_type         STRING,   -- SCHEDULE | MANUAL | BACKFILL
    started_at           TIMESTAMP,
    completed_at         TIMESTAMP,
    error_message        STRING,
    config_hash          STRING,   -- optional: detect config drift
    created_at           TIMESTAMP,
    updated_at           TIMESTAMP
)
USING DELTA
PARTITIONED BY (pipeline_name);
```


**Key Notes**
-	run_id: UUID or timestamp-based
-	config_hash: prevents resuming with changed YAML
-	Watermark is NOT advanced here directly, only when status → SUCCESS


---


### 2️⃣ Task Run Checkpoint (Recovery-critical)

**Purpose**

-	Enables skip-successful-tasks
-	Supports partial retry
-	Tracks critical vs non-critical failures


Table: dap_meta.pipeline_task_runs

```sql
CREATE TABLE dap_meta.pipeline_task_runs (
    pipeline_name        STRING,
    run_id               STRING,
    task_name            STRING,
    status               STRING,   -- PENDING | RUNNING | SUCCESS | FAILED | SKIPPED
    critical             BOOLEAN,
    attempt              INT,
    started_at           TIMESTAMP,
    completed_at         TIMESTAMP,
    error_message        STRING,
    created_at           TIMESTAMP,
    updated_at           TIMESTAMP
)
USING DELTA
PARTITIONED BY (pipeline_name, task_name);
```

Why this table is essential
-	Restart logic:

```css
if task.status == SUCCESS → skip
else → retry
```

-	Lets you:
-	Retry only failed tasks
-	Continue remaining tasks
-	Fail pipeline only if critical task fails


---


### 3️⃣ Watermark State Table (Source-level truth)

**Purpose**

-	Tracks what data has been consumed
-	Advanced only after all critical tasks succeed
-	Shared across retries

Table: dap_meta.pipeline_watermarks

```sql
CREATE TABLE dap_meta.pipeline_watermarks (
    pipeline_name        STRING,
    source_name          STRING,   -- e.g. wos_articles, grants, patents
    watermark_type       STRING,   -- VERSION | TIMESTAMP
    watermark_value      STRING,   -- "12345" or "2025-01-01T00:00:00Z"
    last_committed_run   STRING,
    updated_at           TIMESTAMP
)
USING DELTA
PARTITIONED BY (pipeline_name);

```

**Design Rule**(Very Important)

Watermark is committed only when
-	Pipeline run = SUCCESS
-	All critical tasks = SUCCESS

This prevents:
-	Partial consumption
-	Silent data loss
-	Inconsistent derived tables

---

### 4️⃣ How These Tables Work Together (Execution Flow)


```css
START RUN
│
├─ pipeline_runs → RUNNING
│
├─ read watermark (pipeline_watermarks)
│
├─ for each task:
│     ├─ check pipeline_task_runs
│     ├─ if SUCCESS → SKIP
│     └─ else → RUN
│
├─ if any CRITICAL task FAILED
│     └─ pipeline_runs → FAILED
│
└─ else
      ├─ commit watermark
      └─ pipeline_runs → SUCCESS
```

---

### 5️⃣ Minimal Required Indexing (Databricks Friendly)


```sql
OPTIMIZE dap_meta.pipeline_task_runs
ZORDER BY (pipeline_name, run_id, task_name);

OPTIMIZE dap_meta.pipeline_runs
ZORDER BY (pipeline_name, run_id);
```


---

### 6️⃣ Optional (Highly Recommended) Enhancements


#### A) Task Output Guard (Idempotency)


```sql
CREATE TABLE dap_meta.pipeline_task_outputs (
    pipeline_name STRING,
    run_id STRING,
    task_name STRING,
    target_table STRING,
    row_count BIGINT,
    checksum STRING,
    created_at TIMESTAMP
)
USING DELTA;
```

Prevents duplicate writes on retries.

---

#### B) Retry Policy Tracking

Add to pipeline_task_runs:

```sql
max_retries INT,
retry_delay_sec INT
```

#### C) DAG Dependencies (Future-proof)


```sql
CREATE TABLE dap_meta.pipeline_task_dependencies (
    pipeline_name STRING,
    task_name STRING,
    depends_on STRING
)
USING DELTA;
```

---

### 7️⃣ Naming Convention (Aligned with Your DAP System)


| Type | Schema |
|------|--------|
| Execution metadata | `dap_meta` |
| Watermarks | `dap_meta.pipeline_watermarks` |
| Pipeline state | `dap_meta.pipeline_runs` |
| Task state | `dap_meta.pipeline_task_runs` |


---

### 8️⃣ Final Recommendation

For your multi-task, watermark-driven pipelines:

- ✔ 3 tables minimum
- ✔ Task-level checkpoint is non-negotiable
- ✔ Watermark commit must be last step
- ✔ YAML + checkpoint tables = safe recovery


If you want, next I can:
-	Provide exact Scala checkpoint APIs
-	Add MERGE-based atomic updates
-	Show backfill + override watermark design
-	Align this with Databricks Jobs YAML & task retries
-	Design monitoring queries / dashboards

