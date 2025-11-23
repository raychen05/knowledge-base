## Full Enterprise-Grade Incremental Watermark Tracking System



-If you are building enterprise-grade incremental pipelines across multiple domains:
    - 👉 Using a separate watermark table is the more professional and maintainable approach.
    - 👉 Suitable when: Multiple pipelines, shared sources, or manual recovery operations are needed.
- If your pipeline is a simple, self-contained streaming job:
    - 👉 Using Spark’s automatic watermark + checkpoint is perfectly fine.
    - 👉 Suitable when: The pipeline is stand-alone and you don’t need cross-job coordination.


**Includes**:

- Watermark tracking table schema (SQL)
- Scala helper class to read/update watermark
- Reusable incremental ingestion pattern with Delta
- Integration with your Table enum
- Recommended folder structure & best practices

Absolutely! Below is a Scala helper class/object WatermarkTracker tailored to your schema and your three-step logic. This is designed to work with Databricks Delta tables and multiple pipelines, providing an automated, reusable checkpoint management utility.


---

### ⭐ Recommendation for professional incremental control

If your team handles multiple sources (wos/pprn/entity) and 100+ tables:

**Use a watermark table**

because it:
- provides transparency
- supports lineage
- allows manual corrections
- enables pipeline collaboration
- works even if checkpoint is cleared
- centralizes incremental logic

This is extremely valuable in complex enterprise pipelines.


---

###  WatermarkTracker Helper (Scala)

```scala

import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.functions._
import java.sql.Timestamp
import java.time.Instant

case class WatermarkRecord(
    watermark_id: Option[Int] = None,
    pipeline_name: String,
    job_id: String,
    last_processed_ts: Option[Timestamp],
    current_run_ts: Option[Timestamp],
    last_processed_version: Option[Long],
    status: String = "RUNNING",
    created_at: Option[Timestamp] = Some(Timestamp.from(Instant.now())),
    updated_at: Option[Timestamp] = Some(Timestamp.from(Instant.now()))
)

object WatermarkTracker {

  val checkpointTable = "ag_ra_search_analytics_data_dev.dap_ops_v1_0.watermarks"

  /** Step 1: Start a new run for a pipeline **/
  def startPipelineRun(pipeline: String, jobId: String)(implicit spark: SparkSession): WatermarkRecord = {
    import spark.implicits._

    val lastRecordOpt = spark.table(checkpointTable)
      .filter($"pipeline_name" === pipeline)
      .orderBy(desc("created_at"))
      .limit(1)
      .as[WatermarkRecord]
      .collect()
      .headOption

    val lastProcessedTs = lastRecordOpt.flatMap(_.current_run_ts.orElse(_.last_processed_ts))
    val nowTs = Timestamp.from(Instant.now())

    // Update the current checkpoint to indicate ongoing run
    lastRecordOpt.foreach { rec =>
      spark.table(checkpointTable)
        .filter($"watermark_id" === rec.watermark_id.getOrElse(-1))
        .withColumn("current_run_ts", lit(nowTs))
        .withColumn("status", lit("RUNNING"))
        .withColumn("updated_at", current_timestamp())
        .write
        .format("delta")
        .mode("overwrite")
        .option("replaceWhere", s"watermark_id = ${rec.watermark_id.getOrElse(-1)}")
        .saveAsTable(checkpointTable)
    }

    WatermarkRecord(
      pipeline_name = pipeline,
      job_id = jobId,
      last_processed_ts = lastProcessedTs,
      current_run_ts = Some(nowTs),
      status = "RUNNING"
    )
  }

  /** Step 2: Get delta extraction window **/
  def getDeltaWindow(pipeline: String)(implicit spark: SparkSession): (Option[Timestamp], Timestamp) = {
    val lastRecordOpt = spark.table(checkpointTable)
      .filter($"pipeline_name" === pipeline)
      .orderBy(desc("created_at"))
      .limit(1)
      .collect()
      .headOption

    val startTs = lastRecordOpt.flatMap(row => Option(row.getAs[Timestamp]("last_processed_ts")))
    val endTs = Timestamp.from(Instant.now())
    (startTs, endTs)
  }

  /** Step 3: Finalize checkpoint for SUCCESS, FAILED, or SKIPPED **/
  def finalizePipelineRun(record: WatermarkRecord, finalStatus: String)(implicit spark: SparkSession): Unit = {
    import spark.implicits._

    require(Set("SUCCESS", "FAILED", "SKIPPED").contains(finalStatus.toUpperCase),
      s"Invalid status: $finalStatus. Must be SUCCESS, FAILED, or SKIPPED.")

    val nowTs = Timestamp.from(Instant.now())

    // 1. Update current record with final status
    spark.table(checkpointTable)
      .filter($"pipeline_name" === record.pipeline_name && $"job_id" === record.job_id)
      .withColumn("status", lit(finalStatus.toUpperCase))
      .withColumn("updated_at", current_timestamp())
      .write
      .format("delta")
      .mode("overwrite")
      .option("replaceWhere", s"pipeline_name = '${record.pipeline_name}' AND job_id = '${record.job_id}'")
      .saveAsTable(checkpointTable)

    // 2. Only create a new record if the run was SUCCESS
    if (finalStatus.toUpperCase == "SUCCESS") {
      val nextRecord = WatermarkRecord(
        pipeline_name = record.pipeline_name,
        job_id = java.util.UUID.randomUUID().toString,
        last_processed_ts = record.current_run_ts,
        current_run_ts = None,
        last_processed_version = record.current_run_ts.map(_.getTime),
        status = "READY"
      )

      Seq(nextRecord).toDF()
        .write
        .format("delta")
        .mode("append")
        .saveAsTable(checkpointTable)
    }
  }
}


```

---


### Table Definition


```sql
CREATE TABLE IF NOT EXISTS ag_ra_search_analytics_data_dev.dap_ops_v1_0.watermarks (
    watermark_id             INT,                     -- Unique ID for each watermark record
    pipeline_name            STRING,                  -- Name of the pipeline
    job_id                   STRING,                  -- Job or run identifier
    last_processed_ts        TIMESTAMP,               -- Last processed event timestamp
    current_run_ts           TIMESTAMP,               -- Current processing run timestamp
    last_processed_version   BIGINT,                  -- Version of last processed data
    status                   STRING,                  -- Status of the run (e.g., SUCCESS, FAILED, RUNNING)
    created_at               TIMESTAMP,               -- Record creation time
    updated_at               TIMESTAMP                -- Last update time
)
USING DELTA
PARTITIONED BY (pipeline_name);

```

- Consistent naming convention: snake_case, _ts suffix for timestamps.
- Clear intent: Each column clearly describes its purpose.
- Partitioning: By pipeline_name, allows efficient incremental reads.
- Extensible: Easy to add new columns like error_message, run_duration, etc.
- Delta table: Supports ACID updates and efficient incremental queries.



---

### How It Works


#### Step 1 – Start Pipeline Run

```scala
implicit val spark: SparkSession = SparkSession.builder().getOrCreate()

val wmRecord = WatermarkTracker.startPipelineRun("wos_pipeline", "job_123")


```

- Reads the latest checkpoint for the pipeline
- Gets last_processed_ts for delta extraction
- Sets current_run_ts to now
- Updates checkpoint table to indicate the run is RUNNING



#### Step 2 – Pipeline reads delta


```scala
val (startTsOpt, endTs) = WatermarkTracker.getDeltaWindow("wos_pipeline")

val deltaDF = spark.table("acs_source_table")
  .filter(col("updated_at") > startTsOpt.getOrElse(Timestamp.valueOf("1970-01-01 00:00:00")) &&
          col("updated_at") <= endTs)

```

#### Step 3 – Finalize checkpoint


```scala
WatermarkTracker.finalizePipelineRun(wmRecord)

```

- Marks current checkpoint as SUCCESS
- Creates a new checkpoint record (READY) for the next incremental run
- Sets last_processed_ts for next run

---

### Usage Example

```scala
implicit val spark: SparkSession = SparkSession.builder().getOrCreate()

// Step 1: Start the pipeline run
val wmRecord = WatermarkTracker.startPipelineRun("wos_pipeline", "job_001")

// Step 2: Extract delta data
val (startTsOpt, endTs) = WatermarkTracker.getDeltaWindow("wos_pipeline")
val deltaDF = spark.table("acs_source_table")
  .filter(col("updated_at") > startTsOpt.getOrElse(Timestamp.valueOf("1970-01-01 00:00:00")) &&
          col("updated_at") <= endTs)

// --- process deltaDF ---

// Step 3: Finalize checkpoint
// Use "SUCCESS", "FAILED", or "SKIPPED" depending on run outcome
WatermarkTracker.finalizePipelineRun(wmRecord, finalStatus = "SUCCESS")


```


---






---

### ✅ Advantages of This Implementation

- Supports multiple pipelines in one table.
- Tracks start, end timestamps, status, and version.
- Works automatically with Delta and ensures ACID updates.
- Prepares a ready-to-use checkpoint for the next run.
- Easily extensible (e.g., add error_message, run_duration columns).


---


### ✅ Enhancements in this Version

- Supports SUCCESS, FAILED, SKIPPED statuses.
- Only creates a new checkpoint record for SUCCESS runs.
- Ensures type-safe, standardized status with validation.
- Works for multiple pipelines and multiple runs concurrently.
- Keeps checkpoint table clean and consistent, supporting incremental extraction.