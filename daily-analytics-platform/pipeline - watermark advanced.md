## Summary of Incremental‑processing Logic for a Watermark Table


Good idea — here’s a clean, organized summary of the incremental‑processing logic for a watermark table + pipeline, along with a few missing/optional logic steps I’d add to make it more robust and production‑ready. Think of this as a “spec sheet” for your watermark + incremental‑load framework.


### ✅ Core Watermark + Incremental Processing Logic: Summary


#### 🎯 Purpose of Watermark Table

- The watermark table holds per‑upstream‑table metadata: last processed version, planned start/end version, pipeline run ID/status, etc.
- It functions as the “source of truth” (checkpoint store) so that subsequent runs know where to resume, avoiding reprocessing or missing data. This is akin to a "high‑watermark" or "control table" as commonly used for incremental/CDC loads. 


---

#### 🔄 Workflow & State Transitions


**When to start a batch process**

1. Trigger batch run (manual or scheduled).
2. Call prepareProcessingPlanForSchemas(...) (or equivalent) to build or resume the plan:
    - Fetch the latest watermark entries for relevant upstream tables.
    - Examine the status of existing watermark records:
        - If status = COMPLETED, treat as “previous run finished” → generate a new watermark record with new run ID and plan.
        - If status = PLANNED, it means a previous run was scheduled/planned but not yet executed (or potentially failed) → reuse that planned version range (do not create a new plan).
    - The result is a set of upstream tables with associated (start_version, end_version) to process.

**During batch process**

- For each upstream table in the plan, read data incrementally (e.g. using Delta change‑data‑feed or Delta versioning) between start_version and end_version.
- Perform transformations, upserts/deletes, or other downstream logic.

**After batch process completes**

- If successful: call markRunCompleted() (or equivalent) to update watermark table — set status = “COMPLETED”, set last_processed_version = end_version, update timestamps/run_id, etc.
- If failed (or aborted/partial): do not mark as completed. This preserves the planned version range so that subsequent run can either retry or resume from that plan.

---

#### 📥 Watermark / Checkpoint Read Functions


- loadCheckpoints(tableNames: Seq[String]) — retrieves checkpoint information (table_name, last_processed_version) for the specified upstream tables. Only returns the most recent completed versions.
- loadVersionRanges(...) / fetchCurrentProcessingPlan(...) — retrieves the currently planned version ranges (start/end) from watermark table where status = “PLANNED”. Used by downstream consumers or orchestration logic to know what to process next.


---


### ⚙️ Additional / Recommended Logic (Missing or Useful Enhancements)

To make the watermark + pipeline logic more robust and production‑ready, consider adding the following:

#### 1. History / Audit Logging
    - Keep a separate history table (e.g. pipeline_watermark_history) to log all runs (planned, completed, failed) with timestamps, run IDs, status, error messages. This helps debugging, backfills, compliance, and monitoring.

#### 2. Failure Handling & Retry Logic
    - If a run fails, mark its watermark status to "FAILED" (or leave as "PLANNED"), record an error_message, failed_at timestamp.
    - Provide a method to retry a failed run (reuse the same planned version range) — avoid data loss or version gaps.

#### 3. Concurrency / Multiple Pipeline Support
    - If multiple pipelines may operate on overlapping upstream tables, include a pipeline_name (or job_name) in watermark metadata so records are scoped per pipeline.
    - Prevent collisions by ensuring upserts/merges consider (table_name, pipeline_name, run_id) when matching rows.

#### 4. Watermark Table Initialization / First-Time Run Handling
    - On first-ever run (when watermark table doesn’t exist or is empty), create watermark entries with e.g. last_processed_version = null or default 0, so pipeline treats them as “never processed before.”
    - Optionally allow configuration of an initial baseline version (e.g. start from full history or a safe baseline) rather than 0.

#### 5. Support for Deletes / Full History / Snapshot Consistency
    - If upstream supports deletes or you need to preserve history, ensure your incremental read + downstream merge logic handles delete operations (or full replays) properly.
    - Optionally include a “snapshot‑id” or “commit timestamp” watermark instead of just version number, if using a system like Delta Lake + CDC to ensure consistency across tables. tabular.io+2TECHCOMMUNITY.MICROSOFT.COM+2

#### 6. Monitoring / Observability
    - Include columns like update_ts, run_id, status, error_message, and possibly execution_duration, records_processed — helps for auditing, alerting, and performance tracking.

#### 7. Schema / Metadata Versioning (if upstream schema changes)
    - Track upstream schema version or model version in watermark metadata; if schema evolves, watermark logic may need to be reset or audited.

#### 8. Atomicity Between Data Load and Watermark Update
    - Ensure that updating watermark status/checkpoint happens after data load commit (and ideally in the same transaction if possible) to avoid mismatches (i.e. watermark moved up but data load failed). This is core to safe incremental/CDC pipelines. tabular.io+1


---

### 🧠 Why This Watermark Pattern Works (and Why It’s a Best Practice)

- The “watermark / high‑watermark + checkpoint / control‑table” pattern is widely used for incremental loads & CDC to avoid reprocessing or missing data — ensures idempotent, efficient ingestion.
- Using a control table (watermark table) with per‑table metadata enables scalable processing across many upstream tables (100+), while keeping state centralized and easy to manage.
- Storing plan status (PLANNED / COMPLETED / FAILED) helps orchestration and monitoring: you know what’s planned, what’s done, what failed — critical for automated pipelines.


---


## Watermark + Incremental Processing — State Diagram & Lifecycle


Good idea — here’s a state‑transition diagram (text + ASCII-style) for the watermark + incremental data‑processing lifecycle in your pipeline design. It includes main states, transitions on success/failure, and what happens on first run or re‑runs. I also highlight where some of the optional/missing logic (from earlier suggestions) fits in.


![alt text](images/image.png)

---

![alt text](images/image-1.png)

---

![alt text](images/image-2.png)

---


### 🔄 Watermark + Incremental Processing — State Diagram & Lifecycle

```css
[Start / Trigger pipeline run]
             │
             ▼
 ┌─────────┐  Prepare plan  ┌────────────────────────────┐
 │ Watermark │ ───────────▶ │ Check watermark entries    │
 │ table empty? ─ yes ───┐  │ for each upstream table   │
 └─────────┘             │  └────────────────────────────┘
                         │
                         │ No / not first run
                         │
                         ▼
             ┌────────────────────────────┐
             │ Existing entries found     │
             │ For each upstream table:  │
             │  if status = COMPLETED    │ → new plan (new run_id) │
             │  if status = PLANNED      │ → reuse existing plan   │
             └────────────────────────────┘
                         │
                         ▼
           ┌───────────────────────────────┐
           │ Write “plan” to watermark      │  (status = PLANNED) │
           │ table (table_name, run_id,     │                     │
           │ start_version, end_version,    │                     │
           │ metadata ...)                  │                     │
           └───────────────────────────────┘
                         │
                         ▼
              [Batch / Incremental Processing]
                         │
                         ▼
           ┌───────────────────────────┐
           │ Process each upstream    │
           │ table: read changes       │
           │ from start_version →      │
           │ end_version               │
           └───────────────────────────┘
                         │
           ┌─────────────┴─────────────┐
           │ success? / all tables processed │
           ▼                               ▼
 ┌────────────────────┐           ┌──────────────────────┐
 │ Batch succeeded    │           │ Batch failed / abort │
 └────────────────────┘           └──────────────────────┘
           │                               │
           ▼                               │
 ┌──────────────────────────────────┐     │
 │ Run markCompleted():             │     │  -- Do not update watermark status --
 │ Update watermark rows:           │     │  (status remains PLANNED) — can retry  │
 │   status = COMPLETED             │     │                                        │
 │   last_processed_version = end_version │ │
 │   update metadata (timestamp, run_id, etc.) │ │
 └──────────────────────────────────┘     │
           │                               │
           ▼                               │
  Next run or schedule future run        │
                                         │
  (start again, using latest checkpoints) │
```


---


### 📌 Flow Description & Key Logic

| Step | Description |
|------|-------------|
| **First time / empty watermark table** | If watermark table doesn't exist or has no entries, pipeline treats all upstream tables as needing a full initial import (e.g. start_version = 0 or baseline), and writes a "PLANNED" record for each table with a new run ID. |
| **Plan creation** | For each upstream table: check latest available version (via getLatestVersions), join with existing watermark to get last processed version (if any), then set start_version and end_version. If previous run was completed, start from last_processed_version + 1; if previous run is still "PLANNED," reuse that plan. |
| **Plan persistence** | Write plan metadata into watermark table (status = PLANNED). This makes which version ranges will be processed explicit and visible. |
| **Batch / incremental processing** | Process upstream changes (CDF or delta versions) between start and end for each table. This can be done table-by-table or in parallel, depending on downstream logic. |
| **On success** | Once processing completes for all upstream tables: call markCompleted() to update watermark entries: set status = COMPLETED, update last_processed_version = end_version, update run metadata (timestamps, run_id). |
| **On failure / abort** | Do not update watermark — leave status as PLANNED. That preserves the plan so you can retry the same version range, avoiding data loss or duplication. |
| **Next run** | On next pipeline trigger, logic inspects watermark: for tables with status = COMPLETED → create a new plan; for tables still PLANNED → either resume or alert (depending on how you want to handle). |


---

### ✅ Optional / Recommended Enhancements (State Extensions)

- History / audit log: Maintain a separate history table logging every plan and run (with status, run_id, timestamps, number of records processed, errors if any). Helps debugging, backfill, metrics.
- Failure tracking / retry logic: If a run fails, mark status as “FAILED” (or leave as PLANNED), capture error_message, and support retries.
- Concurrency / pipeline‑name scoping: If multiple pipelines run over overlapping upstream tables, include pipeline_name in watermark metadata so they don’t clash.
- Schema‑evolution / migration handling: If upstream table schema changes, logic to detect and optionally reinitialize or backfill full history (or alert).
- Atomic commit between data load and watermark update — ensure that data load and watermark update happen together (or in a fault-tolerant manner) to prevent inconsistent state (watermark advanced but data not applied).
- Monitoring / alerting — detect stuck PLANNED entries (e.g. plan created but not completed for a long time), missing runs, or repeated failures.

---

###🧩 Why This Pattern Works (Watermark + Plan + State Machine)


- The watermark pattern is widely used for incremental and CDC-based data synchronization. It lets you “resume where you left off” safely, without reprocessing all data or risking missed changes. Wikipedia+2Microsoft Learn+2
- Having explicit plan and status (PLANNED / COMPLETED / FAILED) gives clarity and control — you know exactly what version ranges are scheduled, what’s done, and what’s pending.
- This model supports both initial full loads (first run) and incremental (subsequent runs), enabling efficient ingestion at scale, even with 100+ upstream tables.
