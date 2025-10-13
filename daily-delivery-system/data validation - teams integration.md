## Slack and Teams Alert Integration


Excellent — adding Slack and Teams alert integration makes your post-load validation pipeline operationally complete.
Below is a production-ready extension of the Scala Spark notebook that integrates both Slack and Microsoft Teams via webhook connectors.


### 🧩 Design Goals

- ✅ Send concise alerts automatically after validation
- ✅ Include key metrics and change percentages
- ✅ Work for both Slack and Teams without major code differences
- ✅ Keep webhook secrets in Databricks Secrets scope

---

### 🔐 Prerequisites

#### 1. Create Webhooks

- Slack:
 - Go to → Slack App → Incoming Webhooks → Add New Webhook → Select channel
 - You’ll get a URL like:
```bash
  https://hooks.slack.com/services/T123456/ABCDEF/xyz
```

- Microsoft Teams:
 - Go to → Teams Channel → Connectors → Incoming Webhook → Configure → Copy URL
 - You’ll get a URL like:
```bash
 - https://outlook.office.com/webhook/xxxx...
```


### 2. Store secrets in Databricks

```bash
databricks secrets create-scope --scope alert_hooks
databricks secrets put --scope alert_hooks --key slack_webhook
databricks secrets put --scope alert_hooks --key teams_webhook
```

---

### 💻 Scala Spark Notebook – Extended with Alerting

```scala
// Databricks Scala notebook: validation_post_load_with_alerts.scala

import org.apache.spark.sql._
import org.apache.spark.sql.functions._
import java.time.LocalDate
import java.net.{HttpURLConnection, URL}
import java.io.OutputStream

// --- CONFIG ---
val runDate = dbutils.widgets.get("run_date")
val basePath = "/mnt/delta/academic"
val validationOutputPath = s"${basePath}/validation_results"
val prevDate = LocalDate.parse(runDate).minusDays(1).toString

val slackWebhook = dbutils.secrets.get(scope = "alert_hooks", key = "slack_webhook")
val teamsWebhook = dbutils.secrets.get(scope = "alert_hooks", key = "teams_webhook")

val datasets = Seq("wos_docs", "patents", "grants", "author_profiles")

case class ValidationRule(metricName: String, thresholdPercent: Double)
val rules = Seq(
  ValidationRule("record_count", 10.0),
  ValidationRule("unique_authors", 10.0),
  ValidationRule("unique_orgs", 10.0),
  ValidationRule("avg_citations", 15.0)
)

// --- Helper: Compute metrics ---
def computeMetrics(df: DataFrame, dataset: String): DataFrame = {
  df.agg(
    count("*").alias("record_count"),
    countDistinct("author_id").alias("unique_authors"),
    countDistinct("org_id").alias("unique_orgs"),
    avg("citation_count").alias("avg_citations")
  ).withColumn("dataset", lit(dataset))
}

// --- Helper: Send Webhook Message ---
def sendWebhook(url: String, message: String, isTeams: Boolean = false): Unit = {
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
  if (code != 200) {
    println(s"⚠️ Webhook failed with code: $code")
  }
}

// --- Validation loop ---
val results = datasets.map { dataset =>
  val todayDf = spark.read.format("delta").load(s"${basePath}/${dataset}/date=${runDate}")
  val prevDf  = spark.read.format("delta").load(s"${basePath}/${dataset}/date=${prevDate}")

  val todayMetrics = computeMetrics(todayDf, dataset).withColumn("date", lit(runDate))
  val prevMetrics  = computeMetrics(prevDf, dataset).withColumn("date", lit(prevDate))

  val joined = todayMetrics.as("t").join(prevMetrics.as("p"), Seq("dataset"), "inner")

  joined.select(
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
}.reduce(_ union _)

// --- Apply rules ---
val ruleThresholds = rules.map(r => (r.metricName, r.thresholdPercent)).toMap

val validated = results.withColumn(
  "alerts",
  array(
    when(abs(col("pct_change_record_count")) > ruleThresholds("record_count"), lit("record_count")),
    when(abs(col("pct_change_unique_authors")) > ruleThresholds("unique_authors"), lit("unique_authors")),
    when(abs(col("pct_change_avg_citations")) > ruleThresholds("avg_citations"), lit("avg_citations"))
  ).filter(x => x.isNotNull)
)

// --- Write results ---
validated.write.format("delta").mode("append").option("mergeSchema", "true").save(validationOutputPath)

// --- Trigger alerts ---
val alertsDf = validated.filter(size(col("alerts")) > 0)
alertsDf.collect().foreach { row =>
  val dataset = row.getAs[String]("dataset")
  val alertMetrics = row.getSeq[String](row.fieldIndex("alerts")).mkString(", ")
  val msg =
    s"""
       |🚨 Validation Alert
       |Dataset: $dataset
       |Date: $runDate
       |Metrics exceeded threshold: $alertMetrics
       |Diffs: record_count=${row.getAs[Double]("pct_change_record_count")}%, unique_authors=${row.getAs[Double]("pct_change_unique_authors")}%
       |""".stripMargin

  sendWebhook(slackWebhook, msg)
  sendWebhook(teamsWebhook, msg, isTeams = true)
}
```

---

### 📢 Example Slack / Teams Alert

```yaml
🚨 Validation Alert
Dataset: author_profiles
Date: 2025-10-13
Metrics exceeded threshold: record_count, unique_authors
Diffs: record_count=+22.4%, unique_authors=-15.6%
```

---

### 🧠 Best Practices

- Send aggregated daily summaries (one message per dataset) to reduce noise.
- Add severity tagging (e.g., CRITICAL if >50% change).
- Store webhook URLs in secrets, never in code.
- Optionally integrate with Databricks Jobs webhooks for orchestration-wide alerts.
