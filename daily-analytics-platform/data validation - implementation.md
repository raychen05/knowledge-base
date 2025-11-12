##  Spark/Scala Notebook Skeleton

Perfect — since your Databricks workflow loads large-scale academic documents (1–20M updates/day) into Elasticsearch and you want a post-load validation and integrity-check job,
 - let’s design a Spark/Scala notebook skeleton that runs after the ES load to validate, detect anomalies, and publish alerts.


### 🧱 Objective

After each daily ES load (for WOS, patents, grants, author profiles, etc.),
 - run a Spark validation job that:
1. Loads daily and historical stats from Delta (or ES).
2. Compares key metrics (counts, distincts, relationships).
3. Detects anomalies or drops/spikes vs. expected baseline.
4. Writes validation results and alerts to Delta or dashboard sink (Slack, email, etc.).

---

### ⚙️ Core Components

*Inputs*:
- Delta tables or ES indices for documents (wos_docs, patents, grants, etc.)
- daily_validation_summary (history of metrics)

**Outputs**:
- validation_results Delta table
- Alert log (alerts_delta)

---

### 🧩 Spark / Scala Skeleton


```scala
// Databricks Scala notebook: PostLoadValidationJob.scala

import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.functions._
import java.time.LocalDate

// ---------------------------------------------------------
// 1. Initialization
// ---------------------------------------------------------
val spark = SparkSession.builder()
  .appName("PostLoadValidationJob")
  .getOrCreate()

val today = LocalDate.now().toString
val yesterday = LocalDate.now().minusDays(1).toString

// Define paths or tables
val basePath = "/mnt/delta/"
val validationTable = basePath + "validation_results"
val alertsTable = basePath + "alerts_delta"

// ---------------------------------------------------------
// 2. Helper: Metric Computation Function
// ---------------------------------------------------------
def computeMetrics(df: DataFrame, entityName: String): DataFrame = {
  df.agg(
    count("*").alias("total_docs"),
    countDistinct("doc_id").alias("unique_docs"),
    countDistinct("author_id").alias("unique_authors"),
    countDistinct("organization_id").alias("unique_orgs"),
    countDistinct("funder_id").alias("unique_funders"),
    countDistinct("journal_id").alias("unique_journals"),
    countDistinct("category_id").alias("unique_categories"),
    countDistinct("country").alias("unique_countries")
  ).withColumn("entity", lit(entityName))
   .withColumn("load_date", lit(today))
}

// ---------------------------------------------------------
// 3. Load Data from Delta or ES
// ---------------------------------------------------------
val wosDF = spark.read.format("delta").load(basePath + "wos_docs")
val patentDF = spark.read.format("delta").load(basePath + "patent_docs")
val grantsDF = spark.read.format("delta").load(basePath + "grant_docs")
val authorDF = spark.read.format("delta").load(basePath + "author_profiles")

// ---------------------------------------------------------
// 4. Compute Validation Metrics per Dataset
// ---------------------------------------------------------
val metricsDF = Seq(
  computeMetrics(wosDF, "wos_docs"),
  computeMetrics(patentDF, "patent_docs"),
  computeMetrics(grantsDF, "grant_docs"),
  computeMetrics(authorDF, "author_profiles")
).reduce(_ union _)

// ---------------------------------------------------------
// 5. Load Yesterday’s Metrics
// ---------------------------------------------------------
val prevMetricsDF = spark.read.format("delta").load(validationTable)
  .filter(col("load_date") === yesterday)

// ---------------------------------------------------------
// 6. Compare and Detect Anomalies
// ---------------------------------------------------------
val joinedDF = metricsDF.as("curr")
  .join(prevMetricsDF.as("prev"), Seq("entity"), "left")
  .withColumn("doc_growth", (col("curr.total_docs") - col("prev.total_docs")) / col("prev.total_docs"))
  .withColumn("author_growth", (col("curr.unique_authors") - col("prev.unique_authors")) / col("prev.unique_authors"))
  .withColumn("org_growth", (col("curr.unique_orgs") - col("prev.unique_orgs")) / col("prev.unique_orgs"))

// Thresholds
val growthThreshold = 0.5 // ±50%
val anomaliesDF = joinedDF.filter(
  abs(col("doc_growth")) > growthThreshold ||
  abs(col("author_growth")) > growthThreshold ||
  abs(col("org_growth")) > growthThreshold
).withColumn("alert_type", lit("volume_change"))
 .withColumn("alert_message",
   concat(
     lit("Significant change detected in "), col("entity"),
     lit(": doc_growth="), format_number(col("doc_growth"), 2)
   )
 )

// ---------------------------------------------------------
// 7. Write Validation & Alerts
// ---------------------------------------------------------
metricsDF.write
  .format("delta")
  .mode("append")
  .save(validationTable)

anomaliesDF.write
  .format("delta")
  .mode("append")
  .save(alertsTable)

// ---------------------------------------------------------
// 8. Optional: Send Alerts via Webhook (Slack/Email/Teams)
// ---------------------------------------------------------
import scalaj.http._

anomaliesDF.collect().foreach { row =>
  val msg = s"[${row.getAs[String]("entity")}] Validation Alert: ${row.getAs[String]("alert_message")}"
  Http("https://hooks.slack.com/services/XXXXX")
    .postData(s"""{"text": "$msg"}""")
    .header("Content-Type", "application/json")
    .asString
}

// ---------------------------------------------------------
// 9. Log Summary
// ---------------------------------------------------------
println(s"✅ Validation completed for $today — ${anomaliesDF.count()} anomalies detected.")

```

---

### 🧠 Extensible Validation Checks

Beyond simple growth checks, you can expand to include:

| Category     | Example Validation                        | Purpose                                 |
|--------------|-------------------------------------------|-----------------------------------------|
| Volume       | Count of docs, distinct authors/orgs      | Detect drops or spikes                  |
| Linkage      | % of docs with author/org/funder links    | Detect schema/data join failures        |
| Type/Schema  | Null or unexpected data types             | Catch pipeline schema drift             |
| Distribution | Country/journal/category share change     | Detect skew or data source issues       |
| Integrity    | Duplicates, missing keys, orphan links    | Detect referential integrity issues     |
| Temporal     | Date coverage vs. expected                | Detect pipeline truncation or lag       |


---

### 📊 Delta Tables Used

| Table               | Purpose                                 |
|---------------------|-----------------------------------------|
| validation_results  | Historical metrics per entity/date       |
| alerts_delta        | Alerts for detected anomalies            |
| *_docs              | Domain datasets (WOS, Patents, etc.)     |


---

### 🧱 Pipeline Integration


1. After each pipeline’s ES load, trigger this notebook as a downstream Databricks Job Task.
2. Write results to validation_results.
3. If alerts exist → send Slack/email/webhook + dashboard update.
4. Optional: use Delta Live Tables or Databricks Workflows for orchestration.


---


## Schema-level Validation 


Excellent — adding schema-level validation (type + column consistency checks) is a critical next step for your Databricks incremental load validation pipeline — especially when your data originates from heterogeneous sources like Web of Science, PubMed, patents, and grants.
Let’s integrate this seamlessly with your existing Spark/Scala validation job.


### 🧩 Design Goals


**Schema-level Validation Objectives**

| Objective                      | Description                                                                                   |
|---------------------------------|----------------------------------------------------------------------------------------------|
| 🧱 Schema Consistency           | Ensure each pipeline’s Delta table schema matches the expected baseline schema (columns and types). |
| 🔍 Type Validation              | Detect column type drift (e.g., `int` → `string`) that may break joins or Elasticsearch mapping. |
| 🧾 Column Completeness          | Identify missing or unexpected columns (added or dropped) in the dataset.                    |
| 🧮 Nulls / Invalid Value Checks | Flag abnormally high null counts or malformed values per column.                             |
| 🚨 Integrated Alerting          | Reuse Slack/Teams hooks for consistent schema drift and data quality reporting.              |


---

### ⚙️ Implementation Strategy


1. Maintain a “Schema Registry”

Store expected schema per dataset as Delta or JSON.

**Example Schema Registry Table**

| dataset   | column_name | data_type | is_nullable | version |
|-----------|-------------|-----------|-------------|---------|
| wos_docs  | author_id   | string    | true        | 1       |
| wos_docs  | pub_year    | int       | false       | 1       |
| grants    | funder_id   | string    | true        | 1       |

Store this table as a Delta table (e.g., `delta_schema_registry`) to track expected columns, types, nullability, and schema versions per dataset.


2.  Compare Current Schema vs Registry

- Use DataFrame.schema to get actual fields.
- Compare names and data types.
- Generate violations list (added, missing, type_changed).

3.  Alert if Schema Drift Detected

Send Slack/Teams message like:

```less
🚨 Schema Drift Detected – dataset: wos_docs
Added: ["topic_keywords"]
Missing: ["doi"]
Type changed: ["pub_year": int → string]
```

---

### 💻 Scala Spark Implementation Skeleton


Below extends your existing validation job:

```scala
// Databricks Scala notebook: validation_post_load_with_schema_check.scala

import org.apache.spark.sql._
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.time.LocalDate

// --- CONFIG ---
val runDate = dbutils.widgets.get("run_date")
val basePath = "/mnt/delta/academic"
val schemaRegistryPath = s"${basePath}/schema_registry"
val validationOutputPath = s"${basePath}/validation_results"

// Load Slack/Teams webhook secrets
val slackWebhook = dbutils.secrets.get(scope = "alert_hooks", key = "slack_webhook")
val teamsWebhook = dbutils.secrets.get(scope = "alert_hooks", key = "teams_webhook")

val datasets = Seq("wos_docs", "patents", "grants", "author_profiles")

// --- Helper: Send alert (reuse from previous) ---
def sendWebhook(url: String, message: String, isTeams: Boolean = false): Unit = {
  import java.net.{HttpURLConnection, URL}
  import java.io.OutputStream
  val conn = new URL(url).openConnection().asInstanceOf[HttpURLConnection]
  conn.setRequestMethod("POST")
  conn.setDoOutput(true)
  conn.setRequestProperty("Content-Type", "application/json")
  val payload = if (isTeams)
    s"""{"text": "${message.replace("\"", "\\\"")}"}"""
  else
    s"""{"text": ":warning: ${message.replace("\"", "\\\"")}"}"""
  val out: OutputStream = conn.getOutputStream
  out.write(payload.getBytes("UTF-8"))
  out.flush()
  out.close()
  val code = conn.getResponseCode
  if (code != 200) println(s"⚠️ Webhook failed with code: $code")
}

// --- Schema comparison logic ---
def validateSchema(dataset: String, df: DataFrame): DataFrame = {
  val expectedSchemaDf = spark.read.format("delta").load(schemaRegistryPath).filter(col("dataset") === dataset)
  val expectedCols = expectedSchemaDf.collect().map(r => (r.getString(1), r.getString(2))).toMap // colName -> dataType

  val actualFields = df.schema.fields.map(f => (f.name, f.dataType.typeName)).toMap

  val addedCols = actualFields.keySet.diff(expectedCols.keySet)
  val missingCols = expectedCols.keySet.diff(actualFields.keySet)
  val typeChanged = actualFields.filter { case (c, t) =>
    expectedCols.contains(c) && expectedCols(c) != t
  }

  val alertMessage = new StringBuilder()
  if (addedCols.nonEmpty || missingCols.nonEmpty || typeChanged.nonEmpty) {
    alertMessage.append(s"🚨 Schema Drift Detected – Dataset: $dataset\n")
    if (addedCols.nonEmpty) alertMessage.append(s"Added: ${addedCols.mkString(", ")}\n")
    if (missingCols.nonEmpty) alertMessage.append(s"Missing: ${missingCols.mkString(", ")}\n")
    if (typeChanged.nonEmpty) alertMessage.append(s"Type changed: ${typeChanged.map{case(k,v)=>s"$k: expected=${expectedCols(k)}, found=$v"}.mkString(", ")}")
  }

  if (alertMessage.nonEmpty) {
    sendWebhook(slackWebhook, alertMessage.toString)
    sendWebhook(teamsWebhook, alertMessage.toString, isTeams = true)
  }

  // Return schema validation summary as DataFrame
  Seq(
    (dataset, runDate, addedCols.mkString(","), missingCols.mkString(","), typeChanged.map(_._1).mkString(","))
  ).toDF("dataset", "date", "added_columns", "missing_columns", "type_changed")
}

// --- Execute schema validation ---
val schemaResults = datasets.map { ds =>
  val df = spark.read.format("delta").load(s"${basePath}/${ds}/date=${runDate}")
  validateSchema(ds, df)
}.reduce(_ union _)

// Write schema validation results
schemaResults.write.format("delta").mode("append").save(s"${validationOutputPath}/schema_validation")
```

---

### 🧮 Optional: Data-Type and Format Validation (Column Profiling)

You can add light profiling on top of schema validation:

```scala
val formatChecks = df.select(
  col("dataset"),
  sum(when(col("doi").rlike("^10\\."), 0).otherwise(1)).alias("invalid_doi_count"),
  sum(when(col("pub_year").cast("int").isNotNull, 0).otherwise(1)).alias("invalid_pub_year_count"),
  sum(when(col("author_id").isNull, 1).otherwise(0)).alias("null_author_id_count")
)
```

This ensures data quality even when schema is technically correct but content is invalid.

---

### 📊 Suggested Dashboard Additions



| Metric                       | Purpose                | Visualization   |
|------------------------------|------------------------|-----------------|
| Missing columns count        | Schema completeness    | Bar chart       |
| Type mismatch count          | Schema drift frequency | Time series     |
| Invalid DOI / pub_year count | Content integrity      | Line chart      |
| Schema change alerts per dataset | Stability measure      | Heatmap         |


Would you like me to include a “schema auto-repair” feature (auto-update registry when intentional schema evolution occurs)?
 - That’s often useful for large, evolving ETL ecosystems.

---

