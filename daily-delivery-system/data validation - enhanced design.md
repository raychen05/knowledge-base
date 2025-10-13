

##  A Configurable Data Validation Rule Registry


Perfect — adding a configurable Data Validation Rule Registry makes your post-load validation pipeline modular, scalable, and easily maintainable.

This means no hardcoding of thresholds, entities, or rules — everything is data-driven and managed from Delta tables (or JSON configs).

Below is the extended design + Spark/Scala skeleton to implement that in Databricks.


### 🧩 1. Design Goals


### 🏆 Design Goals

| Goal              | Description                                                                                   |
|-------------------|----------------------------------------------------------------------------------------------|
| Dynamic Rules     | Each dataset (WOS, Patents, Grants, Authors, etc.) has its own validation rules and thresholds. |
| Centralized Config| All validation logic is stored in the Delta table `validation_rules` for easy management.      |
| Auto-Adaptation   | The validation job reads rules dynamically, applies them to datasets, and produces results.    |
| Easy to Update    | Thresholds, rule types, or datasets can be changed without modifying code.                     |

---

### 🗂️ 2. Validation Rule Registry Schema

**Table: validation_rules**

| Column           | Type    | Description                                                        |
|------------------|---------|--------------------------------------------------------------------|
| entity           | STRING  | Dataset name, e.g., `"wos_docs"`                                   |
| metric           | STRING  | Metric to validate, e.g., `"total_docs"`, `"unique_authors"`       |
| rule_type        | STRING  | Validation type: `"growth_rate"`, `"null_ratio"`, `"distribution_change"` |
| threshold_upper  | DOUBLE  | Maximum acceptable change (e.g., `0.3` = +30%)                     |
| threshold_lower  | DOUBLE  | Minimum acceptable change (e.g., `-0.3` = -30%)                    |
| severity         | STRING  | Alert level: `"warn"` or `"critical"`                              |
| description      | STRING  | Human-readable rule description                                    |
| enabled          | BOOLEAN | Whether this rule is active                                        |


**Example SQL DDL**

```sql
CREATE TABLE delta.validation_rules (
  entity STRING,
  metric STRING,
  rule_type STRING,
  threshold_upper DOUBLE,
  threshold_lower DOUBLE,
  severity STRING,
  description STRING,
  enabled BOOLEAN
)
USING delta;

INSERT INTO delta.validation_rules VALUES
  ("wos_docs", "total_docs", "growth_rate", 0.5, -0.5, "critical", "Daily doc count change >50% or <-50%", true),
  ("patent_docs", "unique_authors", "growth_rate", 0.3, -0.3, "warn", "Author count drift beyond ±30%", true),
  ("grant_docs", "unique_orgs", "growth_rate", 0.4, -0.4, "warn", "Organization coverage fluctuation", true);

```

---

### ⚙️ 3. Extended Validation Job Skeleton


```scala
// Databricks Scala notebook: PostLoadValidationWithRules.scala

import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import java.time.LocalDate

val spark = SparkSession.builder().appName("PostLoadValidationWithRules").getOrCreate()

val today = LocalDate.now().toString
val yesterday = LocalDate.now().minusDays(1).toString
val basePath = "/mnt/delta/"
val validationTable = basePath + "validation_results"
val alertsTable = basePath + "alerts_delta"
val rulesTable = basePath + "validation_rules"

// ---------------------------------------------------------
// 1. Load rules and datasets
// ---------------------------------------------------------
val rulesDF = spark.read.format("delta").load(rulesTable).filter(col("enabled") === true)

// Load dataset metrics (same as before)
val metricsDF = spark.read.format("delta").load(validationTable).filter(col("load_date") === today)
val prevMetricsDF = spark.read.format("delta").load(validationTable).filter(col("load_date") === yesterday)

// Join metrics for diff comparison
val joinedDF = metricsDF.as("curr")
  .join(prevMetricsDF.as("prev"), Seq("entity"), "left")
  .withColumn("growth_total_docs", (col("curr.total_docs") - col("prev.total_docs")) / col("prev.total_docs"))
  .withColumn("growth_unique_authors", (col("curr.unique_authors") - col("prev.unique_authors")) / col("prev.unique_authors"))
  .withColumn("growth_unique_orgs", (col("curr.unique_orgs") - col("prev.unique_orgs")) / col("prev.unique_orgs"))

// ---------------------------------------------------------
// 2. Apply dynamic rule checks
// ---------------------------------------------------------
def applyRule(joinedDF: DataFrame, rulesDF: DataFrame): DataFrame = {
  joinedDF.join(rulesDF, Seq("entity"), "inner")
    .filter(col("rule_type") === "growth_rate")
    .withColumn("metric_value",
      when(col("metric") === "total_docs", col("growth_total_docs"))
        .when(col("metric") === "unique_authors", col("growth_unique_authors"))
        .when(col("metric") === "unique_orgs", col("growth_unique_orgs"))
        .otherwise(lit(null))
    )
    .filter(col("metric_value").isNotNull)
    .withColumn("alert_flag",
      when(col("metric_value") > col("threshold_upper") || col("metric_value") < col("threshold_lower"), lit(true)).otherwise(lit(false))
    )
    .filter(col("alert_flag") === true)
    .withColumn("alert_message",
      concat(
        lit("⚠️ Entity: "), col("entity"), lit(" | Metric: "), col("metric"),
        lit(" | Value: "), format_number(col("metric_value"), 2),
        lit(" | Thresholds: ["),
        format_number(col("threshold_lower"), 2), lit(", "),
        format_number(col("threshold_upper"), 2), lit("]")
      )
    )
}

// Generate anomalies from rules
val anomaliesDF = applyRule(joinedDF, rulesDF)

// ---------------------------------------------------------
// 3. Save results and alerts
// ---------------------------------------------------------
anomaliesDF.write.format("delta").mode("append").save(alertsTable)

// Optional: send Slack alerts
import scalaj.http._
anomaliesDF.collect().foreach { row =>
  val msg = s"[${row.getAs[String]("severity").toUpperCase}] ${row.getAs[String]("alert_message")}"
  Http("https://hooks.slack.com/services/XXXXX")
    .postData(s"""{"text": "$msg"}""")
    .header("Content-Type", "application/json")
    .asString
}

println(s"✅ Validation with dynamic rules completed. Alerts: ${anomaliesDF.count()}")
```

---

### 🧠 4. Advantages of the Rule Registry Approach


| Benefit             | Description                                                         |
|---------------------|---------------------------------------------------------------------|
| Extensible          | Add or modify rules per entity or metric without changing code.      |
| Centralized Control | All validation logic is managed in a single, data-driven location.   |
| Auditable           | Rules are versioned and changes are logged in Delta tables.          |
| Configurable Severity| Different thresholds and alert levels for "warn" vs. "critical".    |
| Reusable            | Framework supports both pre-load and post-load validation tasks.     |

---

### 🧮 5. Example Rules
| Entity          | Metric           | Rule Type    | Lower  | Upper  | Severity  | Description             |
|-----------------|------------------|--------------|--------|--------|-----------|-------------------------|
| wos_docs        | total_docs       | growth_rate  | -0.4   | 0.4    | critical  | Document count drift    |
| author_profiles | unique_authors   | growth_rate  | -0.2   | 0.3    | warn      | Author volume deviation |
| grants          | unique_funders   | growth_rate  | -0.5   | 0.5    | critical  | Funder data loss/growth |
| patent_docs     | unique_orgs      | growth_rate  | -0.3   | 0.3    | warn      | Organization linkage drift |


---

### 📈 6. Optional Enhancements


| Extension                      | Description                                                                                   |
|---------------------------------|----------------------------------------------------------------------------------------------|
| **Rule Type: absolute_threshold*- | Trigger alerts when metrics cross fixed values (e.g., `total_docs < 10M`).                   |
| **Rule Type: distribution_change*- | Compare category/country shares using KL-divergence to detect distribution shifts.           |
| **Schema Drift Check*-            | Automatically detect schema or column type changes using DataFrame schema hashing.            |
| **Automatic Baseline Calculation**| Compute rolling mean ± standard deviation for adaptive thresholds instead of static values.   |
| **Integration with MLflow*-       | Track validation results and metrics for each run using MLflow for experiment management.     |


---

✅ Summary

Your Data Validation Pipeline (Databricks, Spark/Scala) now consists of:

1. Metric Extraction Job – aggregates key counts per dataset.
2. Validation Rule Registry – defines per-entity, per-metric rules & thresholds.
3. Validation Executor Job – reads rules, compares metrics, flags anomalies.
4. Alert Writer – saves alerts, posts Slack/email messages.
5. Historical Reporting – query trends over time in validation_results.

Would you like me to extend this next with a “baseline learning mode”,
 - where thresholds are auto-learned from historical data (mean ± 3σ per metric per entity), instead of manually configured limits?


---



## Enhanced Design + Full Scala Spark Skeleton


Perfect ✅ — now let’s extend your post-load validation pipeline into a more complete, production-ready Spark/Scala skeleton that supports:

- Incremental comparisons (day-to-day or run-to-run)
- Validation rule registry (configurable)
- Summary + alert output (to Delta/ES/Slack/etc.)
- Works for multiple datasets (WOS, patents, grants, author profiles, etc.)

Here’s the enhanced design + full Scala Spark skeleton:

---

### 🧩 Design Overview

🔁 **Workflow**

1. Load yesterday’s snapshot and today’s snapshot for each index.
2. Compute metrics (record counts, distinct entities, aggregates).
3. Compare metrics and apply rules (threshold %, absolute difference).
4. Detect anomalies or schema/data format issues.
5. Emit a validation summary and alerts.

🗃️ **Input**

- Delta tables (incremental datasets)
- Validation rule config (JSON or Delta table)
- Historical metrics (for trend analysis)

🧾 **Output**

- delta.table("validation_results_daily")
- Alerts to Slack or ES via webhook
- Optional dashboard table for Databricks SQL


---

### 💻 Scala Spark Skeleton


```scala
// Databricks Scala notebook: validation_post_load.scala

import org.apache.spark.sql._
import org.apache.spark.sql.functions._
import java.time.LocalDate

// --- CONFIG ---
val runDate = dbutils.widgets.get("run_date")
val basePath = "/mnt/delta/academic"
val validationOutputPath = s"${basePath}/validation_results"
val prevDate = LocalDate.parse(runDate).minusDays(1).toString

// Define your datasets
val datasets = Seq("wos_docs", "patents", "grants", "author_profiles")

// --- RULE CONFIG ---
case class ValidationRule(
  metricName: String,
  thresholdPercent: Double,
  alertIfIncrease: Boolean = true,
  alertIfDecrease: Boolean = true
)

val rules = Seq(
  ValidationRule("record_count", 10.0),
  ValidationRule("unique_authors", 10.0),
  ValidationRule("unique_orgs", 10.0),
  ValidationRule("avg_citations", 15.0)
)

// --- HELPER: Compute metrics ---
def computeMetrics(df: DataFrame, dataset: String): DataFrame = {
  df.agg(
    count("*").alias("record_count"),
    countDistinct("author_id").alias("unique_authors"),
    countDistinct("org_id").alias("unique_orgs"),
    avg("citation_count").alias("avg_citations")
  ).withColumn("dataset", lit(dataset))
}

// --- MAIN VALIDATION ---
val results = datasets.map { dataset =>
  val todayDf = spark.read.format("delta").load(s"${basePath}/${dataset}/date=${runDate}")
  val prevDf  = spark.read.format("delta").load(s"${basePath}/${dataset}/date=${prevDate}")

  val todayMetrics = computeMetrics(todayDf, dataset).withColumn("date", lit(runDate))
  val prevMetrics  = computeMetrics(prevDf, dataset).withColumn("date", lit(prevDate))

  val joined = todayMetrics.as("t").join(prevMetrics.as("p"), Seq("dataset"), "inner")

  val diffMetrics = joined.select(
    col("dataset"),
    col("t.date").alias("current_date"),
    col("p.date").alias("previous_date"),
    (col("t.record_count") - col("p.record_count")).alias("diff_record_count"),
    ((col("t.record_count") - col("p.record_count")) / col("p.record_count") - 100).alias("pct_change_record_count"),
    (col("t.unique_authors") - col("p.unique_authors")).alias("diff_unique_authors"),
    ((col("t.unique_authors") - col("p.unique_authors")) / col("p.unique_authors") - 100).alias("pct_change_unique_authors"),
    (col("t.avg_citations") - col("p.avg_citations")).alias("diff_avg_citations"),
    ((col("t.avg_citations") - col("p.avg_citations")) / col("p.avg_citations") - 100).alias("pct_change_avg_citations")
  )

  diffMetrics
}.reduce(_ union _)

// --- APPLY RULES ---
val ruleThresholds = rules.map(r => (r.metricName, r.thresholdPercent)).toMap

val validated = results.withColumn(
  "alerts",
  array(
    when(abs(col("pct_change_record_count")) > ruleThresholds("record_count"), lit("record_count")).otherwise(null),
    when(abs(col("pct_change_unique_authors")) > ruleThresholds("unique_authors"), lit("unique_authors")).otherwise(null),
    when(abs(col("pct_change_avg_citations")) > ruleThresholds("avg_citations"), lit("avg_citations")).otherwise(null)
  ).filter(x => x.isNotNull)
)

// --- WRITE OUTPUT ---
validated.write
  .format("delta")
  .mode("append")
  .option("mergeSchema", "true")
  .save(validationOutputPath)

// --- ALERTS (Slack / Logging) ---
val alertsDf = validated.filter(size(col("alerts")) > 0)
alertsDf.collect().foreach { row =>
  val dataset = row.getAs[String]("dataset")
  val alertMetrics = row.getSeq[String](row.fieldIndex("alerts")).mkString(", ")
  val msg = s"⚠️ Validation alert on $dataset – metrics: $alertMetrics exceeded threshold."
  println(msg)
  // TODO: send to Slack webhook or ES index
}
```

---


### 📊 Suggested Dashboards - Visualizations


| Metric                   | Visualization   | Description                                 |
|--------------------------|-----------------|---------------------------------------------|
| Record count trend       | Line chart      | Tracks document volume day-to-day           |
| % change by dataset      | Bar chart       | Detects sudden jumps or drops per dataset   |
| Entity linkage counts    | Table           | Shows unique author/org/funder/journal daily|
| Failed validation count  | Counter         | Displays number of alerts triggered per run |


Would you like me to extend this skeleton with:
- 🔔 Slack/Teams alert integration, or
- 🧠 Schema-level validation (type/column consistency check)?


---

