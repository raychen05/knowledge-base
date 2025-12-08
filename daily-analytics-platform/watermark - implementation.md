
## Watermark Implementation



Nice — below is a ready-to-run, self-contained Scala object that implements:

- a coordinator that discovers latest versions for upstream Delta tables and creates an atomic batch (watermark rows) for a list of upstreams,
- a pipeline helper that reads watermark rows for a batch and processes each upstream deterministically (using version ranges or timestamp fallback), and writes pipeline checkpoints, and
- a finalizer that advances per-upstream committed watermark only after all pipelines that depend on those upstreams have succeeded for the batch.

The code uses Spark SQL + Delta (DeltaTable) APIs and assumes you have Delta Lake on classpath and a SparkSession available. It also creates the required Delta tables if they do not exist.

Drop this into your job repo (adjust package/imports as needed) and run.

```scala
import org.apache.spark.sql.{DataFrame, Row, SaveMode, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import io.delta.tables.DeltaTable
import java.util.UUID
import java.sql.Timestamp

object IncrementalCoordinator {

  // === Configuration / constants ===
  val WATERMARK_TABLE = "gold.watermarks"              // per-batch per-upstream rows
  val COMMITTED_WATERMARK_TABLE = "gold.committed_watermarks" // last committed per upstream
  val PIPELINE_CHECKPOINT_TABLE = "gold.pipeline_checkpoints"

  // === Case classes for convenience ===
  case class WatermarkRow(
    batch_id: String,
    table_name: String,
    start_version: Long,
    end_version: Long,
    last_processed_version: Long,
    latest_available_version: Long,
    start_ts: Timestamp,
    end_ts: Timestamp,
    cdf_enabled: Boolean,
    update_ts: Timestamp,
    updated_by: String,
    status: String,
    error_message: String
  )

  case class PipelineCheckpoint(
    pipeline_name: String,
    batch_id: String,
    processed_ts: Timestamp,
    status: String,
    rows_read: Long,
    rows_written: Long,
    metrics: Map[String,String],
    error_message: String
  )

  // === Utilities ===
  def nowTs(): Timestamp = new Timestamp(System.currentTimeMillis())

  def ensureTablesExist(): Unit = {

    // Watermark table
    spark.sql(
      s"""
         |CREATE TABLE IF NOT EXISTS $WATERMARK_TABLE (
         |  batch_id STRING,
         |  table_name STRING,
         |  start_version LONG,
         |  end_version LONG,
         |  last_processed_version LONG,
         |  latest_available_version LONG,
         |  start_ts TIMESTAMP,
         |  end_ts TIMESTAMP,
         |  cdf_enabled BOOLEAN,
         |  update_ts TIMESTAMP,
         |  updated_by STRING,
         |  status STRING,
         |  error_message STRING
         |) USING DELTA
       """.stripMargin)

    // Committed watermark: single row per upstream storing last committed version
    spark.sql(
      s"""
         |CREATE TABLE IF NOT EXISTS $COMMITTED_WATERMARK_TABLE (
         |  table_name STRING,
         |  last_committed_version LONG,
         |  commit_ts TIMESTAMP,
         |  updated_by STRING
         |) USING DELTA
       """.stripMargin)

    // Pipeline checkpoint table
    spark.sql(
      s"""
         |CREATE TABLE IF NOT EXISTS $PIPELINE_CHECKPOINT_TABLE (
         |  pipeline_name STRING,
         |  batch_id STRING,
         |  processed_ts TIMESTAMP,
         |  status STRING,
         |  rows_read LONG,
         |  rows_written LONG,
         |  metrics MAP<STRING,STRING>,
         |  error_message STRING
         |) USING DELTA
       """.stripMargin)
  }

  // Discover latest version and whether CDF is enabled for a Delta table.
  // Accepts either a table name (db.table) or a path.
  def discoverLatestVersionAndCdf(tableIdentifier: String): (Long, Boolean) = {
    try {
      val hist = spark.sql(s"DESCRIBE HISTORY $tableIdentifier")
      val maxVer = hist.agg(max(col("version")).cast("long")).as[Long].collect().headOption.getOrElse(-1L)
      val detail = spark.sql(s"DESCRIBE DETAIL $tableIdentifier")
      val cdf = if (detail.columns.contains("properties")) {
        val propsOpt = detail.select("properties").collect().headOption.map { r =>
          // r.getMap returns java map; convert safely
          val m = r.getMap
          import scala.jdk.CollectionConverters._
          m.asScala.toMap
        }
        propsOpt.exists(_.get("delta.enableChangeDataFeed").exists(_.toLowerCase == "true"))
      } else false
      (maxVer, cdf)
    } catch {
      case e: Throwable =>
        // If anything fails (non-delta upstream), return -1 and cdf false; caller should fallback to timestamp reading.
        (-1L, false)
    }
  }

  // Read last committed version for an upstream from committed watermark table (if exists)
  def readLastCommittedVersion(tableName: String): Long = {
    import spark.implicits._
    val df = spark.table(COMMITTED_WATERMARK_TABLE).filter(col("table_name") === tableName)
    df.select("last_committed_version").as[Long].collect().headOption.getOrElse(-1L)
  }

  // Coordinator: create a batch for a set of upstream tables.
  // upstreams: Seq of upstream table identifier strings (db.table or path)
  // owner: string used for updated_by
  // maxWindowVersions: optional limit on how big end_version can be relative to start_version
  def createBatch(
    upstreams: Seq[String],
    owner: String,
    maxWindowVersions: Option[Long] = None
  ): String = {
    import spark.implicits._

    ensureTablesExist(spark)

    val batchId = s"batch_${java.time.Instant.now.toString}_${UUID.randomUUID().toString.take(8)}"
    val ts = nowTs()

    // For each upstream compute last committed, latest version, cdf flag, start/end versions
    val wmRows = upstreams.map { u =>
      val lastCommitted = readLastCommittedVersion( u)           // -1 if unknown
      val (latestVersion, cdfEnabled) = discoverLatestVersionAndCdf( u)
      val startVersion = lastCommitted + 1
      // If no version capability (latestVersion == -1) we'll fallback to timestamps and mark start_version/end_version = -1
      val rawEnd = if (latestVersion >= startVersion) latestVersion else lastCommitted
      val endVersion = maxWindowVersions match {
        case Some(maxWin) if rawEnd - startVersion > maxWin => startVersion + maxWin
        case _ => rawEnd
      }
      val status = if (endVersion >= startVersion && startVersion >= 0) "PENDING" else "NOOP"
      WatermarkRow(
        batch_id = batchId,
        table_name = u,
        start_version = if (cdfEnabled && startVersion >= 0) startVersion else -1L,
        end_version = if (cdfEnabled && endVersion >= 0) endVersion else -1L,
        last_processed_version = lastCommitted,
        latest_available_version = latestVersion,
        start_ts = ts,
        end_ts = ts,
        cdf_enabled = cdfEnabled,
        update_ts = ts,
        updated_by = owner,
        status = status,
        error_message = ""
      )
    }

    val wmDF = wmRows.toDF()

    // Atomically write watermark rows in one transaction (append)
    wmDF.write.format("delta").mode(SaveMode.Append).saveAsTable(WATERMARK_TABLE)

    batchId
  }

  // Pipeline runner helper:
  // - reads watermark rows for a pipeline's batch (pipelineDeps is list of upstreams this pipeline depends on)
  // - iterates and reads each upstream deterministically (versionAsOf or changes or timestamp fallback)
  // - userProcessing: function that consumes Map[tableName -> DataFrame] and returns (rowsRead, rowsWritten, metrics)
  // This design reads each upstream into an inputDF and passes all to the pipeline processing function.
  def runPipelineForBatch(
    pipelineName: String,
    batchId: String,
    pipelineDeps: Seq[String],
    owner: String,
    userProcessing: Map[String, DataFrame] => (Long, Long, Map[String,String]) // returns (rowsRead, rowsWritten, metrics)
  ): Unit = {
    import spark.implicits._

    ensureTablesExist(spark)

    // Mark RUNNING in checkpoint
    val runningRow = PipelineCheckpoint(pipelineName, batchId, nowTs(), "RUNNING", 0L, 0L, Map.empty[String,String], "")
    Seq(runningRow).toDF().write.format("delta").mode(SaveMode.Append).saveAsTable(PIPELINE_CHECKPOINT_TABLE)

    try {
      // Load watermark rows for this batch filtered to the pipeline's dependencies
      val wmDF = spark.table(WATERMARK_TABLE)
        .filter(col("batch_id") === batchId && col("table_name").isin(pipelineDeps: _*))
        .select(
          col("table_name"),
          col("start_version"),
          col("end_version"),
          col("cdf_enabled"),
          col("latest_available_version"),
          col("start_ts"),
          col("end_ts"),
          col("status")
        )

      val wmRows = wmDF.collect()

      // Build map of table -> DataFrame
      val inputMap: Map[String, DataFrame] = wmRows.map { r =>
        val tname = r.getAs[String]("table_name")
        val startV = r.getAs[Long]("start_version")
        val endV = r.getAs[Long]("end_version")
        val cdf = r.getAs[Boolean]("cdf_enabled")
        val status = r.getAs[String]("status")

        val df: DataFrame = if (status == "NOOP") {
          // empty DF with no columns
          spark.emptyDataFrame
        } else if (cdf && startV >= 0 && endV >= startV) {
          // Use Delta CDF read if possible: spark.read.format("delta").option("readChangeData","true") ...
          // Use table(...) API with options; depending on Delta version, change reading API may vary.
          // We'll attempt version-based snapshot if CDF read isn't available in runtime environment.
          try {
            spark.read.format("delta")
              .option("readChangeData", "true")
              .option("startingVersion", startV.toString)
              .option("endingVersion", endV.toString)
              .table(tname)
          } catch {
            case _: Throwable =>
              // fallback to reading snapshot at end_version (deterministic)
              spark.read.format("delta").option("versionAsOf", endV).table(tname)
          }
        } else if (endV >= 0) {
          // Snapshot read deterministically at end_version
          spark.read.format("delta").option("versionAsOf", endV).table(tname)
        } else {
          // Upstream doesn't support versioning; use time window (start_ts/end_ts) to filter if the table has an ingestion timestamp column.
          // We can't guess the timestamp column name generically. For this helper, try reading the whole table and the pipeline should filter.
          spark.table(tname)
        }

        (tname -> df)
      }.toMap

      // Call user-provided processing function and collect metrics
      val (rowsRead, rowsWritten, metrics) = userProcessing(inputMap)

      // Mark SUCCESS in checkpoint (update last row)
      val successRow = PipelineCheckpoint(pipelineName, batchId, nowTs(), "SUCCESS", rowsRead, rowsWritten, metrics, "")
      // append success row (we use append semantics for checkpoint history)
      Seq(successRow).toDF().write.format("delta").mode(SaveMode.Append).saveAsTable(PIPELINE_CHECKPOINT_TABLE)

    } catch {
      case e: Throwable =>
        val err = Option(e.getMessage).getOrElse("unknown").take(4000)
        val failedRow = PipelineCheckpoint(pipelineName, batchId, nowTs(), "FAILED", 0L, 0L, Map.empty, err)
        Seq(failedRow).toDF().write.format("delta").mode(SaveMode.Append).saveAsTable(PIPELINE_CHECKPOINT_TABLE)
        throw e
    }
  }

  // Finalizer: for a batch, advance committed watermark for upstreams only if ALL pipelines that depend on those upstreams have SUCCESS for that batch.
  // pipelineRegistry: map pipelineName -> Seq[upstreams it depends on]
  // If pipelineRegistry is not provided, the finalizer will discover pipelines that ran for the batch by scanning checkpoints (best if registry is known).
  def finalizeBatch(
    batchId: String,
    pipelineRegistry: Map[String, Seq[String]],
    owner: String
  ): Seq[String] = {
    import spark.implicits._

    ensureTablesExist(spark)

    // discover which pipelines are expected to run for this batch by inverting registry to get upstream->expected pipelines
    val upstreamToPipelines: Map[String, Seq[String]] = pipelineRegistry.toSeq
      .flatMap { case (p, ups) => ups.map(u => (u, p)) }
      .groupBy(_._1)
      .mapValues(_.map(_._2).distinct)
      .map(identity)

    // For each upstream in this batch, check if all pipelines in upstreamToPipelines(upstream) have SUCCESS for this batch
    val wmRows = spark.table(WATERMARK_TABLE).filter(col("batch_id") === batchId).collect()

    val advanced: scala.collection.mutable.ListBuffer[String] = scala.collection.mutable.ListBuffer.empty

    wmRows.foreach { r =>
      val upstream = r.getAs[String]("table_name")
      val endVersion = r.getAs[Long]("end_version")
      val status = r.getAs[String]("status")

      // If NOOP or endVersion < startVersion etc, nothing to advance
      if (status == "NOOP" || endVersion < 0) {
        // nothing to advance
      } else {
        val expectingPipelines = upstreamToPipelines.getOrElse(upstream, Seq.empty)
        val checkpoints = spark.table(PIPELINE_CHECKPOINT_TABLE)
          .filter(col("batch_id") === batchId && col("pipeline_name").isin(expectingPipelines: _*))

        // Are all expectingPipelines present and SUCCESS?
        val successPipelines: Array[String] = checkpoints.filter(col("status") === "SUCCESS").select("pipeline_name").as[String].distinct().collect()

        val allSucceeded = expectingPipelines.forall(p => successPipelines.contains(p))

        if (expectingPipelines.isEmpty) {
          // No registry info: fallback to require that at least one pipeline succeeded for the batch on this upstream
          val anySuccess = checkpoints.filter(col("status") === "SUCCESS").count() > 0
          if (anySuccess) {
            // advance
            upsertCommittedWatermark( upstream, endVersion, owner)
            advanced += upstream
          }
        } else if (allSucceeded) {
          upsertCommittedWatermark( upstream, endVersion, owner)
          advanced += upstream
        } else {
          // not all succeeded yet; skip advancement
        }
      }
    }

    advanced.toSeq
  }

  // Upsert helper for committed watermark table: set last_committed_version = newVersion if newVersion > existing
  def upsertCommittedWatermark(tableName: String, newVersion: Long, owner: String): Unit = {
    import spark.implicits._
    ensureTablesExist(spark)
    val committedPath = COMMITTED_WATERMARK_TABLE

    val exists = try {
      spark.table(committedPath)
      true
    } catch {
      case _: Throwable => false
    }

    // We'll MERGE using SQL for portability
    val tmpDf = Seq((tableName, newVersion, nowTs(), owner)).toDF("table_name","last_committed_version","commit_ts","updated_by")
    tmpDf.createOrReplaceTempView("tmp_committed_new")

    // Merge: if not exists insert; if exists and newVersion > existing update; else do nothing
    // Note: The SQL below assumes Delta supports WHEN MATCHED AND ... THEN UPDATE
    spark.sql(
      s"""
         |MERGE INTO $committedPath tgt
         |USING tmp_committed_new src
         |  ON tgt.table_name = src.table_name
         |WHEN MATCHED AND src.last_committed_version > tgt.last_committed_version
         |  THEN UPDATE SET tgt.last_committed_version = src.last_committed_version, tgt.commit_ts = src.commit_ts, tgt.updated_by = src.updated_by
         |WHEN NOT MATCHED
         |  THEN INSERT (table_name, last_committed_version, commit_ts, updated_by)
         |  VALUES (src.table_name, src.last_committed_version, src.commit_ts, src.updated_by)
       """.stripMargin)
  }

  // === Example main to demonstrate flow ===
  // NOTE: Replace exampleProcessing with your real logic.
  def mainExample(spark: SparkSession): Unit = {
    // pipeline registry example: mapping from pipeline to upstreams it reads
    val pipelineRegistry: Map[String, Seq[String]] = Map(
      "pipeline_a" -> Seq("upstream_db.table1", "upstream_db.table2"),
      "pipeline_b" -> Seq("upstream_db.table2", "upstream_db.table3")
    )

    // 1) Coordinator: create a batch across all upstreams used by the pipelines
    val allUpstreams = pipelineRegistry.values.flatten.toSeq.distinct
    val owner = "orchestrator_user"
    val batchId = createBatch( allUpstreams, owner, maxWindowVersions = Some(10000L))
    println(s"Created batchId: $batchId")

    // 2) Run pipelines (in real life you might run these in parallel or submit jobs)
    // Provide a simple userProcessing that just counts input rows and returns metrics.
    def exampleProcessing(inputs: Map[String, DataFrame]): (Long, Long, Map[String, String]) = {
      var totalRead = 0L
      var totalWritten = 0L
      inputs.foreach { case (t, df) =>
        val cnt = try { df.count() } catch { case _: Throwable => 0L }
        totalRead += cnt
      }
      // For demo: no writes, metrics contain rows read per table
      val metrics = inputs.map { case (t, df) =>
        val cnt = try { df.count() } catch { case _: Throwable => 0L }
        (t -> cnt.toString)
      }.toMap
      (totalRead, totalWritten, metrics)
    }

    // Run pipeline_a
    runPipelineForBatch( "pipeline_a", batchId, pipelineRegistry("pipeline_a"), owner, exampleProcessing)

    // Run pipeline_b
    runPipelineForBatch( "pipeline_b", batchId, pipelineRegistry("pipeline_b"), owner, exampleProcessing)

    // 3) Finalizer: after pipelines have run, finalize batch; returns list of upstreams advanced.
    val advanced = finalizeBatch( batchId, pipelineRegistry, owner)
    println(s"Advanced upstreams for batch $batchId: ${advanced.mkString(",")}")
  }
}

```

---

#### How to use / integrate

1. Put the object into your Scala project that has Spark + Delta dependencies.
2. Call IncrementalCoordinator.ensureTablesExist(spark) once at startup (or rely on the code that calls it).
3. Use createBatch from your orchestrator to create a deterministic per-upstream batch. Save/return the batchId.
4. Submit pipeline jobs that call runPipelineForBatch(...) with a userProcessing function that performs the transforms/writes for that pipeline. Use the pipelineName and pipelineDeps consistent with pipelineRegistry.
5. After pipelines finish, call finalizeBatch with the pipelineRegistry to safely advance last_committed_version for upstreams which all pipelines have successfully processed.


#### Notes & recommended tweaks

- This example uses saveAsTable and Spark SQL MERGE — ensure your runtime supports Delta MERGE. If you prefer the DeltaTable API, you can replace the SQL MERGE with DeltaTable.forName(...).as("tgt").merge(...).
- The code assumes upstreams are Delta tables or accessible via Spark catalog. For upstreams that are not Delta, discoverLatestVersionAndCdf will return -1 and the watermark written will use -1 for versions; pipelines must then rely on timestamps or ingestion flags for filtering. You can extend createBatch to compute start_ts/end_ts for those upstreams.
- For large-scale production: run coordinator, pipelines and finalizer as independent jobs, add retries, backoff, metrics collection, and robust error handling.
- If pipelines run in parallel, make sure your finalizer waits or is triggered after pipelines are done (e.g., via orchestration or events).
- Consider storing the schema fingerprint in watermark rows to detect incompatible schema changes.

If you’d like, I can:
- convert the code to use the DeltaTable Java/Scala API for MERGE (instead of SQL MERGE),
- add a timed-backoff retry wrapper for pipeline execution, or
- produce an SQL-based finalizer job instead of Scala.
Which of those would help most next?


---

##  DeltaTable Java/Scala API for MERGE (instead of SQL MERGE),


Great — below is the same full IncrementalCoordinator Scala object you already have, but with the upsertCommittedWatermark function re-implemented using the DeltaTable Scala API (io.delta.tables.DeltaTable) instead of running a SQL MERGE. I also kept the rest of the object unchanged except for small helper adjustments so the DeltaTable flow is robust when the committed watermark table does not yet exist.
Key behavior:

- If gold.committed_watermarks does not exist, we create it by writing the new row as a Delta table.
- If it exists we perform a merge using the DeltaTable API, updating only when the incoming last_committed_version is greater than the existing one; otherwise we do nothing.
- This uses whenMatched(condition, updateMap) and whenNotMatched(insertMap) operations provided by the Delta API.

Paste this object into your project (with Delta Lake on the classpath) — it replaces the previous object but keeps all functionality.

```scala
import org.apache.spark.sql.{DataFrame, Row, SaveMode, SparkSession, Column}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import io.delta.tables.DeltaTable
import java.util.UUID
import java.sql.Timestamp

object IncrementalCoordinator {

  // === Configuration / constants ===
  val WATERMARK_TABLE = "gold.watermarks"              // per-batch per-upstream rows
  val COMMITTED_WATERMARK_TABLE = "gold.committed_watermarks" // last committed per upstream
  val PIPELINE_CHECKPOINT_TABLE = "gold.pipeline_checkpoints"

  // === Case classes for convenience ===
  case class WatermarkRow(
    batch_id: String,
    table_name: String,
    start_version: Long,
    end_version: Long,
    last_processed_version: Long,
    latest_available_version: Long,
    start_ts: Timestamp,
    end_ts: Timestamp,
    cdf_enabled: Boolean,
    update_ts: Timestamp,
    updated_by: String,
    status: String,
    error_message: String
  )

  case class PipelineCheckpoint(
    pipeline_name: String,
    batch_id: String,
    processed_ts: Timestamp,
    status: String,
    rows_read: Long,
    rows_written: Long,
    metrics: Map[String,String],
    error_message: String
  )

  // === Utilities ===
  def nowTs(): Timestamp = new Timestamp(System.currentTimeMillis())

  def ensureTablesExist(spark: SparkSession): Unit = {
    import spark.implicits._

    // Watermark table
    spark.sql(
      s"""
         |CREATE TABLE IF NOT EXISTS $WATERMARK_TABLE (
         |  batch_id STRING,
         |  table_name STRING,
         |  start_version LONG,
         |  end_version LONG,
         |  last_processed_version LONG,
         |  latest_available_version LONG,
         |  start_ts TIMESTAMP,
         |  end_ts TIMESTAMP,
         |  cdf_enabled BOOLEAN,
         |  update_ts TIMESTAMP,
         |  updated_by STRING,
         |  status STRING,
         |  error_message STRING
         |) USING DELTA
       """.stripMargin)

    // Committed watermark: single row per upstream storing last committed version
    spark.sql(
      s"""
         |CREATE TABLE IF NOT EXISTS $COMMITTED_WATERMARK_TABLE (
         |  table_name STRING,
         |  last_committed_version LONG,
         |  commit_ts TIMESTAMP,
         |  updated_by STRING
         |) USING DELTA
       """.stripMargin)

    // Pipeline checkpoint table
    spark.sql(
      s"""
         |CREATE TABLE IF NOT EXISTS $PIPELINE_CHECKPOINT_TABLE (
         |  pipeline_name STRING,
         |  batch_id STRING,
         |  processed_ts TIMESTAMP,
         |  status STRING,
         |  rows_read LONG,
         |  rows_written LONG,
         |  metrics MAP<STRING,STRING>,
         |  error_message STRING
         |) USING DELTA
       """.stripMargin)
  }

  // Discover latest version and whether CDF is enabled for a Delta table.
  // Accepts either a table name (db.table) or a path.
  def discoverLatestVersionAndCdf(tableIdentifier: String): (Long, Boolean) = {
    try {
      val hist = spark.sql(s"DESCRIBE HISTORY $tableIdentifier")
      val maxVer = hist.agg(max(col("version")).cast("long")).as[Long].collect().headOption.getOrElse(-1L)
      val detail = spark.sql(s"DESCRIBE DETAIL $tableIdentifier")
      val cdf = if (detail.columns.contains("properties")) {
        val propsOpt = detail.select("properties").collect().headOption.map { r =>
          // r.getMap returns java map; convert safely
          val m = r.getMap
          import scala.jdk.CollectionConverters._
          m.asScala.toMap
        }
        propsOpt.exists(_.get("delta.enableChangeDataFeed").exists(_.toLowerCase == "true"))
      } else false
      (maxVer, cdf)
    } catch {
      case e: Throwable =>
        // If anything fails (non-delta upstream), return -1 and cdf false; caller should fallback to timestamp reading.
        (-1L, false)
    }
  }

  // Read last committed version for an upstream from committed watermark table (if exists)
  def readLastCommittedVersion(tableName: String): Long = {
    import spark.implicits._
    val df = try {
      spark.table(COMMITTED_WATERMARK_TABLE).filter(col("table_name") === tableName)
    } catch {
      case _: Throwable => spark.emptyDataFrame
    }
    df.select("last_committed_version").as[Long].collect().headOption.getOrElse(-1L)
  }

  // Coordinator: create a batch for a set of upstream tables.
  def createBatch(
    spark: SparkSession,
    upstreams: Seq[String],
    owner: String,
    maxWindowVersions: Option[Long] = None
  ): String = {
    import spark.implicits._

    ensureTablesExist(spark)

    val batchId = s"batch_${java.time.Instant.now.toString}_${UUID.randomUUID().toString.take(8)}"
    val ts = nowTs()

    val wmRows = upstreams.map { u =>
      val lastCommitted = readLastCommittedVersion( u)
      val (latestVersion, cdfEnabled) = discoverLatestVersionAndCdf( u)
      val startVersion = lastCommitted + 1
      val rawEnd = if (latestVersion >= startVersion) latestVersion else lastCommitted
      val endVersion = maxWindowVersions match {
        case Some(maxWin) if rawEnd - startVersion > maxWin => startVersion + maxWin
        case _ => rawEnd
      }
      val status = if (endVersion >= startVersion && startVersion >= 0) "PENDING" else "NOOP"
      WatermarkRow(
        batch_id = batchId,
        table_name = u,
        start_version = if (cdfEnabled && startVersion >= 0) startVersion else -1L,
        end_version = if (cdfEnabled && endVersion >= 0) endVersion else -1L,
        last_processed_version = lastCommitted,
        latest_available_version = latestVersion,
        start_ts = ts,
        end_ts = ts,
        cdf_enabled = cdfEnabled,
        update_ts = ts,
        updated_by = owner,
        status = status,
        error_message = ""
      )
    }

    val wmDF = wmRows.toDF()

    // Atomically write watermark rows in one transaction (append)
    wmDF.write.format("delta").mode(SaveMode.Append).saveAsTable(WATERMARK_TABLE)

    batchId
  }

  // Pipeline runner helper (unchanged)
  def runPipelineForBatch(
    spark: SparkSession,
    pipelineName: String,
    batchId: String,
    pipelineDeps: Seq[String],
    owner: String,
    userProcessing: Map[String, DataFrame] => (Long, Long, Map[String,String])
  ): Unit = {
    import spark.implicits._

    ensureTablesExist(spark)

    val runningRow = PipelineCheckpoint(pipelineName, batchId, nowTs(), "RUNNING", 0L, 0L, Map.empty[String,String], "")
    Seq(runningRow).toDF().write.format("delta").mode(SaveMode.Append).saveAsTable(PIPELINE_CHECKPOINT_TABLE)

    try {
      val wmDF = spark.table(WATERMARK_TABLE)
        .filter(col("batch_id") === batchId && col("table_name").isin(pipelineDeps: _*))
        .select(
          col("table_name"),
          col("start_version"),
          col("end_version"),
          col("cdf_enabled"),
          col("latest_available_version"),
          col("start_ts"),
          col("end_ts"),
          col("status")
        )

      val wmRows = wmDF.collect()

      val inputMap: Map[String, DataFrame] = wmRows.map { r =>
        val tname = r.getAs[String]("table_name")
        val startV = r.getAs[Long]("start_version")
        val endV = r.getAs[Long]("end_version")
        val cdf = r.getAs[Boolean]("cdf_enabled")
        val status = r.getAs[String]("status")

        val df: DataFrame = if (status == "NOOP") {
          spark.emptyDataFrame
        } else if (cdf && startV >= 0 && endV >= startV) {
          try {
            spark.read.format("delta")
              .option("readChangeData", "true")
              .option("startingVersion", startV.toString)
              .option("endingVersion", endV.toString)
              .table(tname)
          } catch {
            case _: Throwable =>
              spark.read.format("delta").option("versionAsOf", endV).table(tname)
          }
        } else if (endV >= 0) {
          spark.read.format("delta").option("versionAsOf", endV).table(tname)
        } else {
          spark.table(tname)
        }

        (tname -> df)
      }.toMap

      val (rowsRead, rowsWritten, metrics) = userProcessing(inputMap)

      val successRow = PipelineCheckpoint(pipelineName, batchId, nowTs(), "SUCCESS", rowsRead, rowsWritten, metrics, "")
      Seq(successRow).toDF().write.format("delta").mode(SaveMode.Append).saveAsTable(PIPELINE_CHECKPOINT_TABLE)

    } catch {
      case e: Throwable =>
        val err = Option(e.getMessage).getOrElse("unknown").take(4000)
        val failedRow = PipelineCheckpoint(pipelineName, batchId, nowTs(), "FAILED", 0L, 0L, Map.empty, err)
        Seq(failedRow).toDF().write.format("delta").mode(SaveMode.Append).saveAsTable(PIPELINE_CHECKPOINT_TABLE)
        throw e
    }
  }

  // Finalizer (unchanged)
  def finalizeBatch(
    spark: SparkSession,
    batchId: String,
    pipelineRegistry: Map[String, Seq[String]],
    owner: String
  ): Seq[String] = {
    import spark.implicits._

    ensureTablesExist(spark)

    val upstreamToPipelines: Map[String, Seq[String]] = pipelineRegistry.toSeq
      .flatMap { case (p, ups) => ups.map(u => (u, p)) }
      .groupBy(_._1)
      .mapValues(_.map(_._2).distinct)
      .map(identity)

    val wmRows = spark.table(WATERMARK_TABLE).filter(col("batch_id") === batchId).collect()

    val advanced: scala.collection.mutable.ListBuffer[String] = scala.collection.mutable.ListBuffer.empty

    wmRows.foreach { r =>
      val upstream = r.getAs[String]("table_name")
      val endVersion = r.getAs[Long]("end_version")
      val status = r.getAs[String]("status")

      if (status == "NOOP" || endVersion < 0) {
        // nothing to advance
      } else {
        val expectingPipelines = upstreamToPipelines.getOrElse(upstream, Seq.empty)
        val checkpoints = spark.table(PIPELINE_CHECKPOINT_TABLE)
          .filter(col("batch_id") === batchId && col("pipeline_name").isin(expectingPipelines: _*))

        val successPipelines: Array[String] = checkpoints.filter(col("status") === "SUCCESS").select("pipeline_name").as[String].distinct().collect()

        val allSucceeded = expectingPipelines.forall(p => successPipelines.contains(p))

        if (expectingPipelines.isEmpty) {
          val anySuccess = checkpoints.filter(col("status") === "SUCCESS").count() > 0
          if (anySuccess) {
            upsertCommittedWatermark( upstream, endVersion, owner)
            advanced += upstream
          }
        } else if (allSucceeded) {
          upsertCommittedWatermark( upstream, endVersion, owner)
          advanced += upstream
        } else {
          // skip
        }
      }
    }

    advanced.toSeq
  }

  // === New: upsertCommittedWatermark using DeltaTable API (instead of SQL MERGE) ===
  def upsertCommittedWatermark(tableName: String, newVersion: Long, owner: String): Unit = {
    import spark.implicits._

    ensureTablesExist(spark)

    // Create a small DataFrame with the new candidate values
    val srcDf = Seq((tableName, newVersion, nowTs(), owner)).toDF("table_name","last_committed_version","commit_ts","updated_by")
    val tgtTableName = COMMITTED_WATERMARK_TABLE

    // If table does not exist, write the source DF as the table (create)
    val tableExists = try {
      spark.catalog.tableExists(tgtTableName)
    } catch {
      case _: Throwable => false
    }

    if (!tableExists) {
      // create the table with this row
      srcDf.write.format("delta").mode(SaveMode.Overwrite).saveAsTable(tgtTableName)
      return
    }

    // Use DeltaTable API to perform merge upsert with conditional update:
    // WHEN MATCHED AND src.last_committed_version > tgt.last_committed_version THEN UPDATE ...
    // WHEN NOT MATCHED THEN INSERT ...
    val deltaT = DeltaTable.forName( tgtTableName)

    // Build update map and insert map
    import scala.collection.JavaConverters._
    val updateMap = Map(
      "last_committed_version" -> col("src.last_committed_version"),
      "commit_ts" -> col("src.commit_ts"),
      "updated_by" -> col("src.updated_by")
    )

    val insertMap = Map(
      "table_name" -> col("src.table_name"),
      "last_committed_version" -> col("src.last_committed_version"),
      "commit_ts" -> col("src.commit_ts"),
      "updated_by" -> col("src.updated_by")
    )

    // Perform merge using the DataFrame as source
    // Note: DeltaTable.merge requires a DataFrame or Table as source; we register srcDf as a temp view.
    srcDf.createOrReplaceTempView("__tmp_committed_src")
    val srcDFforMerge = spark.table("__tmp_committed_src")

    // execute merge
    deltaT.as("tgt")
      .merge(
        srcDFforMerge.as("src"),
        expr("tgt.table_name = src.table_name")
      )
      .whenMatched(expr("src.last_committed_version > tgt.last_committed_version"), updateMap)
      .whenNotMatched(insertMap)
      .execute()
  }

  // === Example main to demonstrate flow ===
  def mainExample(spark: SparkSession): Unit = {
    val pipelineRegistry: Map[String, Seq[String]] = Map(
      "pipeline_a" -> Seq("upstream_db.table1", "upstream_db.table2"),
      "pipeline_b" -> Seq("upstream_db.table2", "upstream_db.table3")
    )

    val allUpstreams = pipelineRegistry.values.flatten.toSeq.distinct
    val owner = "orchestrator_user"
    val batchId = createBatch( allUpstreams, owner, maxWindowVersions = Some(10000L))
    println(s"Created batchId: $batchId")

    def exampleProcessing(inputs: Map[String, DataFrame]): (Long, Long, Map[String, String]) = {
      var totalRead = 0L
      var totalWritten = 0L
      inputs.foreach { case (t, df) =>
        val cnt = try { df.count() } catch { case _: Throwable => 0L }
        totalRead += cnt
      }
      val metrics = inputs.map { case (t, df) =>
        val cnt = try { df.count() } catch { case _: Throwable => 0L }
        (t -> cnt.toString)
      }.toMap
      (totalRead, totalWritten, metrics)
    }

    runPipelineForBatch( "pipeline_a", batchId, pipelineRegistry("pipeline_a"), owner, exampleProcessing)
    runPipelineForBatch( "pipeline_b", batchId, pipelineRegistry("pipeline_b"), owner, exampleProcessing)

    val advanced = finalizeBatch( batchId, pipelineRegistry, owner)
    println(s"Advanced upstreams for batch $batchId: ${advanced.mkString(",")}")
  }
}

```

If you'd like, I can:
- convert the other MERGE/SQL usages (if any) to DeltaTable API as well,
- show a small unit-test or local run example using in-memory testing, or
- modify the upsertCommittedWatermark to use DeltaTable.forPath(...) if you prefer storing tables at explicit paths rather than managed catalog tables.


---


##  A small unit-test or local run example using in-memory testing,


Local unit-test (ScalaTest) + runnable example — uses local Spark + Delta in temp directories
Below is a small, self-contained ScalaTest suite and a standalone main runner you can drop into your project to exercise the IncrementalCoordinator object (the version that uses DeltaTable API). The test:

- starts a local SparkSession with Delta enabled,
- creates three small upstream Delta tables and commits multiple versions (simulating incremental commits),
- invokes createBatch, runs two simple pipelines using runPipelineForBatch (their userProcessing counts rows), calls finalizeBatch, and
- asserts that gold.committed_watermarks has advanced to the expected versions.

Use this as a unit test or as a local integration test.

```scala
build.sbt (dependencies)
Add Delta + Spark + ScalaTest dependencies (adjust versions to match your environment):

scalaVersion := "2.12.17" // or 2.13 if your Spark supports it

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-sql" % "3.3.2" % "provided",   // mark provided if running on cluster; for local test remove provided
  "io.delta" %% "delta-core" % "2.5.0",                       // adjust delta version to match your spark
  "org.scalatest" %% "scalatest" % "3.2.17" % Test
)

resolvers += "Delta" at "https://repo1.maven.org/maven2/"
If you run tests locally (not on a cluster), remove the % "provided" for spark-sql and ensure the correct Spark & Delta JARs are on your classpath.

Test code (ScalaTest FunSuite)
Create src/test/scala/IncrementalCoordinatorSpec.scala:

import org.scalatest.funsuite.AnyFunSuite
import org.apache.spark.sql.SparkSession
import java.nio.file.Files
import java.io.File
import org.apache.spark.sql.functions._
import java.sql.Timestamp

// Make sure IncrementalCoordinator is in your project package or adjust import
// import your.package.IncrementalCoordinator

class IncrementalCoordinatorSpec extends AnyFunSuite {

  // Build a local SparkSession configured for Delta
  def withSpark(testCode: SparkSession => Any): Unit = {
    val spark = SparkSession.builder()
      .master("local[2]")
      .appName("IncrementalCoordinatorSpec")
      // enable Delta extensions (Spark 3.3+ style)
      .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
      .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
      // reduce logging noise
      .config("spark.ui.enabled", "false")
      .getOrCreate()

    try {
      testCode(spark)
    } finally {
      spark.stop()
    }
  }

  test("coordinator -> pipeline -> finalizer end-to-end with local delta tables") {
    withSpark { spark =>
      import spark.implicits._
      // create a temporary directory for managed tables (so we don't corrupt system)
      val tmp = Files.createTempDirectory("delta_test_").toFile
      tmp.deleteOnExit()
      // point Spark to a temporary warehouse to make saveAsTable write to local disk
      spark.conf.set("spark.sql.warehouse.dir", new File(tmp, "warehouse").getAbsolutePath)

      // Ensure schema/table creation uses our IncrementalCoordinator helpers
      IncrementalCoordinator.ensureTablesExist(spark)

      // Create three upstream delta tables and produce multiple commits (versions)
      def createUpstream(tableName: String, commits: Seq[Seq[(Int,String)]]): Unit = {
        // first commit: create table
        commits.zipWithIndex.foreach { case (rows, idx) =>
          val df = rows.toDF("id","payload")
          if (idx == 0) {
            df.write.format("delta").saveAsTable(tableName)
          } else {
            // append commit
            df.write.format("delta").mode("append").saveAsTable(tableName)
          }
        }
      }

      // upstream1: 3 commits (versions 0,1,2)
      createUpstream("up1", Seq(
        Seq((1,"a"), (2,"b")),      // v0
        Seq((3,"c")),               // v1
        Seq((4,"d"), (5,"e"))       // v2
      ))

      // upstream2: 2 commits (versions 0,1)
      createUpstream("up2", Seq(
        Seq((10,"x")),              // v0
        Seq((11,"y"), (12,"z"))     // v1
      ))

      // upstream3: 1 commit (version 0)
      createUpstream("up3", Seq(
        Seq((100,"p"))              // v0
      ))

      // Confirm versions exist using DESCRIBE HISTORY
      val up1Max = spark.sql("DESCRIBE HISTORY up1").agg(max(col("version")).cast("long")).as[Long].collect().head
      val up2Max = spark.sql("DESCRIBE HISTORY up2").agg(max(col("version")).cast("long")).as[Long].collect().head
      val up3Max = spark.sql("DESCRIBE HISTORY up3").agg(max(col("version")).cast("long")).as[Long].collect().head

      assert(up1Max >= 2)
      assert(up2Max >= 1)
      assert(up3Max >= 0)

      // Create a simple pipeline registry: two pipelines depend on tables
      val pipelineRegistry: Map[String, Seq[String]] = Map(
        "pipelineA" -> Seq("up1","up2"),
        "pipelineB" -> Seq("up2","up3")
      )

      // Create a batch across all upstreams
      val allUps = pipelineRegistry.values.flatten.toSeq.distinct
      val batchId = IncrementalCoordinator.createBatch( allUps, owner = "test_orch", maxWindowVersions = Some(100L))
      assert(batchId.startsWith("batch_"))

      // Implement a trivial userProcessing that returns counts
      def userProcessing(inputs: Map[String, org.apache.spark.sql.DataFrame]): (Long, Long, Map[String,String]) = {
        var rowsRead = 0L
        inputs.foreach { case (tbl, df) =>
          // For fairness, handle emptyDataFrame gracefully
          val cnt = try { df.count() } catch { case _: Throwable => 0L }
          rowsRead += cnt
        }
        val metrics = inputs.map { case (t, df) =>
          val cnt = try { df.count() } catch { case _: Throwable => 0L }
          (t -> cnt.toString)
        }.toMap
        (rowsRead, 0L, metrics)
      }

      // Run pipelines sequentially (simulating two jobs)
      IncrementalCoordinator.runPipelineForBatch( "pipelineA", batchId, pipelineRegistry("pipelineA"), owner = "test_orch", userProcessing)
      IncrementalCoordinator.runPipelineForBatch( "pipelineB", batchId, pipelineRegistry("pipelineB"), owner = "test_orch", userProcessing)

      // Finalize the batch: should advance committed_watermarks for upstreams where all dependent pipelines succeeded
      val advanced = IncrementalCoordinator.finalizeBatch( batchId, pipelineRegistry, owner = "test_orch")

      // Read committed watermark table and assert versions have advanced (last_committed_version >= respective end_version)
      val committed = spark.table("gold.committed_watermarks").select("table_name","last_committed_version").as[(String,Long)].collect().toMap

      // The createBatch logic uses discovered latest versions; ensure committed map contains the upstreams we expect
      allUps.foreach { up =>
        assert(committed.contains(up), s"committed watermark should contain $up")
        // Ensure last_committed_version is >= 0 (advanced)
        assert(committed(up) >= 0, s"committed version for $up should be non-negative")
      }

      // Also ensure 'advanced' contains at least some upstreams
      assert(advanced.nonEmpty, "expected some upstreams to be advanced")

      // Print for debug
      println(s"BatchId: $batchId; advanced upstreams: ${advanced.mkString(",")}")
      println("Committed watermark table snapshot:")
      spark.table("gold.committed_watermarks").show(false)
    }
  }
}
```

#### Standalone main runner

If you prefer to run as a simple object (not a test), add this file src/main/scala/LocalRunIncremental.scala:

```scala
import org.apache.spark.sql.SparkSession

object LocalRunIncremental {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .master("local[2]")
      .appName("LocalRunIncremental")
      .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
      .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
      .getOrCreate()

    try {
      IncrementalCoordinator.mainExample(spark)
    } finally {
      spark.stop()
    }
  }
}
```

#### Notes / troubleshooting

- Delta + Spark versions must be compatible. If you get NoSuchMethodError or similar, check Delta / Spark compatibility matrix and choose matching versions.
- The test writes managed tables into a temporary spark.sql.warehouse.dir so it doesn't touch your cluster metastore. If you want explicit paths instead of table names, modify createUpstream to write to a path via .save(path) and pass that path as the upstream identifier. The IncrementalCoordinator accepts either table name or path for DESCRIBE/DESCRIBE HISTORY calls.
- If running in CI, ensure the runner has enough memory for Spark local mode. Adjust master("local[1]") or driver/executor memory configs as needed.

If you want, I can:
- adapt the test to use explicit table paths instead of catalog-managed tables, or
- convert the test to a purely JUnit-style test, or
- add assertions that verify exact version numbers advanced (reading gold.watermarks to find the end_version per upstream and comparing to gold.committed_watermarks).


---

## ERD of the watermark/checkpoint tables and example SQL to do the finalizer/advance step.


ERD (Entity Relationship Diagram) — watermark & checkpoint tables
Below is a compact ERD showing the tables, their key fields, and relationships. Use this as the canonical data model for coordinating batches, pipelines, and committed watermarks.

```sql
erDiagram
  WATERMARKS {
    STRING batch_id PK
    STRING table_name PK
    LONG start_version
    LONG end_version
    LONG last_processed_version
    LONG latest_available_version
    TIMESTAMP start_ts
    TIMESTAMP end_ts
    BOOLEAN cdf_enabled
    TIMESTAMP update_ts
    STRING updated_by
    STRING status
    STRING error_message
  }

  PIPELINE_CHECKPOINTS {
    STRING pipeline_name PK
    STRING batch_id PK
    TIMESTAMP processed_ts
    STRING status
    LONG rows_read
    LONG rows_written
    MAP metrics
    STRING error_message
  }

  COMMITTED_WATERMARKS {
    STRING table_name PK
    LONG last_committed_version
    TIMESTAMP commit_ts
    STRING updated_by
  }

  PIPELINE_REGISTRY {
    STRING pipeline_name PK
    ARRAY<STRING> upstream_tables
  }

  WATERMARKS ||--o{ PIPELINE_REGISTRY : "upstreams used by"
  PIPELINE_REGISTRY ||--o{ PIPELINE_CHECKPOINTS : "pipelines run for batch"
  WATERMARKS ||--|| COMMITTED_WATERMARKS : "per-upstream committed version"
```

**Notes**:

- WATERMARKS contains one row per (batch_id, table_name) — the planned read window for that upstream for a given batch.
- PIPELINE_CHECKPOINTS contains one or more rows per (pipeline_name, batch_id) capturing run status and metrics. Use append-history (multiple rows) or keep latest by upserting.
- COMMITTED_WATERMARKS stores the last fully committed (advanced) version for each upstream. It is the canonical progress pointer.
- PIPELINE_REGISTRY is optional but recommended: it maps each pipeline to the list of upstreams it must consume. This allows the finalizer to determine when all dependent pipelines have succeeded.


---

### Example SQL: Finalizer / Advance step (Delta SQL)

Goal: For a given batch_id, advance (upsert) COMMITTED_WATERMARKS.last_committed_version = watermark.end_version for an upstream only if all pipelines that depend on that upstream have a SUCCESS checkpoint for that batch_id.

Two variants below:
1. SQL-only finalizer assuming a PIPELINE_REGISTRY table (recommended).
2. Fallback SQL when there is no registry — advance upstreams that have at least one pipeline with SUCCESS for the batch.
Replace :BATCH_ID with your batch id (or bind it in your orchestration).


#### 1) Prereqs — table creation (if not existing)

```sql
-- watermark rows per batch+upstream
CREATE TABLE IF NOT EXISTS gold.watermarks (
  batch_id STRING,
  table_name STRING,
  start_version BIGINT,
  end_version BIGINT,
  last_processed_version BIGINT,
  latest_available_version BIGINT,
  start_ts TIMESTAMP,
  end_ts TIMESTAMP,
  cdf_enabled BOOLEAN,
  update_ts TIMESTAMP,
  updated_by STRING,
  status STRING,
  error_message STRING
) USING DELTA;

-- pipeline checkpoints (append history)
CREATE TABLE IF NOT EXISTS gold.pipeline_checkpoints (
  pipeline_name STRING,
  batch_id STRING,
  processed_ts TIMESTAMP,
  status STRING,
  rows_read BIGINT,
  rows_written BIGINT,
  metrics MAP<STRING,STRING>,
  error_message STRING
) USING DELTA;

-- committed watermark (canonical per-upstream progress)
CREATE TABLE IF NOT EXISTS gold.committed_watermarks (
  table_name STRING,
  last_committed_version BIGINT,
  commit_ts TIMESTAMP,
  updated_by STRING
) USING DELTA;

-- optional pipeline registry mapping pipeline -> array of upstreams
CREATE TABLE IF NOT EXISTS gold.pipeline_registry (
  pipeline_name STRING,
  upstream_tables ARRAY<STRING>
) USING DELTA;
```

---

#### 1) Step: compute candidate upstreams ready to advance

This query computes, for each table_name in the batch, whether all its dependent pipelines succeeded.

```sql
-- 1. Expand pipeline_registry into (pipeline_name, table_name) rows so we can join
WITH registry_expanded AS (
  SELECT pipeline_name, explode(upstream_tables) AS table_name
  FROM gold.pipeline_registry
),

-- 2. Take the watermark rows for this batch (only those that had a real end_version)
batch_wms AS (
  SELECT batch_id, table_name, start_version, end_version, status
  FROM gold.watermarks
  WHERE batch_id = ':BATCH_ID'
    AND status = 'PENDING'  -- only care about those that were intended to be processed
),

-- 3. pipelines expected to run for each upstream
expected AS (
  SELECT be.table_name, re.pipeline_name
  FROM batch_wms be
  LEFT JOIN registry_expanded re
    ON be.table_name = re.table_name
),

-- 4. actual pipeline runs and their final status for this batch
actual AS (
  SELECT pipeline_name, batch_id, status
  FROM (
    SELECT pipeline_name, batch_id, status,
           row_number() OVER (PARTITION BY pipeline_name, batch_id ORDER BY processed_ts DESC) rn
    FROM gold.pipeline_checkpoints
    WHERE batch_id = ':BATCH_ID'
  ) t
  WHERE rn = 1  -- latest checkpoint per pipeline for this batch
),

-- 5. Determine for each upstream whether all expected pipelines have SUCCESS
upstream_status AS (
  SELECT
    e.table_name,
    COUNT(DISTINCT e.pipeline_name) AS expected_pipelines,
    SUM(CASE WHEN a.status = 'SUCCESS' THEN 1 ELSE 0 END) AS succeeded_pipelines,
    MAX(b.end_version) AS end_version
  FROM expected e
  LEFT JOIN actual a
    ON e.pipeline_name = a.pipeline_name
  JOIN batch_wms b
    ON e.table_name = b.table_name
  GROUP BY e.table_name
)

SELECT table_name, expected_pipelines, succeeded_pipelines, end_version
FROM upstream_status;
```

**Interpretation**:

- For each table_name this returns how many pipelines were expected and how many actually succeeded, plus the end_version discovered at batch creation.
- Upstreams where expected_pipelines = succeeded_pipelines are safe to advance.

---

#### 2) Finalizer MERGE — update gold.committed_watermarks for ready upstreams

Now perform an atomic MERGE that updates last_committed_version for upstreams that are ready.

**Approach**: write the set of to-be-advanced upstreams into a temp view and MERGE into gold.committed_watermarks. The MERGE logic updates only when src.end_version > tgt.last_committed_version (so we never move backwards).

```sql
-- Prepare the source rows (table_name, end_version) for advance
WITH ready_to_advance AS (
  SELECT u.table_name, u.end_version
  FROM (
    -- reuse upstream_status logic inline for brevity
    WITH registry_expanded AS (
      SELECT pipeline_name, explode(upstream_tables) AS table_name
      FROM gold.pipeline_registry
    ),
    batch_wms AS (
      SELECT batch_id, table_name, start_version, end_version, status
      FROM gold.watermarks
      WHERE batch_id = ':BATCH_ID' AND status = 'PENDING'
    ),
    expected AS (
      SELECT be.table_name, re.pipeline_name
      FROM batch_wms be
      LEFT JOIN registry_expanded re
        ON be.table_name = re.table_name
    ),
    actual AS (
      SELECT pipeline_name, batch_id, status
      FROM (
        SELECT pipeline_name, batch_id, status,
               row_number() OVER (PARTITION BY pipeline_name, batch_id ORDER BY processed_ts DESC) rn
        FROM gold.pipeline_checkpoints
        WHERE batch_id = ':BATCH_ID'
      ) t
      WHERE rn = 1
    )
    SELECT
      e.table_name,
      COUNT(DISTINCT e.pipeline_name) AS expected_pipelines,
      SUM(CASE WHEN a.status = 'SUCCESS' THEN 1 ELSE 0 END) AS succeeded_pipelines,
      MAX(b.end_version) AS end_version
    FROM expected e
    LEFT JOIN actual a ON e.pipeline_name = a.pipeline_name
    JOIN batch_wms b ON e.table_name = b.table_name
    GROUP BY e.table_name
  ) u
  WHERE u.expected_pipelines = u.succeeded_pipelines
)

-- MERGE into committed watermark (atomic)
MERGE INTO gold.committed_watermarks tgt
USING ready_to_advance src
  ON tgt.table_name = src.table_name
WHEN MATCHED AND src.end_version > tgt.last_committed_version
  THEN UPDATE SET
    tgt.last_committed_version = src.end_version,
    tgt.commit_ts = current_timestamp(),
    tgt.updated_by = 'finalizer_job'
WHEN NOT MATCHED
  THEN INSERT (table_name, last_committed_version, commit_ts, updated_by)
  VALUES (src.table_name, src.end_version, current_timestamp(), 'finalizer_job');
```


**Notes**:

- The MERGE will insert rows for upstreams not yet present in gold.committed_watermarks.
- The WHEN MATCHED uses a condition src.end_version > tgt.last_committed_version to avoid regressing the pointer.
- Wrap this MERGE inside orchestration (or run it as a single SQL job) to guarantee atomicity.

---

#### 3) Fallback: no PIPELINE_REGISTRY available

If you don't have a registry mapping pipelines → upstreams, a simpler (but weaker) logic is: advance upstreams that had at least one pipeline SUCCESS in this batch.

```sql
WITH batch_wms AS (
  SELECT batch_id, table_name, end_version
  FROM gold.watermarks
  WHERE batch_id = ':BATCH_ID' AND status = 'PENDING'
),
successful_pipelines AS (
  SELECT DISTINCT pipeline_name
  FROM (
    SELECT pipeline_name, batch_id, status,
           row_number() OVER (PARTITION BY pipeline_name, batch_id ORDER BY processed_ts DESC) rn
    FROM gold.pipeline_checkpoints
    WHERE batch_id = ':BATCH_ID'
  ) t
  WHERE rn = 1 AND status = 'SUCCESS'
),
-- find upstreams that had at least one pipeline success (join logic depends on your orchestration)
-- naive approach: assume every pipeline may reference many upstreams; if you have a separate table mapping pipeline->upstream,
-- use it. Otherwise, this simply advances all batch_wms where any pipeline succeeded (lowest confidence).
upstreams_with_any_success AS (
  SELECT bw.table_name, bw.end_version
  FROM batch_wms bw
  CROSS JOIN successful_pipelines sp
  LIMIT 1  -- this is just illustrating the weakness; realistically you'd need mapping info
)
```

-- MERGE similar to above using upstreams_with_any_success as src

Caveat: the fallback approach is risky — it may advance an upstream while some dependent pipeline failed. Use only if you know your pipelines are independent or you have other compensation logic.

---

### Transactional / concurrency recommendations

1. Single finalizer process per batch: only one finalizer job should run per batch to avoid races. Use job orchestration locks (e.g., job scheduler locks, metastore lock row) if needed.
2. Idempotence: MERGE is idempotent when your source rows and conditional update use > checks. Re-running finalizer is safe.
3. Audit trail: keep gold.watermarks and gold.pipeline_checkpoints history so you can replay or debug why an upstream wasn't advanced.
4. Advance only after ALL dependent pipelines succeed: rely on PIPELINE_REGISTRY to be authoritative mapping. If pipelines change, update the registry.
5. Retries & backoff: if a pipeline failed, you can re-run that single pipeline for the same batch_id — because watermarks hold exact version ranges, reprocessing is deterministic.


### Quick examples: read-only checks you may run before finalizer

```sql
- See which upstreams in batch have PENDING watermarks:

SELECT table_name, start_version, end_version, status
FROM gold.watermarks
WHERE batch_id = ':BATCH_ID' AND status = 'PENDING';
- See pipeline statuses for this batch:

SELECT pipeline_name,
       first(status) AS latest_status,
       max(processed_ts) AS last_update
FROM (
  SELECT pipeline_name, batch_id, status, processed_ts,
         row_number() OVER (PARTITION BY pipeline_name, batch_id ORDER BY processed_ts DESC) rn
  FROM gold.pipeline_checkpoints
  WHERE batch_id = ':BATCH_ID'
) t
WHERE rn = 1
GROUP BY pipeline_name;
```

If you want, I can now:
- produce the exact DeltaTable Scala API equivalent for the MERGE shown in SQL (so you can run it in a Spark job),
- or generate a templated finalizer Scala object that runs the SQL/DeltaTable steps and returns the list of advanced upstreams.


---

## DeltaTable Scala API equivalent for the MERGE shown in SQL (so you can run it in a Spark job)


Nice — below is a ready-to-run Scala function that implements the exact same finalizer/advance logic you showed in SQL, but using the DeltaTable Scala API (io.delta.tables.DeltaTable). It:

-computes which upstreams in a given batch_id are ready to advance (i.e., all pipelines that depend on that upstream have SUCCESS for the batch),
-constructs a small source DataFrame (table_name, end_version) for those ready upstreams, and
-performs an atomic merge into gold.committed_watermarks using the DeltaTable API, updating only when src.end_version > tgt.last_committed_version and inserting when missing.

Drop this function into your job code (it expects your gold.* tables to exist or it will create them). Example usage follows the function.

```scala
import org.apache.spark.sql.{DataFrame, SparkSession, Column}
import org.apache.spark.sql.functions._
import io.delta.tables._
import scala.jdk.CollectionConverters._
import java.sql.Timestamp

object FinalizerDeltaApi {

  // Ensure tables exist (idempotent)
  def ensureFinalizerTables(spark: SparkSession): Unit = {
    spark.sql(
      s"""
         |CREATE TABLE IF NOT EXISTS gold.watermarks (
         |  batch_id STRING,
         |  table_name STRING,
         |  start_version BIGINT,
         |  end_version BIGINT,
         |  last_processed_version BIGINT,
         |  latest_available_version BIGINT,
         |  start_ts TIMESTAMP,
         |  end_ts TIMESTAMP,
         |  cdf_enabled BOOLEAN,
         |  update_ts TIMESTAMP,
         |  updated_by STRING,
         |  status STRING,
         |  error_message STRING
         |) USING DELTA
       """.stripMargin)

    spark.sql(
      s"""
         |CREATE TABLE IF NOT EXISTS gold.pipeline_checkpoints (
         |  pipeline_name STRING,
         |  batch_id STRING,
         |  processed_ts TIMESTAMP,
         |  status STRING,
         |  rows_read BIGINT,
         |  rows_written BIGINT,
         |  metrics MAP<STRING,STRING>,
         |  error_message STRING
         |) USING DELTA
       """.stripMargin)

    spark.sql(
      s"""
         |CREATE TABLE IF NOT EXISTS gold.committed_watermarks (
         |  table_name STRING,
         |  last_committed_version BIGINT,
         |  commit_ts TIMESTAMP,
         |  updated_by STRING
         |) USING DELTA
       """.stripMargin)

    spark.sql(
      s"""
         |CREATE TABLE IF NOT EXISTS gold.pipeline_registry (
         |  pipeline_name STRING,
         |  upstream_tables ARRAY<STRING>
         |) USING DELTA
       """.stripMargin)
  }

  /**
   * Finalizer using DeltaTable API.
   *
   * @param spark SparkSession
   * @param batchId Batch identifier to finalize
   * @param pipelineRegistry Map[pipelineName -> Seq[upstream_table]]
   *                         (if empty, function will fallback to "any pipeline success" logic)
   * @param finalizerUser who performs the update (updated_by)
   * @return Seq of advanced upstream table names
   */
  def finalizeBatchDeltaApi(
    spark: SparkSession,
    batchId: String,
    pipelineRegistry: Map[String, Seq[String]],
    finalizerUser: String = "finalizer_job"
  ): Seq[String] = {
    import spark.implicits._

    ensureFinalizerTables(spark)

    // 1) Read watermark rows for the batch that are PENDING (or you may remove filter and allow configurable statuses)
    val batchWmDF = spark.table("gold.watermarks")
      .filter(col("batch_id") === lit(batchId) && col("status") === lit("PENDING"))
      .select("table_name", "start_version", "end_version", "status")

    // If no rows, return empty
    if (batchWmDF.isEmpty) return Seq.empty[String]

    // 2) Build expected pipeline mapping (upstream -> Seq[pipeline])
    val upstreamToPipelines: Map[String, Seq[String]] = pipelineRegistry.toSeq
      .flatMap { case (p, ups) => ups.map(u => (u, p)) }
      .groupBy(_._1)
      .mapValues(_.map(_._2).distinct)
      .map(identity)

    // 3) Build a DataFrame of latest checkpoint status per pipeline for this batch (latest processed_ts per pipeline)
    val latestCheckpoints = {
      val cp = spark.table("gold.pipeline_checkpoints")
        .filter(col("batch_id") === lit(batchId))
        .select("pipeline_name","batch_id","processed_ts","status")

      // Windowing to get latest status per pipeline_name for this batch
      val windowed = cp.withColumn("rn", row_number().over(
        org.apache.spark.sql.expressions.Window.partitionBy(col("pipeline_name"), col("batch_id"))
          .orderBy(col("processed_ts").desc)
      )).filter(col("rn") === 1).drop("rn")

      windowed.select("pipeline_name","status")
    }

    // materialize as Map pipeline -> status
    val pipelineStatusMap: Map[String, String] = latestCheckpoints
      .as[(String,String)]
      .collect()
      .toMap

    // 4) Determine which upstreams are ready:
    //    - If pipelineRegistry contains entries for the upstream: require all expected pipelines' statuses == SUCCESS
    //    - If no registry entry for an upstream: require at least one pipeline with SUCCESS (fallback)
    // We'll join logic with batchWmDF to get end_version for ready upstreams.
    val batchWm = batchWmDF.as("bw")

    val candidateRows = batchWm.collect().flatMap { row =>
      val tableName = row.getAs[String]("table_name")
      val endVersion = row.getAs[Long]("end_version")
      val status = row.getAs[String]("status")

      if (status != "PENDING" || endVersion < 0) {
        None
      } else {
        val expectedPipelines = upstreamToPipelines.getOrElse(tableName, Seq.empty)
        if (expectedPipelines.nonEmpty) {
          // require all expected pipelines to be SUCCESS
          val allSucceeded = expectedPipelines.forall { p =>
            pipelineStatusMap.get(p).contains("SUCCESS")
          }
          if (allSucceeded) Some((tableName, endVersion)) else None
        } else {
          // no registry info: fallback - require at least one pipeline succeeded in this batch
          val anySucceeded = pipelineStatusMap.values.exists(_ == "SUCCESS")
          if (anySucceeded) Some((tableName, endVersion)) else None
        }
      }
    }

    val readyToAdvance = candidateRows.toSeq.distinct

    if (readyToAdvance.isEmpty) return Seq.empty[String]

    // 5) Convert readyToAdvance to a source DataFrame for the MERGE
    val srcDf = readyToAdvance.toDF("table_name","end_version")
      .withColumn("commit_ts", current_timestamp())
      .withColumn("updated_by", lit(finalizerUser))

    // 6) Ensure committed_watermarks table exists (already created in ensureFinalizerTables)
    val tgtName = "gold.committed_watermarks"
    if (!spark.catalog.tableExists(tgtName)) {
      // create table by writing an empty DF with schema (defensive)
      srcDf.limit(0).write.format("delta").mode("overwrite").saveAsTable(tgtName)
    }

    // 7) Perform DeltaTable merge using API
    val deltaT = DeltaTable.forName(spark, tgtName)

    // DeltaTable.merge with condition: tgt.table_name = src.table_name
    // Update only when src.end_version > tgt.last_committed_version
    // We'll use Scala Map[String, Column] for update/insert expressions.
    val updateSet: Map[String, Column] = Map(
      "last_committed_version" -> col("src.end_version"),
      "commit_ts" -> col("src.commit_ts"),
      "updated_by" -> col("src.updated_by")
    )

    val insertSet: Map[String, Column] = Map(
      "table_name" -> col("src.table_name"),
      "last_committed_version" -> col("src.end_version"),
      "commit_ts" -> col("src.commit_ts"),
      "updated_by" -> col("src.updated_by")
    )

    // register src as temp view and then use DataFrame for merge
    srcDf.createOrReplaceTempView("__ready_to_advance_src")

    deltaT.as("tgt")
      .merge(
        spark.table("__ready_to_advance_src").as("src"),
        expr("tgt.table_name = src.table_name")
      )
      .whenMatched(expr("src.end_version > tgt.last_committed_version"), updateSet.asJava)
      .whenNotMatched(insertSet.asJava)
      .execute()

    // Return advanced upstream table names
    readyToAdvance.map(_._1)
  }
}
```

#### Example usage


```scala
val spark: SparkSession = SparkSession.builder()
  .appName("finalizer-demo")
  .master("local[2]")
  .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
  .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
  .getOrCreate()

// Example pipeline registry (pipeline -> upstreams)
val pipelineRegistry: Map[String, Seq[String]] = Map(
  "pipeline_a" -> Seq("up1","up2"),
  "pipeline_b" -> Seq("up2","up3")
)

// Call finalizer for a batch
val advanced = FinalizerDeltaApi.finalizeBatchDeltaApi(spark, "batch_2025-12-01T12:00:00Z_abc123", pipelineRegistry, "finalizer_job")
println(s"Advanced upstreams: ${advanced.mkString(",")}")

```

#### Notes & tips

-The function uses the Spark catalog tables gold.watermarks, gold.pipeline_checkpoints, gold.committed_watermarks. Ensure these tables exist in the Spark catalog / metastore (the function will create them if missing).
-The DeltaTable API whenMatched accepts a condition and a Java Map[String, Column]. We convert Scala Map to Java via .asJava.
-The finalizer is idempotent: re-running it for the same ready source won't regress pointers because the update uses src.end_version > tgt.last_committed_version guard.
-If you prefer to run the entire ready-to-advance computation inside Spark SQL (rather than in Scala collect()), you can rewrite steps 3–4 as DataFrame SQL joins and aggregations; this implementation uses a small collect() because the number of watermark rows per batch is expected to be small. If you expect thousands of upstreams per batch, rewrite the readiness detection as pure DataFrame operations (I can provide that variant on request).


---


