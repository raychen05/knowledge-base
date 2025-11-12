
## Databricks Scala Notebooks Logging Run Tracker Enrichment Eswriter


###   Databricks Scala Notebook Set


**Notebooks included*- (all in this single notebook document as separate sections):

1) 0_CONFIG - configuration cell (set paths, secrets scope/names, ES settings)
2) 1_DeltaLogger - a lightweight structured logger that appends JSON rows to a Delta log table
3) 2_RunTracker - functions to start/finish/update pipeline run status in a Delta table
4) 3_EnrichmentJob - simple batch enrichment/compaction job for logs_delta -> logs_delta_enriched
5) 4_ESWriter - idempotent Elasticsearch writer (uses connector if installed) and alternative foreachPartition writer
6) 5_UsageExample - shows how to instrument a pipeline step using DeltaLogger + RunTracker and write index to ES

**INSTRUCTIONS BEFORE RUNNING**:

- Install required libraries on the cluster (Maven coordinates):
  - For ES connector (match your ES & Spark versions): e.g. org.elasticsearch:elasticsearch-spark-30_2.12:8.6.3
  - If using elasticsearch-java REST client in custom code, install appropriate client libs.
- Create Databricks Secret Scope and store ES credentials: e.g. secret scope `es_scope` keys `es_user`, `es_pwd`, `es_host`.
- Adjust table names and storage locations below in the CONFIG section.
- This notebook is written for Databricks Runtime Spark 3.x and Scala 2.12. Adjust as needed.



```scala

/*
Databricks Scala Notebook Set
Files / Notebooks included (all in this single notebook document as separate sections):

1) 0_CONFIG - configuration cell (set paths, secrets scope/names, ES settings)
2) 1_DeltaLogger - a lightweight structured logger that appends JSON rows to a Delta log table
3) 2_RunTracker - functions to start/finish/update pipeline run status in a Delta table
4) 3_EnrichmentJob - simple batch enrichment/compaction job for logs_delta -> logs_delta_enriched
5) 4_ESWriter - idempotent Elasticsearch writer (uses connector if installed) and alternative foreachPartition writer
6) 5_UsageExample - shows how to instrument a pipeline step using DeltaLogger + RunTracker and write index to ES

INSTRUCTIONS BEFORE RUNNING:
- Install required libraries on the cluster (Maven coordinates):
  - For ES connector (match your ES & Spark versions): e.g. org.elasticsearch:elasticsearch-spark-30_2.12:8.6.3
  - If using elasticsearch-java REST client in custom code, install appropriate client libs.
- Create Databricks Secret Scope and store ES credentials: e.g. secret scope `es_scope` keys `es_user`, `es_pwd`, `es_host`.
- Adjust table names and storage locations below in the CONFIG section.
- This notebook is written for Databricks Runtime Spark 3.x and Scala 2.12. Adjust as needed.
*/

// =====================
// 0_CONFIG
// =====================
// Cell: CONFIG
val CONF = Map(
  "env" -> "prod",
  "logs_table" -> "default.logs_delta",           // Delta table to store raw structured logs
  "runs_table" -> "default.pipeline_runs_delta", // Delta table to store run metadata
  "enriched_logs_table" -> "default.logs_delta_enriched",
  "es_index" -> "user_index_v1",
  // secret scope and keys (Databricks Secrets)
  "es_secret_scope" -> "es_scope",
  "es_user_key" -> "es_user",
  "es_pwd_key" -> "es_pwd",
  "es_host_key" -> "es_host",
  // optional staging index/alias
  "es_alias" -> "user_index",
  "es_staging_index" -> "user_index_v1_staging"
)

println("Config:")
CONF.foreach{case (k,v) => println(s"  $k -> $v")}

// Ensure tables exist (create minimal schema if not exist)
import java.sql.Timestamp
import org.apache.spark.sql.types._
import org.apache.spark.sql._

// Raw log schema (as used by DeltaLogger)
val logSchema = StructType(List(
  StructField("timestamp", StringType, true),
  StructField("env", StringType, true),
  StructField("pipeline_id", StringType, true),
  StructField("run_id", StringType, true),
  StructField("step", StringType, true),
  StructField("component", StringType, true),
  StructField("level", StringType, true),
  StructField("message", StringType, true),
  StructField("error", StringType, true),
  StructField("metrics", StringType, true),
  StructField("correlation_id", StringType, true),
  StructField("tags", StringType, true),
  StructField("raw", StringType, true)
))

// Runs schema
val runsSchema = StructType(List(
  StructField("run_id", StringType, false),
  StructField("pipeline_id", StringType, true),
  StructField("trigger_type", StringType, true),
  StructField("start_ts", StringType, true),
  StructField("end_ts", StringType, true),
  StructField("status", StringType, true),
  StructField("current_step", StringType, true),
  StructField("last_error", StringType, true),
  StructField("retry_count", IntegerType, true),
  StructField("owner", StringType, true),
  StructField("correlation_id", StringType, true),
  StructField("dag_version", StringType, true)
))

// Create the Delta tables if not exist (write empty DF with schema)
if (spark.catalog.tableExists(CONF("logs_table"))) {
  println(s"Table ${CONF("logs_table")} exists")
} else {
  val emptyLogs = spark.createDataFrame(spark.sparkContext.emptyRDD[Row], logSchema)
  emptyLogs.write.format("delta").mode("overwrite").saveAsTable(CONF("logs_table"))
  println(s"Created table ${CONF("logs_table")}")
}

if (spark.catalog.tableExists(CONF("runs_table"))) {
  println(s"Table ${CONF("runs_table")} exists")
} else {
  val emptyRuns = spark.createDataFrame(spark.sparkContext.emptyRDD[Row], runsSchema)
  emptyRuns.write.format("delta").mode("overwrite").saveAsTable(CONF("runs_table"))
  println(s"Created table ${CONF("runs_table")}")
}

if (!spark.catalog.tableExists(CONF("enriched_logs_table"))) {
  val empty = spark.createDataFrame(spark.sparkContext.emptyRDD[Row], logSchema)
  empty.write.format("delta").mode("overwrite").saveAsTable(CONF("enriched_logs_table"))
  println(s"Created table ${CONF("enriched_logs_table")}")
} else println(s"Table ${CONF("enriched_logs_table")} exists")

// =====================
// 1_DeltaLogger
// =====================
// Cell: DeltaLogger
import java.time.Instant
import org.apache.spark.sql.Row
import org.apache.spark.sql.functions._
import java.util.UUID

object DeltaLogger {
  // Simple structured logger that appends one row per event to the logs Delta table.
  // NOTE: for very high event rates prefer buffering / Kafka -> stream write to Delta.

  def nowIso(): String = Instant.now().toString

  def makeEvent(pipelineId: String,
                runId: String,
                step: String,
                level: String,
                message: String,
                correlationId: Option[String] = None,
                component: Option[String] = None,
                metricsJson: Option[String] = None,
                tagsJson: Option[String] = None,
                errorJson: Option[String] = None,
                rawJson: Option[String] = None): org.apache.spark.sql.DataFrame = {

    val row = Row(nowIso(), CONF("env"), pipelineId, runId, step, component.getOrElse("driver"), level, message,
      errorJson.getOrElse(null), metricsJson.getOrElse(null), correlationId.getOrElse(null), tagsJson.getOrElse(null), rawJson.getOrElse(null))

    val df = spark.createDataFrame(spark.sparkContext.parallelize(Seq(row)), logSchema)
    df
  }

  def info(pipelineId:String, runId:String, step:String, message:String, extra:Map[String,String] = Map.empty): Unit = {
    val df = makeEvent(pipelineId, runId, step, "INFO", message, correlationId = extra.get("correlation_id"), metricsJson = extra.get("metrics"), tagsJson = extra.get("tags"))
    df.write.format("delta").mode("append").saveAsTable(CONF("logs_table"))
  }

  def warn(pipelineId:String, runId:String, step:String, message:String, extra:Map[String,String] = Map.empty): Unit = {
    val df = makeEvent(pipelineId, runId, step, "WARN", message, correlationId = extra.get("correlation_id"), metricsJson = extra.get("metrics"), tagsJson = extra.get("tags"))
    df.write.format("delta").mode("append").saveAsTable(CONF("logs_table"))
  }

  def error(pipelineId:String, runId:String, step:String, message:String, errorJson: String, extra:Map[String,String] = Map.empty): Unit = {
    val df = makeEvent(pipelineId, runId, step, "ERROR", message, correlationId = extra.get("correlation_id"), metricsJson = extra.get("metrics"), tagsJson = extra.get("tags"), errorJson = Some(errorJson))
    df.write.format("delta").mode("append").saveAsTable(CONF("logs_table"))
  }
}

println("DeltaLogger defined. Example: DeltaLogger.info(\"pipeline\", \"run1\", \"step1\", \"starting\")")

// =====================
// 2_RunTracker
// =====================
// Cell: RunTracker
import org.apache.spark.sql.functions._
import io.delta.tables._

object RunTracker {
  def startRun(pipelineId: String, runId: String, triggerType: String = "cron", owner: String = "unknown", correlationId: String = null, dagVersion: String = null): Unit = {
    val startTs = Instant.now().toString
    val row = Row(runId, pipelineId, triggerType, startTs, null, "RUNNING", null, null, 0, owner, correlationId, dagVersion)
    val df = spark.createDataFrame(spark.sparkContext.parallelize(Seq(row)), runsSchema)
    df.write.format("delta").mode("append").saveAsTable(CONF("runs_table"))
  }

  def finishRun(runId: String, status: String, lastError: String = null): Unit = {
    val dt = DeltaTable.forName(spark, CONF("runs_table"))
    val endTs = Instant.now().toString
    dt.update(expr(s"run_id = '$runId"), Map("end_ts" -> lit(endTs), "status" -> lit(status), "last_error" -> lit(lastError)))
  }

  def updateCurrentStep(runId: String, step: String): Unit = {
    val dt = DeltaTable.forName(spark, CONF("runs_table"))
    dt.update(expr(s"run_id = '$runId"), Map("current_step" -> lit(step)))
  }
}

println("RunTracker defined. Use RunTracker.startRun(...), RunTracker.finishRun(...)")

// =====================
// 3_EnrichmentJob
// =====================
// Cell: EnrichmentJob
// Simple batch enrichment: read raw logs for a date window, parse JSON columns, normalize fields, write to enriched logs table

object EnrichmentJob {
  import org.apache.spark.sql.functions._

  def compactAndEnrich(dateMinIso: String, dateMaxIso: String): Unit = {
    // Simple filter by timestamp text (ISO). For production use, store timestamp as actual timestamp type.
    val raw = spark.table(CONF("logs_table")).filter(col("timestamp") >= lit(dateMinIso) && col("timestamp") <= lit(dateMaxIso))

    // Example enrichment: promote metrics/tags if JSON strings
    val enriched = raw.withColumn("metrics_json_parsed", from_json(col("metrics"), MapType(StringType,StringType)))
      .withColumn("tags_json_parsed", from_json(col("tags"), MapType(StringType,StringType)))
      .withColumn("ts", col("timestamp"))
      .drop("raw")

    // write to enriched table as partitioned by date (optional)
    enriched.write.format("delta").mode("append").saveAsTable(CONF("enriched_logs_table"))
  }
}

println("EnrichmentJob defined. Example: EnrichmentJob.compactAndEnrich(\"2025-01-01T00:00:00Z\", \"2025-12-31T23:59:59Z\")")

// =====================
// 4_ESWriter
// =====================
// Cell: ESWriter
// Two approaches included: (A) Use elasticsearch-spark connector via DataFrameWriter, (B) Use foreachPartition with elasticsearch REST helper

import scala.collection.JavaConverters._
import org.apache.spark.sql._

object ESWriter {
  // Read secrets from Databricks secret scope
  def esConn(): Map[String,String] = {
    val scope = CONF("es_secret_scope")
    val host = dbutils.secrets.get(scope, CONF("es_host_key"))
    val user = dbutils.secrets.get(scope, CONF("es_user_key"))
    val pwd  = dbutils.secrets.get(scope, CONF("es_pwd_key"))
    Map("es.host" -> host, "es.user" -> user, "es.pwd" -> pwd)
  }

  // A: DataFrameWriter using ES connector (ensure connector library installed on cluster)
  def writeDfToEsConnector(df: DataFrame, index: String, idCol: String = null): Unit = {
    val conn = esConn()
    var w = df.write
      .format("org.elasticsearch.spark.sql")
      .option("es.nodes", conn("es.host"))
      .option("es.net.http.auth.user", conn("es.user"))
      .option("es.net.http.auth.pass", conn("es.pwd"))
      .option("es.nodes.wan.only", "true")
      .mode("append")

    if (idCol != null) w = w.option("es.mapping.id", idCol)

    w.option("es.resource", s"$index/_doc").save()
  }

  // B: foreachPartition with elasticsearch-java REST client (more control). This is a minimal example using elasticsearch-rest-high-level-client style pseudo-code.
  // You will need to add the ES REST client jars and adapt to the client version. The code below is schematic and demonstrates the pattern.

  def writeDfToEsForeach(df: DataFrame, index: String, idCol: String): Unit = {
    df.foreachPartition { iter =>
      // Create client per partition (or use a pooled client). Pseudo-code below - replace with concrete client creation.
      import org.elasticsearch.client.RestClient
      import org.elasticsearch.client.RestClientBuilder
      import org.elasticsearch.client.RequestOptions
      import org.elasticsearch.client.RestHighLevelClient
      import org.elasticsearch.action.bulk._
      import org.elasticsearch.action.index.IndexRequest
      import org.elasticsearch.common.xcontent.XContentType

      val conn = esConn()
      val host = conn("es.host")
      // Example: host might be "es-host:9200" or list of hosts; adapt accordingly

      // Build client (replace with correct host parsing for your environment)
      val client = new RestHighLevelClient(RestClient.builder(new org.apache.http.HttpHost(host.split(":")(0), host.split(":")(1).toInt, "http")))

      val bulkRequest = new BulkRequest()
      var count = 0
      iter.foreach { row =>
        val id = if (idCol != null) row.getAs[String](idCol) else java.util.UUID.randomUUID().toString
        val src = row.getValuesMap(row.schema.fieldNames).asJava
        val json = new com.fasterxml.jackson.databind.ObjectMapper().writeValueAsString(src)
        val req = new IndexRequest(index).id(id).source(json, XContentType.JSON)
        bulkRequest.add(req)
        count += 1
        if (count % 500 == 0) {
          client.bulk(bulkRequest, RequestOptions.DEFAULT)
          bulkRequest.requests().clear()
        }
      }
      if (bulkRequest.numberOfActions() > 0) client.bulk(bulkRequest, RequestOptions.DEFAULT)
      client.close()
    }
  }
}

println("ESWriter defined. Choose writeDfToEsConnector or writeDfToEsForeach depending on installed libraries.")

// =====================
// 5_UsageExample
// =====================
// Cell: UsageExample
// Example pattern for instrumenting a pipeline run

import java.util.UUID

val pipelineId = "user_index_pipeline"
val runId = UUID.randomUUID().toString
val owner = "search-team"
val correlationId = UUID.randomUUID().toString

// Start run
RunTracker.startRun(pipelineId, runId, triggerType = "cron", owner = owner, correlationId = correlationId, dagVersion = "git-sha-abcdef")
DeltaLogger.info(pipelineId, runId, "start", s"Pipeline $pipelineId starting", Map("correlation_id" -> correlationId))

try {
  // step: read delta table
  val users = spark.table("default.delta_user_profile").filter("active = true")
  DeltaLogger.info(pipelineId, runId, "read_users", s"Read users count: ${users.count}", Map("correlation_id" -> correlationId, "metrics" -> "{\"rows_read\":"+users.count+"}"))

  // transform to ES docs
  val docs = users.selectExpr("id as doc_id", "name", "email", "updated_at")
    .withColumn("pipeline_id", lit(pipelineId)).withColumn("run_id", lit(runId))

  // write to ES (choose connector or foreach)
  // Option A: connector (simpler if installed)
  ESWriter.writeDfToEsConnector(docs.withColumnRenamed("doc_id","id"), CONF("es_staging_index"), idCol = "id")

  // After all partitions written, swap alias (not shown here). Mark success
  DeltaLogger.info(pipelineId, runId, "es_write", "Wrote docs to ES staging", Map("correlation_id" -> correlationId, "metrics" -> "{\"rows_written\":"+docs.count+"}"))

  RunTracker.finishRun(runId, "SUCCEEDED", null)
  DeltaLogger.info(pipelineId, runId, "finish", "Pipeline finished successfully", Map("correlation_id" -> correlationId))
} catch {
  case e: Exception =>
    val err = org.apache.commons.lang3.exception.ExceptionUtils.getStackTrace(e)
    DeltaLogger.error(pipelineId, runId, "failure", "Pipeline failed", err, Map("correlation_id" -> correlationId))
    RunTracker.finishRun(runId, "FAILED", e.getMessage)
    throw e
}

// End of notebook set
println("Notebook set loaded. Use the sections to instrument your Databricks jobs.")

```

---

Next steps I can do for you (pick any, I'll produce immediately):

- Install-ready cluster library list / exact Maven coordinates for the ES connector matching your Databricks runtime (I can look up versions if you tell me the runtime or want me to fetch them).
- Convert the canvas into separate .scala files or Databricks notebook files (DBC / source) and provide download links.
- Add OpenTelemetry/metrics export scaffolding (Datadog/Prometheus) & alerting SQL queries.
- Add resume-from-step logic and a small orchestration example (Databricks Jobs JSON or Airflow DAG) with automatic retries.
  
Which one would you like next?


---


### SQL DDL for the Delta tables


✅ Added full SQL DDL definitions for Delta tables, including delta_logs, pipeline_runs_delta, delta_logs_enriched, and pipeline_metrics_daily, all optimized for structured logging, tracking, and reporting.


```sql
-- =============================================
-- Databricks Delta Table DDL for Logging & Run Tracking
-- =============================================

-- 1️⃣ LOGGING TABLE
CREATE TABLE IF NOT EXISTS delta_logs (
    event_time TIMESTAMP DEFAULT current_timestamp(),
    run_id STRING,
    pipeline_name STRING,
    stage_name STRING,
    level STRING,               -- INFO / WARN / ERROR
    message STRING,
    exception STRING,
    stack_trace STRING,
    metadata MAP<STRING, STRING>,
    source_file STRING,
    host STRING,
    cluster_id STRING,
    user STRING
) USING DELTA
COMMENT 'Central structured logging table for all pipelines';

-- Partition by date for better query performance
ALTER TABLE delta_logs SET TBLPROPERTIES ('delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCompact' = 'true');

-- 2️⃣ PIPELINE RUN TRACKER TABLE
CREATE TABLE IF NOT EXISTS pipeline_runs_delta (
    run_id STRING,
    pipeline_name STRING,
    triggered_by STRING,        -- user, scheduler, etc.
    trigger_time TIMESTAMP,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status STRING,              -- INIT, RUNNING, SUCCESS, FAILED
    error_message STRING,
    total_records_processed LONG,
    success_records LONG,
    failed_records LONG,
    duration_seconds DOUBLE,
    metadata MAP<STRING, STRING>
) USING DELTA
COMMENT 'Tracks pipeline run states, metrics, and execution status';

-- 3️⃣ ENRICHED LOG TABLE (Derived)
CREATE TABLE IF NOT EXISTS delta_logs_enriched (
    event_date DATE GENERATED ALWAYS AS (CAST(event_time AS DATE)),
    pipeline_name STRING,
    stage_name STRING,
    level STRING,
    error_count LONG,
    warn_count LONG,
    info_count LONG,
    last_error_message STRING,
    last_run_id STRING,
    last_event_time TIMESTAMP
) USING DELTA
COMMENT 'Aggregated and enriched log metrics for dashboarding and alerting';

-- 4️⃣ OPTIONAL: PIPELINE METRICS TABLE (Daily Summary)
CREATE TABLE IF NOT EXISTS pipeline_metrics_daily (
    event_date DATE,
    pipeline_name STRING,
    total_runs LONG,
    success_runs LONG,
    failed_runs LONG,
    avg_duration DOUBLE,
    total_records_processed LONG,
    success_rate DOUBLE,
    fail_rate DOUBLE
) USING DELTA
COMMENT 'Daily aggregated pipeline performance metrics';

```

---

### Sample Sql Queries For Reporting & Alerting


✅ Added a full suite of SQL queries for reporting and alerting — including recent failures, daily success rates, error counts, average duration, top errors, and SLA compliance dashboards.

```sql
-- =============================================
-- 📊 SAMPLE SQL QUERIES FOR REPORTING & ALERTING
-- =============================================


-- 🔹 1. Recent failed pipeline runs
SELECT pipeline_name, run_id, start_time, end_time, error_message
FROM pipeline_runs_delta
WHERE status = 'FAILED'
ORDER BY end_time DESC
LIMIT 50;


-- 🔹 2. Pipeline success/failure summary (daily)
SELECT DATE(start_time) AS event_date,
pipeline_name,
COUNT(*) AS total_runs,
SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) AS success_runs,
SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) AS failed_runs,
ROUND(100 - SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate
FROM pipeline_runs_delta
GROUP BY DATE(start_time), pipeline_name
ORDER BY event_date DESC;


-- 🔹 3. Error count by pipeline and stage (last 24h)
SELECT pipeline_name, stage_name, COUNT(*) AS error_count
FROM delta_logs
WHERE level = 'ERROR'
AND event_time >= current_timestamp() - INTERVAL 24 HOURS
GROUP BY pipeline_name, stage_name
ORDER BY error_count DESC;


-- 🔹 4. Average pipeline duration (7-day rolling)
SELECT pipeline_name,
ROUND(AVG(duration_seconds), 2) AS avg_duration_sec,
COUNT(*) AS runs
FROM pipeline_runs_delta
WHERE start_time >= current_date() - INTERVAL 7 DAYS
GROUP BY pipeline_name
ORDER BY avg_duration_sec DESC;


-- 🔹 5. Error trend by date (for visualization)
SELECT CAST(event_time AS DATE) AS event_date,
pipeline_name,
COUNT(*) AS error_count
FROM delta_logs
WHERE level = 'ERROR'
GROUP BY CAST(event_time AS DATE), pipeline_name
ORDER BY event_date DESC;


-- 🔹 6. Top 10 most frequent error messages
SELECT message, COUNT(*) AS occurrences
FROM delta_logs
WHERE level = 'ERROR'
GROUP BY message
ORDER BY occurrences DESC
LIMIT 10;


-- 🔹 7. Stale / long-running jobs (>1 hour)
SELECT run_id, pipeline_name, start_time, current_timestamp() AS now,
ROUND((unix_timestamp(current_timestamp()) - unix_timestamp(start_time)) / 60, 2) AS runtime_minutes
FROM pipeline_runs_delta
WHERE status = 'RUNNING'
AND start_time < current_timestamp() - INTERVAL 1 HOUR;


-- 🔹 8. Dashboard Query: Daily pipeline SLA compliance
SELECT event_date,
pipeline_name,
success_runs,
failed_runs,
ROUND(success_rate, 2) AS success_rate,
ROUND(avg_duration, 2) AS avg_duration_sec
FROM pipeline_metrics_daily
ORDER BY event_date DESC, pipeline_name;

```


--- 

### 📈 Dashboard Visualization Suggestions


✅ Added a complete alerting and dashboard pack with Databricks SQL queries and suggested visuals (error trends, SLA breaches, pipeline success rate, top errors, latency distribution) — including real-time alert configuration guidance for Slack, Teams, and email.


1️⃣ Overview Dashboard: "Pipeline Health Monitor"

- 🔹 KPI Tiles:
      - Total Runs Today
      - Success Rate (%)
      - Total Failures (Red)
      - Avg Duration (min)
- 🔹 Line Chart: Success Rate by Date (last 30 days)
- 🔹 Heatmap: Errors per Pipeline per Day
- 🔹 Bar Chart: Avg Duration per Pipeline (Top 10)
- 🔹 Table: Latest 20 Failures with error messages

2️⃣ Alerting Dashboard: "Error & SLA Breach Monitor"

- 🔹 Time-series Line Chart: Daily Error Counts
- 🔹 Bar Chart: Pipelines breaching SLA
- 🔹 Table: Long-running or stuck runs
- 🔹 Conditional Alert Tile: Red if success_rate < 95%

3️⃣ Operational Dashboard: "Run Performance Insights"

- 🔹 Scatter Plot: Duration vs Records Processed
- 🔹 Histogram: Runtime Distribution by Pipeline
- 🔹 Table: Top Error Messages (last 7 days)
- 🔹 KPI Tile: # of distinct pipelines run in last 24h



```sql
-- =============================================
-- 🧠 Databricks Delta Logging & Monitoring Pack
-- Includes: DDL + Reporting + Alerting + Dashboard Visuals
-- =============================================

-- 1️⃣ LOGGING TABLE
CREATE TABLE IF NOT EXISTS delta_logs (
    event_time TIMESTAMP DEFAULT current_timestamp(),
    run_id STRING,
    pipeline_name STRING,
    stage_name STRING,
    level STRING,               -- INFO / WARN / ERROR
    message STRING,
    exception STRING,
    stack_trace STRING,
    metadata MAP<STRING, STRING>,
    source_file STRING,
    host STRING,
    cluster_id STRING,
    user STRING
) USING DELTA;

-- 2️⃣ PIPELINE RUN TRACKER TABLE
CREATE TABLE IF NOT EXISTS pipeline_runs_delta (
    run_id STRING,
    pipeline_name STRING,
    triggered_by STRING,
    trigger_time TIMESTAMP,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status STRING,
    error_message STRING,
    total_records_processed LONG,
    success_records LONG,
    failed_records LONG,
    duration_seconds DOUBLE,
    metadata MAP<STRING, STRING>
) USING DELTA;

-- 3️⃣ ENRICHED LOG TABLE
CREATE TABLE IF NOT EXISTS delta_logs_enriched (
    event_date DATE GENERATED ALWAYS AS (CAST(event_time AS DATE)),
    pipeline_name STRING,
    stage_name STRING,
    level STRING,
    error_count LONG,
    warn_count LONG,
    info_count LONG,
    last_error_message STRING,
    last_run_id STRING,
    last_event_time TIMESTAMP
) USING DELTA;

-- 4️⃣ DAILY METRICS TABLE
CREATE TABLE IF NOT EXISTS pipeline_metrics_daily (
    event_date DATE,
    pipeline_name STRING,
    total_runs LONG,
    success_runs LONG,
    failed_runs LONG,
    avg_duration DOUBLE,
    total_records_processed LONG,
    success_rate DOUBLE,
    fail_rate DOUBLE
) USING DELTA;

-- =============================================
-- 📊 ALERTING & DASHBOARD PACK (SQL + VISUALS)
-- =============================================

-- 🔔 ALERT 1: Failed Pipelines (Realtime or 1h schedule)
SELECT pipeline_name, run_id, start_time, end_time, error_message
FROM pipeline_runs_delta
WHERE status = 'FAILED'
  AND end_time >= current_timestamp() - INTERVAL 1 HOUR;
-- Visual: Table + Conditional Formatting (Red for FAILED)
-- Alert Trigger: count(*) > 0

-- 🔔 ALERT 2: High Error Rate (>5% failures daily)
SELECT event_date, pipeline_name, success_rate
FROM pipeline_metrics_daily
WHERE success_rate < 95;
-- Visual: Line chart (success_rate over time)
-- Alert Trigger: success_rate < 95 for 2 consecutive days

-- 🔔 ALERT 3: Slow Pipeline (SLA breach)
SELECT pipeline_name, avg_duration
FROM pipeline_metrics_daily
WHERE avg_duration > 3600;
-- Visual: Bar chart (avg_duration per pipeline)
-- Alert Trigger: avg_duration > 3600 (1 hour)

-- 🔔 ALERT 4: Error Spike Detection (Day-over-day increase)
SELECT a.event_date,
       a.pipeline_name,
       a.error_count,
       b.error_count AS prev_day_errors,
       (a.error_count - b.error_count) AS delta_errors
FROM (
  SELECT CAST(event_time AS DATE) AS event_date, pipeline_name, COUNT(*) AS error_count
  FROM delta_logs WHERE level = 'ERROR'
  GROUP BY CAST(event_time AS DATE), pipeline_name
) a
LEFT JOIN (
  SELECT CAST(event_time AS DATE) AS event_date, pipeline_name, COUNT(*) AS error_count
  FROM delta_logs WHERE level = 'ERROR'
  GROUP BY CAST(event_time AS DATE), pipeline_name
) b
ON a.pipeline_name = b.pipeline_name AND a.event_date = b.event_date + INTERVAL 1 DAY
WHERE (a.error_count - b.error_count) > 10;
-- Visual: Heatmap of delta_errors by pipeline/date
-- Alert Trigger: delta_errors > threshold

-- 🔔 ALERT 5: Long-running Jobs (>1h)
SELECT run_id, pipeline_name, start_time, current_timestamp() AS now,
       ROUND((unix_timestamp(current_timestamp()) - unix_timestamp(start_time)) / 60, 2) AS runtime_minutes
FROM pipeline_runs_delta
WHERE status = 'RUNNING' AND start_time < current_timestamp() - INTERVAL 1 HOUR;
-- Visual: Table with runtime_minutes highlight
-- Alert Trigger: runtime_minutes > 60

-- =============================================
-- 📈 DASHBOARD VISUALIZATION SUGGESTIONS
-- =============================================
-- 1️⃣ Overview Dashboard: "Pipeline Health Monitor"
--   🔹 KPI Tiles:
--       - Total Runs Today
--       - Success Rate (%)
--       - Total Failures (Red)
--       - Avg Duration (min)
--   🔹 Line Chart: Success Rate by Date (last 30 days)
--   🔹 Heatmap: Errors per Pipeline per Day
--   🔹 Bar Chart: Avg Duration per Pipeline (Top 10)
--   🔹 Table: Latest 20 Failures with error messages

-- 2️⃣ Alerting Dashboard: "Error & SLA Breach Monitor"
--   🔹 Time-series Line Chart: Daily Error Counts
--   🔹 Bar Chart: Pipelines breaching SLA
--   🔹 Table: Long-running or stuck runs
--   🔹 Conditional Alert Tile: Red if success_rate < 95%

-- 3️⃣ Operational Dashboard: "Run Performance Insights"
--   🔹 Scatter Plot: Duration vs Records Processed
--   🔹 Histogram: Runtime Distribution by Pipeline
--   🔹 Table: Top Error Messages (last 7 days)
--   🔹 KPI Tile: # of distinct pipelines run in last 24h

-- =============================================
-- 🚨 DATBRICKS ALERTING AUTOMATION
-- =============================================
-- 1️⃣ In Databricks SQL UI:
--     - Create each query as a saved query.
--     - Add an alert rule (e.g., count > 0, avg_duration > SLA).
--     - Configure email / webhook / Slack notification channel.
-- 2️⃣ Recommended refresh schedule:
--     - Critical alerts: every 15 minutes
--     - Daily reports: every 1 hour or daily at midnight
--     - Metrics aggregation jobs: daily at 2 AM
-- =============================================

```


---

## Integration to External Monitoring Tools



Perfect ✅ — next I’ll extend the notebook and SQL-based logging system with external observability integration so Databricks pipelines’ logs and metrics can be correlated in Prometheus, Grafana, or Elastic Observability (Kibana).
Here’s what I’ll add next in the document:


### 🔗 External Monitoring & Observability Integration Pack

#### 1. Prometheus + Grafana

- Metric Exporter Notebook (Scala or Python)
  - Periodically reads pipeline_metrics_daily and delta_logs_enriched and exposes key metrics (success_rate, avg_duration, error_count) on an HTTP endpoint using prometheus_client.

- PromQL Examples
```promsql
  pipeline_success_rate{pipeline="index_load"} < 0.95
  avg(pipeline_duration_seconds{pipeline=~".*"}) by (pipeline)
```
- Grafana Dashboards
    - Panel 1: Success Rate (per pipeline, over 24h)
    - Panel 2: Error Rate (stacked by stage)
    - Panel 3: SLA Breaches (threshold heatmap)
    - Panel 4: Latency Trend (Spark stage duration)


#### 2. Elastic Observability (Kibana)

- Ingest Integration
    - Use the existing es_writer job to push delta_logs_enriched and pipeline_metrics_daily into ES indices:
```nginx
   es_index_pipeline_logs
    es_index_pipeline_metrics
```
    - Each doc includes:
        - pipeline_name, stage, status, duration_ms, timestamp, error_message, spark_job_id

- Kibana Dashboards
    - Error Heatmap: Errors by pipeline & stage
    - Trend Line: Daily success/failure counts
    - Latency Breakdown: Duration per job and executor
    - SLA View: Compare actual vs. expected completion time


#### 3. Alert Routing

- Grafana Alerts
    - Trigger on PromQL thresholds (e.g., error_rate > 5%)
    - Send to Slack, Teams, or Email via Grafana Alert Center

- Elastic Watcher
    - JSON Watch to detect if status:FAILED count > threshold per pipeline within last N minutes
    - Example Slack message:
  ```vbnet
  🚨 Databricks Pipeline Alert:
    Pipeline: index_load
    Failures: 3 in last 15m
    Last Error: Timeout in stage "delta_merge"
```


#### 4. Unified Observability Architecture

- Databricks Delta Tables → ElasticSearch (structured logs)
- Databricks Metrics Exporter → Prometheus (quantitative metrics)
- Grafana → unified visualization
- Kibana → detailed log drilldown

Would you like me to also include setup code snippets (e.g., Prometheus exporter script and Databricks → ES connector config) in the next update?


---












