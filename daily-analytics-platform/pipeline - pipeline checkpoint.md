

## Pipeline Checkpoint Management

Below is a full professional review, improved schema, and pipeline usage guide for a checkpoint table designed to coordinate 20+ pipelines (status, retry, restart, audit, run history, duration, etc.).
Your current schema is good but can be simplified, normalized, and made more robust for orchestration, especially for multi-pipeline 
environments.


### ✅ 1. Analysis of Your Current Schema


Your table:
```sql
CREATE TABLE IF NOT EXISTS ppl_checkpoint (
  run_id STRING PRIMARY KEY,
  batch_id LONG,
  job_id LONG,
  pipeline_name STRING,
  last_batch_id LONG,
  start_ts TIMESTAMP,
  end_ts TIMESTAMP,
  update_ts TIMESTAMP,
  updated_by STRING,
  status STRING,
  error_message STRING
)
USING DELTA;
```

Identified issues / opportunities to improve:

❌ Issue 1 — run_id is the PRIMARY KEY
- This prevents multiple runs of the same pipeline from being stored historically.

❌ Issue 2 — Missing separation between pipeline definition and pipeline run
- You need separate tables for:
  -  pipeline metadata (job id, pipeline type, owner)
  -  pipeline run / execution history

Right now everything is mixed.

❌ Issue 3 — last_batch_id is ambiguous
- Does this mean last processed? or last successful? or last attempted?

❌ Issue 4 — batch_id does not indicate if this is incremental or baseline
- You need a field like "run_type": baseline | incremental.

❌ Issue 5 — No field storing duration or restart counters

❌ Issue 6 — error_message is too short; better use error_details (long string)

--

### ✅ 2. Improved Schema for Multi-Pipeline Orchestration

I recommend splitting into 2 tables:

#### ⭐ Table 1 – pipeline_definition

Stores one row per pipeline, not per run.

- ✔ Stable configuration
- ✔ Not updated often
- ✔ Referenced by pipeline runs

```sql
CREATE TABLE IF NOT EXISTS pipeline_definition (
  pipeline_name STRING PRIMARY KEY,
  job_id LONG,                            -- Airflow / Databricks job ID
  owner STRING,                           -- engineering owner
  description STRING,
  is_active BOOLEAN,
  created_ts TIMESTAMP,
  updated_ts TIMESTAMP
)
USING DELTA;
```

---

#### ⭐ Table 2 – pipeline_run_history

Stores history for every pipeline execution.

This is where your "checkpoint" logic happens.

```sql
CREATE TABLE IF NOT EXISTS pipeline_run_history (
  run_id STRING,                             -- UUID generated per run
  pipeline_name STRING,                      -- FK to pipeline_definition
  run_type STRING,                           -- 'baseline' | 'incremental'
  batch_id LONG,                             -- version or id being processed
  last_success_batch_id LONG,                -- checkpoint
  status STRING,                             -- PLANNED, RUNNING, COMPLETED, FAILED, RETRY
  start_ts TIMESTAMP,
  end_ts TIMESTAMP,
  duration_ms LONG,
  retry_count INT,
  updated_by STRING,
  update_ts TIMESTAMP,
  error_details STRING,
  PRIMARY KEY (run_id)
)
USING DELTA;
```

- - Benefits- - :
- ✔ Allows unlimited run history
- ✔ Allows tracking retries and failures
- ✔ Duration is precomputed
- ✔ Supports baseline/incremental mode
- ✔ Safely links to pipeline config
- ✔ Cleaner and scalable for >20 pipelines

---

### 🔥 3. Pipeline Operational Workflow (How each pipeline should use this table)

Here is the standard flow every pipeline should follow.


#### Step 1 — Pipeline registers its run (PLANNED)

```sql
INSERT INTO pipeline_run_history (
  run_id, pipeline_name, run_type, batch_id, last_success_batch_id,
  status, start_ts, update_ts, updated_by
)
VALUES (
  uuid(), 'authorprofile', 'incremental', 1050, 1049,
  'PLANNED', current_timestamp(), current_timestamp(), 'scheduler'
);
```

---

### Step 2 — Pipeline starts and marks RUNNING

```sql
UPDATE pipeline_run_history
SET status = 'RUNNING',
    start_ts = current_timestamp(),
    update_ts = current_timestamp(),
    updated_by = 'authorprofile-job'
WHERE run_id = '<run-id>';
```

---

#### Step 3 — Pipeline runs business logic

No DB operations—actual processing.


---

#### Step 4 — Pipeline marks COMPLETED

UPDATE pipeline_run_history

```sql
SET status = 'COMPLETED',
    end_ts = current_timestamp(),
    duration_ms = unix_timestamp(end_ts) - unix_timestamp(start_ts),
    last_success_batch_id = batch_id,
    update_ts = current_timestamp(),
    updated_by = 'authorprofile-job'
WHERE run_id = '<run-id>';
```

---

#### Step 5 — Pipeline failure handling

On failure:

```sql
UPDATE pipeline_run_history
SET status = 'FAILED',
    error_details = '<full stacktrace>',
    end_ts = current_timestamp(),
    update_ts = current_timestamp()
WHERE run_id = '<run-id>';
```


Retry logic:

```sql
UPDATE pipeline_run_history
SET retry_count = retry_count + 1,
    status = 'RETRY',
    update_ts = current_timestamp()
WHERE run_id = '<run-id>';
```

---

### 🎯 4. Dashboard / Monitoring Use Cases

Example queries supported by improved schema:

- ✔ Get latest run per pipeline

```sql
SELECT - 
FROM pipeline_run_history
QUALIFY row_number() OVER (PARTITION BY pipeline_name ORDER BY start_ts DESC) = 1;
```

- ✔ View failure rate

```sql
SELECT pipeline_name, COUNT(- ) FILTER (WHERE status='FAILED')
FROM pipeline_run_history
GROUP BY pipeline_name;
```

- ✔ Checkpoint lookup for incremental pipelines

```sql
SELECT pipeline_name, last_success_batch_id
FROM pipeline_run_history
WHERE status='COMPLETED'
QUALIFY row_number() OVER (PARTITION BY pipeline_name ORDER BY end_ts DESC) = 1;
```

--

### 🎉 5. Summary of Improvements

| Topic | Original | Improved |
|-------|----------|----------|
| Run history | Overwritten | Fully tracked |
| Logical separation | Mixed | 2 tables: definition + run history |
| Durations | Missing | Stored |
| Retry support | Missing | Built-in |
| Baseline vs Incremental | Missing | Explicit run_type |
| Failure details | Short | Long text |
| Multiple pipelines | Weak | Strong multi-pipeline isolation |
| Checkpoint accuracy | Limited | Clean last_success_batch_id |

👍 If you want

I can also generate:

- ✅ Databricks SQL Dashboard
- ✅ REST API or Scala utility for updating runs
- ✅ Example orchestration YAML
- ✅ Example with Delta CDF version checkpointing


--

## Production-ready Scala Utility object


Below is a production-ready Scala utility object that manages pipeline runs for 20+ pipelines, including:

- ✔ create new run
- ✔ update to RUNNING
- ✔ complete run
- ✔ fail run
- ✔ retry handling
- ✔ fetch latest checkpoint
- ✔ supports baseline / incremental
- ✔ supports Spark + Delta Lake


It uses the improved schema:
-  pipeline_definition
-  pipeline_run_history

If your table names differ, you can parameterize them easily.

---

### ✅ Scala Utility Object: PipelineRunManager

```scala
package com.example.pipeline

import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import java.util.UUID

object PipelineRunManager {

  val spark: SparkSession = SparkSession.getActiveSession.get

  private val runTable = "ag_ra_search_analytics_data_dev.sandbox_v1_0.pipeline_run_history"

  // ---------------------------------------------------------------------------
  // 1. Create PLANNED Run
  // ---------------------------------------------------------------------------
  def createRun(
      pipelineName: String,
      runType: String,                 // "baseline" | "incremental"
      batchId: Long,
      lastSuccessBatchId: Long,
      updatedBy: String = "system"
  ): String = {

    val runId = UUID.randomUUID().toString

    val df = Seq((runId, pipelineName, runType, batchId, lastSuccessBatchId,
      "PLANNED", java.time.Instant.now(), java.time.Instant.now(), updatedBy))
      .toDF("run_id", "pipeline_name", "run_type", "batch_id", "last_success_batch_id",
        "status", "start_ts", "update_ts", "updated_by")

    df.write.format("delta").mode("append").saveAsTable(runTable)

    println(s"Created PLANNED run: $runId")
    runId
  }

  // ---------------------------------------------------------------------------
  // 2. Mark RUNNING
  // ---------------------------------------------------------------------------
  def setRunning(runId: String, updatedBy: String = "system"): Unit = {
    spark.sql(
      s"""
         |UPDATE $runTable
         |SET status = 'RUNNING',
         |    start_ts = current_timestamp(),
         |    update_ts = current_timestamp(),
         |    updated_by = '$updatedBy'
         |WHERE run_id = '$runId'
       """.stripMargin)
  }

  // ---------------------------------------------------------------------------
  // 3. Mark COMPLETED
  // ---------------------------------------------------------------------------
  def setCompleted(runId: String, updatedBy: String = "system"): Unit = {
    spark.sql(
      s"""
         |UPDATE $runTable
         |SET status = 'COMPLETED',
         |    end_ts = current_timestamp(),
         |    duration_ms = (unix_timestamp(current_timestamp()) - unix_timestamp(start_ts)) -  1000,
         |    update_ts = current_timestamp(),
         |    updated_by = '$updatedBy',
         |    last_success_batch_id = batch_id
         |WHERE run_id = '$runId'
       """.stripMargin)
  }

  // ---------------------------------------------------------------------------
  // 4. Mark FAILED
  // ---------------------------------------------------------------------------
  def setFailed(runId: String, error: String, updatedBy: String = "system"): Unit = {
    val safeError = error.replace("'", "''") // escape quotes
    spark.sql(
      s"""
         |UPDATE $runTable
         |SET status = 'FAILED',
         |    error_details = '$safeError',
         |    end_ts = current_timestamp(),
         |    update_ts = current_timestamp(),
         |    updated_by = '$updatedBy'
         |WHERE run_id = '$runId'
       """.stripMargin)
  }

  // ---------------------------------------------------------------------------
  // 5. Retry run
  // ---------------------------------------------------------------------------
  def setRetry(runId: String, updatedBy: String = "system"): Unit = {
    spark.sql(
      s"""
         |UPDATE $runTable
         |SET retry_count = coalesce(retry_count, 0) + 1,
         |    status = 'RETRY',
         |    update_ts = current_timestamp(),
         |    updated_by = '$updatedBy'
         |WHERE run_id = '$runId'
       """.stripMargin)
  }

  // ---------------------------------------------------------------------------
  // 6. Get latest COMPLETED checkpoint (for incremental jobs)
  // ---------------------------------------------------------------------------
  def getLatestCheckpoint(pipelineName: String): Option[Long] = {
    val df = spark.sql(
      s"""
         |SELECT last_success_batch_id
         |FROM $runTable
         |WHERE pipeline_name = '$pipelineName' AND status = 'COMPLETED'
         |ORDER BY end_ts DESC
         |LIMIT 1
       """.stripMargin)

    if (df.isEmpty) None else Some(df.head().getLong(0))
  }

  // ---------------------------------------------------------------------------
  // 7. Get latest run (PLANNED, RUNNING, COMPLETED, FAILED)
  // ---------------------------------------------------------------------------
  def getLatestRun(pipelineName: String): DataFrame = {
    spark.sql(
      s"""
         |SELECT - 
         |FROM $runTable
         |WHERE pipeline_name = '$pipelineName'
         |ORDER BY update_ts DESC
         |LIMIT 1
       """.stripMargin)
  }

  // ---------------------------------------------------------------------------
  // 8. List all runs for audit/history
  // ---------------------------------------------------------------------------
  def getRunHistory(pipelineName: String): DataFrame = {
    spark.sql(
      s"""
         |SELECT - 
         |FROM $runTable
         |WHERE pipeline_name = '$pipelineName'
         |ORDER BY start_ts DESC
       """.stripMargin)
  }

}
```

---


### ✅ How Pipelines Should Use This Utility


#### Use Case: Incremental Pipeline

```scala
import com.example.pipeline.PipelineRunManager

// load checkpoint
val checkpoint = PipelineRunManager.getLatestCheckpoint("authorprofile")

val nextBatch = checkpoint.getOrElse(0L) + 1

// start new run
val runId = PipelineRunManager.createRun(
  pipelineName = "authorprofile",
  runType = "incremental",
  batchId = nextBatch,
  lastSuccessBatchId = checkpoint.getOrElse(0L),
  updatedBy = "authorprofile-job"
)

// Mark running
PipelineRunManager.setRunning(runId)

try {
  // --- pipeline business logic ---
  processAuthorProfile(nextBatch)

  PipelineRunManager.setCompleted(runId)
} catch {
  case e: Exception =>
    PipelineRunManager.setFailed(runId, e.toString)
    throw e
}
```


#### Use Case: Baseline Pipeline

```scala
val runId = PipelineRunManager.createRun(
  pipelineName = "authorprofile",
  runType = "baseline",
  batchId = 0,
  lastSuccessBatchId = 0,
  updatedBy = "baseline-loader"
)

PipelineRunManager.setRunning(runId)

try {
  runBaselineLoad()
  PipelineRunManager.setCompleted(runId)
} catch {
  case e: Exception =>
    PipelineRunManager.setFailed(runId, e.toString)
}
```

---

### 🚀 Benefits of This Utility

- ✔ Works for 20+ pipelines
- ✔ Central management of statuses
- ✔ Unified API for incremental/baseline runs
- ✔ Fully supports retries and failure logging
- ✔ Improves observability and auditability
- ✔ Simple for pipelines to use (just call functions)
- ✔ Supports dashboards, alerts, SLA tracking

If you want, I can also generate:
-  ⭐ A Databricks SQL dashboard to monitor pipelines
-  ⭐ A wrapper class to integrate with Airflow/Databricks jobs
-  ⭐ A CLI tool to inspect and manage runs

---

##  Production-ready CDFPipelineRunner 

Below is a complete, production-ready CDFPipelineRunner that provides a unified pipeline execution framework for baseline + incremental, including:

- ✅ Automatic run creation
- ✅ CDF version checkpointing
- ✅ Baseline / incremental unified logic
- ✅ Robust error handling
- ✅ Start/end timestamps, duration, status updates
- ✅ Built-in metrics
- ✅ Pluggable business logic function
- ✅ Reusable across 20+ pipelines

---

### 🚀 CDFPipelineRunner (Full Implementation)

```scala
package com.example.pipeline

import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import java.util.UUID

class CDFPipelineRunner(runTable: String)(implicit spark: SparkSession) {

  /- -  --------------------------------------------------------------
    -  Utility helpers
    -  -------------------------------------------------------------- - /

  private def nowTs = current_timestamp()

  /- -  Read latest Delta table version - /
  def getLatestTableVersion(table: String): Long = {
    spark.sql(s"DESCRIBE HISTORY $table")
      .select(max("version")).as[Long].first()
  }

  /- -  Get last successfully processed CDF version for the pipeline - /
  def getLastSuccessVersion(pipeline: String): Long = {
    val df = spark.sql(
      s"""
         |SELECT last_success_version
         |FROM $runTable
         |WHERE pipeline_name = '$pipeline'
         |  AND status = 'COMPLETED'
         |ORDER BY end_ts DESC
         |LIMIT 1
       """.stripMargin)

    if (df.isEmpty) 0L else df.head().getLong(0)
  }


  /- -  --------------------------------------------------------------
    -  Run Management
    -  -------------------------------------------------------------- - /

  /- -  Create a new run record (baseline or incremental) - /
  def createRun(
      pipelineName: String,
      table: String,
      runType: String,               // "baseline" | "incremental"
      updatedBy: String = "system"
  ): (String, Long, Long) = {

    val lastVersion =
      if (runType == "incremental") getLastSuccessVersion(pipelineName)
      else 0L

    val latestVersion =
      if (runType == "incremental") getLatestTableVersion(table)
      else 0L

    val runId = UUID.randomUUID().toString

    val df = Seq(
      (runId, pipelineName, runType, lastVersion, latestVersion,
        "PLANNED", java.time.Instant.now(), java.time.Instant.now(), updatedBy)
    ).toDF("run_id", "pipeline_name", "run_type",
      "start_version", "end_version",
      "status", "start_ts", "update_ts", "updated_by")

    df.write.format("delta").mode("append").saveAsTable(runTable)

    (runId, lastVersion, latestVersion)
  }

  def setRunning(runId: String): Unit = {
    spark.sql(
      s"""
         |UPDATE $runTable
         |SET status = 'RUNNING',
         |    update_ts = current_timestamp()
         |WHERE run_id = '$runId'
       """.stripMargin)
  }

  def setCompleted(runId: String): Unit = {
    spark.sql(
      s"""
         |UPDATE $runTable
         |SET status = 'COMPLETED',
         |    end_ts = current_timestamp(),
         |    duration_ms = 
         |      (unix_timestamp(current_timestamp()) - unix_timestamp(start_ts)) -  1000,
         |    last_success_version = end_version,
         |    update_ts = current_timestamp()
         |WHERE run_id = '$runId'
       """.stripMargin)
  }

  def setFailed(runId: String, error: String): Unit = {
    spark.sql(
      s"""
         |UPDATE $runTable
         |SET status = 'FAILED',
         |    end_ts = current_timestamp(),
         |    error_message = '${error.replace("'", "")}',
         |    update_ts = current_timestamp()
         |WHERE run_id = '$runId'
       """.stripMargin)
  }


  /- -  --------------------------------------------------------------
    -  Core Pipeline Runner (baseline & incremental)
    -  -------------------------------------------------------------- - /

  /- - 
    -  Run a pipeline using a provided transformation function.
    - 
    -  @param pipelineName    Name of pipeline (e.g. "authorprofile")
    -  @param sourceTable     Delta source table with CDF enabled
    -  @param toOutputTable   Function to write the final result
    -  @param transformFn     Business logic: DataFrame => DataFrame
    -  @param runType         "baseline" or "incremental"
    -  @param updatedBy       Who triggered pipeline
    - /
  def runPipeline(
      pipelineName: String,
      sourceTable: String,
      transformFn: DataFrame => DataFrame,
      toOutputTable: DataFrame => Unit,
      runType: String,                      // "baseline" | "incremental"
      updatedBy: String = "system"
  ): Unit = {

    val (runId, startVersion, endVersion) =
      createRun(pipelineName, sourceTable, runType, updatedBy)

    setRunning(runId)

    try {

      val inputDF =
        if (runType == "baseline") {
          spark.table(sourceTable)
        } else {
          // CDF Incremental Load
          spark.read
            .format("delta")
            .option("readChangeData", "true")
            .option("startingVersion", startVersion)
            .option("endingVersion", endVersion)
            .table(sourceTable)
            .filter("_change_type IN ('insert', 'update_postimage')")
        }

      val result = transformFn(inputDF)

      toOutputTable(result)

      setCompleted(runId)

    } catch {
      case e: Exception =>
        setFailed(runId, e.toString)
        throw e
    }
  }

}
```


### 🚀 How to Use CDFPipelineRunner

#### Initialize

```scala
import com.example.pipeline.CDFPipelineRunner

implicit val spark = sparkSession

val runner = new CDFPipelineRunner(
  runTable = "ag_ra_search_analytics_data_dev.sandbox_v1_0.pipeline_run_history"
)
```

---

#### 🧪 Incremental Pipeline Example

```scala
runner.runPipeline(
  pipelineName = "authorprofile",
  sourceTable = "gold_wos.d_publication",
  transformFn = df => processAuthorProfile(df),
  toOutputTable = df => df.write.mode("overwrite").saveAsTable("gold.authorprofile"),
  runType = "incremental",
  updatedBy = "author-profile-job"
)
```

---

#### 🧪 Baseline Pipeline Example


```scala
runner.runPipeline(
  pipelineName = "authorprofile",
  sourceTable = "gold_wos.d_publication",
  transformFn = df => processAuthorProfile(df),
  toOutputTable = df => df.write.mode("overwrite").saveAsTable("gold.authorprofile"),
  runType = "baseline"
)
```

---

### 🧩 PipelineRunHistory Table Schema

This runner expects:

```sql
CREATE TABLE pipeline_run_history (
  run_id STRING,
  pipeline_name STRING,
  run_type STRING,
  start_version LONG,
  end_version LONG,
  last_success_version LONG,
  start_ts TIMESTAMP,
  end_ts TIMESTAMP,
  duration_ms LONG,
  status STRING,        -- PLANNED, RUNNING, FAILED, COMPLETED
  updated_by STRING,
  update_ts TIMESTAMP,
  error_message STRING
) USING DELTA;
```

---

🎯 Done — You now have a complete CDF pipeline framework

Used for 20+ pipelines and scalable to 100+.
If you want, I can also generate:

- ✅ A template folder structure for all pipelines
- ✅ A sample "authorprofile" implementation
- ✅ Airflow / ADF wrapper for triggering
- ✅ Monitoring dashboard SQL


---

## Databricks SQL Dashboard Design


Below is a ready-to-use Databricks SQL Dashboard design to monitor 20+ CDF pipelines, including:

-  Pipeline status (running, completed, failed)
-  SLA tracking
-  Run duration
-  Error messages
-  Trend over time
-  Incremental vs Baseline runs
-  Latest CDF versions processed

All queries assume the run-history table:

ag_ra_search_analytics_data_dev.sandbox_v1_0.pipeline_run_history

---

### 🚀 1. Dashboard Layout

Your Databricks SQL dashboard will include:

| Widget | Purpose |
|--------|---------|
| 1. Pipeline Overview (Status Heatmap) | Quick view of last status for each pipeline |
| 2. Failures (Last 7 Days) | Shows failed runs + errors |
| 3. Run Duration Trend (Line Chart) | Duration over time |
| 4. Latest CDF Versions Processed | Tracks version progression |
| 5. Pipeline SLA Indicator | Check if runs are stale or delayed |
| 6. Recent Run Details (Table) | All pipeline execution logs |

---

### 🟦 2. SQL Queries for Dashboard Widgets


#### Widget 1 — Latest Pipeline Status (Heatmap)

```sql
WITH latest AS (
  SELECT *
  FROM ag_ra_search_analytics_data_dev.sandbox_v1_0.pipeline_run_history
  QUALIFY ROW_NUMBER() OVER (PARTITION BY pipeline_name ORDER BY end_ts DESC) = 1
)
SELECT
  pipeline_name,
  status,
  run_type,
  start_version,
  end_version,
  end_ts
FROM latest
ORDER BY pipeline_name;
```

- *Visualization**:
-  Chart type: Heatmap or Color-coded table
-  Color by status:
    -  🟩 COMPLETED
    -  🟨 RUNNING
    -  🟥 FAILED
    -  ⚪ PLANNED

---

#### Widget 2 — Failures in Last 7 Days

```sql
SELECT 
  pipeline_name,
  run_id,
  start_ts,
  end_ts,
  status,
  error_message
FROM ag_ra_search_analytics_data_dev.sandbox_v1_0.pipeline_run_history
WHERE status = 'FAILED'
  AND start_ts >= current_timestamp() - INTERVAL 7 DAYS
ORDER BY end_ts DESC;
```

- *Visualization**:
-  Table
-  Highlight rows with errors

---

#### Widget 3 — Run Duration Trend (Line Chart)

```sql
SELECT
  pipeline_name,
  end_ts,
  duration_ms / 1000 AS duration_sec
FROM ag_ra_search_analytics_data_dev.sandbox_v1_0.pipeline_run_history
WHERE status = 'COMPLETED'
ORDER BY pipeline_name, end_ts;
```

- *Visualization**:
-  Line chart
-  X-axis: end_ts
-  Y-axis: duration_sec
-  Series: pipeline_name
Great to observe performance degradation.

---

### Widget 4 — Latest Processed CDF Version

```sql
WITH latest AS (
  SELECT *
  FROM ag_ra_search_analytics_data_dev.sandbox_v1_0.pipeline_run_history
  QUALIFY ROW_NUMBER() OVER (PARTITION BY pipeline_name ORDER BY end_ts DESC) = 1
)
SELECT 
  pipeline_name,
  run_type,
  start_version,
  end_version,
  end_version - start_version AS delta_processed,
  end_ts
FROM latest
ORDER BY pipeline_name;
```

- *Visualization**:
-  Table
-  Or bar chart of delta_processed
Useful to detect:
-  Stuck pipelines
-  No CDF changes
-  Oversized increments

---

#### Widget 5 — Pipeline SLA Monitor

Tracks pipelines not run for >24 hours.

```sql
WITH latest AS (
  SELECT *
  FROM ag_ra_search_analytics_data_dev.sandbox_v1_0.pipeline_run_history
  QUALIFY ROW_NUMBER() OVER (PARTITION BY pipeline_name ORDER BY end_ts DESC) = 1
)
SELECT
  pipeline_name,
  end_ts AS last_run,
  CASE 
    WHEN end_ts < current_timestamp() - INTERVAL 24 HOURS
      THEN 'MISSED_SLA'
    ELSE 'OK'
  END AS sla_status
FROM latest
ORDER BY sla_status DESC, pipeline_name;
```

- *Visualization**:
-  Color-coded table
-  Red = SLA missed

---

#### Widget 6 — Recent Runs Table (Detailed Logging)

```sql
SELECT
  run_id,
  pipeline_name,
  run_type,
  start_ts,
  end_ts,
  ROUND(duration_ms/1000, 1) AS duration_sec,
  status,
  updated_by,
  start_version,
  end_version,
  error_message
FROM ag_ra_search_analytics_data_dev.sandbox_v1_0.pipeline_run_history
ORDER BY start_ts DESC
LIMIT 500;
```

- *Visualization**:
-  Table with sorting + search

---

### 🎨 Dashboard Style Tips

-  Create Dashboard Filters:
    -  pipeline_name (dropdown)
    -  date range
    -  run_type: baseline / incremental
    -  status filter
-  Use Color rules:
    -  status = FAILED → red
    -  duration_sec > threshold → yellow
    -  SLA missed → red
-  Auto-refresh every 5 or 15 minutes.

---

### 🧩 Optional: Alerts

Enable Databricks SQL Alerts:

- *Alert if pipeline fails**

```sql
SELECT COUNT(*) 
FROM pipeline_run_history 
WHERE status = 'FAILED'
  AND end_ts >= current_timestamp() - INTERVAL 1 HOUR;
```

Trigger when count > 0.

- *Alert if SLA missed**

```sql
WITH latest AS (
  SELECT pipeline_name, end_ts
  FROM pipeline_run_history
  QUALIFY ROW_NUMBER() OVER (PARTITION BY pipeline_name ORDER BY end_ts DESC) = 1
)
SELECT COUNT(*)
FROM latest
WHERE end_ts < current_timestamp() - INTERVAL 24 HOURS;
```
---

### ✔️ Next Steps

I can also generate:

- ✅ A complete Databricks SQL dashboard export .json
- ✅ HTML wireframe of the dashboard layout
- ✅ A Databricks Job workflow integrating this dashboard
- ✅ A CI/CD pattern for dashboards


---

## Databricks SQL Dashboard JSON template

Below is a ready-to-import Databricks SQL Dashboard JSON template, containing all widgets described earlier:

-  Pipeline Status Heatmap
-  Failure Log (7 days)
-  Duration Trend
-  Latest CDF Versions
-  SLA Monitor
-  Recent Run Details

You can import this JSON directly into Databricks SQL UI:
SQL → Dashboards → Import → Upload JSON

---

### 📦 Databricks SQL Dashboard JSON Template

NOTE: 
- Replace the schema/table names as needed.
- Dashboard uses default catalog ag_ra_search_analytics_data_dev.sandbox_v1_0.

```json
{
  "version": "1.0",
  "dashboard": {
    "name": "CDF Pipeline Monitoring Dashboard",
    "description": "Monitor 20+ Delta CDF pipelines: status, duration, versions, SLA, history.",
    "widgets": [
      {
        "title": "Pipeline Status (Latest Run)",
        "visualization": "table",
        "position": { "row": 0, "col": 0, "width": 6, "height": 6 },
        "query": {
          "name": "latest_pipeline_status",
          "sql": "WITH latest AS (\n  SELECT *\n  FROM ag_ra_search_analytics_data_dev.sandbox_v1_0.pipeline_run_history\n  QUALIFY ROW_NUMBER() OVER (PARTITION BY pipeline_name ORDER BY end_ts DESC) = 1\n)\nSELECT pipeline_name, status, run_type, start_version, end_version, end_ts\nFROM latest\nORDER BY pipeline_name;"
        }
      },
      {
        "title": "Pipeline Failures (Last 7 Days)",
        "visualization": "table",
        "position": { "row": 0, "col": 6, "width": 6, "height": 6 },
        "query": {
          "name": "recent_failures",
          "sql": "SELECT pipeline_name, run_id, start_ts, end_ts, status, error_message\nFROM ag_ra_search_analytics_data_dev.sandbox_v1_0.pipeline_run_history\nWHERE status = 'FAILED' AND start_ts >= current_timestamp() - INTERVAL 7 DAYS\nORDER BY end_ts DESC;"
        }
      },
      {
        "title": "Pipeline Duration Trend",
        "visualization": "line",
        "position": { "row": 6, "col": 0, "width": 12, "height": 6 },
        "query": {
          "name": "duration_trend",
          "sql": "SELECT pipeline_name, end_ts, duration_ms / 1000 AS duration_sec\nFROM ag_ra_search_analytics_data_dev.sandbox_v1_0.pipeline_run_history\nWHERE status = 'COMPLETED'\nORDER BY pipeline_name, end_ts;"
        },
        "config": {
          "x_column": "end_ts",
          "y_column": "duration_sec",
          "series": "pipeline_name"
        }
      },
      {
        "title": "Latest CDF Versions Processed",
        "visualization": "table",
        "position": { "row": 12, "col": 0, "width": 6, "height": 6 },
        "query": {
          "name": "latest_versions",
          "sql": "WITH latest AS (\n  SELECT *\n  FROM ag_ra_search_analytics_data_dev.sandbox_v1_0.pipeline_run_history\n  QUALIFY ROW_NUMBER() OVER (PARTITION BY pipeline_name ORDER BY end_ts DESC) = 1\n)\nSELECT pipeline_name, run_type, start_version, end_version,\n       end_version - start_version AS delta_processed,\n       end_ts\nFROM latest\nORDER BY pipeline_name;"
        }
      },
      {
        "title": "Pipeline SLA (24h check)",
        "visualization": "table",
        "position": { "row": 12, "col": 6, "width": 6, "height": 6 },
        "query": {
          "name": "sla_check",
          "sql": "WITH latest AS (\n  SELECT pipeline_name, end_ts\n  FROM ag_ra_search_analytics_data_dev.sandbox_v1_0.pipeline_run_history\n  QUALIFY ROW_NUMBER() OVER (PARTITION BY pipeline_name ORDER BY end_ts DESC) = 1\n)\nSELECT pipeline_name, end_ts AS last_run,\n  CASE WHEN end_ts < current_timestamp() - INTERVAL 24 HOURS\n       THEN 'MISSED_SLA'\n       ELSE 'OK'\n  END AS sla_status\nFROM latest\nORDER BY sla_status DESC, pipeline_name;"
        }
      },
      {
        "title": "Recent Runs (Detailed Logs)",
        "visualization": "table",
        "position": { "row": 18, "col": 0, "width": 12, "height": 8 },
        "query": {
          "name": "run_details",
          "sql": "SELECT run_id, pipeline_name, run_type, start_ts, end_ts,\n  ROUND(duration_ms / 1000, 1) AS duration_sec,\n  status, updated_by, start_version, end_version, error_message\nFROM ag_ra_search_analytics_data_dev.sandbox_v1_0.pipeline_run_history\nORDER BY start_ts DESC\nLIMIT 500;"
        }
      }
    ],
    "parameters": [
      {
        "name": "pipeline_name_filter",
        "title": "Pipeline Name",
        "type": "text",
        "default": ""
      },
      {
        "name": "date_range_filter",
        "title": "Date Range",
        "type": "date_range",
        "default": "last_7_days"
      }
    ]
  }
}
```

---

### 🧩 What You Get

- ✔ Full monitoring dashboard
- ✔ Fully importable JSON
- ✔ Works for 20+ pipelines automatically
- ✔ Uses your existing checkpoint table
- ✔ Includes SLA logic, duration tracking, version tracking


### 📌 Want an Expanded Dashboard?

I can generate optional add-ons:
- ✅ Latency Heatmap
- ✅ Pipeline dependency graph (DAG)
- ✅ CDF version drift detector
- ✅ Alert dashboard for failures & SLA breaches
- ✅ Cost & cluster runtime metrics

Just tell me "Add latency panel" or "Add SLA alert panel".

---


